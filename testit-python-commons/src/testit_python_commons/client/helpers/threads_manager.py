import typing
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


class ThreadsManager:
    def __init__(self):
        self.__threads_for_create: typing.List[typing.Dict[str, AutoTestPostModel]] = []
        self.__threads_for_update: typing.List[typing.Dict[str, AutoTestPutModel]] = []
        self.__threads_results_for_created_autotests: typing.List[typing.List[AutoTestResultsForTestRunModel]] = []
        self.__threads_results_for_updated_autotests: typing.List[typing.List[AutoTestResultsForTestRunModel]] = []
        self.__threads_for_autotest_links_to_wi_for_update: typing.List[typing.Dict[str, typing.List[str]]] = []

    @adapter_logger
    def get_thread_for_create_and_result(self, external_id: str) -> ThreadForCreateAndResult:
        thread_for_create = self.__get_thread_for_create(external_id)
        thread_index = self.__threads_for_create.index(thread_for_create)
        thread_results_for_created_autotests = self.__get_thread_results_for_created_autotests(thread_index)

        return ThreadForCreateAndResult(thread_for_create, thread_results_for_created_autotests)

    @adapter_logger
    def get_all_threads_for_create_and_result(self) -> ThreadsForCreateAndResult:
        return ThreadsForCreateAndResult(self.__threads_for_create, self.__threads_results_for_created_autotests)

    @adapter_logger
    def get_thread_for_update_and_result(self, external_id: str) -> ThreadForUpdateAndResult:
        thread_for_update = self.__get_thread_for_update(external_id)
        thread_index = self.__threads_for_update.index(thread_for_update)
        thread_results_for_updated_autotests = self.__get_thread_results_for_updated_autotests(thread_index)
        thread_for_autotest_links_to_wi_for_update = self.__get_thread_for_autotest_links_to_wi_for_update(thread_index)

        return ThreadForUpdateAndResult(
            thread_for_update,
            thread_results_for_updated_autotests,
            thread_for_autotest_links_to_wi_for_update
        )

    @adapter_logger
    def get_all_threads_for_update_and_result(self) -> ThreadsForUpdateAndResult:
        return ThreadsForUpdateAndResult(
            self.__threads_for_update,
            self.__threads_results_for_updated_autotests,
            self.__threads_for_autotest_links_to_wi_for_update
        )

    @adapter_logger
    def delete_thread_for_create_and_result(self, thread_for_create_and_result: ThreadForCreateAndResult):
        thread_for_create = thread_for_create_and_result.get_thread_for_create()
        thread_results_for_created_autotests = thread_for_create_and_result.get_thread_results_for_created_autotests()

        self.__threads_for_create.remove(thread_for_create)
        self.__threads_results_for_created_autotests.remove(thread_results_for_created_autotests)

    @adapter_logger
    def delete_thread_for_update_and_result(self, thread_for_update_and_result: ThreadForUpdateAndResult):
        thread_for_update = thread_for_update_and_result.get_thread_for_update()
        thread_results_for_updated_autotests = thread_for_update_and_result.get_thread_results_for_updated_autotests()
        thread_for_autotest_links_to_wi_for_update = thread_for_update_and_result\
            .get_thread_for_autotest_links_to_wi_for_update()

        self.__threads_for_update.remove(thread_for_update)
        self.__threads_results_for_updated_autotests.remove(thread_results_for_updated_autotests)
        self.__threads_for_autotest_links_to_wi_for_update.remove(thread_for_autotest_links_to_wi_for_update)

    @adapter_logger
    def __get_thread_for_create(self, external_id: str) -> typing.Dict[str, AutoTestPostModel]:
        for thread in self.__threads_for_create:
            if external_id not in thread.keys():
                return thread

        new_thread: typing.Dict[str, AutoTestPostModel] = {}

        self.__threads_for_create.append(new_thread)

        return new_thread

    @adapter_logger
    def __get_thread_for_update(self, external_id: str) -> typing.Dict[str, AutoTestPutModel]:
        for thread in self.__threads_for_update:
            if external_id not in thread.keys():
                return thread

        new_thread: typing.Dict[str, AutoTestPutModel] = {}

        self.__threads_for_update.append(new_thread)

        return new_thread

    @adapter_logger
    def __get_thread_results_for_created_autotests(
            self, thread_index: int) -> typing.List[AutoTestResultsForTestRunModel]:
        if 0 <= thread_index < len(self.__threads_results_for_created_autotests):
            return self.__threads_results_for_created_autotests[thread_index]

        new_thread_results_for_created_autotests: typing.List[AutoTestResultsForTestRunModel] = []

        self.__threads_results_for_created_autotests.append(new_thread_results_for_created_autotests)

        return new_thread_results_for_created_autotests

    @adapter_logger
    def __get_thread_results_for_updated_autotests(
            self, thread_index: int) -> typing.List[AutoTestResultsForTestRunModel]:
        if 0 <= thread_index < len(self.__threads_results_for_updated_autotests):
            return self.__threads_results_for_updated_autotests[thread_index]

        new_thread_results_for_updated_autotests: typing.List[AutoTestResultsForTestRunModel] = []

        self.__threads_results_for_updated_autotests.append(new_thread_results_for_updated_autotests)

        return new_thread_results_for_updated_autotests

    @adapter_logger
    def __get_thread_for_autotest_links_to_wi_for_update(
            self, thread_index: int) -> typing.Dict[str, typing.List[str]]:
        if 0 <= thread_index < len(self.__threads_for_autotest_links_to_wi_for_update):
            return self.__threads_for_autotest_links_to_wi_for_update[thread_index]

        new_thread_for_autotest_links_to_wi_for_update: typing.Dict[str, typing.List[str]] = {}

        self.__threads_for_autotest_links_to_wi_for_update.append(new_thread_for_autotest_links_to_wi_for_update)

        return new_thread_for_autotest_links_to_wi_for_update
