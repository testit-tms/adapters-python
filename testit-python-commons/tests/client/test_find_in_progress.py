import pytest

from testit_python_commons.client.api_client import ApiClientWorker


class TestFindInProgressAndUpdate:
    @pytest.fixture
    def worker(self, mocker):
        mocker.patch.object(
            ApiClientWorker,
            "_ApiClientWorker__get_status_codes",
            return_value=["PASSED", "FAILED", "INPROGRESS", "SKIPPED", "BLOCKED"],
        )
        mocker.patch.object(ApiClientWorker, "_ApiClientWorker__get_api_client_configuration")
        mocker.patch.object(ApiClientWorker, "_ApiClientWorker__get_api_client")
        mocker.patch("testit_python_commons.client.api_client.TestRunsApi")
        mocker.patch("testit_python_commons.client.api_client.AutoTestsApi")
        mocker.patch("testit_python_commons.client.api_client.AttachmentsApi")
        mocker.patch("testit_python_commons.client.api_client.TestResultsApi")
        mocker.patch("testit_python_commons.client.api_client.WorkItemsApi")
        mocker.patch("testit_python_commons.client.api_client.ProjectsApi")
        mocker.patch("testit_python_commons.client.api_client.WorkflowsApi")

        config = mocker.Mock()
        config.get_url.return_value = "https://tms.example"
        config.get_private_token.return_value = "token"
        config.get_cert_validation.return_value = True
        config.get_project_id.return_value = "proj"
        config.get_test_run_id.return_value = "run-1"
        config.get_configuration_id.return_value = "cfg-1"
        config.get_proxy.return_value = None

        return ApiClientWorker(config)

    def test_find_in_progress_prefers_valid_test_point(self, worker, mocker):
        orphan = mocker.Mock(id="orphan-id", autotest_external_id="ext-1")
        bound = mocker.Mock(id="bound-id", autotest_external_id="ext-1")
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_results",
            return_value=[orphan, bound],
        )
        mocker.patch.object(
            worker,
            "_ApiClientWorker__has_valid_test_point_id_v2",
            side_effect=lambda rid: rid == "bound-id",
        )

        assert worker.find_in_progress_test_result_id("ext-1") == "bound-id"

    def test_load_test_result_updates_existing(self, worker, mocker):
        mocker.patch.object(
            worker,
            "find_in_progress_test_result_id",
            return_value="existing-id",
        )
        update = mocker.patch.object(
            worker,
            "_ApiClientWorker__update_existing_test_result",
            return_value="existing-id",
        )
        create_post = mocker.patch.object(
            worker._ApiClientWorker__test_run_api,
            "adapters_test_runs_id_test_results_post",
        )

        test_result = mocker.Mock()
        test_result.get_external_id.return_value = "ext-1"

        assert worker._ApiClientWorker__load_test_result(test_result) == "existing-id"
        update.assert_called_once()
        create_post.assert_not_called()
