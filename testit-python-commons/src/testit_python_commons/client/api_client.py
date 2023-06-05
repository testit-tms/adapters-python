import logging
import os
from datetime import datetime

from testit_api_client import ApiClient, Configuration
from testit_api_client.apis import AttachmentsApi, AutoTestsApi, TestRunsApi
from testit_api_client.models import (
    AttachmentPutModel,
    WorkItemIdModel
)

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.logger import adapter_logger


class ApiClientWorker:
    def __init__(self, config: ClientConfiguration):
        client_config = Configuration(host=config.get_url())

        if config.get_cert_validation() == 'false':
            client_config.verify_ssl = False

        client_config.proxy = config.get_proxy()

        self.__api_client = ApiClient(
            configuration=client_config,
            header_name='Authorization',
            header_value='PrivateToken ' + config.get_private_token()
        )
        self.__config = config

    @adapter_logger
    def create_test_run(self):
        test_run_api = TestRunsApi(api_client=self.__api_client)

        test_run_name = f'TestRun_{datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}' if \
            not self.__config.get_test_run_name() else self.__config.get_test_run_name()
        model = Converter.test_run_to_test_run_short_model(
            self.__config.get_project_id(),
            test_run_name
        )

        response = test_run_api.create_empty(test_run_v2_post_short_model=model)

        return Converter.get_id_from_create_test_run_response(response)

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__config.set_test_run_id(test_run_id)

    @adapter_logger
    def get_autotests_by_test_run_id(self):
        test_run_api = TestRunsApi(api_client=self.__api_client)

        response = test_run_api.get_test_run_by_id(self.__config.get_test_run_id())

        return Converter.get_resolved_autotests_from_get_test_run_response(
            response,
            self.__config.get_configuration_id())

    @adapter_logger
    def write_test(self, test_result: TestResult):
        test_run_api = TestRunsApi(api_client=self.__api_client)
        autotest_api = AutoTestsApi(api_client=self.__api_client)

        autotest = autotest_api.get_all_auto_tests(project_id=self.__config.get_project_id(),
                                                   external_id=test_result.get_external_id(),
                                                  deleted=False)

        if autotest:
            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was found')

            model = Converter.test_result_to_autotest_put_model(
                test_result,
                self.__config.get_project_id())
            model.is_flaky = autotest[0]['is_flaky']

            autotest_api.update_auto_test(auto_test_put_model=model)
            autotest_global_id = autotest[0]['id']

            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was updated')
        else:
            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was not found')

            model = Converter.test_result_to_autotest_post_model(
                test_result,
                self.__config.get_project_id())

            autotest_response = autotest_api.create_auto_test(auto_test_post_model=model)
            autotest_global_id = autotest_response['id']

            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was created')

        if autotest_global_id:
            for work_item_id in test_result.get_work_item_ids():
                try:
                    autotest_api.link_auto_test_to_work_item(
                        autotest_global_id,
                        work_item_id_model=WorkItemIdModel(id=work_item_id))

                    logging.debug(f'Autotest "{test_result.get_autotest_name()}" was linked with workItem "{work_item_id}"')
                except Exception as exc:
                    logging.error(f'Link with workItem "{work_item_id}" status: {exc.status}\n{exc.body}')

        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())

        test_run_api.set_auto_test_results_for_test_run(
            id=self.__config.get_test_run_id(),
            auto_test_results_for_test_run_model=[model])

        logging.debug(f'Result of the autotest "{test_result.get_autotest_name()}" was set '
                      f'in the test run "{self.__config.get_test_run_id()}"')

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        attachments_api = AttachmentsApi(api_client=self.__api_client)

        attachments = []
        for path in attach_paths:
            if os.path.isfile(path):
                try:
                    attachment_response = attachments_api.api_v2_attachments_post(file=open(path, "rb"))

                    attachments.append(AttachmentPutModel(attachment_response['id']))

                    logging.debug(f'Attachment "{path}" was uploaded')
                except Exception as exc:
                    logging.error(f'Upload attachment "{path}" status: {exc.status}\n{exc.body}')
            else:
                logging.error(f'File "{path}" was not found!')
        return attachments
