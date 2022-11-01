from robot.libraries.BuiltIn import BuiltIn
from robot.api import SuiteVisitor, logger
from testit_python_commons.services import Utils

from .utils import convert_time, STATUSES
from .models import Autotest


class AutotestAdapter:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, adapter_manager):
        self.adapter_manager = adapter_manager
        self.active_test = None

    @staticmethod
    def get_test_title(attrs):
        t = attrs['type']
        return "\t".join(attrs['assign'] +
                         [t if t not in ["SETUP", "TEARDOWN", "KEYWORD"] else "", attrs['kwname']] + attrs['args'])

    @staticmethod
    def parse_arguments(args):
        parameters = {}
        for arg in args:
            arg = arg.replace('"', '').replace("'", '').replace("/", '')
            if '$' in arg or '@' in arg or '&' in arg:
                value = str(BuiltIn().get_variable_value(arg))
                if len(value) > 2000:
                    value = value[:2000]
                parameters[arg] = value
        return parameters if parameters else None

    def start_test(self, name, attributes):
        self.active_test = Autotest(autoTestName=name)
        self.active_test.add_attributes(attributes)
        BuiltIn().remove_tags("testit*")

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
            outcome = STATUSES[attributes['status']]
            self.active_test.add_step_result(title, start, end, duration, outcome)

    def end_test(self, name, attributes):
        if self.active_test:
            self.active_test.outcome = STATUSES[attributes['status']]
            self.active_test.started_on = convert_time(attributes['starttime'])
            self.active_test.completed_on = convert_time(attributes['endtime'])
            if not self.active_test.message:
                if self.active_test.outcome == 'Failed':
                    for s in self.active_test.setupResults + self.active_test.stepResults \
                             + self.active_test.teardownResults:
                        if s.outcome == 'Failed':
                            self.active_test.message = f"Failed on step: '{s.title}'"
                            break
            self.active_test.traces = attributes['message']
            self.active_test.duration = attributes['elapsedtime']
            self.adapter_manager.write_test(self.active_test.dict())


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
        if len(self.tests):
            logger.error('No tests to run!')
            raise SystemExit

    def start_suite(self, suite):
        suite.tests = [t for t in suite.tests if self._is_included(t)]

    def _is_included(self, test):
        tags = test.tags
        external_id = Utils.getHash(test.longname.split('.', 1)[-1])
        for tag in tags:
            if str(tag).lower().startswith('testit.externalid'):
                external_id = tag.split(':', 1)[-1].strip()
        return external_id in self.tests

    def end_suite(self, suite):
        suite.suites = [s for s in suite.suites if s.test_count > 0]

    def visit_test(self, test):
        pass
