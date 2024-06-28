import logging
import os
import typing
from datetime import datetime

from testit_api_client import ApiClient, Configuration
from testit_api_client.apis import AttachmentsApi, AutoTestsApi, TestRunsApi, TestResultsApi
from testit_api_client.models import (
    AttachmentPutModel,
    TestResultModel,
    LinkAutoTestToWorkItemRequest
)

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import \
    TestResultWithAllFixtureStepResults
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.retry import retry


class ApiClientWorker:
    def __init__(self, config: ClientConfiguration):
        api_client_config = self.__get_api_client_configuration(
            url=config.get_url(),
            verify_ssl=config.get_cert_validation() != 'false',
            proxy=config.get_proxy())
        api_client = self.__get_api_client(api_client_config, config.get_private_token())

        self.__test_run_api = TestRunsApi(api_client=api_client)
        self.__autotest_api = AutoTestsApi(api_client=api_client)
        self.__attachments_api = AttachmentsApi(api_client=api_client)
        self.__test_results_api = TestResultsApi(api_client=api_client)
        self.__config = config

    @staticmethod
    @adapter_logger
    def __get_api_client_configuration(url: str, verify_ssl: bool = True, proxy: str = None) -> Configuration:
        api_client_configuration = Configuration(host=url)
        api_client_configuration.verify_ssl = verify_ssl
        api_client_configuration.proxy = proxy

        return api_client_configuration

    @staticmethod
    @adapter_logger
    def __get_api_client(api_client_config: Configuration, token: str) -> ApiClient:
        return ApiClient(
            configuration=api_client_config,
            header_name='Authorization',
            header_value='PrivateToken ' + token)

    @adapter_logger
    def create_test_run(self):
        test_run_name = f'TestRun_{datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}' if \
            not self.__config.get_test_run_name() else self.__config.get_test_run_name()
        model = Converter.test_run_to_test_run_short_model(
            self.__config.get_project_id(),
            test_run_name
        )

        response = self.__test_run_api.create_empty(create_empty_request=model)

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
        model = Converter.project_id_and_external_id_to_auto_tests_search_post_request(
            self.__config.get_project_id(),
            test_result.get_external_id())

        autotest = self.__autotest_api.api_v2_auto_tests_search_post(api_v2_auto_tests_search_post_request=model)

        if autotest:
            self.__update_test(test_result, autotest[0]['is_flaky'])

            autotest_global_id = autotest[0]['id']
        else:
            autotest_global_id = self.__create_test(test_result)

        if autotest_global_id:
            self.__update_autotest_link_from_work_items(autotest_global_id, test_result.get_work_item_ids())

        return self.__load_test_result(test_result)

    @adapter_logger
    def __get_work_items_linked_to_autotest(self, autotest_global_id: str) -> list:
        return self.__autotest_api.get_work_items_linked_to_auto_test(id=autotest_global_id)

    @adapter_logger
    def __update_autotest_link_from_work_items(self, autotest_global_id: str, work_item_ids: list):

        linked_work_items = self.__get_work_items_linked_to_autotest(autotest_global_id)

        for linked_work_item in linked_work_items:
            linked_work_item_id = str(linked_work_item['global_id'])

            if linked_work_item_id in work_item_ids:
                work_item_ids.remove(linked_work_item_id)

                continue

            if self.__config.get_automatic_updation_links_to_test_cases() != 'false':
                self.__unlink_test_to_work_item(autotest_global_id, linked_work_item_id)

        for work_item_id in work_item_ids:
            self.__link_test_to_work_item(autotest_global_id, work_item_id)

    @adapter_logger
    def __create_test(self, test_result: TestResult) -> str:
        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was not found')

        model = Converter.test_result_to_autotest_post_model(
            test_result,
            self.__config.get_project_id())

        autotest_response = self.__autotest_api.create_auto_test(create_auto_test_request=model)

        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was created')

        return autotest_response['id']

    @adapter_logger
    def __update_test(self, test_result: TestResult, is_flaky: bool):
        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was found')

        model = Converter.test_result_to_autotest_put_model(
            test_result,
            self.__config.get_project_id())
        model.is_flaky = is_flaky

        self.__autotest_api.update_auto_test(update_auto_test_request=model)

        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was updated')

    @adapter_logger
    @retry
    def __unlink_test_to_work_item(self, autotest_global_id: str, work_item_id: str):
        self.__autotest_api.delete_auto_test_link_from_work_item(
            id=autotest_global_id,
            work_item_id=work_item_id)

        logging.debug(f'Autotest was unlinked with workItem "{work_item_id}" by global id "{autotest_global_id}')

    @adapter_logger
    @retry
    def __link_test_to_work_item(self, autotest_global_id: str, work_item_id: str):
        self.__autotest_api.link_auto_test_to_work_item(
            autotest_global_id,
            link_auto_test_to_work_item_request=LinkAutoTestToWorkItemRequest(id=work_item_id))

        logging.debug(f'Autotest was linked with workItem "{work_item_id}" by global id "{autotest_global_id}')

    @adapter_logger
    def __load_test_result(self, test_result: TestResult) -> str:
        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())

        response = self.__test_run_api.set_auto_test_results_for_test_run(
            id=self.__config.get_test_run_id(),
            auto_test_results_for_test_run_model=[model])

        logging.debug(f'Result of the autotest "{test_result.get_autotest_name()}" was set '
                      f'in the test run "{self.__config.get_test_run_id()}"')

        return Converter.get_test_result_id_from_testrun_result_post_response(response)

    @adapter_logger
    def get_test_result_by_id(self, test_result_id: str) -> TestResultModel:
        return self.__test_results_api.api_v2_test_results_id_get(id=test_result_id)

    @adapter_logger
    def update_test_results(self, test_results: typing.List[TestResultWithAllFixtureStepResults]):
        for test_result in test_results:
            model = Converter.convert_test_result_model_to_test_results_id_put_request(
                self.get_test_result_by_id(test_result.get_test_result_id()))

            model.set_attribute(
                "setup_results",
                Converter.step_results_to_attachment_put_model_autotest_step_results_model(
                    test_result.get_setup_results()))
            model.set_attribute(
                "teardown_results",
                Converter.step_results_to_attachment_put_model_autotest_step_results_model(
                    test_result.get_teardown_results()))

            try:
                self.__test_results_api.api_v2_test_results_id_put(
                    id=test_result.get_test_result_id(),
                    api_v2_test_results_id_put_request=model)
            except Exception as exc:
                logging.error(f'Cannot update test result with id "{test_result.get_test_result_id()}" status: {exc}')

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        attachments = []

        for path in attach_paths:
            if os.path.isfile(path):
                try:
                    attachment_response = self.__attachments_api.api_v2_attachments_post(file=open(path, "rb"))

                    attachments.append(AttachmentPutModel(attachment_response['id']))

                    logging.debug(f'Attachment "{path}" was uploaded')
                except Exception as exc:
                    logging.error(f'Upload attachment "{path}" status: {exc}')
            else:
                logging.error(f'File "{path}" was not found!')
        return attachments
