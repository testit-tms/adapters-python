import pytest
from pytest_mock import MockerFixture

from testit_adapter_robotframework.listeners import AutotestAdapter


class TestAutotestAdapter:
    def test_parse_arguments(self, mocker: MockerFixture):
        # Arrange
        args = ["${var1}", "prefix_${var2}_suffix", "${var3_with_long_value}"]
        
        mock_builtin = mocker.patch('testit_adapter_robotframework.listeners.BuiltIn')
        
        mock_builtin.return_value.get_variable_value.side_effect = [
            "value1",
            "value2",
            "a" * 2500  # A value longer than 2000 characters
        ]

        # Act
        parameters = AutotestAdapter.parse_arguments(args)

        # Assert
        assert parameters == {
            "${var1}": "value1",
            "${var2}": "value2",
            "${var3_with_long_value}": "a" * 2000  # Should be truncated
        }
        
        # Verify that get_variable_value was called with the correct arguments
        expected_calls = [
            mocker.call("${var1}"),
            mocker.call("${var2}"), # Corrected from "${var2_suffix}" based on the parsing logic
            mocker.call("${var3_with_long_value}")
        ]
        mock_builtin.return_value.get_variable_value.assert_has_calls(expected_calls, any_order=True) 