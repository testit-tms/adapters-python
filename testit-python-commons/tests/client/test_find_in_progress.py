import pytest

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.client.helpers.test_result_matching import (
    normalize_parameters,
    parameters_empty,
    pick_best_in_progress_id,
)


class TestParameterMatching:
    def test_normalize_parameters(self):
        assert normalize_parameters(None) == {}
        assert normalize_parameters({}) == {}
        assert normalize_parameters({"a": 1, "b": None}) == {"a": "1", "b": ""}

    def test_parameters_empty(self):
        assert parameters_empty(None)
        assert parameters_empty({})
        assert not parameters_empty({"x": "1"})

    def test_pick_exact_match_over_empty(self):
        candidates = [
            {"id": "empty-tp", "has_test_point": True, "parameters": {}},
            {"id": "exact-tp", "has_test_point": True, "parameters": {"browser": "chrome"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) == "exact-tp"

    def test_pick_empty_fallback_when_no_exact(self):
        candidates = [
            {"id": "empty-tp", "has_test_point": True, "parameters": {}},
            {"id": "other-tp", "has_test_point": True, "parameters": {"browser": "firefox"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) == "empty-tp"

    def test_skip_incompatible_parameters(self):
        candidates = [
            {"id": "ff", "has_test_point": True, "parameters": {"browser": "firefox"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) is None

    def test_prefer_test_point_among_exact(self):
        candidates = [
            {"id": "orphan", "has_test_point": False, "parameters": {"a": "1"}},
            {"id": "bound", "has_test_point": True, "parameters": {"a": "1"}},
        ]
        assert pick_best_in_progress_id(candidates, {"a": "1"}) == "bound"

    def test_non_parametrized_picks_empty_with_tp(self):
        candidates = [
            {"id": "orphan", "has_test_point": False, "parameters": {}},
            {"id": "bound", "has_test_point": True, "parameters": {}},
        ]
        assert pick_best_in_progress_id(candidates, None) == "bound"


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
            "_ApiClientWorker__get_test_result_v2_meta",
            side_effect=lambda rid: {
                "orphan-id": {"testPointId": None, "parameters": {}},
                "bound-id": {"testPointId": "tp-1", "parameters": {}},
            }[rid],
        )

        assert worker.find_in_progress_test_result_id("ext-1") == "bound-id"

    def test_find_exact_parameters_among_multiple(self, worker, mocker):
        a = mocker.Mock(id="res-a", autotest_external_id="ext-1")
        b = mocker.Mock(id="res-b", autotest_external_id="ext-1")
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_results",
            return_value=[a, b],
        )
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_result_v2_meta",
            side_effect=lambda rid: {
                "res-a": {"testPointId": "tp-a", "parameters": {"x": "1"}},
                "res-b": {"testPointId": "tp-b", "parameters": {"x": "2"}},
            }[rid],
        )

        assert worker.find_in_progress_test_result_id("ext-1", {"x": "2"}) == "res-b"

    def test_find_empty_wi_params_fallback_and_claim(self, worker, mocker):
        a = mocker.Mock(id="res-a", autotest_external_id="ext-1")
        b = mocker.Mock(id="res-b", autotest_external_id="ext-1")
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_results",
            return_value=[a, b],
        )
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_result_v2_meta",
            side_effect=lambda rid: {
                "res-a": {"testPointId": "tp-a", "parameters": {}},
                "res-b": {"testPointId": "tp-b", "parameters": {}},
            }[rid],
        )

        first = worker.find_in_progress_test_result_id("ext-1", {"browser": "chrome"})
        second = worker.find_in_progress_test_result_id("ext-1", {"browser": "firefox"})

        assert first == "res-a"
        assert second == "res-b"
        assert first != second

    def test_find_returns_none_for_incompatible_only(self, worker, mocker):
        a = mocker.Mock(id="res-a", autotest_external_id="ext-1")
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_results",
            return_value=[a],
        )
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_result_v2_meta",
            return_value={"testPointId": "tp-a", "parameters": {"x": "1"}},
        )

        assert worker.find_in_progress_test_result_id("ext-1", {"x": "2"}) is None

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
        test_result.get_parameters.return_value = {"x": "1"}

        assert worker._ApiClientWorker__load_test_result(test_result) == "existing-id"
        worker.find_in_progress_test_result_id.assert_called_once_with("ext-1", {"x": "1"})
        update.assert_called_once()
        create_post.assert_not_called()
