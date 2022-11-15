import os
import logging
from datetime import datetime

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


class ApiClientWorker:

    def __init__(self, config: ClientConfiguration):
        self.__api_client = ApiClient(
            configuration=Configuration(host=config.get_url()),
            header_name='Authorization',
            header_value='PrivateToken ' + config.get_private_token()
        )

        self.__config = config

    def create_test_run(self):
        test_run_api = TestRunsApi(api_client=self.__api_client)

        test_run_name = f'TestRun_{datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}' if not self.__config.get_test_run_name() else self.__config.get_test_run_name()
        model = TestRunV2PostShortModel(
            project_id=self.__config.get_project_id(),
            name=test_run_name
        )

        response = test_run_api.create_empty(test_run_v2_post_short_model=model)

        return response['id']

    def set_test_run_id(self, test_run_id: str):
        self.__config.set_test_run_id(test_run_id)

    def get_autotests_by_test_run_id(self):
        test_run_api = TestRunsApi(api_client=self.__api_client)

        response = test_run_api.get_test_run_by_id(self.__config.get_test_run_id())

        test_results = response['_data_store']['test_results']

        return Utils.autotests_parser(
            test_results,
            self.__config.get_configuration_id())

    def write_test(self, test_result: dict):
        test_run_api = TestRunsApi(api_client=self.__api_client)
        autotest_api = AutoTestsApi(api_client=self.__api_client)

        autotest = autotest_api.get_all_auto_tests(project_id=self.__config.get_project_id(),
                                                   external_id=test_result['externalID'])
        autotest_global_id = None
        if autotest:
            model = Converter.test_result_to_autotest_put_model(
                test_result,
                self.__config.get_project_id())

            autotest_api.update_auto_test(auto_test_put_model=model)
            autotest_global_id = autotest[0]['id']

        else:
            model = Converter.test_result_to_autotest_post_model(
                test_result,
                self.__config.get_project_id())

            autotest_response = autotest_api.create_auto_test(auto_test_post_model=model)
            autotest_global_id = autotest_response['id']

        if autotest_global_id:
            for work_item_id in test_result['workItemsID']:
                try:
                    autotest_api.link_auto_test_to_work_item(
                        autotest_global_id,
                        work_item_id_model=WorkItemIdModel(id=work_item_id))
                except Exception as exc:
                    logging.error(f"Link with workItem {work_item_id} status: {exc.status}\n{exc.body}")

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
                    logging.error(f'Load {path} status: {exc.status}\n{exc.body}')
            else:
                logging.error(f'File ({path}) not found!')
        return attachments
