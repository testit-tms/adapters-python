import logging
import typing

from testit_api_client.apis import AutoTestsApi, TestRunsApi
from testit_api_client.models import (
    AutoTestPostModel,
    AutoTestPutModel,
    AutoTestResultsForTestRunModel,
    LinkAutoTestToWorkItemRequest,
    WorkItemIdentifierModel,
)

from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.retry import retry
from testit_python_commons.utils.html_escape_utils import HtmlEscapeUtils


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
        self.__autotests_for_create = []
        self.__autotests_for_update = []
        self.__autotest_links_to_wi_for_update = {}
        self.__results_for_autotests_being_created = []
        self.__results_for_autotests_being_updated = []

    @adapter_logger
    def add_for_create(
            self,
            create_model: AutoTestPostModel,
            result_model: AutoTestResultsForTestRunModel):
        self.__autotests_for_create.append(create_model)
        self.__results_for_autotests_being_created.append(result_model)

        if len(self.__autotests_for_create) >= self.__max_tests_for_import:
            self.__bulk_create()

    @adapter_logger
    def add_for_update(
            self,
            update_model: AutoTestPutModel,
            result_model: AutoTestResultsForTestRunModel,
            autotest_links_to_wi_for_update: dict):
        self.__autotests_for_update.append(update_model)
        self.__results_for_autotests_being_updated.append(result_model)
        self.__autotest_links_to_wi_for_update.update(autotest_links_to_wi_for_update)

        if len(self.__autotests_for_create) >= self.__max_tests_for_import:
            self.__bulk_update()

    @adapter_logger
    def teardown(self):
        if len(self.__autotests_for_create) > 0:
            self.__bulk_create()

        if len(self.__autotests_for_update) > 0:
            self.__bulk_update()

    @adapter_logger
    def __bulk_create(self):
        self.__create_tests(self.__autotests_for_create)
        self.__load_test_results(self.__results_for_autotests_being_created)

        self.__autotests_for_create.clear()
        self.__results_for_autotests_being_created.clear()

    @adapter_logger
    def __bulk_update(self):
        self.__update_tests(self.__autotests_for_update)
        self.__load_test_results(self.__results_for_autotests_being_updated)

        for autotest_id, work_item_ids in self.__autotest_links_to_wi_for_update.items():
            self.__update_autotest_link_from_work_items(autotest_id, work_item_ids)

        self.__autotests_for_update.clear()
        self.__results_for_autotests_being_updated.clear()
        self.__autotest_links_to_wi_for_update.clear()

    @adapter_logger
    def __create_tests(self, autotests_for_create: typing.List[AutoTestPostModel]):
        logging.debug(f'Creating autotests: "{autotests_for_create}')

        autotests_for_create = HtmlEscapeUtils.escape_html_in_object(autotests_for_create)
        self.__autotests_api.create_multiple(auto_test_post_model=autotests_for_create)

        logging.debug(f'Autotests were created')

    @adapter_logger
    def __update_tests(self, autotests_for_update: typing.List[AutoTestPutModel]):
        logging.debug(f'Updating autotests: {autotests_for_update}')

        autotests_for_update = HtmlEscapeUtils.escape_html_in_object(autotests_for_update)
        self.__autotests_api.update_multiple(auto_test_put_model=autotests_for_update)

        logging.debug(f'Autotests were updated')

    @adapter_logger
    def __load_test_results(self, test_results: typing.List[AutoTestResultsForTestRunModel]):
        logging.debug(f'Loading test results: {test_results}')

        test_results = HtmlEscapeUtils.escape_html_in_object(test_results)
        self.__test_runs_api.set_auto_test_results_for_test_run(
            id=self.__test_run_id,
            auto_test_results_for_test_run_model=test_results)

    # TODO: delete after fix PUT/api/v2/autoTests
    @adapter_logger
    def __get_work_items_linked_to_autotest(self, autotest_global_id: str) -> typing.List[WorkItemIdentifierModel]:
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

            if self.__automatic_updation_links_to_test_cases != 'false':
                self.__unlink_test_to_work_item(autotest_global_id, linked_work_item_id)

        for work_item_id in work_item_ids:
            self.__link_test_to_work_item(autotest_global_id, work_item_id)
