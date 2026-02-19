import threading
from time import sleep
from unittest.mock import MagicMock, Mock, patch

import pytest
from testit_python_commons.services.sync_storage.sync_storage_runner import (
    SyncStorageRunner,
)


@pytest.fixture
def sync_storage_runner():
    """Create a SyncStorageRunner instance for testing."""
    return SyncStorageRunner(
        test_run_id="tr-123",
        port="49152",
        base_url="https://testit.example.com",
        private_token="token123",
    )


def test_sync_storage_runner_initialization(sync_storage_runner):
    """Test SyncStorageRunner initialization."""
    assert sync_storage_runner.test_run_id == "tr-123"
    assert sync_storage_runner.port == "49152"
    assert sync_storage_runner.base_url == "https://testit.example.com"
    assert sync_storage_runner.private_token == "token123"
    assert sync_storage_runner.is_master is False
    assert sync_storage_runner.is_external_service is False
    assert sync_storage_runner.already_in_progress is False
    assert sync_storage_runner.sync_storage_process is None
    assert sync_storage_runner.workers_api is None
    assert sync_storage_runner.test_results_api is None


def test_sync_storage_runner_pid_generation():
    """Test that PID is generated correctly."""
    runner1 = SyncStorageRunner("tr-123")
    sleep(1)
    runner2 = SyncStorageRunner("tr-456")

    # PIDs should be different
    assert runner1.pid != runner2.pid

    # PIDs should contain worker identifier
    assert "worker-" in runner1.pid
    assert "worker-" in runner2.pid


@patch("testit_python_commons.services.sync_storage.sync_storage_runner.requests.get")
def test_is_sync_storage_running_true(mock_requests_get, sync_storage_runner):
    """Test _is_sync_storage_running returns True when service is running."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_requests_get.return_value = mock_response

    result = sync_storage_runner._is_sync_storage_running()

    assert result is True
    mock_requests_get.assert_called_once_with(
        "http://localhost:49152/health", timeout=5, verify=False
    )


@patch("testit_python_commons.services.sync_storage.sync_storage_runner.requests.get")
def test_is_sync_storage_running_false(mock_requests_get, sync_storage_runner):
    """Test _is_sync_storage_running returns False when service is not running."""
    mock_requests_get.side_effect = Exception("Connection failed")

    result = sync_storage_runner._is_sync_storage_running()

    assert result is False


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.system"
)
@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.machine"
)
def test_get_os_architecture_windows_x64(mock_machine, mock_system):
    """Test _get_os_architecture for Windows x64."""
    mock_system.return_value = "windows"
    mock_machine.return_value = "x86_64"

    result = SyncStorageRunner("tr-123")._get_os_architecture()

    assert result == "windows-x64"


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.system"
)
@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.machine"
)
def test_get_os_architecture_linux_x64(mock_machine, mock_system):
    """Test _get_os_architecture for Linux x64."""
    mock_system.return_value = "linux"
    mock_machine.return_value = "x86_64"

    result = SyncStorageRunner("tr-123")._get_os_architecture()

    assert result == "linux-x64"


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.system"
)
@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.machine"
)
def test_get_os_architecture_macos_x64(mock_machine, mock_system):
    """Test _get_os_architecture for macOS x64."""
    mock_system.return_value = "darwin"
    mock_machine.return_value = "x86_64"

    result = SyncStorageRunner("tr-123")._get_os_architecture()

    assert result == "macos-x64"


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.system"
)
@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.platform.machine"
)
def test_get_os_architecture_unsupported(mock_machine, mock_system):
    """Test _get_os_architecture for unsupported platform."""
    mock_system.return_value = "unsupported"
    mock_machine.return_value = "unknown"

    result = SyncStorageRunner("tr-123")._get_os_architecture()

    assert result is None


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.SyncStorageApiClient"
)
@patch("testit_python_commons.services.sync_storage.sync_storage_runner.WorkersApi")
@patch("testit_python_commons.services.sync_storage.sync_storage_runner.TestResultsApi")
def test_initialize_api_clients(
    mock_test_results_api, mock_workers_api, mock_api_client, sync_storage_runner
):
    """Test _initialize_api_clients initializes APIs correctly."""
    sync_storage_runner._initialize_api_clients()

    # Check that API client was created with correct configuration
    mock_api_client.assert_called_once()
    config = mock_api_client.call_args[1]["configuration"]
    assert config.host == "http://localhost:49152"
    assert config.verify_ssl is False

    # Check that APIs were created
    mock_workers_api.assert_called_once_with(api_client=mock_api_client.return_value)
    mock_test_results_api.assert_called_once_with(
        api_client=mock_api_client.return_value
    )

    # Check that runner properties were set
    assert sync_storage_runner.workers_api == mock_workers_api.return_value
    assert sync_storage_runner.test_results_api == mock_test_results_api.return_value


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.AutoTestResultsForTestRunModel"
)
def test_send_in_progress_test_result_success(
    mock_auto_test_model, sync_storage_runner, sample_test_result
):
    """Test send_in_progress_test_result succeeds when master and not in progress."""
    # Setup
    sync_storage_runner.is_master = True
    sync_storage_runner.already_in_progress = False
    mock_test_results_api = Mock()
    sync_storage_runner.test_results_api = mock_test_results_api
    mock_test_results_api.in_progress_test_result_post.return_value = "success"

    # Execute
    result = sync_storage_runner.send_in_progress_test_result(sample_test_result)

    # Assert
    assert result is True
    assert sync_storage_runner.already_in_progress is True
    mock_auto_test_model.assert_called_once_with(**sample_test_result)
    mock_test_results_api.in_progress_test_result_post.assert_called_once()


def test_send_in_progress_test_result_not_master(
    sync_storage_runner, sample_test_result
):
    """Test send_in_progress_test_result returns False when not master."""
    sync_storage_runner.is_master = False

    result = sync_storage_runner.send_in_progress_test_result(sample_test_result)

    assert result is False


def test_send_in_progress_test_result_already_in_progress(
    sync_storage_runner, sample_test_result
):
    """Test send_in_progress_test_result returns False when already in progress."""
    sync_storage_runner.is_master = True
    sync_storage_runner.already_in_progress = True

    result = sync_storage_runner.send_in_progress_test_result(sample_test_result)

    assert result is False


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.AutoTestResultsForTestRunModel"
)
def test_send_in_progress_test_result_api_not_initialized(
    mock_auto_test_model, sync_storage_runner, sample_test_result
):
    """Test send_in_progress_test_result fails when API not initialized."""
    sync_storage_runner.is_master = True
    sync_storage_runner.already_in_progress = False
    sync_storage_runner.test_results_api = None

    result = sync_storage_runner.send_in_progress_test_result(sample_test_result)

    assert result is False
    mock_auto_test_model.assert_not_called()


def test_reset_in_progress_flag(sync_storage_runner):
    """Test reset_in_progress_flag resets the flag."""
    sync_storage_runner.already_in_progress = True

    sync_storage_runner.reset_in_progress_flag()

    assert sync_storage_runner.already_in_progress is False


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.RegisterRequest"
)
def test_register_worker_success(
    mock_register_request, sync_storage_runner, mock_register_response
):
    """Test _register_worker succeeds."""
    mock_workers_api = Mock()
    mock_workers_api.register_post.return_value = mock_register_response
    sync_storage_runner.workers_api = mock_workers_api

    result = sync_storage_runner._register_worker()

    assert result is True
    assert sync_storage_runner.is_master is True
    mock_register_request.assert_called_once_with(
        pid=sync_storage_runner.pid, test_run_id="tr-123"
    )
    mock_workers_api.register_post.assert_called_once_with(
        register_request=mock_register_request.return_value
    )


def test_register_worker_api_not_initialized(sync_storage_runner):
    """Test _register_worker fails when API not initialized."""
    sync_storage_runner.workers_api = None

    result = sync_storage_runner._register_worker()

    assert result is False


@patch(
    "testit_python_commons.services.sync_storage.sync_storage_runner.RegisterRequest"
)
def test_register_worker_exception(mock_register_request, sync_storage_runner):
    """Test _register_worker handles exceptions."""
    mock_workers_api = Mock()
    mock_workers_api.register_post.side_effect = Exception("API error")
    sync_storage_runner.workers_api = mock_workers_api

    result = sync_storage_runner._register_worker()

    assert result is False
