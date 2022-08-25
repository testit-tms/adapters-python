import pickle
import pytest

from testit_python_commons.step import Step
from testit_python_commons.services import AdapterManager
from testit_python_commons.services import Utils
import testit_python_commons.services as adapter


class TmsListener(object):
    __executable_test = None

    def __init__(self, adapter_manager: AdapterManager):
        self.__adapter_manager = adapter_manager

    @pytest.hookimpl
    def pytest_configure_node(self, node):
        if not hasattr(self, "testrun_id"):
            node.workerinput["testrun_id"] = pickle.dumps(node.config.testrun_id)

    @pytest.hookimpl
    def pytest_collection_modifyitems(self, config, items):
        index = 0
        selected_items = []
        deselected_items = []
        resolved_autotests = []
        plugin_info = config.pluginmanager.list_plugin_distinfo()

        for plugin, dist in plugin_info:
            if 'pytest_check' == dist.project_name:
                from pytest_check import check_methods
                self.__pytest_check_get_failures = check_methods.get_failures
                break

        for item in items:
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

                if resolved_autotests:
                    if item.test_external_id in resolved_autotests:
                        selected_items.append(item)
        if resolved_autotests:
            if not selected_items:
                print('The specified tests were not found!')
                raise SystemExit
            config.hook.pytest_deselected(items=deselected_items)
            items[:] = selected_items

    @pytest.hookimpl
    def pytest_runtest_protocol(self, item):
        if hasattr(item.function, 'test_external_id'):
            if not hasattr(item.function,
                           'test_displayname') and not item.function.__doc__:
                raise Exception(
                    f'{item.originalname} must have @testit.displayName or documentation!')

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
            if report.failed or hasattr(report, 'wasxfail') \
                    and not report.passed or report.outcome == 'rerun':

                if report.longreprtext:
                    self.__executable_test['traces'] = report.longreprtext

            self.__executable_test['duration'] += report.duration * 1000

    @pytest.hookimpl
    def pytest_runtest_logfinish(self):
        if not self.__executable_test:
            return

        self.__adapter_manager.write_test(self.__executable_test)

    @adapter.hookimpl
    def add_link(self, link_url: str, link_title: str, link_type: str, link_description: str):
        if self.__executable_test:
            self.__executable_test['resultLinks'].append(
                {
                    'url': link_url,
                    'title': link_title,
                    'type': link_type,
                    'description': link_description
                })

    @adapter.hookimpl
    def add_message(self, test_message):
        if self.__executable_test:
            self.__executable_test['message'] = str(test_message)

    @adapter.hookimpl
    def add_attachments(self, attach_paths: str):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.load_attachments(attach_paths)

    @adapter.hookimpl
    def create_attachment(self, body, name: str):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.create_attachment(body, name)
