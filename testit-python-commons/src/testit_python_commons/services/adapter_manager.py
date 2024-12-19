import os
import uuid

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.fixture_manager import FixtureManager
from testit_python_commons.services.adapter_manager_configuration import AdapterManagerConfiguration
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils


class AdapterManager:
    def __init__(
            self,
            adapter_configuration: AdapterManagerConfiguration,
            client_configuration: ClientConfiguration,
            fixture_manager: FixtureManager):
        self.__config = adapter_configuration
        self.__api_client = ApiClientWorker(client_configuration)
        self.__fixture_manager = fixture_manager
        self.__test_result_map = {}
        self.__test_results = []

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
    def write_test(self, test_result: TestResult):
        if self.__config.should_import_realtime():
            self.__write_test_realtime(test_result)

            return

        self.__test_results.append(test_result)

    @adapter_logger
    def __write_test_realtime(self, test_result: TestResult):
        test_result.set_automatic_creation_test_cases(
            self.__config.should_automatic_creation_test_cases())

        self.__test_result_map[test_result.get_external_id()] = self.__api_client.write_test(test_result)

    @adapter_logger
    def write_tests(self):
        if self.__config.should_import_realtime():
            self.__load_setup_and_teardown_step_results()

            return

        self.__write_tests_after_all()

    @adapter_logger
    def __load_setup_and_teardown_step_results(self):
        self.__api_client.update_test_results(self.__fixture_manager.get_all_items(), self.__test_result_map)

    @adapter_logger
    def __write_tests_after_all(self):
        fixtures = self.__fixture_manager.get_all_items()

        self.__api_client.write_tests(self.__test_results, fixtures)

    @adapter_logger
    def load_attachments(self, attach_paths: list or tuple):
        return self.__api_client.load_attachments(attach_paths)

    @adapter_logger
    def create_attachment(self, body, name: str):
        if name is None:
            name = str(uuid.uuid4()) + '-attachment.txt'

        path = os.path.join(os.path.abspath(''), name)

        with open(path, 'wb') as attached_file:
            attached_file.write(
                Utils.convert_body_of_attachment(body))

        attachment_id = self.__api_client.load_attachments((path,))

        os.remove(path)

        return attachment_id
