import os

from testit_api_client import ApiClient
from testit_api_client import Configuration
from testit_api_client.models import (
    TestRunV2PostShortModel,
    WorkItemIdModel,
    AttachmentPutModel
    )
from testit_api_client.apis import TestRunsApi
from testit_api_client.apis import AutoTestsApi
from testit_api_client.apis import AttachmentsApi

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter
from testit_python_commons.services.utils import Utils
from testit_python_commons.models.adapter_mode import AdapterMode


class ApiClientWorker:

    def __init__(self, config: ClientConfiguration):
        self.__api_client = ApiClient(
            configuration=Configuration(host=config.get_url()),
            header_name='Authorization',
            header_value='PrivateToken ' + config.get_private_token()
        )

        self.__config = config

    def start_launch(self):
        test_run_api = TestRunsApi(api_client=self.__api_client)

        if self.__config.get_mode() == AdapterMode.NEW_TEST_RUN:
            model = TestRunV2PostShortModel(
                project_id=self.__config.get_project_id(),
                name=self.__config.get_test_run_name()
            )

            response = test_run_api.create_empty(test_run_v2_post_short_model=model)

            test_run_id = response['id']

            test_run_api.start_test_run(test_run_id)

            self.__config.set_test_run_id(test_run_id)

            return

        response = test_run_api.get_test_run_by_id(self.__config.get_test_run_id())

        self.__config.set_project_id(response['projectId'])

        if self.__config.get_mode() == AdapterMode.RUN_ALL_TESTS:
            return

        test_results = response['testResults']

        return Utils.autotests_parser(
                test_results,
                self.__config.get_configuration_id())

    def write_test(self, test_result: dict):
        test_run_api = TestRunsApi(api_client=self.__api_client)
        autotest_api = AutoTestsApi(api_client=self.__api_client)

        model = Converter.test_result_to_autotest_post_model(
            test_result,
            self.__config.get_project_id())
        try:
            autotest_response = autotest_api.create_auto_test(auto_test_post_model=model)
        except Exception as exc:
            if exc.status == 409:
                model = Converter.test_result_to_autotest_put_model(
                    test_result,
                    self.__config.get_project_id())

                autotest_response = autotest_api.update_auto_test(auto_test_put_model=model)
            else:
                raise exc

        if autotest_response:
            for work_item_id in test_result['workItemsID']:
                try:
                    autotest_api.link_auto_test_to_work_item(
                        autotest_response['id'],
                        work_item_id_model=WorkItemIdModel(id=work_item_id))
                except Exception as exc:
                    print(f"Link with workItem {work_item_id} status: {exc.status}\n{exc.body}")

        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())

        test_run_api.set_auto_test_results_for_test_run(
            id=self.__config.get_test_run_id(),
            auto_test_results_for_test_run_model=[model])

    def load_attachments(self, attach_paths: list or tuple):
        attachments_api = AttachmentsApi(api_client=self.__api_client)

        attachments = []
        for path in attach_paths:
            if os.path.isfile(path):
                try:
                    attachment_response = attachments_api.api_v2_attachments_post(file=open(path, "rb"))

                    attachments.append(AttachmentPutModel(attachment_response['id']))
                except Exception as exc:
                    print(f'Load {path} status: {exc.status}\n{exc.body}')
            else:
                print(f'File ({path}) not found!')
        return attachments
