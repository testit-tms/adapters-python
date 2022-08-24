from pluggy import PluginManager

import testit_python_commons.services.adapter_manager as adapter_manager


class TmsPluginManager:
    __plugin_manager = None
    __adapter_manager = None

    @classmethod
    def get_plugin_manager(cls):
        if cls.__plugin_manager is None:
            cls.__plugin_manager = PluginManager('testit')

        return cls.__plugin_manager

    @classmethod
    def get_adapter_manager(cls, option=None):
        if cls.__adapter_manager is None:
            cls.__adapter_manager = adapter_manager.AdapterManager(option)

        return cls.__adapter_manager

    @classmethod
    def __getattr__(cls, attribute):
        return getattr(cls.get_plugin_manager(), attribute)
