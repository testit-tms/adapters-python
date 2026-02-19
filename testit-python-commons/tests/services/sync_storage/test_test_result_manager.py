from unittest.mock import Mock, patch

import pytest
from testit_python_commons.services.sync_storage.sync_storage_runner import (
    SyncStorageRunner,
)
from testit_python_commons.services.sync_storage.test_result_manager import (
    TestResultManager,
)


@pytest.fixture
def mock_sync_storage_runner():
    """Create a mock SyncStorageRunner for testing."""
    runner = Mock(spec=SyncStorageRunner)
    runner.is_master = False
    runner.already_in_progress = False
    return runner


@pytest.fixture
def test_result_manager(mock_sync_storage_runner):
    """Create a TestResultManager instance for testing."""
    return TestResultManager(mock_sync_storage_runner)


def test_test_result_manager_initialization(
    test_result_manager, mock_sync_storage_runner
):
    """Test TestResultManager initialization."""
    assert test_result_manager.sync_storage_runner == mock_sync_storage_runner


def test_handle_test_completion_master_worker_not_in_progress(
    test_result_manager, mock_sync_storage_runner, sample_test_result
):
    """Test handle_test_completion when master and not in progress."""
    # Setup
    mock_sync_storage_runner.is_master = True
    mock_sync_storage_runner.already_in_progress = False
    mock_sync_storage_runner.send_in_progress_test_result.return_value = True

    # Execute
    result = test_result_manager.handle_test_completion(sample_test_result)

    # Assert
    assert result is True
    mock_sync_storage_runner.send_in_progress_test_result.assert_called_once_with(
        sample_test_result
    )


def test_handle_test_completion_master_worker_send_fails(
    test_result_manager, mock_sync_storage_runner, sample_test_result
):
    """Test handle_test_completion when sending to Sync Storage fails."""
    # Setup
    mock_sync_storage_runner.is_master = True
    mock_sync_storage_runner.already_in_progress = False
    mock_sync_storage_runner.send_in_progress_test_result.return_value = False

    # Execute
    result = test_result_manager.handle_test_completion(sample_test_result)

    # Assert
    assert result is False
    mock_sync_storage_runner.send_in_progress_test_result.assert_called_once_with(
        sample_test_result
    )


def test_handle_test_completion_master_worker_already_in_progress(
    test_result_manager, mock_sync_storage_runner, sample_test_result
):
    """Test handle_test_completion when already in progress."""
    # Setup
    mock_sync_storage_runner.is_master = True
    mock_sync_storage_runner.already_in_progress = True

    # Execute
    result = test_result_manager.handle_test_completion(sample_test_result)

    # Assert
    assert result is False
    mock_sync_storage_runner.send_in_progress_test_result.assert_not_called()


def test_handle_test_completion_non_master_worker(
    test_result_manager, mock_sync_storage_runner, sample_test_result
):
    """Test handle_test_completion when not master worker."""
    # Setup
    mock_sync_storage_runner.is_master = False

    # Execute
    result = test_result_manager.handle_test_completion(sample_test_result)

    # Assert
    assert result is False
    mock_sync_storage_runner.send_in_progress_test_result.assert_not_called()


@patch("testit_python_commons.services.sync_storage.test_result_manager.logger")
def test_handle_test_completion_exception(
    mock_logger, test_result_manager, mock_sync_storage_runner, sample_test_result
):
    """Test handle_test_completion handles exceptions gracefully."""
    # Setup
    mock_sync_storage_runner.is_master = True
    mock_sync_storage_runner.already_in_progress = False
    mock_sync_storage_runner.send_in_progress_test_result.side_effect = Exception(
        "Test error"
    )

    # Execute
    result = test_result_manager.handle_test_completion(sample_test_result)

    # Assert
    assert result is False
    mock_logger.error.assert_called_once()


def test_finalize_test_handling_master_worker(
    test_result_manager, mock_sync_storage_runner
):
    """Test finalize_test_handling for master worker."""
    # Setup
    mock_sync_storage_runner.is_master = True

    # Execute
    test_result_manager.finalize_test_handling()

    # Assert
    mock_sync_storage_runner.reset_in_progress_flag.assert_called_once()


def test_finalize_test_handling_non_master_worker(
    test_result_manager, mock_sync_storage_runner
):
    """Test finalize_test_handling for non-master worker."""
    # Setup
    mock_sync_storage_runner.is_master = False

    # Execute
    test_result_manager.finalize_test_handling()

    # Assert
    mock_sync_storage_runner.reset_in_progress_flag.assert_not_called()


@patch("testit_python_commons.services.sync_storage.test_result_manager.logger")
def test_finalize_test_handling_exception(
    mock_logger, test_result_manager, mock_sync_storage_runner
):
    """Test finalize_test_handling handles exceptions gracefully."""
    # Setup
    mock_sync_storage_runner.is_master = True
    mock_sync_storage_runner.reset_in_progress_flag.side_effect = Exception(
        "Test error"
    )

    # Execute
    test_result_manager.finalize_test_handling()

    # Assert
    mock_logger.warning.assert_called_once()
