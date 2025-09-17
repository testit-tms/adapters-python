from testit_api_client.models import (
    AutoTestPostModel,
    AutoTestPutModel,
    AutoTestResultsForTestRunModel,
)

from testit_python_commons.client.models import (
    ThreadForCreateAndResult,
    ThreadsForCreateAndResult,
    ThreadForUpdateAndResult,
    ThreadsForUpdateAndResult
)
from testit_python_commons.services.logger import adapter_logger
from typing import Dict, List


class ThreadsManager:
    def __init__(self):
        self.__thread_for_create: Dict[str, AutoTestPostModel] = {}
        self.__thread_for_update: Dict[str, AutoTestPutModel] = {}
        self.__threads_results_for_created_autotests: List[Dict[str, AutoTestResultsForTestRunModel]] = []
        self.__threads_results_for_updated_autotests: List[Dict[str, AutoTestResultsForTestRunModel]] = []
        self.__thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]] = {}

    @adapter_logger
    def get_thread_for_create_and_result(self, external_id: str) -> ThreadForCreateAndResult:
        thread_results_for_created_autotests = self.__get_thread_results_for_created_autotests(external_id)

        return ThreadForCreateAndResult(self.__thread_for_create, thread_results_for_created_autotests)

    @adapter_logger
    def get_all_threads_for_create_and_result(self) -> ThreadsForCreateAndResult:
        return ThreadsForCreateAndResult(self.__thread_for_create, self.__threads_results_for_created_autotests)

    @adapter_logger
    def get_thread_for_update_and_result(self, external_id: str) -> ThreadForUpdateAndResult:
        thread_results_for_updated_autotests = self.__get_thread_results_for_updated_autotests(external_id)

        return ThreadForUpdateAndResult(
            self.__thread_for_update,
            thread_results_for_updated_autotests,
            self.__thread_for_autotest_links_to_wi_for_update
        )

    @adapter_logger
    def get_all_threads_for_update_and_result(self) -> ThreadsForUpdateAndResult:
        return ThreadsForUpdateAndResult(
            self.__thread_for_update,
            self.__threads_results_for_updated_autotests,
            self.__thread_for_autotest_links_to_wi_for_update
        )

    @adapter_logger
    def delete_threads_for_create_and_result(self):
        self.__thread_for_create.clear()
        self.__threads_results_for_created_autotests.clear()

    @adapter_logger
    def delete_threads_for_update_and_result(self):
        self.__thread_for_update.clear()
        self.__threads_results_for_updated_autotests.clear()
        self.__thread_for_autotest_links_to_wi_for_update.clear()

    @adapter_logger
    def __get_thread_results_for_created_autotests(self, external_id: str) -> Dict[str, AutoTestResultsForTestRunModel]:
        for thread in self.__threads_results_for_created_autotests:
            if external_id not in thread.keys():
                return thread

        new_thread: Dict[str, AutoTestResultsForTestRunModel] = {}

        self.__threads_results_for_created_autotests.append(new_thread)

        return new_thread

    @adapter_logger
    def __get_thread_results_for_updated_autotests(self, external_id: str) -> Dict[str, AutoTestResultsForTestRunModel]:
        for thread in self.__threads_results_for_updated_autotests:
            if external_id not in thread.keys():
                return thread

        new_thread: Dict[str, AutoTestResultsForTestRunModel] = {}

        self.__threads_results_for_updated_autotests.append(new_thread)

        return new_thread
