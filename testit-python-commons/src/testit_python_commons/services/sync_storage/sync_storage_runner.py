import logging
import os
import platform
import subprocess

import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

import urllib3
from api_client_syncstorage.api.test_results_api import TestResultsApi
from api_client_syncstorage.api.workers_api import WorkersApi
from api_client_syncstorage.api_client import ApiClient as SyncStorageApiClient
from api_client_syncstorage.configuration import (
    Configuration as SyncStorageConfiguration,
)
from api_client_syncstorage.model.test_result_cut_api_model import (
    TestResultCutApiModel,
)
from api_client_syncstorage.model.register_request import RegisterRequest
from urllib3.exceptions import InsecureRequestWarning
from api_client_syncstorage.model.set_worker_status_request import SetWorkerStatusRequest
from testit_python_commons.models.test_result import TestResult


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
    SYNC_STORAGE_VERSION = "v0.1.18"
    SYNC_STORAGE_REPO_URL = (
        "https://github.com/testit-tms/sync-storage-public/releases/download/"
    )
    AMD64 = "amd64"
    ARM64 = "arm64"
    SYNC_STORAGE_STARTUP_TIMEOUT = 30  # seconds

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
        self.test_run_id = test_run_id
        self.port = port or self.DEFAULT_PORT
        self.base_url = base_url
        self.private_token = private_token

        # Worker identification
        self.worker_pid: str = f"worker-{threading.get_ident()}-{int(time.time())}"
        self.is_master: bool = False
        self.is_already_in_progress: bool = False
        self.is_running: bool = False
        self.is_external: bool = False

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
        logger.info("Starting Sync Storage service!")
        try:
            if self.is_running:
                logger.info("SyncStorage already running")
                return True

            logger.info("SyncStorage is not running")

            # Check if Sync Storage is already running
            if self._is_sync_storage_already_running():
                logger.info(
                    f"SyncStorage already started {self.port}. Connecting to existing one..."
                )
                self.is_running = True
                self.is_external = True

                try:
                    self._register_worker_with_retry()
                except Exception as e:
                    logger.error(f"Error registering worker: {e}")

                return True

            # Get executable file name for current platform
            executable_filename = self._get_file_name_by_arch_and_os()

            # Prepare command to start Sync Storage
            command = [executable_filename]

            if self.test_run_id:
                command.extend(["--testRunId", self.test_run_id])

            if self.port:
                command.extend(["--port", self.port])

            if self.base_url:
                command.extend(["--baseURL", self.base_url])

            if self.private_token:
                command.extend(["--privateToken", self.private_token])

            # Prepare executable file (download if needed)
            prepared_executable_path = self._prepare_executable_file(
                executable_filename
            )

            # Update command with prepared path
            command[0] = prepared_executable_path

            logger.info(f"Starting SyncStorage with command: {' '.join(command)}")

            # Start process
            process_builder = subprocess.Popen(
                command,
                cwd=os.path.dirname(prepared_executable_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            self.sync_storage_process = process_builder

            # Start output reader in background thread
            self._start_output_reader()

            # Wait for server startup
            if self._wait_for_server_startup(self.SYNC_STORAGE_STARTUP_TIMEOUT):
                self.is_running = True
                logger.info(f"SyncStorage started successfully on port {self.port}")
                time.sleep(2)  # Wait a bit more as in Java implementation

                try:
                    self._register_worker_with_retry()
                except Exception as e:
                    logger.error(f"Error registering worker: {e}")

                return True
            else:
                raise RuntimeError("Cannot start the SyncStorage until timeout")

        except Exception as e:
            logger.error(f"Error starting Sync Storage: {e}", exc_info=True)
            return False

    def get_worker_pid(self) -> str:
        """Get the worker PID."""
        return self.worker_pid

    def get_test_run_id(self) -> str:
        """Get the test run ID."""
        return self.test_run_id

    def is_master_worker(self) -> bool:
        """Check if this is the master worker."""
        return self.is_master

    def is_already_in_progress_flag(self) -> bool:
        """Check if already in progress flag is set."""
        return self.is_already_in_progress

    def set_is_already_in_progress(self, value: bool):
        """Set the already in progress flag."""
        self.is_already_in_progress = value

    def is_running_status(self) -> bool:
        """Check if Sync Storage is running."""
        return self.is_running

    def is_running_as_process(self) -> bool:
        """Check if Sync Storage is running as a process."""
        return (
            self.sync_storage_process is not None
            and self.sync_storage_process.poll() is None
        )

    def get_url(self) -> str:
        """Get the Sync Storage URL."""
        return f"http://localhost:{self.port}"

    def send_in_progress_test_result(
        self, model: TestResultCutApiModel
    ) -> bool:
        """
        Send test result to Sync Storage if this worker is the master.

        :param model: TestResultCutApiModel instance
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
            if self.is_already_in_progress:
                logger.debug("Test already in progress, skipping duplicate send")
                return False

            logger.debug("Sending in-progress test result to Sync Storage")


            # Send to Sync Storage using API client
            if self.test_results_api is not None:
                response = self.test_results_api.in_progress_test_result_post(
                    self.test_run_id,
                    model, # test_result_cut_api_model
                )

                # Mark as in progress to prevent duplicates
                self.is_already_in_progress = True

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

    def _is_sync_storage_already_running(self) -> bool:
        """
        Check if Sync Storage is already running on the specified port.


        :return: True if running, False otherwise

        """

        try:
            url = f"http://localhost:{self.port}/health"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.getcode() == 200
        except Exception:
            return False

    def _register_worker_with_retry(self):
        """Register worker with retry logic."""
        self._register_worker()

    def _start_output_reader(self):
        """Start reading output from Sync Storage process in a background thread."""

        def read_output():
            try:
                if self.sync_storage_process and self.sync_storage_process.stdout:
                    # Read output with explicit encoding (e.g., 'utf-8' or 'latin-1')
                    for line in iter(self.sync_storage_process.stdout.readline, ""):
                        if line:
                            # Decode the line explicitly to avoid encoding issues
                            logger.info(f"SyncStorage: {line.rstrip()}")
                    self.sync_storage_process.stdout.close()
            except Exception as e:
                logger.warning(f"Error reading SyncStorage output: {e}")

        output_thread = threading.Thread(target=read_output, daemon=True)
        output_thread.start()

    def _wait_for_server_startup(self, timeout_seconds: int) -> bool:
        """
        Wait for Sync Storage server to start up.

        :param timeout_seconds: Timeout in seconds
        :return: True if server started, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            if self._is_sync_storage_already_running():
                return True
            time.sleep(1)
        return False

    def _prepare_executable_file(self, original_executable_path: str) -> str:
        """
        Prepare executable file by downloading if needed.

        :param original_executable_path: Original executable path
        :return: Path to prepared executable
        """
        try:
            current_dir = os.getcwd()
            caches_dir = os.path.join(current_dir, "build", ".caches")

            # Create caches directory if it doesn't exist
            os.makedirs(caches_dir, exist_ok=True)

            original_path = Path(original_executable_path)
            file_name = original_path.name
            target_path = os.path.join(caches_dir, file_name)

            if os.path.exists(target_path):
                logger.info(f"Using existing file: {target_path}")

                # Make file executable for Unix-based systems
                if not platform.system().lower().startswith("windows"):
                    os.chmod(target_path, 0o755)

                return target_path

            logger.info("File not present, downloading from GitHub Releases")
            self._download_executable_from_github(target_path)

            return target_path
        except Exception as e:
            logger.error(f"Error preparing executable file: {e}")
            raise

    def _download_executable_from_github(self, target_path: str):
        """
        Download Sync Storage executable from GitHub.

        :param target_path: Target path to save the executable
        """
        try:
            # Determine download URL
            download_url = self._get_download_url_for_current_platform()

            logger.info(f"Downloading file from: {download_url}")
            logger.info(f"Saving in: {target_path}")

            # Download file
            req = urllib.request.Request(download_url)
            req.add_header("User-Agent", "TestIT Python Adapter")

            with urllib.request.urlopen(req, timeout=30) as response:
                with open(target_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            logger.info(f"File downloaded successfully: {target_path}")

            # Make file executable for Unix-based systems
            if not platform.system().lower().startswith("windows"):
                os.chmod(target_path, 0o755)

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise

    def _get_file_name_by_arch_and_os(self) -> str:
        """
        Get executable file name based on OS and architecture.

        :return: File name
        """
        os_name = platform.system().lower()
        os_arch = platform.machine().lower()

        # Determine OS part
        if "win" in os_name:
            os_part = "windows"
        elif "mac" in os_name or "darwin" in os_name:
            os_part = "darwin"
        elif "linux" in os_name:
            os_part = "linux"
        else:
            raise RuntimeError(f"Unsupported OS, please contact dev team: {os_name}")

        return self._make_file_name(os_arch, os_part)

    def _is_mac_os(self, os_name: str) -> bool:
        """Check if OS is macOS."""
        return "mac" in os_name or "darwin" in os_name

    def _is_linux(self, os_name: str) -> bool:
        """Check if OS is Linux."""
        return "linux" in os_name

    def _get_download_url_for_current_platform(self) -> str:
        """
        Get download URL for current platform.

        :return: Download URL
        """
        file_name = self._get_file_name_by_arch_and_os()
        return f"{self.SYNC_STORAGE_REPO_URL}{self.SYNC_STORAGE_VERSION}/{file_name}"

    def _make_file_name(self, os_arch: str, os_part: str) -> str:
        """
        Make file name based on OS architecture and platform.

        :param os_arch: OS architecture
        :param os_part: OS part
        :return: File name
        """
        # Determine architecture part
        if self.AMD64 in os_arch or "x86_64" in os_arch:
            arch_part = self.AMD64
        elif self.ARM64 in os_arch or "aarch64" in os_arch:
            arch_part = self.ARM64
        else:
            raise RuntimeError(f"Unsupported architecture: {os_arch}")

        # Form file name
        file_name = f"syncstorage-{self.SYNC_STORAGE_VERSION}-{os_part}_{arch_part}"
        if os_part == "windows":
            file_name += ".exe"
        return file_name

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
            # Initialize API clients if not already done

            if self.workers_api is None:
                self._initialize_api_clients()

            if self.workers_api is None:
                logger.error("WorkersApi not initialized")
                return False

            logger.info(
                f"Registering worker {self.worker_pid} with test run {self.test_run_id}"
            )

            # Create registration request

            register_request = RegisterRequest(
                pid=self.worker_pid, test_run_id=self.test_run_id
            )

            # Send registration request

            response = self.workers_api.register_post(register_request=register_request)

            # Check if this worker is the master

            self.is_master = getattr(response, "is_master", False)

            if self.is_master:
                logger.info(f"Master worker registered, PID: {self.worker_pid}")

            else:
                logger.info(f"Worker registered successfully, PID: {self.worker_pid}")

            return True

        except Exception as e:
            logger.error(f"Error registering worker: {e}", exc_info=True)

            return False

    def set_worker_status(self, status: str):
        if self.workers_api is None:
            self._initialize_api_clients()
        try:
            request = SetWorkerStatusRequest(pid=self.worker_pid, status=status, test_run_id=self.test_run_id)
            self.workers_api.set_worker_status_post(set_worker_status_request=request)
            logging.info(f"Successfully set worker {self.worker_pid} status to {status}")
        except Exception as e:
            logger.error(f"Error setting worker status: {e}", exc_info=False)


    @classmethod
    def test_result_to_test_result_cut_api_model(
            cls,
            test_result: TestResult) -> TestResultCutApiModel:
        return TestResultCutApiModel(
            auto_test_external_id=test_result.get_external_id(),
            status_code=test_result.get_outcome(),
            started_on=test_result.get_started_on(),
        )
