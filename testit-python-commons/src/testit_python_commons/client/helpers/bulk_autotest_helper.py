import logging

from testit_api_client.apis import AutoTestsApi, TestRunsApi
from testit_api_client.models import (
    AutoTestCreateApiModel,
    AutoTestUpdateApiModel,
    AutoTestResultsForTestRunModel,
    LinkAutoTestToWorkItemRequest,
    AutoTestWorkItemIdentifierApiResult,
)

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.client.helpers.threads_manager import ThreadsManager
from testit_python_commons.client.models import (
    ThreadForCreateAndResult,
    ThreadsForCreateAndResult,
    ThreadForUpdateAndResult,
    ThreadsForUpdateAndResult
)
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.retry import retry
from testit_python_commons.utils.html_escape_utils import HtmlEscapeUtils
from typing import Dict, List


class BulkAutotestHelper:
    __max_tests_for_import = 100

    def __init__(
            self,
            autotests_api: AutoTestsApi,
            test_runs_api: TestRunsApi,
            config: ClientConfiguration):
        self.__autotests_api = autotests_api
        self.__test_runs_api = test_runs_api
        self.__test_run_id = config.get_test_run_id()
        self.__automatic_updation_links_to_test_cases = config.get_automatic_updation_links_to_test_cases()
        self.__threads_manager = ThreadsManager()

    @adapter_logger
    def add_for_create(
            self,
            create_model: AutoTestCreateApiModel,
            result_model: AutoTestResultsForTestRunModel):
        thread_for_create_and_result: ThreadForCreateAndResult = self.__threads_manager.\
            get_thread_for_create_and_result(create_model.external_id)

        thread_for_create: Dict[str, AutoTestCreateApiModel] = thread_for_create_and_result.get_thread_for_create()
        thread_for_create[create_model.external_id] = create_model

        thread_results_for_created_autotests: Dict[str, AutoTestResultsForTestRunModel] = thread_for_create_and_result\
            .get_thread_results_for_created_autotests()
        thread_results_for_created_autotests[result_model.auto_test_external_id] = result_model

        if len(thread_for_create) >= self.__max_tests_for_import:
            self.__teardown_for_create()

    @adapter_logger
    def add_for_update(
            self,
            update_model: AutoTestUpdateApiModel,
            result_model: AutoTestResultsForTestRunModel,
            autotest_links_to_wi_for_update: Dict[str, List[str]]):
        thread_for_update_and_result: ThreadForUpdateAndResult = self.__threads_manager.\
            get_thread_for_update_and_result(update_model.external_id)

        thread_for_update: Dict[str, AutoTestUpdateApiModel] = thread_for_update_and_result.get_thread_for_update()
        thread_for_update[update_model.external_id] = update_model

        thread_results_for_updated_autotests: Dict[str, AutoTestResultsForTestRunModel] = thread_for_update_and_result\
            .get_thread_results_for_updated_autotests()
        thread_results_for_updated_autotests[result_model.auto_test_external_id] = result_model

        thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]] = thread_for_update_and_result\
            .get_thread_for_autotest_links_to_wi_for_update()
        thread_for_autotest_links_to_wi_for_update.update(autotest_links_to_wi_for_update)

        if len(thread_for_update) >= self.__max_tests_for_import:
            self.__teardown_for_update()

    @adapter_logger
    def teardown(self):
        self.__teardown_for_create()
        self.__teardown_for_update()

    def __teardown_for_create(self):
        all_threads_for_create_and_result: ThreadsForCreateAndResult = self.__threads_manager\
            .get_all_threads_for_create_and_result()

        thread_for_create: Dict[str, AutoTestCreateApiModel] = all_threads_for_create_and_result\
            .get_threads_for_create()
        autotests_for_create = list(thread_for_create.values())

        if autotests_for_create:
            self.__create_tests(autotests_for_create)

        threads_results_for_created_autotests: List[Dict[str, AutoTestResultsForTestRunModel]] = all_threads_for_create_and_result\
            .get_threads_results_for_created_autotests()

        for thread_results_for_created_autotests in threads_results_for_created_autotests:
            self.__load_test_results(list(thread_results_for_created_autotests.values()))

        self.__threads_manager.delete_threads_for_create_and_result()

    def __teardown_for_update(self):
        all_threads_for_update_and_result: ThreadsForUpdateAndResult = self.__threads_manager\
            .get_all_threads_for_update_and_result()

        thread_for_update: Dict[str, AutoTestUpdateApiModel] = all_threads_for_update_and_result\
            .get_threads_for_update()

        autotests_for_update = list(thread_for_update.values())

        if autotests_for_update:
            self.__update_tests(autotests_for_update)

        thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]] = all_threads_for_update_and_result\
            .get_threads_for_autotest_links_to_wi_for_update()

        for autotest_id, work_item_ids in thread_for_autotest_links_to_wi_for_update.items():
            self.__update_autotest_link_from_work_items(autotest_id, work_item_ids)

        threads_results_for_updated_autotests: List[Dict[str, AutoTestResultsForTestRunModel]] = all_threads_for_update_and_result\
            .get_threads_results_for_updated_autotests()

        for thread_results_for_updated_autotests in threads_results_for_updated_autotests:
            self.__load_test_results(list(thread_results_for_updated_autotests.values()))

        self.__threads_manager.delete_threads_for_update_and_result()

    @adapter_logger
    def __bulk_create(
            self,
            thread_for_create: List[AutoTestCreateApiModel],
            thread_results_for_created_autotests: List[AutoTestResultsForTestRunModel]
    ):
        self.__create_tests(thread_for_create)
        self.__load_test_results(thread_results_for_created_autotests)

    @adapter_logger
    def __bulk_update(
            self,
            thread_for_update: Dict[str, AutoTestUpdateApiModel],
            thread_results_for_updated_autotests: List[AutoTestResultsForTestRunModel],
            thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]]
    ):
        self.__update_tests(list(thread_for_update.values()))
        self.__load_test_results(thread_results_for_updated_autotests)

        for autotest_id, work_item_ids in thread_for_autotest_links_to_wi_for_update.items():
            self.__update_autotest_link_from_work_items(autotest_id, work_item_ids)

    @adapter_logger
    def __create_tests(self, autotests_for_create: List[AutoTestCreateApiModel]):
        logging.debug(f'Creating autotests: "{autotests_for_create}')

        autotests_for_create = HtmlEscapeUtils.escape_html_in_object(autotests_for_create)
        self.__autotests_api.create_multiple(auto_test_create_api_model=autotests_for_create)

        logging.debug(f'Autotests were created')

    @adapter_logger
    def __update_tests(self, autotests_for_update: List[AutoTestUpdateApiModel]):
        logging.debug(f'Updating autotests: {autotests_for_update}')

        autotests_for_update = HtmlEscapeUtils.escape_html_in_object(autotests_for_update)
        self.__autotests_api.update_multiple(auto_test_update_api_model=autotests_for_update)

        logging.debug(f'Autotests were updated')

    @adapter_logger
    def __load_test_results(self, test_results: List[AutoTestResultsForTestRunModel]):
        logging.debug(f'Loading test results: {test_results}')

        test_results = HtmlEscapeUtils.escape_html_in_object(test_results)
        self.__test_runs_api.set_auto_test_results_for_test_run(
            id=self.__test_run_id,
            auto_test_results_for_test_run_model=test_results)

    # TODO: delete after fix PUT/api/v2/autoTests
    @adapter_logger
    def __get_work_items_linked_to_autotest(self, autotest_global_id: str) -> List[AutoTestWorkItemIdentifierApiResult]:
        return self.__autotests_api.get_work_items_linked_to_auto_test(id=autotest_global_id)

    # TODO: delete after fix PUT/api/v2/autoTests
    @adapter_logger
    @retry
    def __unlink_test_to_work_item(self, autotest_global_id: str, work_item_id: str):
        self.__autotests_api.delete_auto_test_link_from_work_item(
            id=autotest_global_id,
            work_item_id=work_item_id)

        logging.debug(f'Autotest was unlinked with workItem "{work_item_id}" by global id "{autotest_global_id}')

    # TODO: delete after fix PUT/api/v2/autoTests
    @adapter_logger
    @retry
    def __link_test_to_work_item(self, autotest_global_id: str, work_item_id: str):
        self.__autotests_api.link_auto_test_to_work_item(
            autotest_global_id,
            link_auto_test_to_work_item_request=LinkAutoTestToWorkItemRequest(id=work_item_id))

        logging.debug(f'Autotest was linked with workItem "{work_item_id}" by global id "{autotest_global_id}')

    # TODO: delete after fix PUT/api/v2/autoTests
    @adapter_logger
    def __update_autotest_link_from_work_items(self, autotest_global_id: str, work_item_ids: list):
        linked_work_items = self.__get_work_items_linked_to_autotest(autotest_global_id)

        for linked_work_item in linked_work_items:
            linked_work_item_id = str(linked_work_item.global_id)

            if linked_work_item_id in work_item_ids:
                work_item_ids.remove(linked_work_item_id)

                continue

            if self.__automatic_updation_links_to_test_cases:
                self.__unlink_test_to_work_item(autotest_global_id, linked_work_item_id)

        for work_item_id in work_item_ids:
            self.__link_test_to_work_item(autotest_global_id, work_item_id)
