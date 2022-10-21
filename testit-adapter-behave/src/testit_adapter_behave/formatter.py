from behave.formatter.base import Formatter

from testit_python_commons.services import TmsPluginManager

from .listener import AdapterListener


class AdapterFormatter(Formatter):
    __adapter_launch_is_started = False

    def __init__(self, stream_opener, config):
        super(AdapterFormatter, self).__init__(stream_opener, config)

        self.__config = config

        self.__listener = AdapterListener(
            TmsPluginManager.get_adapter_manager())

        TmsPluginManager.get_plugin_manager().register(self.__listener)

    def start_adapter_launch(self):
        self.__listener.start_launch()

        self.__adapter_launch_is_started = True

    def uri(self, uri):
        if not self.__adapter_launch_is_started:
            self.start_adapter_launch()

    def background(self, background):
        self.__listener.add_setup()

    def scenario(self, scenario):
        self.__listener.get_scenario(scenario)

    def result(self, step):
        self.__listener.add_step()

    def eof(self):
        self.__listener.set_scenario()
