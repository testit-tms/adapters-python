"""Test that all sync storage modules can be imported correctly."""


def test_import_sync_storage_runner():
    """Test that SyncStorageRunner can be imported."""
    from testit_python_commons.services.sync_storage.sync_storage_runner import (
        SyncStorageRunner,
    )

    assert SyncStorageRunner is not None


def test_import_test_result_manager():
    """Test that TestResultManager can be imported."""
    from testit_python_commons.services.sync_storage.test_result_manager import (
        TestResultManager,
    )

    assert TestResultManager is not None


def test_import_sync_storage_config():
    """Test that SyncStorageConfig can be imported."""
    from testit_python_commons.services.sync_storage.config import SyncStorageConfig

    assert SyncStorageConfig is not None


def test_import_sync_storage_adapter_interface():
    """Test that SyncStorageAdapterInterface can be imported."""
    from testit_python_commons.services.sync_storage.adapter_interface import (
        SyncStorageAdapterInterface,
    )

    assert SyncStorageAdapterInterface is not None


def test_import_from_services_package():
    """Test that sync storage components can be imported from services package."""
    from testit_python_commons.services import (
        SyncStorageAdapterInterface,
        SyncStorageConfig,
        SyncStorageRunner,
        TestResultManager,
    )

    assert SyncStorageRunner is not None
    assert TestResultManager is not None
    assert SyncStorageConfig is not None
    assert SyncStorageAdapterInterface is not None
