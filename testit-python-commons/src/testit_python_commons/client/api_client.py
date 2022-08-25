import os

from testit_api_client import Api, JSONFixture

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter


class ApiClientWorker:

    def __init__(self, config: ClientConfiguration):
        self.__api_client = Api(
            config.get_url(),
            config.get_private_token(),
            config.get_proxy()
        )
        self.__config = config

    def start_launch(self):
        if self.__config.get_testrun_id():
            project_id, json_points = self.__api_client.get_testrun(
                self.__config.get_testrun_id())

            self.__config.set_project_id(project_id)
            return

        model = JSONFixture.create_testrun(
            self.__config.get_project_id(),
            self.__config.get_testrun_name()
        )

        testrun_id = self.__api_client.create_testrun(model)

        self.__api_client.testrun_activity(testrun_id, 'start')
        self.__config.set_testrun_id(testrun_id)

    def write_test(self, test_result: dict):
        autotest = self.__api_client.get_autotest(
            test_result['externalID'],
            self.__config.get_project_id()).json()

        if not autotest:
            model = Converter.test_result_to_autotest_post_model(
                test_result,
                self.__config.get_project_id())

            autotest_id = self.__api_client.create_autotest(model)
        else:
            autotest_id = autotest[0]['id']

            model = Converter.test_result_to_autotest_put_model(
                autotest[0],
                test_result,
                self.__config.get_project_id())

            self.__api_client.update_autotest(model)

        for workitem_id in test_result['workItemsID']:
            self.__api_client.link_autotest(autotest_id, workitem_id)

        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())

        self.__api_client.set_results_for_testrun(
            self.__config.get_testrun_id(),
            model)

    def load_attachments(self, attach_paths):
        attachments = []
        for path in attach_paths:
            if os.path.isfile(path):
                attachment_id = self.__api_client.load_attachment(open(path, "rb"))

                if attachment_id:
                    attachments.append(
                        {
                            'id': attachment_id
                        })
            else:
                print(f'File ({path}) not found!')
        return attachments
