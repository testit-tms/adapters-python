import pytest
import logging

from testit_python_commons.services.plugin_manager import TmsPluginManager
from testit_python_commons.services.fixture_manager import FixtureManager

@pytest.fixture(autouse=True)
def reset_tms_plugin_manager_singletons():
    TmsPluginManager._TmsPluginManager__plugin_manager = None
    TmsPluginManager._TmsPluginManager__adapter_manager = None
    TmsPluginManager._TmsPluginManager__fixture_manager = None
    TmsPluginManager._TmsPluginManager__step_manager = None
    TmsPluginManager._TmsPluginManager__logger = None

class TestTmsPluginManager:
    def test_get_plugin_manager_creates_instance(self):
        from pluggy import PluginManager
        pm = TmsPluginManager.get_plugin_manager()
        assert pm is not None
        assert isinstance(pm, PluginManager)
        assert pm.project_name == 'testit'

    def test_get_fixture_manager_creates_instance(self):
        fm = TmsPluginManager.get_fixture_manager()
        assert fm is not None
        assert isinstance(fm, FixtureManager)

    def test_get_step_manager_creates_instance(self):
        from testit_python_commons.services.step_manager import StepManager
        sm = TmsPluginManager.get_step_manager()
        assert sm is not None
        assert isinstance(sm, StepManager)

    def test_get_logger_creates_instance(self):
        logger = TmsPluginManager.get_logger()
        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == 'TmsLogger'

    def test_get_adapter_manager_creates_instance(self, mocker):
        mocks = self._setup_adapter_manager_dependencies_mocks(mocker, logs_enabled_str='false')
        
        test_option = "test_config_option"
        adapter_manager_instance = TmsPluginManager.get_adapter_manager(option=test_option)

        assert adapter_manager_instance is mocks['adapter_manager_ctor'].return_value
        assert TmsPluginManager._TmsPluginManager__adapter_manager is mocks['adapter_manager_ctor'].return_value

        mocks['load_properties'].assert_called_once_with(test_option)
        mocks['app_properties_instance'].get.assert_called_once_with('logs')
        mocks['get_logger'].assert_called_once_with(False)
        
        mocks['client_configuration_ctor'].assert_called_once_with(mocks['app_properties_instance'])
        mocks['adapter_manager_configuration_ctor'].assert_called_once_with(mocks['app_properties_instance'])

        mocks['adapter_manager_ctor'].assert_called_once_with(
            mocks['adapter_manager_configuration_ctor'].return_value,
            mocks['client_configuration_ctor'].return_value,
            mocks['fixture_manager_instance']
        )

    def _setup_adapter_manager_dependencies_mocks(self, mocker, logs_enabled_str: str = 'false'):
        mock_app_properties_instance = mocker.MagicMock()
        mock_app_properties_instance.get.return_value = logs_enabled_str

        mock_load_properties = mocker.patch(
            'testit_python_commons.app_properties.AppProperties.load_properties',
            return_value=mock_app_properties_instance)

        mock_get_logger = mocker.patch.object(TmsPluginManager, 'get_logger')

        mock_fixture_manager_instance = mocker.MagicMock(spec=FixtureManager)
        mocker.patch.object(TmsPluginManager, 'get_fixture_manager', return_value=mock_fixture_manager_instance)

        mock_client_configuration_ctor = mocker.patch(
            'testit_python_commons.client.client_configuration.ClientConfiguration')
        mock_adapter_manager_configuration_ctor = mocker.patch(
            'testit_python_commons.services.adapter_manager_configuration.AdapterManagerConfiguration')
        mock_adapter_manager_ctor = mocker.patch('testit_python_commons.services.adapter_manager.AdapterManager')

        return {
            'load_properties': mock_load_properties,
            'app_properties_instance': mock_app_properties_instance,
            'get_logger': mock_get_logger,
            'fixture_manager_instance': mock_fixture_manager_instance,
            'client_configuration_ctor': mock_client_configuration_ctor,
            'adapter_manager_configuration_ctor': mock_adapter_manager_configuration_ctor,
            'adapter_manager_ctor': mock_adapter_manager_ctor
        }