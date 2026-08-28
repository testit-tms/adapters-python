from unittest.mock import Mock

import pytest

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult


@pytest.fixture
def worker(mocker):
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


def test_load_test_result_always_uses_send_test_results(worker, mocker):
    post_mock = mocker.patch.object(
        worker._ApiClientWorker__test_run_api,
        "adapters_test_runs_id_test_results_post",
        return_value=["result-id"],
    )
    put_mock = mocker.patch.object(
        worker._ApiClientWorker__test_results_api,
        "adapters_test_results_id_put",
    )

    step = StepResult().set_title("write step").set_outcome(OutcomeType.PASSED)
    test_result = TestResult()
    test_result.set_step_results([step])
    test_result.set_outcome("Passed")
    test_result.set_duration(100)
    test_result.set_autotest_name("test")
    test_result.set_external_id("ext-1")
    test_result.set_parameters({"x": "1"})
    test_result.set_status_type("Succeeded")

    assert worker._ApiClientWorker__load_test_result(test_result) == "result-id"

    post_mock.assert_called_once()
    model = post_mock.call_args.kwargs["auto_test_results_for_test_run_model"][0]
    assert len(model.step_results) == 1
    assert model.step_results[0].title == "write step"
    assert model.status_code == "Passed"
    assert model.duration == 100
    put_mock.assert_not_called()
