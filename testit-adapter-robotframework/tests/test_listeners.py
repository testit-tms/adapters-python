import re
import sys
import types
from pytest_mock import MockerFixture
from unittest.mock import MagicMock

if "robot.api" not in sys.modules:
    robot_module = types.ModuleType("robot")
    robot_api_module = types.ModuleType("robot.api")
    robot_api_module.logger = MagicMock()
    robot_module.api = robot_api_module
    sys.modules["robot"] = robot_module
    sys.modules["robot.api"] = robot_api_module

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

    def test_title_falls_back_to_display_name_when_title_absent(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs(["testit.displayName:DisplayName"]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title == "DisplayName"

    def test_title_has_priority_over_display_name(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs([
            "testit.displayName:DisplayName",
            "testit.title:CardTitle",
        ]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title == "CardTitle"