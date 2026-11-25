from nose2.events import Plugin

from testit_python_commons.services import TmsPluginManager

from .listener import AdapterListener


class TmsPlugin(Plugin):
    configSection = 'testit'
    commandLineSwitch = (None, 'testit', 'TMS adapter for Nose')
    __listener = None
    __tests_for_launch = None
    __top_level_directory = None

    def __init__(self, *args, **kwargs):
        super(TmsPlugin, self).__init__(*args, **kwargs)

    def handleDir(self, event):
        if not self.__top_level_directory:
            self.__top_level_directory = event.topLevelDirectory

    def startTestRun(self, event):
        self.__listener = AdapterListener(
            TmsPluginManager.get_adapter_manager(),
            TmsPluginManager.get_step_manager(),
            self.__top_level_directory)

        TmsPluginManager.get_plugin_manager().register(self.__listener)

        self.__listener.start_launch()
        self.__tests_for_launch = self.__listener.get_tests_for_launch()

    def afterTestRun(self, event):
        self.__listener.stop_launch()

    def startTest(self, event):
        if self.__is_synthetic_loader_test(event.test):
            event.test._testit_skip = True
            return
        self.__listener.start_test(event.test)

    def stopTest(self, event):
        if getattr(event.test, '_testit_skip', False):
            return
        self.__listener.stop_test()

    def testOutcome(self, event):
        if getattr(event.test, '_testit_skip', False):
            return
        self.__listener.set_outcome(event)

    @staticmethod
    def __is_synthetic_loader_test(test) -> bool:
        # nose2.loader._makeFailedTest creates a ghost testFailure that must not go to TMS.
        module = getattr(type(test), '__module__', '') or ''
        name = getattr(test, '_testMethodName', None) or getattr(test, 'id', lambda: '')()
        return module.startswith('nose2.loader') or name == 'testFailure'
