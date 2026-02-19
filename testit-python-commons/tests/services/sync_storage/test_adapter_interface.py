from abc import ABC, abstractmethod

import pytest
from testit_python_commons.services.sync_storage.adapter_interface import (
    SyncStorageAdapterInterface,
)


class ConcreteSyncStorageAdapter(SyncStorageAdapterInterface):
    """Concrete implementation of SyncStorageAdapterInterface for testing."""

    def initialize_sync_storage(self, config):
        # Simple implementation for testing
        return True

    def start_sync_storage(self):
        # Simple implementation for testing
        return True

    def stop_sync_storage(self):
        # Simple implementation for testing
        pass

    def on_test_case_completed(self, test_result):
        # Simple implementation for testing
        return False

    def finalize_test_case_handling(self):
        # Simple implementation for testing
        pass


def test_sync_storage_adapter_interface_cannot_be_instantiated():
    """Test that SyncStorageAdapterInterface cannot be instantiated directly."""
    with pytest.raises(TypeError):
        SyncStorageAdapterInterface()


def test_concrete_adapter_initialization():
    """Test that concrete adapter can be instantiated."""
    adapter = ConcreteSyncStorageAdapter()

    # Check that properties are initialized to None
    assert adapter.sync_storage_runner is None
    assert adapter.test_result_manager is None


def test_concrete_adapter_implements_all_abstract_methods():
    """Test that concrete adapter implements all required abstract methods."""
    adapter = ConcreteSyncStorageAdapter()

    # Check that all abstract methods are implemented
    assert callable(adapter.initialize_sync_storage)
    assert callable(adapter.start_sync_storage)
    assert callable(adapter.stop_sync_storage)
    assert callable(adapter.on_test_case_completed)
    assert callable(adapter.finalize_test_case_handling)


def test_is_master_worker_without_runner():
    """Test is_master_worker returns False when runner is not set."""
    adapter = ConcreteSyncStorageAdapter()

    result = adapter.is_master_worker()

    assert result is False


def test_is_master_worker_with_runner():
    """Test is_master_worker returns correct value from runner."""
    adapter = ConcreteSyncStorageAdapter()

    # Mock runner with is_master = True
    mock_runner = type("MockRunner", (), {"is_master": True})()
    adapter.sync_storage_runner = mock_runner

    result = adapter.is_master_worker()

    assert result is True
