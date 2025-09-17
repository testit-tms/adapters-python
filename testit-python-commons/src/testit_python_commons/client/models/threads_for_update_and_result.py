from typing import Dict, List

from testit_api_client.models import AutoTestPutModel, AutoTestResultsForTestRunModel


class ThreadForUpdateAndResult:
    def __init__(
            self,
            thread_for_update: Dict[str, AutoTestPutModel],
            thread_results_for_updated_autotests: List[AutoTestResultsForTestRunModel],
            thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]]
    ):
        self.__thread_for_update = thread_for_update
        self.__thread_results_for_updated_autotests = thread_results_for_updated_autotests
        self.__thread_for_autotest_links_to_wi_for_update = thread_for_autotest_links_to_wi_for_update

    def get_thread_for_update(self) -> Dict[str, AutoTestPutModel]:
        return self.__thread_for_update

    def get_thread_results_for_updated_autotests(self) -> List[AutoTestResultsForTestRunModel]:
        return self.__thread_results_for_updated_autotests

    def get_thread_for_autotest_links_to_wi_for_update(self) -> Dict[str, List[str]]:
        return self.__thread_for_autotest_links_to_wi_for_update


class ThreadsForUpdateAndResult:
    def __init__(
            self,
            threads_for_update: List[Dict[str, AutoTestPutModel]],
            threads_results_for_updated_autotests: List[List[AutoTestResultsForTestRunModel]],
            threads_for_autotest_links_to_wi_for_update: List[Dict[str, List[str]]]
    ):
        self.__threads_for_update = threads_for_update
        self.__threads_results_for_updated_autotests = threads_results_for_updated_autotests
        self.__threads_for_autotest_links_to_wi_for_update = threads_for_autotest_links_to_wi_for_update

    def get_threads_for_update(self) -> List[Dict[str, AutoTestPutModel]]:
        return self.__threads_for_update

    def get_threads_results_for_updated_autotests(self) -> List[List[AutoTestResultsForTestRunModel]]:
        return self.__threads_results_for_updated_autotests

    def get_threads_for_autotest_links_to_wi_for_update(self) -> List[Dict[str, List[str]]]:
        return self.__threads_for_autotest_links_to_wi_for_update
