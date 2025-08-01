import logging

from pluggy import PluginManager

from testit_python_commons.services.step_manager import StepManager
from testit_python_commons.app_properties import AppProperties


class TmsPluginManager:
    __plugin_manager = None
    __adapter_manager = None
    __fixture_manager = None
    __step_manager = None
    __logger = None

    @classmethod
    def get_plugin_manager(cls):
        if cls.__plugin_manager is None:
            cls.__plugin_manager = PluginManager('testit')

        return cls.__plugin_manager

    @classmethod
    def get_adapter_manager(cls, option=None):
        if cls.__adapter_manager is None:
            from testit_python_commons.services.adapter_manager import AdapterManager
            from testit_python_commons.client.client_configuration import ClientConfiguration
            from testit_python_commons.services.adapter_manager_configuration import AdapterManagerConfiguration

            app_properties = AppProperties.load_properties(option)

            cls.get_logger(app_properties.get('logs') == 'true')

            client_configuration = ClientConfiguration(app_properties)
            adapter_configuration = AdapterManagerConfiguration(app_properties)
            fixture_manager = cls.get_fixture_manager()

            cls.__adapter_manager = AdapterManager(adapter_configuration, client_configuration, fixture_manager)

        return cls.__adapter_manager

    @classmethod
    def get_fixture_manager(cls):
        if cls.__fixture_manager is None:
            from testit_python_commons.services.fixture_manager import FixtureManager

            cls.__fixture_manager = FixtureManager()

        return cls.__fixture_manager

    @classmethod
    def get_step_manager(cls) -> StepManager:
        if cls.__step_manager is None:
            cls.__step_manager = StepManager()

        return cls.__step_manager

    @classmethod
    def get_logger(cls, debug: bool = False):
        if cls.__logger is None:
            # Always show WARNING and above (WARNING, ERROR, CRITICAL)
            # Only show DEBUG and INFO when debug mode is enabled
            level = logging.DEBUG if debug else logging.WARNING
            logging.basicConfig(format='\n%(levelname)s (%(asctime)s): %(message)s', level=level)

            cls.__logger = logging.getLogger('TmsLogger')

        return cls.__logger

    @classmethod
    def __getattr__(cls, attribute):
        return getattr(cls.get_plugin_manager(), attribute)
