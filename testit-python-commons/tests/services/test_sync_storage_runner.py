import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
import urllib.error

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

    def test_keep_alive_ignores_connection_errors(self):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        runner.worker_pid = "worker-1"

        with patch("urllib.request.urlopen", side_effect=OSError("down")):
            runner._keep_alive()

    def test_keep_alive_worker_not_found_is_warning(self, mocker):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        runner.worker_pid = "worker-1"
        error = urllib.error.HTTPError(
            url="http://localhost:49152/keep_alive",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=BytesIO(b"Worker not found"),
        )
        warn = mocker.patch(
            "testit_python_commons.services.sync_storage.sync_storage_runner.logger.warning"
        )
        with patch("urllib.request.urlopen", side_effect=error):
            runner._keep_alive()
        warn.assert_called_once()
        assert "worker not found" in warn.call_args[0][0]

    def test_keep_alive_missing_route_404_is_debug(self, mocker):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        runner.worker_pid = "worker-1"
        error = urllib.error.HTTPError(
            url="http://localhost:49152/keep_alive",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=BytesIO(b"404 page not found"),
        )
        debug = mocker.patch(
            "testit_python_commons.services.sync_storage.sync_storage_runner.logger.debug"
        )
        with patch("urllib.request.urlopen", side_effect=error):
            runner._keep_alive()
        assert any(
            "endpoint unavailable" in str(call.args[0])
            for call in debug.call_args_list
        )

    def test_start_keep_alive_starts_background_thread(self):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        runner.worker_pid = "worker-1"

        with patch.object(runner, "_keep_alive_loop") as loop_mock:
            runner._start_keep_alive()
            runner._keep_alive_stop_event.set()
            runner._keep_alive_thread.join(timeout=1)

        loop_mock.assert_called_once()

    def test_set_worker_status_completed_stops_keep_alive(self, mocker):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        runner.worker_pid = "worker-1"
        runner.workers_api = MagicMock()
        stop = mocker.patch.object(runner, "_stop_keep_alive")

        runner.set_worker_status("completed")

        stop.assert_called_once()


class TestSyncStorageHealthReuse:
    def test_extract_json_string_field(self):
        assert (
            SyncStorageRunner.extract_json_string_field(
                '{"status":"ok","testRunId":"abc-123","last_update":"x"}',
                "testRunId",
            )
            == "abc-123"
        )
        assert SyncStorageRunner.extract_json_string_field(
            '{"status":"ok"}', "testRunId"
        ) is None

    def test_ensure_compatible_raises_on_mismatch(self):
        runner = SyncStorageRunner(test_run_id="run-new", port="49152")
        with patch.object(runner, "_fetch_health_test_run_id", return_value="run-old"):
            with pytest.raises(RuntimeError, match="another testRunId"):
                runner._ensure_compatible_existing_instance()

    def test_ensure_compatible_allows_same_test_run(self):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        with patch.object(runner, "_fetch_health_test_run_id", return_value="run-id"):
            runner._ensure_compatible_existing_instance()

    def test_start_rejects_incompatible_existing_instance(self):
        runner = SyncStorageRunner(test_run_id="run-new", port="49152")
        with patch.object(runner, "_is_sync_storage_already_running", return_value=True):
            with patch.object(
                runner, "_fetch_health_test_run_id", return_value="run-old"
            ):
                assert runner.start() is False


class TestSyncStorageVersion:
    def test_pin_is_at_least_0_4_2(self):
        assert SyncStorageRunner.SYNC_STORAGE_VERSION.startswith("v0.4.2")
