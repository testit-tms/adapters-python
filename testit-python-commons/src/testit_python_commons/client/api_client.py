import logging
import os
import typing
from datetime import datetime

from testit_api_client import ApiClient, Configuration
from testit_api_client.api import AttachmentsApi, AutoTestsApi, TestRunsApi, TestResultsApi, WorkItemsApi
from testit_api_client.models import (
    AutoTestApiResult,
    AutoTestPostModel,
    AutoTestPutModel,
    AttachmentPutModel,
    AutoTestResultsForTestRunModel,
    TestResultResponse,
    WorkItemIdModel,
    WorkItemIdentifierModel
)

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.retry import retry
from testit_python_commons.utils.html_escape_utils import HtmlEscapeUtils


class ApiClientWorker:
    __max_tests_for_write = 100

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
        self.__work_items_api = WorkItemsApi(api_client=api_client)
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

    @staticmethod
    def _escape_html_in_model(model):
        """Apply HTML escaping to all models before sending to API"""
        return HtmlEscapeUtils.escape_html_in_object(model)

    @adapter_logger
    def create_test_run(self):
        test_run_name = f'TestRun_{datetime.today().strftime("%Y-%m-%dT%H:%M:%S")}' if \
            not self.__config.get_test_run_name() else self.__config.get_test_run_name()
        model = Converter.test_run_to_test_run_short_model(
            self.__config.get_project_id(),
            test_run_name
        )
        model = self._escape_html_in_model(model)

        response = self.__test_run_api.create_empty(create_empty_test_run_api_model=model)

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

        autotests = self.__autotest_api.api_v2_auto_tests_search_post(auto_test_search_api_model=model)

        if autotests:
            self.__update_test(test_result, autotests[0])
        else:
            self.__create_test(test_result)

        return self.__load_test_result(test_result)

    @adapter_logger
    def write_tests(self, test_results: typing.List[TestResult], fixture_containers: dict):
        autotests_for_create = []
        autotests_for_update = []
        results_for_autotests_being_created = []
        results_for_autotests_being_updated = []

        for test_result in test_results:
            test_result = self.__add_fixtures_to_test_result(test_result, fixture_containers)

            model = Converter.project_id_and_external_id_to_auto_tests_search_post_request(
                self.__config.get_project_id(),
                test_result.get_external_id())

            test_result_model = Converter.test_result_to_testrun_result_post_model(
                test_result,
                self.__config.get_configuration_id())

            autotests = self.__autotest_api.api_v2_auto_tests_search_post(auto_test_search_api_model=model)

            if autotests:
                autotest_for_update = self.__prepare_to_update_autotest(test_result, autotests[0])

                autotests_for_update.append(autotest_for_update)
                results_for_autotests_being_updated.append(test_result_model)

                if len(autotests_for_update) >= self.__max_tests_for_write:
                    self.__update_tests(autotests_for_update)
                    self.__load_test_results(results_for_autotests_being_updated)

                    autotests_for_update.clear()
                    results_for_autotests_being_updated.clear()
            else:
                autotest_for_create = self.__prepare_to_create_autotest(test_result)

                autotests_for_create.append(autotest_for_create)
                results_for_autotests_being_created.append(test_result_model)

                if len(autotests_for_create) >= self.__max_tests_for_write:
                    self.__create_tests(autotests_for_create)
                    self.__load_test_results(results_for_autotests_being_created)

                    autotests_for_create.clear()
                    results_for_autotests_being_created.clear()

        if len(autotests_for_update) > 0:
            self.__update_tests(autotests_for_update)
            self.__load_test_results(results_for_autotests_being_updated)

            autotests_for_update.clear()
            results_for_autotests_being_updated.clear()

        if len(autotests_for_create) > 0:
            self.__create_tests(autotests_for_create)
            self.__load_test_results(results_for_autotests_being_created)

            autotests_for_create.clear()
            results_for_autotests_being_created.clear()

    @adapter_logger
    def __prepare_to_create_autotest(self, test_result: TestResult) -> AutoTestPostModel:
        logging.debug('Preparing to create the auto test ', test_result.get_external_id())

        model = Converter.test_result_to_autotest_post_model(
            test_result,
            self.__config.get_project_id())
        model.work_item_ids_for_link_with_auto_test = self.__get_work_item_uuids_for_link_with_auto_test(
            test_result.get_work_item_ids())

        return model

    @adapter_logger
    def __prepare_to_update_autotest(
            self,
            test_result: TestResult,
            autotest: AutoTestApiResult) -> AutoTestPutModel:
        logging.debug('Preparing to update the auto test ', test_result.get_external_id())

        model = Converter.test_result_to_autotest_put_model(
            test_result,
            self.__config.get_project_id())
        model.is_flaky = autotest.is_flaky
        model.work_item_ids_for_link_with_auto_test = self.__get_work_item_uuids_for_link_with_auto_test(
            test_result.get_work_item_ids(),
            str(autotest.global_id))

        return model

    @staticmethod
    @adapter_logger
    def __add_fixtures_to_test_result(
            test_result: TestResult,
            fixtures_containers: dict) -> TestResult:
        setup_results = []
        teardown_results = []

        for uuid, fixtures_container in fixtures_containers.items():
            if test_result.get_external_id() in fixtures_container.external_ids:
                if fixtures_container.befores:
                    setup_results += fixtures_container.befores[0].steps

                if fixtures_container.afters:
                    teardown_results = fixtures_container.afters[0].steps + teardown_results

        test_result.set_setup_results(setup_results)
        test_result.set_teardown_results(teardown_results)

        return test_result

    @adapter_logger
    def __get_work_item_uuids_for_link_with_auto_test(
            self,
            work_item_ids: list,
            autotest_global_id: str = None) -> list:
        linked_work_items = []

        if autotest_global_id:
            linked_work_items = self.__get_work_items_linked_to_autotest(autotest_global_id)

        work_item_uuids = self.__prepare_list_of_work_item_uuids(linked_work_items, work_item_ids)

        return work_item_uuids

    @adapter_logger
    def __prepare_list_of_work_item_uuids(
            self,
            linked_work_items: list,
            work_item_ids: list) -> list:
        work_item_uuids = []

        for linked_work_item in linked_work_items:
            linked_work_item_id = str(linked_work_item.global_id)
            linked_work_item_uuid = linked_work_item.id

            if linked_work_item_id in work_item_ids:
                work_item_ids.remove(linked_work_item_id)
                work_item_uuids.append(linked_work_item_uuid)

                continue

            if self.__config.get_automatic_updation_links_to_test_cases() != 'true':
                work_item_uuids.append(linked_work_item_uuid)

        for work_item_id in work_item_ids:
            work_item_uuid = self.__get_work_item_uuid_by_work_item_id(work_item_id)

            if work_item_uuid:
                work_item_uuids.append(work_item_uuid)

        return work_item_uuids

    @adapter_logger
    def __get_work_item_uuid_by_work_item_id(self, work_item_id: str) -> str or None:
        logging.debug('Getting workitem by id ' + work_item_id)

        try:
            work_item = self.__work_items_api.get_work_item_by_id(id=work_item_id)

            logging.debug(f'Got workitem {work_item}')

            return work_item.id
        except Exception as exc:
            logging.error(f'Getting workitem by id {work_item_id} status: {exc}')

    @adapter_logger
    def __get_work_items_linked_to_autotest(self, autotest_global_id: str) -> typing.List[WorkItemIdentifierModel]:
        return self.__autotest_api.get_work_items_linked_to_auto_test(id=autotest_global_id)

    @adapter_logger
    def __update_autotest_link_from_work_items(self, autotest_global_id: str, work_item_ids: list):
        linked_work_items = self.__get_work_items_linked_to_autotest(autotest_global_id)

        for linked_work_item in linked_work_items:
            linked_work_item_id = str(linked_work_item.global_id)

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

        model = self.__prepare_to_create_autotest(test_result)
        model = self._escape_html_in_model(model)

        autotest_response = self.__autotest_api.create_auto_test(auto_test_post_model=model)

        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was created')

        return autotest_response.id

    @adapter_logger
    def __create_tests(self, autotests_for_create: typing.List[AutoTestPostModel]):
        logging.debug(f'Creating autotests: "{autotests_for_create}')

        autotests_for_create = self._escape_html_in_model(autotests_for_create)
        self.__autotest_api.create_multiple(auto_test_post_model=autotests_for_create)

        logging.debug(f'Autotests were created')

    @adapter_logger
    def __update_test(self, test_result: TestResult, autotest: AutoTestApiResult):
        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was found')

        model = self.__prepare_to_update_autotest(test_result, autotest)
        model = self._escape_html_in_model(model)

        self.__autotest_api.update_auto_test(auto_test_put_model=model)

        logging.debug(f'Autotest "{test_result.get_autotest_name()}" was updated')

    @adapter_logger
    def __update_tests(self, autotests_for_update: typing.List[AutoTestPutModel]):
        logging.debug(f'Updating autotests: {autotests_for_update}')

        autotests_for_update = self._escape_html_in_model(autotests_for_update)
        self.__autotest_api.update_multiple(auto_test_put_model=autotests_for_update)

        logging.debug(f'Autotests were updated')

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
            work_item_id_model=WorkItemIdModel(id=work_item_id))

        logging.debug(f'Autotest was linked with workItem "{work_item_id}" by global id "{autotest_global_id}')

    @adapter_logger
    def __load_test_result(self, test_result: TestResult) -> str:
        model = Converter.test_result_to_testrun_result_post_model(
            test_result,
            self.__config.get_configuration_id())
        model = self._escape_html_in_model(model)

        response = self.__test_run_api.set_auto_test_results_for_test_run(
            id=self.__config.get_test_run_id(),
            auto_test_results_for_test_run_model=[model])

        logging.debug(f'Result of the autotest "{test_result.get_autotest_name()}" was set '
                      f'in the test run "{self.__config.get_test_run_id()}"')

        return Converter.get_test_result_id_from_testrun_result_post_response(response)

    @adapter_logger
    def __load_test_results(self, test_results: typing.List[AutoTestResultsForTestRunModel]):
        logging.debug(f'Loading test results: {test_results}')

        test_results = self._escape_html_in_model(test_results)
        self.__test_run_api.set_auto_test_results_for_test_run(
            id=self.__config.get_test_run_id(),
            auto_test_results_for_test_run_model=test_results)

    @adapter_logger
    def get_test_result_by_id(self, test_result_id: str) -> TestResultResponse:
        return self.__test_results_api.api_v2_test_results_id_get(id=test_result_id)

    @adapter_logger
    def update_test_results(self, fixtures_containers: dict, test_result_ids: dict):
        test_results = Converter.fixtures_containers_to_test_results_with_all_fixture_step_results(
            fixtures_containers, test_result_ids)

        for test_result in test_results:
            model = Converter.convert_test_result_model_to_test_results_id_put_request(
                self.get_test_result_by_id(test_result.get_test_result_id()))

            model.setup_results = Converter.step_results_to_auto_test_step_result_update_request(
                    test_result.get_setup_results())
            model.teardown_results = Converter.step_results_to_auto_test_step_result_update_request(
                    test_result.get_teardown_results())
            
            model = self._escape_html_in_model(model)

            try:
                self.__test_results_api.api_v2_test_results_id_put(
                    id=test_result.get_test_result_id(),
                    test_result_update_v2_request=model)
            except Exception as exc:
                logging.error(f'Cannot update test result with id "{test_result.get_test_result_id()}" status: {exc}')

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        attachments = []

        for path in attach_paths:
            if os.path.isfile(path):
                try:
                    attachment_response = self.__attachments_api.api_v2_attachments_post(
                        file=path)

                    attachment_model = AttachmentPutModel(id=attachment_response.id)
                    attachment_model = self._escape_html_in_model(attachment_model)
                    attachments.append(attachment_model)

                    logging.debug(f'Attachment "{path}" was uploaded')
                except Exception as exc:
                    logging.error(f'Upload attachment "{path}" status: {exc}')
            else:
                logging.error(f'File "{path}" was not found!')
        return attachments
