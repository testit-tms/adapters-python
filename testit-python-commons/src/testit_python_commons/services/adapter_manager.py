import logging
import os
import uuid

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.adapter_manager_configuration import (
    AdapterManagerConfiguration,
)
from testit_python_commons.services.fixture_manager import FixtureManager
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils

from testit_python_commons.services.sync_storage.config import SyncStorageConfig
from testit_python_commons.services.sync_storage.sync_storage_runner import (
    SyncStorageRunner,
)

SYNC_STORAGE_AVAILABLE = True
IN_PROGRESS_LITERAL = "InProgress"


class AdapterManager:
    def __init__(
        self,
        adapter_configuration: AdapterManagerConfiguration,
        client_configuration: ClientConfiguration,
        fixture_manager: FixtureManager,
    ):

        self.__config = adapter_configuration
        self.__api_client = ApiClientWorker(client_configuration)
        self.__fixture_manager = fixture_manager
        self.__test_result_map = {}
        self.__test_results = []

        # Sync Storage integration
        self.__sync_storage_runner = None
        # Initialize Sync Storage if available and enabled
        if SYNC_STORAGE_AVAILABLE:
            self.__sync_storage_runner = self._initialize_sync_storage(
                client_configuration
            )


    def _initialize_sync_storage(self, client_configuration):
        """Initialize Sync Storage runner if enabled."""
        try:
            # Get test run ID - create one if needed
            test_run_id = self.__config.get_test_run_id()

            # If no test run ID, create one (as in Java implementation)
            if not test_run_id:
                test_run_id = self.__api_client.create_test_run(
                    self.__config.get_test_run_name()
                )
                self.__config.set_test_run_id(test_run_id)
                self.__api_client.set_test_run_id(test_run_id)

            # Extract configuration properties
            url = getattr(client_configuration, "_ClientConfiguration__url", None)
            private_token = getattr(
                client_configuration, "_ClientConfiguration__private_token", None
            )

            # Port defaults to 49152
            port = "49152"

            # Create and start Sync Storage runner
            if SYNC_STORAGE_AVAILABLE:
                sync_storage_runner = SyncStorageRunner(
                    test_run_id=test_run_id,
                    port=port,
                    base_url=url,
                    private_token=private_token,
                )

                if sync_storage_runner.start():
                    logging.info("Sync Storage started successfully")
                    return sync_storage_runner
                else:
                    logging.warning("Failed to start Sync Storage")

        except Exception as e:
            logging.warning(f"Failed to initialize SyncStorage: {e}", exc_info=True)

        return None


    @adapter_logger
    def set_test_run_id(self, test_run_id: str) -> None:

        self.__config.set_test_run_id(test_run_id)

        self.__api_client.set_test_run_id(test_run_id)

        # Update Sync Storage with test run ID if available
        if self.__sync_storage_runner:
            self.__sync_storage_runner.test_run_id = test_run_id

    @adapter_logger
    def get_test_run_id(self) -> str:
        if self.__config.get_mode() != AdapterMode.NEW_TEST_RUN:
            test_run_id = self.__config.get_test_run_id()

            if test_run_id:
                self.__update_test_run_name(test_run_id)

            return test_run_id or ""

        result = self.__config.get_test_run_id()
        if result is not None:
            return result

        # create if not exists
        test_run_name = self.__config.get_test_run_name()
        return self.__api_client.create_test_run(test_run_name if test_run_name else "")

    @adapter_logger
    def __update_test_run_name(self, test_run_id: str) -> None:
        test_run_name = self.__config.get_test_run_name()

        if not test_run_name:
            return

        test_run = self.__api_client.get_test_run(test_run_id)

        if test_run_name == test_run.name:
            return

        test_run.name = test_run_name

        self.__api_client.update_test_run(test_run)

    @adapter_logger
    def get_autotests_for_launch(self):
        if self.__config.get_mode() == AdapterMode.USE_FILTER:
            return self.__api_client.get_external_ids_for_test_run_id()

        return

    @adapter_logger
    def write_test(self, test_result: TestResult) -> None:
        if self.__config.should_import_realtime():
            self.__write_test_realtime(test_result)
            return

        # for realtime false
        # if
        logging.warning("Is already in progress: " + str(self.__sync_storage_runner.is_already_in_progress_flag()))
        # Handle Sync Storage integration if available
        # Check if current worker is master and no test is in progress
        if self.__is_active_syncstorage_instance() and self.__is_master_and_no_in_progress():
            logging.warning(f"Outcome: {test_result.get_outcome()}")
            is_ok = self.on_master_no_already_in_progress(test_result)
            if is_ok:
                return
            # else continue normal processing

        self.__test_results.append(test_result)


    @adapter_logger
    def on_master_no_already_in_progress(self, test_result: TestResult) -> bool:
        # Convert TestResult to TestResultCutApiModel
        tr_cut_api_model = SyncStorageRunner.test_result_to_test_result_cut_api_model(
            test_result
        )
        logging.warning("Set as in progress status_code, auto_test_external_id: "
                        + tr_cut_api_model.status_code + " " + tr_cut_api_model.auto_test_external_id)

        # Send test result to Sync Storage
        success = self.__sync_storage_runner.send_in_progress_test_result(
            tr_cut_api_model
        )

        if not success:
            return False

        # Set the in-progress flag in the runner
        self.__sync_storage_runner.set_is_already_in_progress(True)

        try:
            # Write test result normally (mark as IN PROGRESS in Test IT)
            logging.warning("Write internally, change status to in progress")
            test_result.set_outcome(IN_PROGRESS_LITERAL)
            self._write_test_realtime_internal(test_result)
            return True
        except Exception as e:
            logging.warning(
                f"Error in Sync Storage handling, falling back to normal processing: {e}"
            )
            # Reset in-progress flag and continue with normal processing
            self.__sync_storage_runner.set_is_already_in_progress(False)
        return False

    @adapter_logger
    def __write_test_realtime(self, test_result: TestResult) -> None:

        logging.warning("Is already in progress: " + str(self.__sync_storage_runner.is_already_in_progress_flag()))

        # Handle Sync Storage integration if available
        if self.__is_active_syncstorage_instance() and self.__is_master_and_no_in_progress():
            # Check if current worker is master and no test is in progress
            is_ok = self.on_master_no_already_in_progress(test_result)
            if is_ok:
                return
            # else continue normal processing

        # Normal processing (also fallback for Sync Storage errors)
        self._write_test_realtime_internal(test_result)

    def _write_test_realtime_internal(self, test_result: TestResult) -> None:
        """Internal method for writing test results to maintain clean separation."""
        test_result.set_automatic_creation_test_cases(
            self.__config.should_automatic_creation_test_cases()
        )

        ext_id = test_result.get_external_id()
        test_result_id = self.__api_client.write_test(test_result)
        if ext_id is None or test_result_id is None:
            logging.warning("test_result got empty external_id or test_result_id")
            logging.warning(test_result)
            return

        self.__test_result_map[ext_id] = test_result_id

    @adapter_logger
    def write_tests(self) -> None:
        if self.__config.should_import_realtime():
            self.__load_setup_and_teardown_step_results()

            return

        self.__write_tests_after_all()

    @adapter_logger
    def __load_setup_and_teardown_step_results(self) -> None:
        self.__api_client.update_test_results(
            self.__fixture_manager.get_all_items(), self.__test_result_map
        )

    @adapter_logger
    def __write_tests_after_all(self) -> None:

        fixtures = self.__fixture_manager.get_all_items()

        self.__api_client.write_tests(self.__test_results, fixtures)

    @adapter_logger
    def load_attachments(self, attach_paths):
        return self.__api_client.load_attachments(attach_paths)

    @adapter_logger
    def create_attachment(self, body, name: str):
        if name is None:
            name = str(uuid.uuid4()) + "-attachment.txt"

        path = os.path.join(os.path.abspath(""), name)

        with open(path, "wb") as attached_file:
            attached_file.write(Utils.convert_body_of_attachment(body))

        attachment_id = self.__api_client.load_attachments((path,))

        os.remove(path)

        return attachment_id

    @adapter_logger
    def on_block_completed(self):
        self.set_worker_status("completed")

    @adapter_logger
    def on_running_started(self):
        self.set_worker_status("in_progress")

    @adapter_logger
    def set_worker_status(self, status: str):
        logging.info(f"Set worker_status to {status}")
        if not self.__is_active_syncstorage_instance():
            return

        self.__sync_storage_runner.set_worker_status(status)

    def __is_active_syncstorage_instance(self):
        return (self.__sync_storage_runner
                and self.__sync_storage_runner.is_running_status()
                )

    def __is_master_and_no_in_progress(self) -> bool:
        return (self.__sync_storage_runner.is_master_worker() and
                not self.__sync_storage_runner.is_already_in_progress_flag())
