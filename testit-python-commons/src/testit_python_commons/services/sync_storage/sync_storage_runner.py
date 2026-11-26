import json
import logging
import os
import platform
import subprocess

import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional, TextIO

import urllib3
from api_client_syncstorage.api.test_results_api import TestResultsApi
from api_client_syncstorage.api.workers_api import WorkersApi
from api_client_syncstorage.api_client import ApiClient as SyncStorageApiClient
from api_client_syncstorage.configuration import (
    Configuration as SyncStorageConfiguration,
)
from api_client_syncstorage.exceptions import ApiException
from api_client_syncstorage.model.test_result_cut_api_model import (
    TestResultCutApiModel,
)
from api_client_syncstorage.model.register_request import RegisterRequest
from urllib3.exceptions import InsecureRequestWarning
from api_client_syncstorage.model.set_worker_status_request import SetWorkerStatusRequest
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.sync_storage.sync_storage_release_resolver import (
    resolve_latest,
)


# Disable SSL warnings
urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)


class SyncStorageRunner:
    """
    Python implementation of the SyncStorageRunner following the Java adapter specification.
    Manages interaction with the Sync Storage service for coordinating test execution
    across multiple workers.
    """

    # Floor: newest patch on the same major.minor + numeric channel is resolved at start.
    SYNC_STORAGE_VERSION = "v0.4.2"
    SYNC_STORAGE_REPO_URL = (
        "https://github.com/testit-tms/sync-storage-public/releases/download/"
    )
    AMD64 = "amd64"
    ARM64 = "arm64"
    SYNC_STORAGE_STARTUP_TIMEOUT = 5  # seconds
    KEEP_ALIVE_INTERVAL_SECONDS = 30
    KEEP_ALIVE_REQUEST_TIMEOUT_SECONDS = 5
    REGISTER_RETRY_ATTEMPTS = 5
    REGISTER_RETRY_DELAY_SECONDS = 0.5
    DEFAULT_PORT_MAX_BUMP = 10
    # Real Go release binaries are multi-MB; HTML/error pages must not be reused.
    MIN_EXECUTABLE_BYTES = 1_000_000

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
        self.preferred_port = self.parse_port(port, 49152)
        self.port = str(self.preferred_port)
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
        self._sync_storage_log_file: Optional[TextIO] = None
        self._resolved_sync_storage_version: Optional[str] = None
        self._resolved_version_lock = threading.Lock()

        # API clients
        self.workers_api: Optional[WorkersApi] = None
        self.test_results_api: Optional[TestResultsApi] = None

        self._keep_alive_stop_event = threading.Event()
        self._keep_alive_thread: Optional[threading.Thread] = None

        logger.debug(
            f"Initialized SyncStorageRunner with test_run_id={test_run_id}, port={self.port}"
        )

    @staticmethod
    def parse_port(value: Optional[str], default_port: int) -> int:
        if value is None or value == "" or value == "null":
            return default_port
        try:
            return int(str(value).strip())
        except (TypeError, ValueError):
            return default_port

    @staticmethod
    def resolve_port_max_bump() -> int:
        raw = os.environ.get("SYNC_STORAGE_PORT_MAX_BUMP") or os.environ.get(
            "TMS_SYNC_STORAGE_PORT_MAX_BUMP"
        )
        if not raw:
            return SyncStorageRunner.DEFAULT_PORT_MAX_BUMP
        try:
            return max(0, int(str(raw).strip()))
        except (TypeError, ValueError):
            return SyncStorageRunner.DEFAULT_PORT_MAX_BUMP

    @staticmethod
    def resolve_port_action(
        health_ok: bool, running_test_run_id: Optional[str], my_test_run_id: str
    ) -> str:
        """Return START_NEW | ATTACH | TRY_NEXT."""
        if not health_ok:
            return "START_NEW"
        if not running_test_run_id:
            return "ATTACH"
        if running_test_run_id == my_test_run_id:
            return "ATTACH"
        return "TRY_NEXT"

    def start(self) -> bool:
        """
        Start Sync Storage or attach to an existing instance.
        Foreign testRunId / bind-register race → try port+1 .. +maxBump.
        """
        logger.info("Starting Sync Storage service!")
        try:
            if self.is_running:
                logger.info("SyncStorage already running")
                return True

            max_bump = self.resolve_port_max_bump()
            prepared_executable_path = None

            for offset in range(max_bump + 1):
                candidate = self.preferred_port + offset
                self.port = str(candidate)
                self.workers_api = None
                self.test_results_api = None

                health_ok = self._is_sync_storage_already_running()
                running_id = (
                    self._fetch_health_test_run_id() if health_ok else None
                )
                action = self.resolve_port_action(
                    health_ok, running_id, self.test_run_id
                )

                if action == "TRY_NEXT":
                    logger.info(
                        "Port %s busy with testRunId=%s; trying %s",
                        candidate,
                        running_id,
                        candidate + 1,
                    )
                    continue

                if candidate != self.preferred_port:
                    logger.info(
                        "syncStoragePort effective=%s (preferred=%s)",
                        self.port,
                        self.preferred_port,
                    )

                if action == "ATTACH":
                    if not running_id:
                        logger.warning(
                            "Existing sync-storage on port %s does not report testRunId "
                            "in /health; compatibility cannot be verified. Prefer a "
                            "sync-storage build that exposes testRunId. Current testRunId: %s",
                            self.port,
                            self.test_run_id,
                        )
                    logger.info(
                        "SyncStorage already started on port %s. Connecting...",
                        self.port,
                    )
                    self.is_running = True
                    self.is_external = True
                    if self._register_worker_with_retry():
                        return True
                    self.is_running = False
                    self.is_external = False
                    logger.info(
                        "Attach/register failed on port %s (race or incompatible); trying next",
                        candidate,
                    )
                    continue

                if prepared_executable_path is None:
                    prepared_executable_path = self._prepare_executable_file(
                        self._get_file_name_by_arch_and_os()
                    )

                if self._try_start_owned_process(prepared_executable_path):
                    return True
                self._cleanup_failed_spawn()
                logger.info(
                    "Could not claim port %s for testRunId=%s; trying next",
                    candidate,
                    self.test_run_id,
                )

            logger.error(
                "No free sync-storage port in %s..%s for testRunId %s. "
                "Stop occupying processes or raise SYNC_STORAGE_PORT_MAX_BUMP.",
                self.preferred_port,
                self.preferred_port + max_bump,
                self.test_run_id,
            )
            return False

        except Exception as e:
            logger.error(f"Error starting Sync Storage: {e}", exc_info=True)
            self._cleanup_failed_spawn()
            return False

    def _build_start_command(self, prepared_executable_path: str) -> list:
        command = [prepared_executable_path]
        if self.test_run_id:
            command.extend(["--testRunId", self.test_run_id])
        if self.port:
            command.extend(["--port", self.port])
        if self.base_url:
            command.extend(["--baseURL", self.base_url])
        if self.private_token:
            command.extend(["--privateToken", self.private_token])
        return command

    def _try_start_owned_process(self, prepared_executable_path: str) -> bool:
        command = self._build_start_command(prepared_executable_path)
        logger.info("Starting SyncStorage with command: %s", " ".join(command))

        # Detach SS from the adapter process: CI calls wait-completion after tests,
        # and Work X must outlive the test runner. Do not atexit-kill (or atexit-block)
        # the child — that regressed pipes/xdist (see fb30546).
        work_dir = os.path.dirname(prepared_executable_path)
        log_path = os.path.join(work_dir, "syncstorage.log")
        self._sync_storage_log_file = open(log_path, "a", encoding="utf-8")
        self.sync_storage_process = subprocess.Popen(
            command,
            cwd=work_dir,
            stdout=self._sync_storage_log_file,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        logger.info("SyncStorage logs: %s", log_path)

        if not self._wait_for_server_startup(self.SYNC_STORAGE_STARTUP_TIMEOUT):
            logger.warning("SyncStorage did not become healthy on port %s", self.port)
            return False

        running_id = self._fetch_health_test_run_id()
        if running_id and running_id != self.test_run_id:
            logger.info(
                "Port %s became sync-storage for other testRunId=%s after start race",
                self.port,
                running_id,
            )
            return False

        time.sleep(2)
        if not self._register_worker_with_retry():
            logger.warning("Failed to register sync-storage worker on port %s", self.port)
            return False

        self.is_running = True
        self.is_external = False
        logger.info("SyncStorage started successfully on port %s", self.port)
        return True

    def _cleanup_failed_spawn(self) -> None:
        self._stop_keep_alive()
        self.is_master = False
        self.is_running = False
        if self.sync_storage_process is not None:
            if self.sync_storage_process.poll() is None:
                try:
                    self.sync_storage_process.terminate()
                    self.sync_storage_process.wait(timeout=3)
                except Exception:
                    try:
                        self.sync_storage_process.kill()
                    except Exception:
                        pass
            self.sync_storage_process = None
        if self._sync_storage_log_file is not None:
            try:
                self._sync_storage_log_file.close()
            except Exception:
                pass
            self._sync_storage_log_file = None
        self.is_external = False

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

    def is_reachable(self) -> bool:
        """True when /health responds — used to drop SS path if the process died."""
        return self._is_sync_storage_already_running()

    def mark_stopped(self) -> None:
        """Disable this runner so the adapter falls back to the normal TMS flow."""
        self.is_running = False
        self.is_master = False
        self.is_already_in_progress = False
        self._stop_keep_alive()

    def is_running_as_process(self) -> bool:
        """Check if Sync Storage is running as a process."""
        return (
            self.sync_storage_process is not None
            and self.sync_storage_process.poll() is None
        )

    def get_url(self) -> str:
        """Get the Sync Storage URL."""
        return f"http://localhost:{self.port}"

    def _keep_alive(self) -> None:
        if not self.worker_pid or not self.test_run_id:
            return
        try:
            payload = json.dumps({
                "pid": self.worker_pid,
                "testRunId": self.test_run_id,
            }).encode("utf-8")
            request = urllib.request.Request(
                f"{self.get_url()}/keep_alive",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(
                request,
                timeout=self.KEEP_ALIVE_REQUEST_TIMEOUT_SECONDS,
            )
        except urllib.error.HTTPError as e:
            # SS returns "Worker not found"; missing route is a generic 404.
            if e.code == 404:
                body = ""
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    pass
                if "Worker not found" in body:
                    logger.warning("keep_alive: worker not found (pid=%s)", self.worker_pid)
                else:
                    logger.debug(
                        "keep_alive endpoint unavailable (HTTP 404, pid=%s)",
                        self.worker_pid,
                    )
            else:
                logger.debug(
                    "keep_alive failed: HTTP %s (pid=%s)", e.code, self.worker_pid
                )
        except Exception as e:
            logger.debug("keep_alive failed for pid=%s: %s", self.worker_pid, e)

    def _keep_alive_loop(self) -> None:
        while not self._keep_alive_stop_event.is_set():
            self._keep_alive()
            if self._keep_alive_stop_event.wait(self.KEEP_ALIVE_INTERVAL_SECONDS):
                break

    def _start_keep_alive(self) -> None:
        if not self.worker_pid:
            return
        if self._keep_alive_thread and self._keep_alive_thread.is_alive():
            return

        self._keep_alive_stop_event.clear()
        self._keep_alive_thread = threading.Thread(
            target=self._keep_alive_loop,
            name="sync-storage-keep-alive",
            daemon=True,
        )
        self._keep_alive_thread.start()
        logger.debug("Sync Storage keep-alive thread started")

    def _stop_keep_alive(self) -> None:
        self._keep_alive_stop_event.set()
        if self._keep_alive_thread and self._keep_alive_thread.is_alive():
            self._keep_alive_thread.join(timeout=1)
        self._keep_alive_thread = None

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

    def _fetch_health_test_run_id(self) -> Optional[str]:
        try:
            req = urllib.request.Request(f"http://localhost:{self.port}/health")
            with urllib.request.urlopen(req, timeout=1) as response:
                if response.getcode() != 200:
                    return None
                body = response.read().decode("utf-8", errors="replace")
                return self.extract_json_string_field(body, "testRunId")
        except Exception:
            return None

    @staticmethod
    def extract_json_string_field(json_text: Optional[str], field: str) -> Optional[str]:
        if not json_text or not field:
            return None
        try:
            data = json.loads(json_text)
        except Exception:
            return None
        value = data.get(field)
        return value if isinstance(value, str) and value else None

    def _register_worker_with_retry(self) -> bool:
        for _ in range(self.REGISTER_RETRY_ATTEMPTS):
            if self._register_worker():
                return True
            time.sleep(self.REGISTER_RETRY_DELAY_SECONDS)
        return False

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

            if os.path.exists(target_path) and self._is_valid_executable(target_path):
                logger.info(f"Using existing file: {target_path}")

                # Make file executable for Unix-based systems
                if not platform.system().lower().startswith("windows"):
                    os.chmod(target_path, 0o755)

                return target_path

            if os.path.exists(target_path):
                logger.warning(
                    "Cached Sync Storage binary looks invalid (%s bytes); re-downloading",
                    os.path.getsize(target_path),
                )
                try:
                    os.remove(target_path)
                except OSError:
                    pass

            logger.info("File not present, downloading from GitHub Releases")
            self._download_executable_from_github(target_path)

            return target_path
        except Exception as e:
            logger.error(f"Error preparing executable file: {e}")
            raise

    @classmethod
    def _is_valid_executable(cls, path: str) -> bool:
        try:
            return os.path.isfile(path) and os.path.getsize(path) >= cls.MIN_EXECUTABLE_BYTES
        except OSError:
            return False

    def _download_executable_from_github(self, target_path: str):
        """
        Download Sync Storage executable from GitHub.

        :param target_path: Target path to save the executable
        """
        tmp_path = f"{target_path}.tmp"
        try:
            # Determine download URL
            download_url = self._get_download_url_for_current_platform()

            logger.info(f"Downloading file from: {download_url}")
            logger.info(f"Saving in: {target_path}")

            # Download file
            req = urllib.request.Request(download_url)
            req.add_header("User-Agent", "testit-python-adapter")

            with urllib.request.urlopen(req, timeout=30) as response:
                with open(tmp_path, "wb") as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)

            if not self._is_valid_executable(tmp_path):
                size = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0
                raise RuntimeError(
                    f"Downloaded Sync Storage binary is too small ({size} bytes): {download_url}"
                )

            os.replace(tmp_path, target_path)
            logger.info(f"File downloaded successfully: {target_path}")

            # Make file executable for Unix-based systems
            if not platform.system().lower().startswith("windows"):
                os.chmod(target_path, 0o755)

        except Exception as e:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except OSError:
                pass
            logger.error(f"Error downloading file: {e}")
            raise

    def _get_file_name_by_arch_and_os(self) -> str:
        """
        Get executable file name based on OS and architecture.

        :return: File name
        """
        os_name = platform.system().lower()
        os_arch = platform.machine().lower()

        # Determine OS part. Check darwin first because "darwin" contains "win".
        if "mac" in os_name or "darwin" in os_name:
            os_part = "darwin"
        elif os_name.startswith("win"):
            os_part = "windows"
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

    def resolved_version(self) -> str:
        """Newest release on the floor's major.minor line and channel."""
        cached = self._resolved_sync_storage_version
        if cached is not None:
            return cached
        with self._resolved_version_lock:
            if self._resolved_sync_storage_version is None:
                self._resolved_sync_storage_version = resolve_latest(
                    self.SYNC_STORAGE_VERSION
                )
            return self._resolved_sync_storage_version

    def _get_download_url_for_current_platform(self) -> str:
        """
        Get download URL for current platform.

        :return: Download URL
        """
        version = self.resolved_version()
        file_name = self._get_file_name_by_arch_and_os()
        return f"{self.SYNC_STORAGE_REPO_URL}{version}/{file_name}"

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

        # Form file name from resolved tag (cache name includes version → auto-download)
        file_name = f"syncstorage-{self.resolved_version()}-{os_part}_{arch_part}"
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
                pid=self.worker_pid, test_run_id=self.test_run_id, base_url=self.base_url, private_token=self.private_token
            )

            # Send registration request

            response = self.workers_api.register_post(register_request=register_request)

            # Check if this worker is the master

            self.is_master = getattr(response, "is_master", False)

            if self.is_master:
                logger.info(f"Master worker registered, PID: {self.worker_pid}")

            else:
                logger.info(f"Worker registered successfully, PID: {self.worker_pid}")

            self._start_keep_alive()
            return True

        except ApiException as e:
            if e.status == 409:
                logger.info(
                    "Port %s sync-storage rejected register (HTTP 409); "
                    "another testRunId may be bound. Current testRunId: %s",
                    self.port,
                    self.test_run_id,
                )
                return False
            logger.error(f"Error registering worker: {e}", exc_info=True)
            return False
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
        if status and status.lower() == "completed":
            self._stop_keep_alive()


    @classmethod
    def test_result_to_test_result_cut_api_model(
            cls,
            test_result: TestResult, project_id: str) -> TestResultCutApiModel:
        return TestResultCutApiModel(
            project_id=project_id,
            auto_test_external_id=test_result.get_external_id(),
            status_type=test_result.get_status_type(),
            status_code=test_result.get_outcome(),
            started_on=test_result.get_started_on(),
        )
