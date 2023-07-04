from nose2.events import Plugin

from testit_python_commons.services import TmsPluginManager

from .listener import AdapterListener


class TmsPlugin(Plugin):
    configSection = 'testit'
    commandLineSwitch = (None, 'testit', 'TMS adapter for Nose')
    __listener = None
    __tests_for_launch = None

    def __init__(self, *args, **kwargs):
        super(TmsPlugin, self).__init__(*args, **kwargs)

    def startTestRun(self, event):
        self.__listener = AdapterListener(
            TmsPluginManager.get_adapter_manager(),
            TmsPluginManager.get_step_manager())

        TmsPluginManager.get_plugin_manager().register(self.__listener)

        self.__listener.start_launch()
        self.__tests_for_launch = self.__listener.get_tests_for_launch()

    def startTest(self, event):
        self.__listener.start_test(event.test)

    def stopTest(self, event):
        self.__listener.stop_test()

    def testOutcome(self, event):
        self.__listener.set_outcome(event)
