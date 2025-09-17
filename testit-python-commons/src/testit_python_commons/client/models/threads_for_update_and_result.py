import typing

from testit_api_client.models import AutoTestPutModel, AutoTestResultsForTestRunModel


class ThreadForUpdateAndResult:
    def __init__(
            self,
            thread_for_update: typing.Dict[str, AutoTestPutModel],
            thread_results_for_updated_autotests: typing.List[AutoTestResultsForTestRunModel],
            thread_for_autotest_links_to_wi_for_update: typing.Dict[str, typing.List[str]]
    ):
        self.__thread_for_update = thread_for_update
        self.__thread_results_for_updated_autotests = thread_results_for_updated_autotests
        self.__thread_for_autotest_links_to_wi_for_update = thread_for_autotest_links_to_wi_for_update

    def get_thread_for_update(self) -> typing.Dict[str, AutoTestPutModel]:
        return self.__thread_for_update

    def get_thread_results_for_updated_autotests(self) -> typing.List[AutoTestResultsForTestRunModel]:
        return self.__thread_results_for_updated_autotests

    def get_thread_for_autotest_links_to_wi_for_update(self) -> typing.Dict[str, typing.List[str]]:
        return self.__thread_for_autotest_links_to_wi_for_update


class ThreadsForUpdateAndResult:
    def __init__(
            self,
            threads_for_update: typing.List[typing.Dict[str, AutoTestPutModel]],
            threads_results_for_updated_autotests: typing.List[typing.List[AutoTestResultsForTestRunModel]],
            threads_for_autotest_links_to_wi_for_update: typing.List[typing.Dict[str, typing.List[str]]]
    ):
        self.__threads_for_update = threads_for_update
        self.__threads_results_for_updated_autotests = threads_results_for_updated_autotests
        self.__threads_for_autotest_links_to_wi_for_update = threads_for_autotest_links_to_wi_for_update

    def get_threads_for_update(self) -> typing.List[typing.Dict[str, AutoTestPutModel]]:
        return self.__threads_for_update

    def get_threads_results_for_updated_autotests(self) -> typing.List[typing.List[AutoTestResultsForTestRunModel]]:
        return self.__threads_results_for_updated_autotests

    def get_threads_for_autotest_links_to_wi_for_update(self) -> typing.List[typing.Dict[str, typing.List[str]]]:
        return self.__threads_for_autotest_links_to_wi_for_update
