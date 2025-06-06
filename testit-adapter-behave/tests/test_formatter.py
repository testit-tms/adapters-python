import pytest
from pytest_mock import MockerFixture

from testit_adapter_behave.formatter import AdapterFormatter
from testit_python_commons.services import TmsPluginManager


class TestAdapterFormatter:
    def test_uri_starts_launch_if_not_started(self, mocker: MockerFixture):
        # Arrange
        mock_config = mocker.Mock()
        mock_config.userdata = {}

        mock_adapter_manager = mocker.Mock()
        mock_step_manager = mocker.Mock()
        mock_plugin_manager_instance = mocker.Mock()

        mocker.patch.object(TmsPluginManager, 'get_adapter_manager', return_value=mock_adapter_manager)
        mocker.patch.object(TmsPluginManager, 'get_step_manager', return_value=mock_step_manager)
        mocker.patch.object(TmsPluginManager, 'get_plugin_manager', return_value=mock_plugin_manager_instance)

        # Mock AdapterListener
        mock_adapter_listener_instance = mocker.Mock()
        mock_adapter_listener_class = mocker.patch(
            'testit_adapter_behave.formatter.AdapterListener',
            return_value=mock_adapter_listener_instance
        )

        formatter = AdapterFormatter(stream_opener=mocker.Mock(), config=mock_config)
        
        # Ensure launch is not started initially
        formatter._AdapterFormatter__adapter_launch_is_started = False
        mocker.patch.object(formatter, 'start_adapter_launch') # Mock the method to check if it's called

        # Act
        formatter.uri("some_uri")

        # Assert
        formatter.start_adapter_launch.assert_called_once()
        mock_adapter_listener_class.assert_called_once_with(mock_adapter_manager, mock_step_manager)
        mock_plugin_manager_instance.register.assert_called_once_with(mock_adapter_listener_instance)

    def test_uri_does_not_start_launch_if_already_started(self, mocker: MockerFixture):
        # Arrange
        mock_config = mocker.Mock()
        mock_config.userdata = {}

        mocker.patch.object(TmsPluginManager, 'get_adapter_manager')
        mocker.patch.object(TmsPluginManager, 'get_step_manager')
        mocker.patch.object(TmsPluginManager, 'get_plugin_manager', return_value=mocker.Mock())

        mocker.patch(
            'testit_adapter_behave.formatter.AdapterListener'
        )

        formatter = AdapterFormatter(stream_opener=mocker.Mock(), config=mock_config)
        
        # Ensure launch is already started
        formatter._AdapterFormatter__adapter_launch_is_started = True
        mocker.patch.object(formatter, 'start_adapter_launch')

        # Act
        formatter.uri("some_uri")

        # Assert
        formatter.start_adapter_launch.assert_not_called() 