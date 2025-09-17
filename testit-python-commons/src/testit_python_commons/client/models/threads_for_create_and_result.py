import typing

from testit_api_client.models import AutoTestPostModel, AutoTestResultsForTestRunModel


class ThreadForCreateAndResult:
    def __init__(
            self,
            thread_for_create: typing.Dict[str, AutoTestPostModel],
            thread_results_for_created_autotests: typing.List[AutoTestResultsForTestRunModel]
    ):
        self.__thread_for_create = thread_for_create
        self.__thread_results_for_created_autotests = thread_results_for_created_autotests

    def get_thread_for_create(self) -> typing.Dict[str, AutoTestPostModel]:
        return self.__thread_for_create

    def get_thread_results_for_created_autotests(self) -> typing.List[AutoTestResultsForTestRunModel]:
        return self.__thread_results_for_created_autotests


class ThreadsForCreateAndResult:
    def __init__(
            self,
            threads_for_create: typing.List[typing.Dict[str, AutoTestPostModel]],
            threads_results_for_created_autotests: typing.List[typing.List[AutoTestResultsForTestRunModel]]
    ):
        self.__threads_for_create = threads_for_create
        self.__threads_results_for_created_autotests = threads_results_for_created_autotests

    def get_threads_for_create(self) -> typing.List[typing.Dict[str, AutoTestPostModel]]:
        return self.__threads_for_create

    def get_threads_results_for_created_autotests(self) -> typing.List[typing.List[AutoTestResultsForTestRunModel]]:
        return self.__threads_results_for_created_autotests
