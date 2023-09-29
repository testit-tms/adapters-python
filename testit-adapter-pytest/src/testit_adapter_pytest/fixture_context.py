from uuid import uuid4

from testit_python_commons.services import Utils, TmsPluginManager


class FixtureContext:
    def __init__(self, fixture_function, parent_uuid=None, name=None):
        self._fixture_function = fixture_function
        self._parent_uuid = parent_uuid
        self.__title = name if name else fixture_function.__name__
        self.__description = fixture_function.__doc__
        self._uuid = uuid4()
        self.parameters = None

    def __call__(self, *args, **kwargs):
        self.parameters = Utils.get_function_parameters(self._fixture_function, *args, **kwargs)

        with self:
            return self._fixture_function(*args, **kwargs)

    def __enter__(self):
        TmsPluginManager.get_plugin_manager().hook.start_fixture(
                                        parent_uuid=self._parent_uuid,
                                        uuid=self._uuid,
                                        title=self.__title,
                                        parameters=self.parameters)

    def __exit__(self, exc_type, exc_val, exc_tb):
        TmsPluginManager.get_plugin_manager().hook.stop_fixture(
                                        uuid=self._uuid,
                                        exc_type=exc_type,
                                        exc_val=exc_val,
                                        exc_tb=exc_tb)
