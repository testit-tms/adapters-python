import logging
from typing import Any, Dict

from .sync_storage_runner import SyncStorageRunner

logger = logging.getLogger(__name__)


class TestResultManager:
    """
    Framework-agnostic manager for handling test results with Sync Storage integration.
    """

    def __init__(self, sync_storage_runner: SyncStorageRunner):
        """
        Initialize the TestResultManager.

        :param sync_storage_runner: Initialized SyncStorageRunner instance
        """
        self.sync_storage_runner = sync_storage_runner
        logger.debug("Initialized TestResultManager")

    def handle_test_completion(self, test_result: Dict[str, Any]) -> bool:
        """
        Handle test completion according to the specification:
        1. If current worker is master and no test is in progress:
           - Send result to Sync Storage
           - Mark as "IN PROGRESS" for Test IT
           - Set in-progress flag
        2. Otherwise:
           - Write result normally to Test IT

        :param test_result: Test result data to handle
        :return: True if handled via Sync Storage, False if normal handling needed
        """
        try:
            # Only master worker handles special Sync Storage logic
            if self.sync_storage_runner.is_master:
                logger.debug("Current worker is master, checking in-progress status")

                # Check if we can send this test result
                if not self.sync_storage_runner.already_in_progress:
                    logger.debug(
                        "No test currently in progress, sending to Sync Storage"
                    )

                    # Send to Sync Storage
                    success = self.sync_storage_runner.send_in_progress_test_result(
                        test_result
                    )

                    if success:
                        # Result was sent to Sync Storage, mark as in progress
                        logger.info("Test result sent to Sync Storage successfully")
                        return True
                    else:
                        # Failed to send, fall back to normal handling
                        logger.warning(
                            "Failed to send test result to Sync Storage, falling back to normal handling"
                        )
                else:
                    logger.debug("Test already in progress, using normal handling")
            else:
                logger.debug("Current worker is not master, using normal handling")

            # Normal handling (non-master workers or fallback)
            return False

        except Exception as e:
            logger.error(f"Error handling test completion: {e}", exc_info=True)
            # Fall back to normal handling on error
            return False

    def finalize_test_handling(self):
        """
        Finalize test handling by resetting the in-progress flag.
        Should be called after the test result has been written to Test IT.
        """
        try:
            if self.sync_storage_runner.is_master:
                self.sync_storage_runner.reset_in_progress_flag()
                logger.debug("Reset in-progress flag after test result handling")
        except Exception as e:
            logger.warning(f"Error finalizing test handling: {e}")


__all__ = ["TestResultManager"]
