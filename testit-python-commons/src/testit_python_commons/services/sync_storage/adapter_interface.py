import abc
from typing import Any, Dict, Optional

from .sync_storage_runner import SyncStorageRunner
from .test_result_manager import TestResultManager


class SyncStorageAdapterInterface(abc.ABC):
    """
    Abstract base class for framework-specific Sync Storage adapters.
    Frameworks should implement this interface to integrate with Sync Storage.
    """

    def __init__(self):
        self.sync_storage_runner: Optional[SyncStorageRunner] = None
        self.test_result_manager: Optional[TestResultManager] = None

    @abc.abstractmethod
    def initialize_sync_storage(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the Sync Storage runner with the provided configuration.

        :param config: Configuration dictionary with test_run_id, port, base_url, private_token
        :return: True if initialization successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def start_sync_storage(self) -> bool:
        """
        Start the Sync Storage service and register the worker.

        :return: True if successfully started, False otherwise
        """
        pass

    @abc.abstractmethod
    def stop_sync_storage(self):
        """
        Stop the Sync Storage service.
        """
        pass

    @abc.abstractmethod
    def on_test_case_completed(self, test_result: Dict[str, Any]) -> bool:
        """
        Handle test case completion.

        :param test_result: Test result data
        :return: True if handled via Sync Storage, False if normal handling needed
        """
        pass

    @abc.abstractmethod
    def finalize_test_case_handling(self):
        """
        Finalize test case handling (reset in-progress flag).
        """
        pass

    def is_master_worker(self) -> bool:
        """
        Check if the current worker is the master.

        :return: True if master worker, False otherwise
        """
        if self.sync_storage_runner:
            return self.sync_storage_runner.is_master
        return False


__all__ = ["SyncStorageAdapterInterface"]
