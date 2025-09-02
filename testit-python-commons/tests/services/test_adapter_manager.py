import pytest
import uuid

from testit_python_commons.services.adapter_manager import AdapterManager
from testit_python_commons.services.adapter_manager_configuration import AdapterManagerConfiguration
from testit_python_commons.client.client_configuration import ClientConfiguration
from testit_python_commons.services.fixture_manager import FixtureManager
from testit_python_commons.models.adapter_mode import AdapterMode

class TestAdapterManager:
    @pytest.fixture
    def mock_adapter_config(self, mocker):
        return mocker.create_autospec(AdapterManagerConfiguration)

    @pytest.fixture
    def mock_client_config(self, mocker):
        return mocker.create_autospec(ClientConfiguration)

    @pytest.fixture
    def mock_fixture_manager(self, mocker):
        return mocker.create_autospec(FixtureManager)

    @pytest.fixture
    def mock_api_client_worker(self, mocker, mock_client_config):
        mock = mocker.patch(
            'testit_python_commons.services.adapter_manager.ApiClientWorker',
            autospec=True)
        return mock.return_value

    @pytest.fixture
    def adapter_manager(self, mock_adapter_config, mock_client_config, mock_fixture_manager, mock_api_client_worker):
        manager = AdapterManager(
            adapter_configuration=mock_adapter_config,
            client_configuration=mock_client_config,
            fixture_manager=mock_fixture_manager
        )
        manager._AdapterManager__api_client = mock_api_client_worker
        return manager

    def test_set_test_run_id(self, adapter_manager, mock_adapter_config, mock_api_client_worker):
        test_run_id = str(uuid.uuid4())
        adapter_manager.set_test_run_id(test_run_id)
        mock_adapter_config.set_test_run_id.assert_called_once_with(test_run_id)
        mock_api_client_worker.set_test_run_id.assert_called_once_with(test_run_id)

    def test_get_test_run_id_new_test_run_mode(self, adapter_manager, mock_adapter_config, mock_api_client_worker):
        test_run_id = str(uuid.uuid4())
        mock_adapter_config.get_mode.return_value = AdapterMode.NEW_TEST_RUN
        mock_api_client_worker.create_test_run.return_value = test_run_id

        test_run_result_id = adapter_manager.get_test_run_id()

        assert test_run_id == test_run_result_id
        mock_adapter_config.get_mode.assert_called_once()
        mock_api_client_worker.create_test_run.assert_called_once()
        mock_adapter_config.get_test_run_id.assert_not_called()

    def test_get_autotests_for_launch_use_filter_mode(self, adapter_manager, mock_adapter_config, mock_api_client_worker):
        mock_adapter_config.get_mode.return_value = AdapterMode.USE_FILTER
        expected_autotests = [str(uuid.uuid4()), str(uuid.uuid4())]
        mock_api_client_worker.get_external_ids_for_test_run_id.return_value = expected_autotests

        autotests = adapter_manager.get_autotests_for_launch()

        assert autotests == expected_autotests
        mock_adapter_config.get_mode.assert_called_once()
        mock_api_client_worker.get_external_ids_for_test_run_id.assert_called_once()

    def test_write_tests_realtime_import_enabled(self, adapter_manager, mock_adapter_config,
                                                 mock_api_client_worker, mock_fixture_manager):
        mock_adapter_config.should_import_realtime.return_value = True
        all_fixture_items = ["setup1", "teardown1"]
        mock_fixture_manager.get_all_items.return_value = all_fixture_items
        adapter_manager._AdapterManager__test_result_map = {"test1": "result1"}

        adapter_manager.write_tests()

        mock_adapter_config.should_import_realtime.assert_called_once()
        mock_fixture_manager.get_all_items.assert_called_once()
        mock_api_client_worker.update_test_results.assert_called_once_with(
            all_fixture_items, {"test1": "result1"}
        )
        mock_api_client_worker.write_tests.assert_not_called()

    def test_load_attachments(self, adapter_manager, mock_api_client_worker):
        attach_paths = ["path/to/attachment1.txt", "path/to/attachment2.jpg"]
        expected_result = ["id1", "id2"]
        mock_api_client_worker.load_attachments.return_value = expected_result

        result = adapter_manager.load_attachments(attach_paths)

        assert result == expected_result
        mock_api_client_worker.load_attachments.assert_called_once_with(attach_paths)

    def test_create_attachment_with_name(self, adapter_manager, mock_api_client_worker, mocker):
        mock_os_path_join = mocker.patch("os.path.join")
        mock_os_path_abspath = mocker.patch("os.path.abspath", return_value="/abs/path")
        mock_open = mocker.patch("builtins.open", mocker.mock_open())
        mock_os_remove = mocker.patch("os.remove")
        mock_utils_convert = mocker.patch(
            "testit_python_commons.services.adapter_manager.Utils.convert_body_of_attachment",
            return_value=b"converted_body"
        )

        file_body = "Hello Attachment"
        file_name = "custom_attachment.txt"
        expected_file_path = "/abs/path/custom_name.txt"
        mock_os_path_join.return_value = expected_file_path
        expected_attachment_id = str(uuid.uuid4())
        mock_api_client_worker.load_attachments.return_value = expected_attachment_id

        attachment_id = adapter_manager.create_attachment(file_body, file_name)

        mock_os_path_abspath.assert_called_once_with('')
        mock_os_path_join.assert_called_once_with("/abs/path", file_name)
        mock_open.assert_called_once_with(expected_file_path, 'wb')
        mock_open().write.assert_called_once_with(b"converted_body")
        mock_utils_convert.assert_called_once_with(file_body)
        mock_api_client_worker.load_attachments.assert_called_once_with((expected_file_path,))
        mock_os_remove.assert_called_once_with(expected_file_path)
        assert attachment_id == expected_attachment_id