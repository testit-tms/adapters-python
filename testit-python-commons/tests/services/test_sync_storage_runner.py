import json
from io import BytesIO
from unittest.mock import MagicMock, patch

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

    def test_resolve_port_action(self):
        assert (
            SyncStorageRunner.resolve_port_action(False, None, "run-b")
            == "START_NEW"
        )
        assert (
            SyncStorageRunner.resolve_port_action(True, "run-a", "run-a")
            == "ATTACH"
        )
        assert (
            SyncStorageRunner.resolve_port_action(True, "run-a", "run-b")
            == "TRY_NEXT"
        )
        assert (
            SyncStorageRunner.resolve_port_action(True, None, "run-b")
            == "ATTACH"
        )

    def test_parse_port_defaults(self):
        assert SyncStorageRunner.parse_port(None, 49152) == 49152
        assert SyncStorageRunner.parse_port("null", 49152) == 49152
        assert SyncStorageRunner.parse_port("50000", 49152) == 50000

    def test_start_bumps_port_on_foreign_testrun(self):
        runner = SyncStorageRunner(test_run_id="run-new", port="49152")

        def health_ok():
            return runner.port == "49152"

        def fetch_id():
            return "run-old" if runner.port == "49152" else None

        with patch.object(
            runner, "_is_sync_storage_already_running", side_effect=health_ok
        ):
            with patch.object(
                runner, "_fetch_health_test_run_id", side_effect=fetch_id
            ):
                with patch.object(
                    runner, "_try_start_owned_process", return_value=True
                ) as start_mock:
                    assert runner.start() is True
                    assert runner.port == "49153"
                    start_mock.assert_called_once()

    def test_start_fails_when_all_ports_busy_with_foreign(self):
        runner = SyncStorageRunner(test_run_id="run-new", port="49152")
        with patch.object(runner, "resolve_port_max_bump", return_value=2):
            with patch.object(
                runner, "_is_sync_storage_already_running", return_value=True
            ):
                with patch.object(
                    runner, "_fetch_health_test_run_id", return_value="run-old"
                ):
                    assert runner.start() is False


class TestSyncStorageVersion:
    def test_floor_is_numeric_0_4_channel(self):
        assert SyncStorageRunner.SYNC_STORAGE_VERSION.startswith("v0.4.")
        assert "-tms-" not in SyncStorageRunner.SYNC_STORAGE_VERSION

    def test_resolved_version_is_cached(self, mocker):
        runner = SyncStorageRunner(test_run_id="run-id", port="49152")
        resolve = mocker.patch(
            "testit_python_commons.services.sync_storage.sync_storage_runner.resolve_latest",
            return_value="v0.4.9",
        )
        assert runner.resolved_version() == "v0.4.9"
        assert runner.resolved_version() == "v0.4.9"
        resolve.assert_called_once_with(SyncStorageRunner.SYNC_STORAGE_VERSION)
