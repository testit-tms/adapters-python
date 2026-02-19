#!/usr/bin/env python3
"""
Standalone test script for Sync Storage components.
This script tests the core functionality without requiring the full project setup.
"""

import os
import sys
import tempfile
from unittest.mock import MagicMock, Mock, patch

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))


def test_sync_storage_config():
    """Test SyncStorageConfig class."""
    print("Testing SyncStorageConfig...")

    try:
        from testit_python_commons.services.sync_storage.config import SyncStorageConfig

        # Test initialization
        config = SyncStorageConfig(
            enabled=True,
            test_run_id="tr-123",
            port="49153",
            base_url="https://testit.example.com",
            private_token="token123",
        )

        assert config.enabled is True
        assert config.test_run_id == "tr-123"
        assert config.port == "49153"
        assert config.base_url == "https://testit.example.com"
        assert config.private_token == "token123"

        # Test default port
        config2 = SyncStorageConfig(test_run_id="tr-456")
        assert config2.port == SyncStorageConfig.DEFAULT_PORT

        # Test validation
        valid_config = SyncStorageConfig(
            enabled=True,
            test_run_id="tr-789",
            base_url="https://testit.example.com",
            private_token="token789",
        )
        assert valid_config.is_valid() is True

        invalid_config = SyncStorageConfig(enabled=True, test_run_id=None)
        assert invalid_config.is_valid() is False

        print("✓ SyncStorageConfig tests passed")
        return True

    except Exception as e:
        print(f"✗ SyncStorageConfig tests failed: {e}")
        return False


def test_sync_storage_runner_import():
    """Test that SyncStorageRunner can be imported."""
    print("Testing SyncStorageRunner import...")

    try:
        from testit_python_commons.services.sync_storage.sync_storage_runner import (
            SyncStorageRunner,
        )

        print("✓ SyncStorageRunner imported successfully")
        return True
    except Exception as e:
        print(f"✗ SyncStorageRunner import failed: {e}")
        return False


def test_test_result_manager_import():
    """Test that TestResultManager can be imported."""
    print("Testing TestResultManager import...")

    try:
        from testit_python_commons.services.sync_storage.test_result_manager import (
            TestResultManager,
        )

        print("✓ TestResultManager imported successfully")
        return True
    except Exception as e:
        print(f"✗ TestResultManager import failed: {e}")
        return False


def test_adapter_interface_import():
    """Test that SyncStorageAdapterInterface can be imported."""
    print("Testing SyncStorageAdapterInterface import...")

    try:
        from testit_python_commons.services.sync_storage.adapter_interface import (
            SyncStorageAdapterInterface,
        )

        print("✓ SyncStorageAdapterInterface imported successfully")
        return True
    except Exception as e:
        print(f"✗ SyncStorageAdapterInterface import failed: {e}")
        return False


def test_package_exports():
    """Test that sync_storage package exports all components."""
    print("Testing package exports...")

    try:
        from testit_python_commons.services.sync_storage import (
            SyncStorageAdapterInterface,
            SyncStorageConfig,
            SyncStorageRunner,
            TestResultManager,
        )

        assert SyncStorageRunner is not None
        assert TestResultManager is not None
        assert SyncStorageConfig is not None
        assert SyncStorageAdapterInterface is not None

        print("✓ Package exports test passed")
        return True
    except Exception as e:
        print(f"✗ Package exports test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running standalone tests for Sync Storage components...\n")

    tests = [
        test_sync_storage_config,
        test_sync_storage_runner_import,
        test_test_result_manager_import,
        test_adapter_interface_import,
        test_package_exports,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"Test {test.__name__} crashed: {e}")
            failed += 1
        print()

    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("All tests passed! 🎉")
        return 0
    else:
        print("Some tests failed! ❌")
        return 1


if __name__ == "__main__":
    sys.exit(main())
