import pickle
from importlib.metadata import metadata
from uuid import uuid4

from packaging import version

import pytest

import testit_python_commons.services as adapter
from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.services import AdapterManager
from testit_python_commons.services import StepManager
from testit_python_commons.services.logger import adapter_logger

import testit_adapter_pytest.utils as utils
from testit_adapter_pytest.fixture_context import FixtureContext
from testit_adapter_pytest.fixture_manager import FixtureManager
from testit_adapter_pytest.models.fixture import FixtureResult, FixturesContainer

STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED
}


class ItemCache:
    def __init__(self):
        self._items = dict()

    def get(self, _id):
        return self._items.get(id(_id))

    def push(self, _id):
        return self._items.setdefault(id(_id), uuid4())

    def pop(self, _id):
        return self._items.pop(id(_id), None)


class SeparationOfTests:
    def __init__(self):
        self._selected_items = []
        self._deselected_items = []

    def add_item_to_selected_items(self, item):
        self._selected_items.append(item)

        return self

    def add_item_to_deselected_items(self, item):
        self._deselected_items.append(item)

        return self

    def get_selected_items(self) -> list:
        return self._selected_items

    def get_deselected_items(self) -> list:
        return self._deselected_items


class TmsListener(object):
    __executable_test = None
    __pytest_info = None
    __pytest_check_info = None
    __failures = None

    def __init__(self, adapter_manager: AdapterManager, step_manager: StepManager):
        self.__adapter_manager = adapter_manager
        self.__step_manager = step_manager
        self.fixture_manager = FixtureManager()
        self._cache = ItemCache()
        self.__test_result_ids = {}

    @pytest.hookimpl
    def pytest_configure(self, config):
        self.__pytest_info = metadata("pytest")

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
        self.__add_pytest_check_info(config.pluginmanager.list_plugin_distinfo())

        resolved_autotests = self.__adapter_manager.get_autotests_for_launch()
        separation_of_tests = self.__get_separation_of_tests(items, resolved_autotests)

        if resolved_autotests:
            if not separation_of_tests.get_selected_items():
                print('The specified tests were not found!')
                raise SystemExit

            config.hook.pytest_deselected(items=separation_of_tests.get_deselected_items())
            items[:] = separation_of_tests.get_selected_items()

    def __add_pytest_check_info(self, plugin_info):
        for plugin, dist in plugin_info:
            if 'pytest-check' == dist.project_name:
                self.__pytest_check_info = dist
                return

    @classmethod
    @adapter_logger
    def __get_separation_of_tests(cls, items, resolved_autotests) -> SeparationOfTests:
        separation_of_tests = SeparationOfTests()
        index = 0

        for item in items:
            if hasattr(item.function, 'test_external_id'):
                item.test_external_id = item.function.test_external_id
            else:
                item.test_external_id = utils.get_hash(item.parent.nodeid + item.function.__name__)

            if item.own_markers:
                for mark in item.own_markers:
                    if mark.name == 'parametrize':
                        if not hasattr(item, 'array_parametrize_mark_id'):
                            item.array_parametrize_mark_id = []
                        item.array_parametrize_mark_id.append(
                            item.own_markers.index(mark))

            params = utils.get_all_parameters(item)
            item.test_external_id = utils.collect_parameters_in_string_attribute(
                item.test_external_id,
                params)

            item.index = index
            item_id = items.index(item)
            index = index + 1 if len(items) > item_id + 1 and items[item_id + 1].originalname == item.originalname \
                else 0

            if cls.__check_external_id_in_resolved_autotests(item.test_external_id, resolved_autotests):
                separation_of_tests.add_item_to_selected_items(item)
            else:
                separation_of_tests.add_item_to_deselected_items(item)

        return separation_of_tests

    @staticmethod
    @adapter_logger
    def __check_external_id_in_resolved_autotests(external_id: str, resolved_autotests: dict) -> bool:
        return resolved_autotests is not None and external_id in resolved_autotests

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_protocol(self, item):
        self.__executable_test = utils.form_test(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item):
        if not self.__executable_test:
            return

        yield

        self._update_fixtures_external_ids(item)

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef):
        fixture_name = getattr(fixturedef.func, 'test_displayname', fixturedef.argname)

        container_uuid = self._cache.get(fixturedef)

        if not container_uuid:
            container_uuid = self._cache.push(fixturedef)
            container = FixturesContainer(uuid=container_uuid)
            self.fixture_manager.start_group(container_uuid, container)

        self.fixture_manager.update_group(container_uuid)

        before_fixture_uuid = uuid4()
        before_fixture = FixtureResult(title=fixture_name)

        self.fixture_manager.start_before_fixture(container_uuid, before_fixture_uuid, before_fixture)

        outcome = yield

        results_steps_data = self.__step_manager.get_steps_tree()

        self.fixture_manager.stop_before_fixture(before_fixture_uuid,
                                                 outcome=utils.get_outcome_status(outcome), steps=results_steps_data)

        finalizers = getattr(fixturedef, '_finalizers', [])
        for index, finalizer in enumerate(finalizers):
            finalizer_name = getattr(finalizer, "__name__", index)
            name = f'{fixture_name}::{finalizer_name}'
            finalizers[index] = FixtureContext(finalizer, parent_uuid=container_uuid, name=name)

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_call(self):
        yield

        if not self.__executable_test:
            return

        test_results_steps = self.__step_manager.get_steps_tree()
        self.__executable_test.step_results = test_results_steps

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_post_finalizer(self, fixturedef):
        if not self.__executable_test:
            return

        yield

        if hasattr(fixturedef, 'cached_result') and self._cache.get(fixturedef):
            group_uuid = self._cache.pop(fixturedef)
            self.fixture_manager.stop_group(group_uuid)

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if self.__executable_test:
            if report.when == 'setup':
                self.__executable_test.outcome = STATUS.get(report.outcome, None)
                if report.longreprtext:
                    self.__executable_test.message = report.longreprtext

            if report.when == 'call':
                self.__executable_test.outcome = STATUS.get(report.outcome, None)

            if report.failed or hasattr(report, 'wasxfail') \
                    and not report.passed or report.outcome == 'rerun':
                self.__executable_test.outcome = STATUS.get('failed', None)

                if report.longreprtext:
                    self.__executable_test.traces = report.longreprtext

            self.__executable_test.duration += report.duration * 1000

    @pytest.hookimpl
    def pytest_runtest_logfinish(self):
        if not self.__executable_test:
            return

        self.__test_result_ids[self.__executable_test.node_id] = self.__adapter_manager.write_test(
            utils.convert_executable_test_to_test_result_model(self.__executable_test))

    @pytest.hookimpl
    def pytest_sessionfinish(self, session):
        if not self.__test_result_ids:
            return

        self.__adapter_manager.load_setup_and_teardown_step_results(
            utils.fixtures_containers_to_test_results_with_all_fixture_step_results(
                self.fixture_manager.get_all_items(),
                self.__test_result_ids
            ))

    @adapter.hookimpl
    def add_link(self, link):
        if self.__executable_test:
            self.__executable_test.result_links.append(link)

    @adapter.hookimpl
    def add_message(self, test_message):
        if self.__executable_test:
            self.__executable_test.message = str(test_message)

    @adapter.hookimpl
    def add_attachments(self, attach_paths: list or tuple):
        if self.__executable_test:
            self.__executable_test.attachments += self.__adapter_manager.load_attachments(attach_paths)

    @adapter.hookimpl
    def create_attachment(self, body, name: str):
        if self.__executable_test:
            self.__executable_test.attachments += self.__adapter_manager.create_attachment(body, name)

    @adapter.hookimpl
    def start_fixture(self, parent_uuid, uuid, title):
        after_fixture = FixtureResult(title=title)
        self.fixture_manager.start_after_fixture(parent_uuid, uuid, after_fixture)

    @adapter.hookimpl
    def stop_fixture(self, uuid, exc_type, exc_val, exc_tb):
        results_steps_data = self.__step_manager.get_steps_tree()

        self.fixture_manager.stop_after_fixture(uuid,
                                                outcome=utils.get_status(exc_val),
                                                steps=results_steps_data,
                                                message=utils.get_message(exc_type, exc_val),
                                                stacktrace=utils.get_traceback(exc_tb))

    def _update_fixtures_external_ids(self, item):
        for fixturedef in self._test_fixtures(item):
            group_uuid = self._cache.get(fixturedef)
            if group_uuid:
                group = self.fixture_manager.get_item(group_uuid)
            else:
                group_uuid = self._cache.push(fixturedef)
                group = FixturesContainer(uuid=group_uuid)
                self.fixture_manager.start_group(group_uuid, group)
            if item.nodeid not in group.node_ids:
                self.fixture_manager.update_group(group_uuid, node_ids=item.nodeid)

    def _test_fixtures(self, item):
        fixturemanager = item.session._fixturemanager
        fixturedefs = []

        if hasattr(item, "_request") and hasattr(item._request, "fixturenames"):
            for name in item._request.fixturenames:
                if self.__pytest_info and version.parse(self.__pytest_info["version"]) >= version.parse("8.1.0"):
                    fixturedefs_pytest = fixturemanager.getfixturedefs(name, item)
                else:
                    fixturedefs_pytest = fixturemanager.getfixturedefs(name, item.nodeid)

                if fixturedefs_pytest:
                    fixturedefs.extend(fixturedefs_pytest)

        return fixturedefs
