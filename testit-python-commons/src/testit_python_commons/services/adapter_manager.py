import os
import typing
import uuid

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import TestResultWithAllFixtureStepResults
from testit_python_commons.services.adapter_manager_configuration import AdapterManagerConfiguration
from testit_python_commons.services.logger import adapter_logger


class AdapterManager:
    def __init__(
            self,
            adapter_configuration: AdapterManagerConfiguration,
            client_configuration: ClientConfiguration):
        self.__config = adapter_configuration
        self.__api_client = ApiClientWorker(client_configuration)

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__config.set_test_run_id(test_run_id)
        self.__api_client.set_test_run_id(test_run_id)

    @adapter_logger
    def get_test_run_id(self):
        if self.__config.get_mode() != AdapterMode.NEW_TEST_RUN:
            return self.__config.get_test_run_id()

        return self.__api_client.create_test_run()

    @adapter_logger
    def get_autotests_for_launch(self):
        if self.__config.get_mode() == AdapterMode.USE_FILTER:
            return self.__api_client.get_autotests_by_test_run_id()

        return

    @adapter_logger
    def write_test(self, test_result: TestResult) -> str:
        test_result.set_automatic_creation_test_cases(
            self.__config.should_automatic_creation_test_cases())

        return self.__api_client.write_test(test_result)

    @adapter_logger
    def load_setup_and_teardown_step_results(self, test_results: typing.List[TestResultWithAllFixtureStepResults]):
        self.__api_client.update_test_results(test_results)

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        return self.__api_client.load_attachments(attach_paths)

    @adapter_logger
    def create_attachment(self, body: str, name: str):
        if name is None:
            name = str(uuid.uuid4()) + '-attachment.txt'

        path = os.path.join(os.path.abspath(''), name)

        with open(path, 'wb') as attached_file:
            attached_file.write(body.encode('utf-8'))

        attachment_id = self.__api_client.load_attachments((path,))

        os.remove(path)

        return attachment_id
