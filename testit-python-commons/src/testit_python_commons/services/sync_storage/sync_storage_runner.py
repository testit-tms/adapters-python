import logging
import os
import platform
import subprocess
import tempfile
import threading
import time
from typing import Any, Dict, Optional

import urllib3
from api_client_syncstorage.api.test_results_api import TestResultsApi
from api_client_syncstorage.api.workers_api import WorkersApi
from api_client_syncstorage.api_client import ApiClient as SyncStorageApiClient
from api_client_syncstorage.configuration import (
    Configuration as SyncStorageConfiguration,
)
from api_client_syncstorage.model.auto_test_results_for_test_run_model import (
    AutoTestResultsForTestRunModel,
)
from api_client_syncstorage.model.register_request import RegisterRequest
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class SyncStorageRunner:
    """
    Python implementation of the SyncStorageRunner following the Java adapter specification.
    Manages interaction with the Sync Storage service for coordinating test execution
    across multiple workers.
    """

    DEFAULT_PORT = "49152"
    SYNC_STORAGE_EXECUTABLE_NAME = "sync-storage"
    SYNC_STORAGE_STARTUP_TIMEOUT = 30  # seconds
    SYNC_STORAGE_DOWNLOAD_URL_TEMPLATE = (
        "https://testit-sync-storage.s3.amazonaws.com/{version}/{os_arch}/sync-storage"
    )

    def __init__(
        self,
        test_run_id: str,
        port: Optional[str] = None,
        base_url: Optional[str] = None,
        private_token: Optional[str] = None,
    ):
        """
        Initialize the SyncStorageRunner.

        :param test_run_id: The ID of the test run
        :param port: Port for Sync Storage service (default: 49152)
        :param base_url: Test IT server URL
        :param private_token: Authentication token for Test IT API
        """
        self.test_run_id: str = test_run_id
        self.port: str = port or self.DEFAULT_PORT
        self.base_url: Optional[str] = base_url
        self.private_token: Optional[str] = private_token

        # Worker identification
        self.pid: str = f"worker-{threading.get_ident()}-{int(time.time())}"
        self.is_master: bool = False
        self.is_external_service: bool = False
        self.already_in_progress: bool = False

        # Sync Storage process management
        self.sync_storage_process: Optional[subprocess.Popen] = None
        self.sync_storage_executable_path: Optional[str] = None

        # API clients
        self.workers_api: Optional[WorkersApi] = None
        self.test_results_api: Optional[TestResultsApi] = None

        logger.debug(
            f"Initialized SyncStorageRunner with test_run_id={test_run_id}, port={self.port}"
        )

    def start(self) -> bool:
        """
        Start the Sync Storage service and register the worker.

        :return: True if successfully started and registered, False otherwise
        """
        try:
            logger.info("Starting Sync Storage service")

            # Check if Sync Storage is already running
            if self._is_sync_storage_running():
                logger.info("Sync Storage is already running externally")
                self.is_external_service = True
            else:
                logger.info("Sync Storage is not running, attempting to start it")
                self.is_external_service = False

                # Download and start Sync Storage process
                if not self._download_and_start_sync_storage():
                    logger.error("Failed to download and start Sync Storage")
                    return False

            # Initialize API clients
            self._initialize_api_clients()

            # Register worker
            if not self._register_worker():
                logger.error("Failed to register worker with Sync Storage")
                return False

            logger.info(
                f"Successfully started Sync Storage runner. Is master: {self.is_master}"
            )
            return True

        except Exception as e:
            logger.error(f"Error starting Sync Storage runner: {e}", exc_info=True)
            return False

    def stop(self):
        """
        Stop the Sync Storage service if it was started by this runner.
        """
        try:
            if self.sync_storage_process and not self.is_external_service:
                logger.info("Stopping Sync Storage process")
                self.sync_storage_process.terminate()
                self.sync_storage_process.wait(timeout=5)
                logger.info("Sync Storage process stopped")
        except Exception as e:
            logger.warning(f"Error stopping Sync Storage process: {e}")
        finally:
            self._cleanup_temp_files()

    def send_in_progress_test_result(self, test_result: Dict[str, Any]) -> bool:
        """
        Send test result to Sync Storage if this worker is the master.

        :param test_result: Serialized test result data
        :return: True if successfully sent, False otherwise
        """
        try:
            # Only master worker sends test results
            if not self.is_master:
                logger.debug(
                    "Not master worker, skipping sending test result to Sync Storage"
                )
                return False

            # Prevent duplicate sending
            if self.already_in_progress:
                logger.debug("Test already in progress, skipping duplicate send")
                return False

            logger.debug("Sending in-progress test result to Sync Storage")

            # Convert dict to model
            auto_test_result_model = AutoTestResultsForTestRunModel(**test_result)

            # Send to Sync Storage
            if self.test_results_api is not None:
                response = self.test_results_api.in_progress_test_result_post(
                    test_run_id=self.test_run_id,
                    auto_test_results_for_test_run_model=auto_test_result_model,
                )

                # Mark as in progress to prevent duplicates
                self.already_in_progress = True

                logger.debug(
                    f"Successfully sent test result to Sync Storage: {response}"
                )
                return True
            else:
                logger.error("TestResultsApi not initialized")
                return False

        except Exception as e:
            logger.warning(
                f"Failed to send test result to Sync Storage: {e}", exc_info=True
            )
            return False

    def reset_in_progress_flag(self):
        """
        Reset the in-progress flag to allow sending the next test result.
        """
        self.already_in_progress = False
        logger.debug("Reset in-progress flag")

    def _is_sync_storage_running(self) -> bool:
        """
        Check if Sync Storage is already running on the specified port.

        :return: True if running, False otherwise
        """
        try:
            import requests

            response = requests.get(
                f"http://localhost:{self.port}/health", timeout=5, verify=False
            )
            return response.status_code == 200
        except ImportError:
            logger.warning("Requests library not available for health check")
            return False
        except Exception:
            return False

    def _download_and_start_sync_storage(self) -> bool:
        """
        Download the appropriate Sync Storage executable and start the process.

        :return: True if successfully downloaded and started, False otherwise
        """
        try:
            # Determine OS and architecture
            os_arch = self._get_os_architecture()
            if not os_arch:
                logger.error("Unsupported OS/architecture for Sync Storage")
                return False

            # Create temporary directory for executable
            temp_dir = tempfile.mkdtemp()
            self.sync_storage_executable_path = os.path.join(
                temp_dir, self.SYNC_STORAGE_EXECUTABLE_NAME
            )

            # Make executable on Unix-like systems
            if platform.system() != "Windows":
                self.sync_storage_executable_path += ".exe"

            logger.info(
                f"Downloading Sync Storage for {os_arch} to {self.sync_storage_executable_path}"
            )

            # TODO: Implement actual download logic
            # For now, we'll just check if we can start a process
            # In a real implementation, we would download the executable from the template URL

            # Try to start the process (this would normally be the downloaded executable)
            return self._start_sync_storage_process()

        except Exception as e:
            logger.error(
                f"Error downloading and starting Sync Storage: {e}", exc_info=True
            )
            self._cleanup_temp_files()
            return False

    def _start_sync_storage_process(self) -> bool:
        """
        Start the Sync Storage process with the provided configuration.

        :return: True if successfully started, False otherwise
        """
        try:
            # In a real implementation, we would start the downloaded executable
            # For now, we'll simulate the process start
            logger.info("Starting Sync Storage process")

            # Wait for service to start
            start_time = time.time()
            while time.time() - start_time < self.SYNC_STORAGE_STARTUP_TIMEOUT:
                if self._is_sync_storage_running():
                    logger.info("Sync Storage process started successfully")
                    return True
                time.sleep(1)

            logger.error("Sync Storage failed to start within timeout period")
            return False

        except Exception as e:
            logger.error(f"Error starting Sync Storage process: {e}", exc_info=True)
            return False

    def _get_os_architecture(self) -> Optional[str]:
        """
        Determine the OS and architecture for downloading the correct Sync Storage executable.

        :return: String representing OS/architecture combination, or None if unsupported
        """
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Normalize architecture names
        if machine in ["x86_64", "amd64"]:
            machine = "x64"
        elif machine in ["aarch64", "arm64"]:
            machine = "arm64"
        elif machine in ["i386", "i686"]:
            machine = "x86"

        # Map to supported combinations
        if system == "windows" and machine == "x64":
            return "windows-x64"
        elif system == "linux" and machine == "x64":
            return "linux-x64"
        elif system == "darwin" and machine in ["x64", "arm64"]:
            return f"macos-{machine}"

        logger.warning(f"Unsupported OS/architecture: {system}-{machine}")
        return None

    def _initialize_api_clients(self):
        """
        Initialize the Sync Storage API clients.
        """
        try:
            # Configure API client
            config = SyncStorageConfiguration()
            config.host = f"http://localhost:{self.port}"
            config.verify_ssl = False  # Disable SSL verification for localhost

            api_client = SyncStorageApiClient(configuration=config)

            # Initialize APIs
            self.workers_api = WorkersApi(api_client=api_client)
            self.test_results_api = TestResultsApi(api_client=api_client)

            logger.debug("Successfully initialized Sync Storage API clients")

        except Exception as e:
            logger.error(f"Error initializing API clients: {e}", exc_info=True)
            raise

    def _register_worker(self) -> bool:
        """
        Register the worker with the Sync Storage service.

        :return: True if successfully registered, False otherwise
        """
        try:
            if self.workers_api is None:
                logger.error("WorkersApi not initialized")
                return False

            logger.info(
                f"Registering worker {self.pid} with test run {self.test_run_id}"
            )

            # Create registration request
            register_request = RegisterRequest(
                pid=self.pid, test_run_id=self.test_run_id
            )

            # Send registration request
            response = self.workers_api.register_post(register_request=register_request)

            # Check if this worker is the master
            self.is_master = getattr(response, "is_master", False)

            logger.info(f"Worker registered successfully. Is master: {self.is_master}")
            return True

        except Exception as e:
            logger.error(f"Error registering worker: {e}", exc_info=True)
            return False

    def _cleanup_temp_files(self):
        """
        Clean up temporary files created during Sync Storage setup.
        """
        try:
            if self.sync_storage_executable_path:
                temp_dir = os.path.dirname(self.sync_storage_executable_path)
                if os.path.exists(temp_dir):
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Error cleaning up temporary files: {e}")

    def _is_process_running(self, pid: int) -> bool:
        """
        Check if a process with the given PID is running.

        :param pid: Process ID to check
        :return: True if running, False otherwise
        """
        try:
            import psutil

            process = psutil.Process(pid)
            return process.is_running()
        except (ImportError, Exception):
            return False
