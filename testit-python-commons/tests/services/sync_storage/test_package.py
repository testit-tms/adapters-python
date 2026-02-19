"""Test that the sync_storage package __init__.py exports all components correctly."""


def test_sync_storage_package_exports():
    """Test that sync_storage package exports all expected components."""
    from testit_python_commons.services.sync_storage import (
        SyncStorageAdapterInterface,
        SyncStorageConfig,
        SyncStorageRunner,
        TestResultManager,
    )

    # Check that all components are exported
    assert SyncStorageRunner is not None
    assert TestResultManager is not None
    assert SyncStorageConfig is not None
    assert SyncStorageAdapterInterface is not None

    # Check that __all__ contains all expected items
    import testit_python_commons.services.sync_storage as sync_storage_pkg

    expected_exports = {
        "SyncStorageRunner",
        "TestResultManager",
        "SyncStorageConfig",
        "SyncStorageAdapterInterface",
    }

    assert set(sync_storage_pkg.__all__) == expected_exports
