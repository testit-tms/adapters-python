import pytest
from testit_python_commons.services.sync_storage.config import SyncStorageConfig


def test_sync_storage_config_initialization():
    """Test SyncStorageConfig initialization with all parameters."""
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


def test_sync_storage_config_default_port():
    """Test SyncStorageConfig uses default port when not specified."""
    config = SyncStorageConfig(test_run_id="tr-123")

    assert config.port == SyncStorageConfig.DEFAULT_PORT


def test_sync_storage_config_from_app_properties():
    """Test creating SyncStorageConfig from application properties."""
    properties = {
        "syncstorage_enabled": "true",
        "testrunid": "tr-456",
        "syncstorage_port": "49154",
        "url": "https://testit2.example.com",
        "privatetoken": "token456",
    }

    config = SyncStorageConfig.from_app_properties(properties)

    assert config.enabled is True
    assert config.test_run_id == "tr-456"
    assert config.port == "49154"
    assert config.base_url == "https://testit2.example.com"
    assert config.private_token == "token456"


def test_sync_storage_config_from_app_properties_defaults():
    """Test creating SyncStorageConfig from app properties with defaults."""
    properties = {
        "testrunid": "tr-789",
        "url": "https://testit3.example.com",
        "privatetoken": "token789",
    }

    config = SyncStorageConfig.from_app_properties(properties)

    assert config.enabled is False  # Default value
    assert config.test_run_id == "tr-789"
    assert config.port == SyncStorageConfig.DEFAULT_PORT  # Default value
    assert config.base_url == "https://testit3.example.com"
    assert config.private_token == "token789"


def test_sync_storage_config_is_valid():
    """Test SyncStorageConfig validation with valid configuration."""
    config = SyncStorageConfig(
        enabled=True,
        test_run_id="tr-123",
        base_url="https://testit.example.com",
        private_token="token123",
    )

    assert config.is_valid() is True


def test_sync_storage_config_is_invalid_when_disabled():
    """Test SyncStorageConfig validation when disabled."""
    config = SyncStorageConfig(
        enabled=False,
        test_run_id="tr-123",
        base_url="https://testit.example.com",
        private_token="token123",
    )

    assert config.is_valid() is False


def test_sync_storage_config_is_invalid_when_missing_required_fields():
    """Test SyncStorageConfig validation with missing required fields."""
    config = SyncStorageConfig(enabled=True, test_run_id=None)

    assert config.is_valid() is False


def test_sync_storage_config_string_representation():
    """Test SyncStorageConfig string representation."""
    config = SyncStorageConfig(
        enabled=True,
        test_run_id="tr-123",
        port="49152",
        base_url="https://testit.example.com",
    )

    repr_str = repr(config)
    assert "SyncStorageConfig" in repr_str
    assert "enabled=True" in repr_str
    assert "test_run_id=tr-123" in repr_str
    assert "port=49152" in repr_str
    assert "base_url=https://testit.example.com" in repr_str
