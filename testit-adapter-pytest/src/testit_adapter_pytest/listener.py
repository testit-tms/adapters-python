import pickle
import pytest

from testit_python_commons.step import Step
from testit_python_commons.services import AdapterManager
from testit_python_commons.services import Utils
from testit_python_commons.models.outcome_type import OutcomeType
import testit_python_commons.services as adapter

STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED
}


class TmsListener(object):
    __executable_test = None

    def __init__(self, adapter_manager: AdapterManager):
        self.__adapter_manager = adapter_manager

    @pytest.hookimpl
    def pytest_configure(self, config):
        if not hasattr(config, "workerinput") and not hasattr(self, "test_run_id"):
            config.test_run_id = self.__adapter_manager.get_test_run_id()
        else:
            config.test_run_id = pickle.loads(config.workerinput["test_run_id"])

        self.__adapter_manager.set_test_run_id(config.test_run_id)

    @pytest.hookimpl
    def pytest_configure_node(self, node):
        if not hasattr(self, "test_run_id"):
            node.workerinput["test_run_id"] = pickle.dumps(node.config.test_run_id)

    @pytest.hookimpl
    def pytest_collection_modifyitems(self, config, items):
        index = 0
        selected_items = []
        deselected_items = []
        plugin_info = config.pluginmanager.list_plugin_distinfo()

        for plugin, dist in plugin_info:
            if 'pytest_check' == dist.project_name:
                from pytest_check import check_methods
                self.__pytest_check_get_failures = check_methods.get_failures
                break

        resolved_autotests = self.__adapter_manager.get_autotests_for_launch()

        for item in items:
            if not hasattr(item.function, 'test_external_id'):
                item.function.test_external_id = Utils.getHash(item.nodeid + item.function.__name__)

            if hasattr(item.function, 'test_external_id'):
                if item.own_markers:
                    for mark in item.own_markers:
                        if mark.name == 'parametrize':
                            if not hasattr(item, 'array_parametrize_mark_id'):
                                item.array_parametrize_mark_id = []
                            item.array_parametrize_mark_id.append(
                                item.own_markers.index(mark))

                item.test_external_id = Utils.param_attribute_collector(
                    item.function.test_external_id,
                    item.callspec.params) if hasattr(item,
                                                     'array_parametrize_mark_id'
                                                     ) else item.function.test_external_id

                item.index = index
                item_id = items.index(item)
                index = index + 1 if item_id + \
                                     1 < len(items) and item.originalname == \
                                     items[item_id + 1].originalname else 0

                if resolved_autotests \
                        and item.test_external_id in resolved_autotests:
                    selected_items.append(item)
        if resolved_autotests:
            if not selected_items:
                print('The specified tests were not found!')
                raise SystemExit

            config.hook.pytest_deselected(items=deselected_items)
            items[:] = selected_items

    @pytest.hookimpl
    def pytest_runtest_protocol(self, item):
        if not hasattr(item.function, 'test_external_id'):
            item.function.test_external_id = Utils.getHash(item.nodeid + item.function.__name__)

        if not hasattr(item.function, 'test_displayname'):
            item.function.test_displayname = item.function.__doc__ if \
                item.function.__doc__ else item.function.__name__
        else:
            if hasattr(item, 'array_parametrize_mark_id'):
                item.function.test_displayname = Utils.param_attribute_collector(
                    item.function.test_displayname,
                    item.callspec.params)

        self.__executable_test = Utils.form_test(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef):
        yield
        if self.__executable_test:
            steps_data, results_steps_data = Step.get_steps_data()

            if fixturedef.scope == 'function':
                self.__executable_test['setUp'] += steps_data
                self.__executable_test['setUpResults'] += results_steps_data

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_call(self):
        yield

        if not self.__executable_test:
            return

        test_steps, test_results_steps = Step.get_steps_data()
        self.__executable_test['steps'] = test_steps
        self.__executable_test['stepResults'] = test_results_steps

    @pytest.hookimpl
    def pytest_fixture_post_finalizer(self, fixturedef):
        if not self.__executable_test:
            return

        teardown_steps, teardown_results_steps = Step.get_steps_data()

        if fixturedef.scope == 'function':
            self.__executable_test['tearDown'] += teardown_steps
            self.__executable_test['tearDownResults'] += teardown_results_steps

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if self.__executable_test:
            if report.when == 'setup':
                self.__executable_test['outcome'] = STATUS.get(report.outcome, None)
                if report.longreprtext:
                    self.__executable_test['message'] = report.longreprtext

            if report.when == 'call':
                self.__executable_test['outcome'] = STATUS.get(report.outcome, None)

            if report.failed or hasattr(report, 'wasxfail') \
                    and not report.passed or report.outcome == 'rerun':
                self.__executable_test['outcome'] = STATUS.get('failed', None)

                if report.longreprtext:
                    self.__executable_test['traces'] = report.longreprtext

            self.__executable_test['duration'] += report.duration * 1000

    @pytest.hookimpl
    def pytest_runtest_logfinish(self):
        if not self.__executable_test:
            return

        self.__adapter_manager.write_test(self.__executable_test)

    @adapter.hookimpl
    def add_link(self, link):
        if self.__executable_test:
            self.__executable_test['resultLinks'].append(link)

    @adapter.hookimpl
    def add_message(self, test_message):
        if self.__executable_test:
            self.__executable_test['message'] = str(test_message)

    @adapter.hookimpl
    def add_attachments(self, attach_paths: list or tuple):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.load_attachments(attach_paths)

    @adapter.hookimpl
    def create_attachment(self, body, name: str):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.create_attachment(body, name)
