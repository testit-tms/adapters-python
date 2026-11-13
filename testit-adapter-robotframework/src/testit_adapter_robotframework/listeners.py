import re

from robot.api import SuiteVisitor, logger
from robot.libraries.BuiltIn import BuiltIn

from testit_python_commons.services import TmsPluginManager

from .models import Autotest, Option
from .utils import STATUS_TYPES, STEP_STATUSES, convert_executable_test_to_test_result_model, convert_time, get_hash

TMS_CLI_PARAMS = (
    "tmsUrl",
    "tmsPrivateToken",
    "tmsProjectId",
    "tmsConfigurationId",
    "tmsTestRunId",
    "tmsProxy",
    "tmsTestRunName",
    "tmsTestRunTags",
    "tmsTestRunLinks",
    "tmsAdapterMode",
    "tmsConfigFile",
    "tmsCertValidation",
    "tmsAutomaticCreationTestCases",
    "tmsAutomaticUpdationLinksToTestCases",
    "tmsImportRealtime",
)


class AutotestAdapter:
    ROBOT_LISTENER_API_VERSION = 2

    # self.adapter_manager.on_block_completed()
    # self.adapter_manager.on_running_started()

    def __init__(self, adapter_manager):
        self.adapter_manager = adapter_manager
        self.active_test = None

    @staticmethod
    def get_test_title(attrs):
        title = attrs['type']
        return "\t".join(
            attrs['assign'] + [title if title not in ["SETUP", "TEARDOWN", "KEYWORD"] else "",
                               attrs['kwname']] + attrs['args'])

    @staticmethod
    def parse_arguments(args):
        parameters = {}
        for arg in args:
            variables = re.findall(r'\${[a-zA-Z-_\\ \d]*}', arg)
            for arg_var in variables:
                value = str(BuiltIn().get_variable_value(arg_var))
                if len(value) > 2000:
                    value = value[:2000]
                parameters[arg_var] = value
        return parameters if parameters else None

    def start_test(self, name, attributes):
        self.active_test = Autotest(autoTestName=name)
        self.active_test.add_attributes(attributes)
        BuiltIn().remove_tags("testit*")
        self.adapter_manager.on_running_started()

    def start_keyword(self, name, attributes):
        if self.active_test:
            title = self.get_test_title(attributes)
            parameters = self.parse_arguments(attributes['args'])
            self.active_test.add_step(attributes['type'], title, attributes['doc'], parameters)

    def end_keyword(self, name, attributes):
        if self.active_test:
            title = self.get_test_title(attributes)
            start = convert_time(attributes['starttime'])
            end = convert_time(attributes['endtime'])
            duration = attributes['elapsedtime']
            outcome = STEP_STATUSES[attributes['status']]
            self.active_test.add_step_result(title, start, end, duration, outcome, self.active_test.attachments)
            self.active_test.attachments = []

    def end_test(self, name, attributes):
        if self.active_test:
            self.active_test.outcome = attributes['status']
            self.active_test.status_type = STATUS_TYPES[attributes['status']]
            self.active_test.started_on = convert_time(attributes['starttime'])
            self.active_test.completed_on = convert_time(attributes['endtime'])
            if not self.active_test.message and self.active_test.outcome == 'FAIL':
                for step in (self.active_test.setUpResults + self.active_test.stepResults +
                             self.active_test.tearDownResults):
                    if step.outcome == 'Failed':
                        self.active_test.message = f"Failed on step: '{step.title}'"
                        break
            self.active_test.traces = attributes['message']
            self.active_test.duration = attributes['elapsedtime']
            self.adapter_manager.write_test(
                convert_executable_test_to_test_result_model(self.active_test.order()))

    def close(self):
        self.adapter_manager.on_block_completed()
        self.adapter_manager.write_tests()


class TestRunAdapter:
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, adapter_manager):
        self.adapter_manager = adapter_manager

    def start_suite(self, suite, result):
        tests = self.adapter_manager.get_autotests_for_launch()
        if tests is not None:
            selector = ExcludeTests(*tests)
            suite.visit(selector)


class ExcludeTests(SuiteVisitor):

    def __init__(self, *tests):
        self.tests = tests
        if not len(self.tests):
            logger.error('No tests to run!')
            raise SystemExit

    def start_suite(self, suite):
        suite.tests = [t for t in suite.tests if self._is_included(t)]

    def _is_included(self, test):
        tags = test.tags
        external_id = get_hash(test.longname)
        for tag in tags:
            if str(tag).lower().startswith('testit.externalid'):
                external_id = tag.split(':', 1)[-1].strip()
        return external_id in self.tests

    def end_suite(self, suite):
        suite.suites = [s for s in suite.suites if s.test_count > 0]

    def visit_test(self, test):
        pass


class testit_adapter_robotframework:  # noqa: N801
    """Module-level listener for ``robot --listener testit_adapter_robotframework``.

    Before, this invocation silently did nothing: Robot Framework imported the
    package, found neither a class named like the module nor listener methods
    in the empty ``__init__.py``, and ran the whole suite without a single
    request to Test IT and without any warning (TMS-38320).

    The adapter is configured at the first ``start_suite`` event from the same
    sources as ``TMSLibrary`` (robot CLI variables ``-v tms...:...`` override
    ``TMS_*`` environment variables and ``connection_config.ini`` /
    ``pyproject.toml``), because robot variables are not accessible in the
    listener constructor yet. When the ``${testit}`` variable is set,
    ``TMSLibrary`` is responsible for exporting results and this listener
    stays idle to avoid duplicating every result.
    """

    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.adapter_manager = None
        self.active_adapter = None
        self._adapter_resolved = False

    def _resolve_adapter(self):
        built_in = BuiltIn()
        if built_in.get_variable_value("${testit}", None) is not None:
            logger.warn("[TestIt] The ${testit} variable is set: TMSLibrary exports results, "
                        "the testit_adapter_robotframework listener stays idle")
            return None

        option = Option(**{param: built_in.get_variable_value(f'${{{param}}}', None) for param in TMS_CLI_PARAMS})
        adapter_manager = TmsPluginManager.get_adapter_manager(option)
        self._set_test_run_id(adapter_manager, built_in.get_variable_value('${PABOTQUEUEINDEX}', None))
        self.adapter_manager = adapter_manager
        return AutotestAdapter(adapter_manager)

    @staticmethod
    def _set_test_run_id(adapter_manager, pabot_index):
        if pabot_index is None:
            adapter_manager.set_test_run_id(adapter_manager.get_test_run_id())
            return

        try:
            from pabot import PabotLib
            pabot = PabotLib()
            if int(pabot_index) == 0:
                test_run_id = adapter_manager.get_test_run_id()
                pabot.set_parallel_value_for_key('test_run_id', test_run_id)
            else:
                while True:
                    test_run_id = pabot.get_parallel_value_for_key('test_run_id')
                    if test_run_id:
                        break
        except RuntimeError:
            logger.warn("[TestIt] pabot is running without --pabotlib: the test run id cannot be shared "
                        "between parallel processes, every process will export on its own "
                        "(a separate test run is created in adapter mode 2)")
            adapter_manager.set_test_run_id(adapter_manager.get_test_run_id())
            return

        adapter_manager.set_test_run_id(test_run_id)

    def start_suite(self, name, attributes):
        if not self._adapter_resolved:
            self._adapter_resolved = True
            self.active_adapter = self._resolve_adapter()

    def start_test(self, name, attributes):
        if self.active_adapter:
            self.active_adapter.start_test(name, attributes)

    def start_keyword(self, name, attributes):
        if self.active_adapter:
            self.active_adapter.start_keyword(name, attributes)

    def end_keyword(self, name, attributes):
        if self.active_adapter:
            self.active_adapter.end_keyword(name, attributes)

    def end_test(self, name, attributes):
        if self.active_adapter:
            self.active_adapter.end_test(name, attributes)

    def close(self):
        if self.active_adapter:
            self.active_adapter.close()
