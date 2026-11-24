from unittest.mock import MagicMock

from adapters_api.exceptions import ApiException

from testit_python_commons.client.helpers.bulk_autotest_helper import (
    BulkAutotestHelper,
    is_already_exists,
)


def test_is_already_exists():
    assert is_already_exists(ApiException(status=409, reason="AlreadyExistsException"))
    assert not is_already_exists(ApiException(status=500, reason="boom"))


def test_teardown_update_sends_results_after_update_failure(mocker):
    helper = BulkAutotestHelper(MagicMock(), MagicMock(), MagicMock())
    helper._BulkAutotestHelper__test_run_id = "run-id"

    update_model = MagicMock(external_id="ext-1")
    result_model = MagicMock(auto_test_external_id="ext-1")

    thread = MagicMock()
    thread.get_thread_for_update.return_value = {"ext-1": update_model}
    thread.get_thread_results_for_updated_autotests.return_value = {
        "ext-1": result_model
    }
    thread.get_thread_for_autotest_links_to_wi_for_update.return_value = {}

    all_threads = MagicMock()
    all_threads.get_threads_for_update.return_value = {"ext-1": update_model}
    all_threads.get_threads_results_for_updated_autotests.return_value = [
        {"ext-1": result_model}
    ]
    all_threads.get_threads_for_autotest_links_to_wi_for_update.return_value = {}

    helper._BulkAutotestHelper__threads_manager = MagicMock()
    helper._BulkAutotestHelper__threads_manager.get_thread_for_update_and_result.return_value = (
        thread
    )
    helper._BulkAutotestHelper__threads_manager.get_all_threads_for_update_and_result.return_value = (
        all_threads
    )

    mocker.patch.object(
        helper,
        "_BulkAutotestHelper__update_tests",
        side_effect=ApiException(status=409, reason="AlreadyExistsException"),
    )
    load = mocker.patch.object(helper, "_BulkAutotestHelper__load_test_results")

    helper.add_for_update(update_model, result_model, {})
    helper.teardown()

    load.assert_called_once()
    assert load.call_args[0][0] == [result_model]
