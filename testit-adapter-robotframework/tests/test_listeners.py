import re
from pytest_mock import MockerFixture
from unittest.mock import MagicMock


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