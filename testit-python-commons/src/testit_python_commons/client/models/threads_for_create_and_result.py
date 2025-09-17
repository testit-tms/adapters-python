from typing import Dict, List

from testit_api_client.models import AutoTestPostModel, AutoTestResultsForTestRunModel


class ThreadForCreateAndResult:
    def __init__(
            self,
            thread_for_create: Dict[str, AutoTestPostModel],
            thread_results_for_created_autotests: List[AutoTestResultsForTestRunModel]
    ):
        self.__thread_for_create = thread_for_create
        self.__thread_results_for_created_autotests = thread_results_for_created_autotests

    def get_thread_for_create(self) -> Dict[str, AutoTestPostModel]:
        return self.__thread_for_create

    def get_thread_results_for_created_autotests(self) -> List[AutoTestResultsForTestRunModel]:
        return self.__thread_results_for_created_autotests


class ThreadsForCreateAndResult:
    def __init__(
            self,
            threads_for_create: List[Dict[str, AutoTestPostModel]],
            threads_results_for_created_autotests: List[List[AutoTestResultsForTestRunModel]]
    ):
        self.__threads_for_create = threads_for_create
        self.__threads_results_for_created_autotests = threads_results_for_created_autotests

    def get_threads_for_create(self) -> List[Dict[str, AutoTestPostModel]]:
        return self.__threads_for_create

    def get_threads_results_for_created_autotests(self) -> List[List[AutoTestResultsForTestRunModel]]:
        return self.__threads_results_for_created_autotests
