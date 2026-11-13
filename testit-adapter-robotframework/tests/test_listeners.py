import re
import sys
import types
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

if "robot.api" not in sys.modules:
    robot_module = types.ModuleType("robot")
    robot_api_module = types.ModuleType("robot.api")
    robot_api_module.logger = MagicMock()
    robot_api_module.SuiteVisitor = MagicMock()
    robot_module.api = robot_api_module
    sys.modules["robot"] = robot_module
    sys.modules["robot.api"] = robot_api_module

if "robot.libraries" not in sys.modules:
    robot_libraries_module = types.ModuleType("robot.libraries")
    robot_builtin_module = types.ModuleType("robot.libraries.BuiltIn")
    robot_builtin_module.BuiltIn = MagicMock()
    robot_libraries_module.BuiltIn = robot_builtin_module
    sys.modules["robot.libraries"] = robot_libraries_module
    sys.modules["robot.libraries.BuiltIn"] = robot_builtin_module

try:
    import testit_python_commons.services  # noqa: F401
except ImportError:
    commons_module = types.ModuleType("testit_python_commons")
    commons_services_module = types.ModuleType("testit_python_commons.services")
    commons_services_module.TmsPluginManager = MagicMock()
    commons_module.services = commons_services_module
    sys.modules["testit_python_commons"] = commons_module
    sys.modules["testit_python_commons.services"] = commons_services_module

from testit_adapter_robotframework.listeners import (
    testit_adapter_robotframework as module_listener,  # noqa: N812
)
from testit_adapter_robotframework.models import Autotest


class TestAutotestAdapter:
    def test_parse_arguments(self, mocker: MockerFixture):
        mock_builtin_class = mocker.Mock()
        mock_builtin_instance = mocker.Mock()
        mock_builtin_class.return_value = mock_builtin_instance
        
        mock_builtin_instance.get_variable_value.side_effect = [
            "value1",
            "value2",
            "a" * 2500  # A value longer than 2000 characters
        ]
        
        def parse_arguments(args):
            parameters = {}
            for arg in args:
                variables = re.findall(r'\${[a-zA-Z-_\\ \d]*}', arg)
                for arg_var in variables:
                    value = str(mock_builtin_instance.get_variable_value(arg_var))
                    if len(value) > 2000:
                        value = value[:2000]
                    parameters[arg_var] = value
            return parameters if parameters else None
        
        # Arrange
        args = ["${var1}", "prefix_${var2}_suffix", "${var3_with_long_value}"]
        
        # Act
        parameters = parse_arguments(args)
        
        # Assert
        assert parameters == {
            "${var1}": "value1",
            "${var2}": "value2",
            "${var3_with_long_value}": "a" * 2000  # Should be truncated
        }
        
        expected_calls = [
            mocker.call("${var1}"),
            mocker.call("${var2}"),
            mocker.call("${var3_with_long_value}")
        ]
        mock_builtin_instance.get_variable_value.assert_has_calls(expected_calls, any_order=True)


class TestAutotestTagParsing:
    @staticmethod
    def _build_attrs(tags):
        return {
            "originalname": "HeaderName",
            "doc": "Doc",
            "template": None,
            "longname": "Suite.HeaderName",
            "tags": tags,
        }

    def test_display_name_does_not_override_title_when_title_absent(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs(["testit.displayName:DisplayName"]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title is None

    def test_title_has_priority_over_display_name(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs([
            "testit.displayName:DisplayName",
            "testit.title:CardTitle",
        ]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title == "CardTitle"

    def test_layer_tag_is_parsed(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs(["testit.layer:API"]))

        assert autotest.layer == "API"


class TestModuleListener:
    @staticmethod
    def _make_listener_with_adapter(mocker: MockerFixture, variables=None):
        variables = variables or {}

        def get_variable_value(name, default=None):
            return variables.get(name, default)

        built_in = mocker.Mock()
        built_in.get_variable_value.side_effect = get_variable_value
        mocker.patch("testit_adapter_robotframework.listeners.BuiltIn", return_value=built_in)

        adapter_manager = mocker.Mock()
        adapter_manager.get_test_run_id.return_value = "11111111-2222-3333-4444-555555555555"
        mocker.patch(
            "testit_adapter_robotframework.listeners.TmsPluginManager.get_adapter_manager",
            return_value=adapter_manager,
        )
        autotest_adapter = mocker.Mock()
        mocker.patch(
            "testit_adapter_robotframework.listeners.AutotestAdapter",
            return_value=autotest_adapter,
        )

        listener = module_listener()
        return listener, adapter_manager, autotest_adapter

    def test_start_suite_resolves_adapter_and_test_run_id(self, mocker: MockerFixture):
        listener, adapter_manager, autotest_adapter = self._make_listener_with_adapter(mocker)

        listener.start_suite("Suite", {"id": "s1"})

        assert listener.active_adapter is autotest_adapter
        adapter_manager.set_test_run_id.assert_called_once_with("11111111-2222-3333-4444-555555555555")

    def test_start_suite_passes_cli_variables_to_option(self, mocker: MockerFixture):
        variables = {"${tmsUrl}": "https://tms.example.com"}
        listener, _, _ = self._make_listener_with_adapter(mocker, variables)

        listener.start_suite("Suite", {})

        from testit_adapter_robotframework.listeners import Option, TmsPluginManager
        option = TmsPluginManager.get_adapter_manager.call_args[0][0]
        assert isinstance(option, Option)
        assert option.set_url == "https://tms.example.com"
        assert not hasattr(option, "set_private_token")
        assert not hasattr(option, "set_project_id")

    def test_nested_start_suite_resolves_adapter_only_once(self, mocker: MockerFixture):
        listener, adapter_manager, _ = self._make_listener_with_adapter(mocker)

        listener.start_suite("Root", {})
        listener.start_suite("Child", {})

        adapter_manager.get_test_run_id.assert_called_once()

    def test_start_suite_stays_idle_when_testit_variable_is_set(self, mocker: MockerFixture):
        variables = {"${testit}": "True"}
        listener, adapter_manager, _ = self._make_listener_with_adapter(mocker, variables)
        logger = mocker.patch("testit_adapter_robotframework.listeners.logger")

        listener.start_suite("Suite", {})
        listener.close()

        assert listener.active_adapter is None
        adapter_manager.set_test_run_id.assert_not_called()
        assert logger.warn.call_count == 1

    def test_events_are_delegated_to_active_adapter(self, mocker: MockerFixture):
        listener, _, autotest_adapter = self._make_listener_with_adapter(mocker)
        listener.start_suite("Suite", {})

        listener.start_test("Test", {"longname": "Suite.Test"})
        listener.start_keyword("Log", {"type": "KEYWORD"})
        listener.end_keyword("Log", {"type": "KEYWORD"})
        listener.end_test("Test", {"status": "PASS"})
        listener.close()

        autotest_adapter.start_test.assert_called_once_with("Test", {"longname": "Suite.Test"})
        autotest_adapter.start_keyword.assert_called_once_with("Log", {"type": "KEYWORD"})
        autotest_adapter.end_keyword.assert_called_once_with("Log", {"type": "KEYWORD"})
        autotest_adapter.end_test.assert_called_once_with("Test", {"status": "PASS"})
        autotest_adapter.close.assert_called_once()

    def test_events_without_resolved_adapter_do_nothing(self):
        listener = module_listener()

        listener.start_test("Test", {})
        listener.start_keyword("Log", {})
        listener.end_keyword("Log", {})
        listener.end_test("Test", {})
        listener.close()

    def test_set_test_run_id_without_pabot_uses_own_run(self, mocker: MockerFixture):
        adapter_manager = mocker.Mock()
        adapter_manager.get_test_run_id.return_value = "run-id"

        module_listener._set_test_run_id(adapter_manager, None)

        adapter_manager.set_test_run_id.assert_called_once_with("run-id")

    @staticmethod
    def _install_fake_pabot(mocker: MockerFixture, pabot_lib):
        pabot_module = types.ModuleType("pabot")
        pabot_module.PabotLib = pabot_lib
        mocker.patch.dict(sys.modules, {"pabot": pabot_module})

    def test_pabot_first_process_shares_created_test_run_id(self, mocker: MockerFixture):
        pabot_lib = MagicMock()
        adapter_manager = mocker.Mock()
        adapter_manager.get_test_run_id.return_value = "created-run-id"
        self._install_fake_pabot(mocker, pabot_lib)

        module_listener._set_test_run_id(adapter_manager, "0")

        pabot_lib.assert_called_once()
        pabot_lib.return_value.set_parallel_value_for_key.assert_called_once_with("test_run_id", "created-run-id")
        adapter_manager.set_test_run_id.assert_called_once_with("created-run-id")

    def test_pabot_other_process_uses_shared_test_run_id(self, mocker: MockerFixture):
        pabot_lib = MagicMock()
        pabot_lib.return_value.get_parallel_value_for_key.return_value = "shared-run-id"
        adapter_manager = mocker.Mock()
        self._install_fake_pabot(mocker, pabot_lib)

        module_listener._set_test_run_id(adapter_manager, "1")

        pabot_lib.return_value.get_parallel_value_for_key.assert_called_once_with("test_run_id")
        adapter_manager.set_test_run_id.assert_called_once_with("shared-run-id")
        adapter_manager.get_test_run_id.assert_not_called()

    def test_pabot_without_pabotlib_falls_back_to_own_test_run(self, mocker: MockerFixture):
        pabot_lib = MagicMock(side_effect=RuntimeError("connection refused"))
        adapter_manager = mocker.Mock()
        adapter_manager.get_test_run_id.return_value = "own-run-id"
        self._install_fake_pabot(mocker, pabot_lib)
        logger = mocker.patch("testit_adapter_robotframework.listeners.logger")

        module_listener._set_test_run_id(adapter_manager, "2")

        assert logger.warn.call_count == 1
        adapter_manager.set_test_run_id.assert_called_once_with("own-run-id")
