from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest
from testit_python_commons.services.sync_storage.config import SyncStorageConfig
from testit_python_commons.services.sync_storage.sync_storage_runner import (
    SyncStorageRunner,
)


@pytest.fixture
def sample_test_result() -> Dict[str, Any]:
    """Sample test result data for testing."""
    return {
        "configurationId": "cfg-123",
        "autoTestExternalId": "test-ext-456",
        "outcome": "Passed",
        "startedOn": "2023-01-01T10:00:00Z",
        "completedOn": "2023-01-01T10:00:05Z",
        "duration": 5000,
        "message": "Test completed successfully",
        "traces": "Stack trace information",
    }


@pytest.fixture
def valid_sync_storage_config() -> SyncStorageConfig:
    """Valid SyncStorageConfig for testing."""
    return SyncStorageConfig(
        enabled=True,
        test_run_id="tr-123",
        port="49152",
        base_url="https://testit.example.com",
        private_token="token123",
    )


@pytest.fixture
def minimal_sync_storage_config() -> SyncStorageConfig:
    """Minimal SyncStorageConfig for testing."""
    return SyncStorageConfig(enabled=True, test_run_id="tr-123")


@pytest.fixture
def invalid_sync_storage_config() -> SyncStorageConfig:
    """Invalid SyncStorageConfig for testing."""
    return SyncStorageConfig(
        enabled=True, test_run_id=None, base_url=None, private_token=None
    )


@pytest.fixture
def mock_workers_api():
    """Mock WorkersApi for testing."""
    with patch(
        "testit_python_commons.services.sync_storage.sync_storage_runner.WorkersApi"
    ) as mock:
        yield mock


@pytest.fixture
def mock_test_results_api():
    """Mock TestResultsApi for testing."""
    with patch(
        "testit_python_commons.services.sync_storage.sync_storage_runner.TestResultsApi"
    ) as mock:
        yield mock


@pytest.fixture
def mock_api_client():
    """Mock ApiClient for testing."""
    with patch(
        "testit_python_commons.services.sync_storage.sync_storage_runner.SyncStorageApiClient"
    ) as mock:
        yield mock


@pytest.fixture
def mock_register_response():
    """Mock RegisterResponse for testing."""
    response = Mock()
    response.is_master = True
    return response
