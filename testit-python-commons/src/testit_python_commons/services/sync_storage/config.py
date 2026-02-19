import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SyncStorageConfig:
    """
    Configuration class for Sync Storage integration.
    """

    DEFAULT_PORT = "49152"
    DEFAULT_ENABLED = False

    def __init__(
        self,
        enabled: bool = DEFAULT_ENABLED,
        test_run_id: Optional[str] = None,
        port: Optional[str] = None,
        base_url: Optional[str] = None,
        private_token: Optional[str] = None,
    ):
        """
        Initialize Sync Storage configuration.

        :param enabled: Whether Sync Storage integration is enabled
        :param test_run_id: Test run identifier
        :param port: Port for Sync Storage service (default: 49152)
        :param base_url: Test IT server URL
        :param private_token: Authentication token for Test IT API
        """
        self.enabled = enabled
        self.test_run_id = test_run_id
        self.port = port or self.DEFAULT_PORT
        self.base_url = base_url
        self.private_token = private_token

        logger.debug(
            f"SyncStorageConfig initialized: enabled={enabled}, port={self.port}"
        )

    @classmethod
    def from_app_properties(cls, properties: Dict[str, Any]) -> "SyncStorageConfig":
        """
        Create SyncStorageConfig from application properties.

        :param properties: Dictionary of application properties
        :return: SyncStorageConfig instance
        """
        # Check if Sync Storage is enabled (this would typically come from config)
        enabled = properties.get("syncstorage_enabled", cls.DEFAULT_ENABLED)
        if isinstance(enabled, str):
            enabled = enabled.lower() in ("true", "1", "yes", "on")

        # Extract required properties
        test_run_id = properties.get("testrunid")
        base_url = properties.get("url")
        private_token = properties.get("privatetoken")
        port = properties.get("syncstorage_port", cls.DEFAULT_PORT)

        logger.debug(f"Creating SyncStorageConfig from properties: enabled={enabled}")

        return cls(
            enabled=enabled,
            test_run_id=test_run_id,
            port=port,
            base_url=base_url,
            private_token=private_token,
        )

    def is_valid(self) -> bool:
        """
        Check if the configuration is valid for Sync Storage integration.

        :return: True if valid, False otherwise
        """
        if not self.enabled:
            return False

        required_fields = [self.test_run_id, self.base_url, self.private_token]
        if not all(required_fields):
            logger.warning(
                "Sync Storage enabled but missing required configuration fields"
            )
            return False

        return True

    def __repr__(self):
        return (
            f"SyncStorageConfig(enabled={self.enabled}, test_run_id={self.test_run_id}, "
            f"port={self.port}, base_url={self.base_url})"
        )


__all__ = ["SyncStorageConfig"]
