"""Simple import tests for sync storage modules."""


def test_import_sync_storage_components():
    """Test that sync storage components can be imported without complex dependencies."""
    # We'll test imports in a way that avoids triggering complex dependency chains

    # Test direct module imports
    from testit_python_commons.services.sync_storage import (
        adapter_interface,
        config,
        sync_storage_runner,
        test_result_manager,
    )

    # Verify modules were imported
    assert sync_storage_runner is not None
    assert test_result_manager is not None
    assert config is not None
    assert adapter_interface is not None


def test_import_classes_directly():
    """Test importing classes directly from their modules."""
    # Test importing SyncStorageRunner
    from testit_python_commons.services.sync_storage.sync_storage_runner import (
        SyncStorageRunner,
    )

    assert SyncStorageRunner is not None

    # Test importing TestResultManager
    from testit_python_commons.services.sync_storage.test_result_manager import (
        TestResultManager,
    )

    assert TestResultManager is not None

    # Test importing SyncStorageConfig
    from testit_python_commons.services.sync_storage.config import SyncStorageConfig

    assert SyncStorageConfig is not None

    # Test importing SyncStorageAdapterInterface
    from testit_python_commons.services.sync_storage.adapter_interface import (
        SyncStorageAdapterInterface,
    )

    assert SyncStorageAdapterInterface is not None
