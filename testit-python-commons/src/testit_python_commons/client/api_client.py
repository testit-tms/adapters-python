import logging
import os
from datetime import datetime

from testit_api_client import ApiClient, Configuration
from testit_api_client.apis.tags import attachments_api, auto_tests_api, test_runs_api

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.logger import adapter_logger


class ApiClientWorker:
    def __init__(self, config: ClientConfiguration):
        client_config = Configuration(host=config.get_url())

        if config.get_cert_validation() == 'false':
            client_config.verify_ssl = False

        api_client = ApiClient(
            configuration=client_config,
            header_name='Authorization',
            header_value='PrivateToken ' + config.get_private_token()
        )
        self.__attachments_api = attachments_api.AttachmentsApi(api_client=api_client)
        self.__autotest_api = auto_tests_api.AutoTestsApi(api_client=api_client)
        self.__test_run_api = test_runs_api.TestRunsApi(api_client=api_client)
        self.__config = config

    @adapter_logger
    def create_test_run(self):
        test_run_name = f'TestRun_{datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}' if \
            not self.__config.get_test_run_name() else self.__config.get_test_run_name()
        model = Converter.test_run_to_test_run_short_model(
            self.__config.get_project_id(),
            test_run_name)

        response = self.__test_run_api.create_empty(body=model)

        return Converter.get_id_from_create_test_run_response(response)

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__config.set_test_run_id(test_run_id)

    @adapter_logger
    def get_autotests_by_test_run_id(self):
        response = self.__test_run_api.get_test_run_by_id(self.__config.get_test_run_id())

        return Converter.get_resolved_autotests_from_get_test_run_response(
            response,
            self.__config.get_configuration_id())

    @adapter_logger
    def write_test(self, test_result: TestResult):
        model = Converter.autotest_to_autotests_select_model(
            self.__config.get_project_id(),
            test_result.get_external_id())

        autotest = self.__autotest_api.api_v2_auto_tests_search_post(body=model)

        if autotest.body:
            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was found')

            model = Converter.test_result_to_autotest_put_model(
                test_result,
                self.__config.get_project_id())

            self.__autotest_api.update_auto_test(body=model)
            autotest_global_id = autotest.body[0]['id']

            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was updated')
        else:
            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was not found')

            model = Converter.test_result_to_autotest_post_model(
                test_result,
                self.__config.get_project_id())

            autotest_response = self.__autotest_api.create_auto_test(body=model)
            autotest_global_id = autotest_response.body['id']

            logging.debug(f'Autotest "{test_result.get_autotest_name()}" was created')

        if autotest_global_id:
            for work_item_id in test_result.get_work_item_ids():
                try:
                    model = Converter.work_item_id_to_work_item_id_model_model(work_item_id)

                    self.__autotest_api.link_auto_test_to_work_item(
                        path_params={
                            'id': autotest_global_id,
                        },
                        body=model)

                    logging.debug(f'Autotest "{test_result.get_autotest_name()}" was linked with workItem "{work_item_id}"')
                except Exception as exc:
                    logging.error(f'Link with workItem "{work_item_id}" status: {exc.status}\n{exc.body}')

        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())

        self.__test_run_api.set_auto_test_results_for_test_run(
            path_params={
                'id': self.__config.get_test_run_id(),
            },
            body=[model])

        logging.debug(f'Result of the autotest "{test_result.get_autotest_name()}" was set '
                      f'in the test run "{self.__config.get_test_run_id()}"')

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        attachments = []
        for path in attach_paths:
            if os.path.isfile(path):
                try:
                    attachment_response = self.__attachments_api.api_v2_attachments_post(
                        body=dict(
                            file=open(path, "rb")))

                    model = Converter.attachment_id_to_attachment_put_model(
                        attachment_response.body['id'])

                    attachments.append(model)

                    logging.debug(f'Attachment "{path}" was uploaded')
                except Exception as exc:
                    logging.error(f'Upload attachment "{path}" status: {exc.status}\n{exc.body}')
            else:
                logging.error(f'File "{path}" was not found!')
        return attachments
