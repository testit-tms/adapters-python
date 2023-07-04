import pickle

from packaging import version

import pytest

import testit_python_commons.services as adapter
from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.services import AdapterManager
from testit_python_commons.services import StepManager

import testit_adapter_pytest.utils as utils

STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED
}


class TmsListener(object):
    __executable_test = None
    __pytest_check_info = None
    __failures = None

    def __init__(self, adapter_manager: AdapterManager, step_manager: StepManager):
        self.__adapter_manager = adapter_manager
        self.__step_manager = step_manager

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

    @adapter.hookimpl
    def get_pytest_check_outcome(self):
        if self.__pytest_check_info:
            if version.parse(self.__pytest_check_info.version) < version.parse("1.1.0"):
                from pytest_check import check_methods as logs
            else:
                from pytest_check import check_log as logs

            failures = logs.get_failures()

            if failures and self.__failures != failures:
                self.__failures = failures[:]
                return 'Failed'
        return 'Passed'

    @pytest.hookimpl
    def pytest_collection_modifyitems(self, config, items):
        index = 0
        selected_items = []
        deselected_items = []
        plugin_info = config.pluginmanager.list_plugin_distinfo()

        for plugin, dist in plugin_info:
            if 'pytest-check' == dist.project_name:
                self.__pytest_check_info = dist
                break

        resolved_autotests = self.__adapter_manager.get_autotests_for_launch()

        for item in items:
            if hasattr(item.function, 'test_external_id'):
                item.test_external_id = item.function.test_external_id
            else:
                item.test_external_id = utils.get_hash(item.nodeid + item.function.__name__)

            if item.own_markers:
                for mark in item.own_markers:
                    if mark.name == 'parametrize':
                        if not hasattr(item, 'array_parametrize_mark_id'):
                            item.array_parametrize_mark_id = []
                        item.array_parametrize_mark_id.append(
                            item.own_markers.index(mark))

            params = utils.get_params(item)
            item.test_external_id = utils.param_attribute_collector(
                item.test_external_id,
                params)

            item.index = index
            item_id = items.index(item)
            index = index + 1 if len(items) > item_id + 1 and items[item_id + 1].originalname == item.originalname \
                else 0

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
            item.test_external_id = utils.get_hash(item.nodeid + item.function.__name__)

        if not hasattr(item.function, 'test_displayname'):
            item.test_displayname = item.function.__doc__ if \
                item.function.__doc__ else item.function.__name__
        else:
            params = utils.get_params(item)

            item.test_displayname = utils.param_attribute_collector(
                item.function.test_displayname,
                params)

        self.__executable_test = utils.form_test(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef):
        yield
        if self.__executable_test:
            results_steps_data = self.__step_manager.get_steps_tree()

            if fixturedef.scope == 'function':
                self.__executable_test['setUpResults'] += results_steps_data

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_call(self):
        yield

        if not self.__executable_test:
            return

        test_results_steps = self.__step_manager.get_steps_tree()
        self.__executable_test['stepResults'] = test_results_steps

    @pytest.hookimpl
    def pytest_fixture_post_finalizer(self, fixturedef):
        if not self.__executable_test:
            return

        teardown_results_steps = self.__step_manager.get_steps_tree()

        if fixturedef.scope == 'function':
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

        self.__adapter_manager.write_test(
            utils.convert_executable_test_to_test_result_model(self.__executable_test))

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
