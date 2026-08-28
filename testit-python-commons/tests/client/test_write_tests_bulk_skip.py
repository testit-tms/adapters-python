import pytest

from testit_python_commons.client.api_client import ApiClientWorker


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


def test_write_tests_skips_send_for_already_finalized(worker, mocker):
    bulk_helper_cls = mocker.patch("testit_python_commons.client.api_client.BulkAutotestHelper")
    bulk_helper = bulk_helper_cls.return_value
    mocker.patch.object(worker, "_ApiClientWorker__add_fixtures_to_test_result", side_effect=lambda tr, _: tr)
    mocker.patch.object(
        worker,
        "_ApiClientWorker__get_autotests_by_external_id",
        return_value=[mocker.Mock(id="autotest-1")],
    )
    update_auto_test = mocker.patch.object(worker, "_ApiClientWorker__update_auto_test")

    finalized = mocker.Mock()
    finalized.get_external_id.return_value = "ext-finalized"
    finalized.get_automatic_creation_test_cases.return_value = False

    pending = mocker.Mock()
    pending.get_external_id.return_value = "ext-pending"
    pending.get_automatic_creation_test_cases.return_value = False
    pending.get_status_type.return_value = "Succeeded"
    pending.get_step_results.return_value = []
    pending.get_setup_results.return_value = []
    pending.get_teardown_results.return_value = []
    pending.get_outcome.return_value = "Passed"
    pending.get_duration.return_value = 0
    pending.get_message.return_value = None
    pending.get_traces.return_value = None
    pending.get_result_links.return_value = []
    pending.get_parameters.return_value = {}
    pending.get_properties.return_value = {}
    pending.get_attachments.return_value = []
    pending.get_started_on.return_value = None
    pending.get_completed_on.return_value = None
    pending.get_work_item_ids.return_value = []

    mocker.patch(
        "testit_python_commons.client.api_client.Converter.prepare_to_mass_update_autotest",
        return_value=mocker.Mock(),
    )

    worker.write_tests(
        [finalized, pending],
        {},
        finalized_external_ids={"ext-finalized"},
    )

    update_auto_test.assert_called_once_with(finalized, mocker.ANY)
    bulk_helper.add_for_create.assert_not_called()
    bulk_helper.add_for_update.assert_called_once()
    bulk_helper.teardown.assert_called_once()
