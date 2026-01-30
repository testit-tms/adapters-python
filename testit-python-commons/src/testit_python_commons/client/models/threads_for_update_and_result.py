from typing import Dict, List

from testit_api_client.models import AutoTestUpdateApiModel, AutoTestResultsForTestRunModel


class ThreadForUpdateAndResult:
    def __init__(
            self,
            thread_for_update: Dict[str, AutoTestUpdateApiModel],
            thread_results_for_updated_autotests: Dict[str, AutoTestResultsForTestRunModel],
            thread_for_autotest_links_to_wi_for_update: Dict[str, List[str]]
    ):
        self.__thread_for_update = thread_for_update
        self.__thread_results_for_updated_autotests = thread_results_for_updated_autotests
        self.__thread_for_autotest_links_to_wi_for_update = thread_for_autotest_links_to_wi_for_update

    def get_thread_for_update(self) -> Dict[str, AutoTestUpdateApiModel]:
        return self.__thread_for_update

    def get_thread_results_for_updated_autotests(self) -> Dict[str, AutoTestResultsForTestRunModel]:
        return self.__thread_results_for_updated_autotests

    def get_thread_for_autotest_links_to_wi_for_update(self) -> Dict[str, List[str]]:
        return self.__thread_for_autotest_links_to_wi_for_update


class ThreadsForUpdateAndResult:
    def __init__(
            self,
            threads_for_update: Dict[str, AutoTestUpdateApiModel],
            threads_results_for_updated_autotests: List[Dict[str, AutoTestResultsForTestRunModel]],
            threads_for_autotest_links_to_wi_for_update: Dict[str, List[str]]
    ):
        self.__threads_for_update = threads_for_update
        self.__threads_results_for_updated_autotests = threads_results_for_updated_autotests
        self.__threads_for_autotest_links_to_wi_for_update = threads_for_autotest_links_to_wi_for_update

    def get_threads_for_update(self) -> Dict[str, AutoTestUpdateApiModel]:
        return self.__threads_for_update

    def get_threads_results_for_updated_autotests(self) -> List[Dict[str, AutoTestResultsForTestRunModel]]:
        return self.__threads_results_for_updated_autotests

    def get_threads_for_autotest_links_to_wi_for_update(self) -> Dict[str, List[str]]:
        return self.__threads_for_autotest_links_to_wi_for_update
