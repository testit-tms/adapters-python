import json
from unittest.mock import MagicMock, patch

from testit_python_commons.services.sync_storage.sync_storage_runner import SyncStorageRunner


class TestSyncStorageKeepAlive:
    def test_keep_alive_posts_expected_payload(self):
        runner = SyncStorageRunner(
            test_run_id="run-id",
            port="49152",
        )
        runner.worker_pid = "worker-1"

        with patch("urllib.request.urlopen") as urlopen_mock:
            runner._keep_alive()

        urlopen_mock.assert_called_once()
        request = urlopen_mock.call_args[0][0]
        assert request.full_url == "http://localhost:49152/keep_alive"
        assert request.method == "POST"
        assert json.loads(request.data.decode("utf-8")) == {
            "pid": "worker-1",
            "testRunId": "run-id",
        }

    def test_keep_alive_ignores_errors(self):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")

        with patch("urllib.request.urlopen", side_effect=OSError("down")):
            runner._keep_alive()

    def test_start_keep_alive_starts_background_thread(self):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")

        with patch.object(runner, "_keep_alive_loop") as loop_mock:
            runner._start_keep_alive()
            runner._keep_alive_stop_event.set()
            runner._keep_alive_thread.join(timeout=1)

        loop_mock.assert_called_once()
