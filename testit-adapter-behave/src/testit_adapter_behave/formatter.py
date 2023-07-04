from behave.formatter.base import Formatter

from testit_python_commons.services import TmsPluginManager

from .listener import AdapterListener
from .utils import filter_out_scenarios, parse_userdata


class AdapterFormatter(Formatter):
    __adapter_launch_is_started = False
    __tests_for_launch = None

    def __init__(self, stream_opener, config):
        super(AdapterFormatter, self).__init__(stream_opener, config)

        option = parse_userdata(config.userdata)

        self.__listener = AdapterListener(
            TmsPluginManager.get_adapter_manager(option),
            TmsPluginManager.get_step_manager())

        TmsPluginManager.get_plugin_manager().register(self.__listener)

    def start_adapter_launch(self):
        self.__listener.start_launch()

        self.__tests_for_launch = self.__listener.get_tests_for_launch()
        self.__adapter_launch_is_started = True

    def uri(self, uri):
        if not self.__adapter_launch_is_started:
            self.start_adapter_launch()

    def feature(self, feature):
        feature.scenarios = filter_out_scenarios(
            self.__tests_for_launch,
            feature.scenarios)

    def scenario(self, scenario):
        self.__listener.get_scenario(scenario)

    def match(self, match):
        self.__listener.get_step_parameters(match)

    def result(self, step):
        self.__listener.get_step_result(step)
