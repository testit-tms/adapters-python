import pytest
import warnings
import inspect
import uuid
import random
import string

from testit_python_commons.services.utils import Utils
from testit_python_commons.models.link import Link

class TestUtils:
    #uuid_check
    def test_uuid_check_valid_uuid(self):
        valid_uuid = str(uuid.uuid4())
        result = Utils.uuid_check(valid_uuid)
        assert result == valid_uuid

    def test_uuid_check_invalid_uuid_raises_system_exit(self):
        invalid_uuid = f"invalid-{random.randint(1000, 9999)}-format"
        with pytest.raises(SystemExit):
            Utils.uuid_check(invalid_uuid)

    def test_uuid_check_empty_string_raises_system_exit(self):
        with pytest.raises(SystemExit):
            Utils.uuid_check("")

    def test_uuid_check_wrong_length_raises_system_exit(self):
        valid_uuid = str(uuid.uuid4())
        wrong_length_uuid = valid_uuid[:-1]
        with pytest.raises(SystemExit):
            Utils.uuid_check(wrong_length_uuid)

    #url_check
    @pytest.mark.parametrize("protocol", ["http", "https", "ftp"])
    def test_url_check_valid_url(self, protocol):
        domain = ''.join(random.choices(string.ascii_lowercase, k=8))
        valid_url = f"{protocol}://{domain}.com"
        result = Utils.url_check(valid_url)
        assert result == valid_url

    def test_url_check_invalid_url_raises_system_exit(self):
        invalid_url = f"not-a-valid-url-{random.randint(100, 999)}"
        with pytest.raises(SystemExit):
            Utils.url_check(invalid_url)

    def test_url_check_empty_string_raises_system_exit(self):
        with pytest.raises(SystemExit):
            Utils.url_check("")

    #deprecated
    def test_deprecated_decorator_shows_warning(self):
        message = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        @Utils.deprecated(message)
        def test_function():
            return f"test_result_{random.randint(1, 100)}"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = test_function()

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "test_function" in str(w[0].message)
            assert message in str(w[0].message)
            assert "test_result_" in result

    #get_function_parameters
    def test_get_function_parameters_with_args_only(self):
        def sample_function(arg1, arg2):
            pass

        args_value = {
            "arg1": f"value_{random.randint(1, 50)}",
            "arg2": f"data_{random.randint(51, 100)}"
        }

        result = Utils.get_function_parameters(sample_function, args_value["arg1"], args_value["arg2"])
        assert result == args_value

    def test_get_function_parameters_with_kwargs_only(self):
        def sample_function(arg1, arg2):
            pass

        args_value = {
            "arg1": f"keyword_{random.randint(1, 25)}",
            "arg2": f"parameter_{random.randint(26, 50)}"
        }

        result = Utils.get_function_parameters(sample_function, arg1=args_value["arg1"], arg2=args_value["arg2"])
        assert result == args_value

    def test_get_function_parameters_empty_function(self):
        def sample_function():
            pass

        result = Utils.get_function_parameters(sample_function)
        assert result == {}

    #exclude_self_parameter
    def test_exclude_self_parameter_removes_self(self):
        parameters = {
            "self": f"instance_{random.randint(1, 100)}",
            "arg1": f"arg_value_{random.randint(101, 200)}",
            "arg2": f"param_value_{random.randint(201, 300)}"
        }

        result = Utils.exclude_self_parameter(parameters)
        assert result == {k: parameters[k] for k in ["arg1", "arg2"]}

    def test_exclude_self_parameter_no_self_present(self):
        parameters = {
            "arg1": f"random_value_{random.randint(1, 50)}",
            "arg2": f"another_value_{random.randint(51, 100)}"
        }

        result = Utils.exclude_self_parameter(parameters)
        assert result == parameters

    def test_exclude_self_parameter_empty_dict(self):
        result = Utils.exclude_self_parameter({})
        assert result == {}

    #collect_parameters_in_string_attribute
    def test_collect_parameters_in_string_attribute_with_placeholders(self):
        attribute = "Tests {value1} - {value2}"
        parameters = {
            "value1": ''.join(random.choices(string.ascii_letters, k=8)),
            "value2": str(random.randint(18, 80))
        }

        result = Utils.collect_parameters_in_string_attribute(attribute, parameters)
        assert result == f"Tests {parameters['value1']} - {parameters['value2']}"

    def test_collect_parameters_in_string_attribute_no_placeholders(self):
        greeting = f"Tests {random.randint(1, 1000)}"
        parameters = {
            "value": ''.join(random.choices(string.ascii_letters, k=6))
        }

        result = Utils.collect_parameters_in_string_attribute(greeting, parameters)
        assert result == greeting

    def test_collect_parameters_in_string_attribute_missing_parameter(self):
        attribute = "Tests {value} - {value_missing}"
        parameters = {
            "value": ''.join(random.choices(string.ascii_letters, k=7))
        }

        result = Utils.collect_parameters_in_string_attribute(attribute, parameters)
        assert result == f"Tests {parameters['value']} - {{value_missing}}"

    def test_collect_parameters_in_string_attribute_empty_string(self):
        parameters = {
            "value": ''.join(random.choices(string.ascii_letters, k=5))
        }

        result = Utils.collect_parameters_in_string_attribute("", parameters)
        assert result == ""

    #convert_link_dict_to_link_model
    def test_convert_link_dict_to_link_model_minimal(self, mocker):
        mock_link = mocker.Mock(spec=Link)
        mocker.patch('testit_python_commons.services.utils.Link', return_value=mock_link)

        domain = ''.join(random.choices(string.ascii_lowercase, k=12))
        link_dict = {"url": f"https://{domain}.example.com"}
        result = Utils.convert_link_dict_to_link_model(link_dict)

        mock_link.set_url.assert_called_once_with(link_dict["url"])
        assert result == mock_link

    def test_convert_link_dict_to_link_model_full(self, mocker):
        mock_link = mocker.Mock(spec=Link)
        mocker.patch('testit_python_commons.services.utils.Link', return_value=mock_link)

        domain = ''.join(random.choices(string.ascii_lowercase, k=10))
        link_dict = {
            "url": f"https://{domain}.test.org",
            "title": ''.join(random.choices(string.ascii_letters, k=8)),
            "type": random.choice(["external", "internal", "documentation", "api"]),
            "description": ''.join(random.choices(string.ascii_lowercase, k=6))
        }
        result = Utils.convert_link_dict_to_link_model(link_dict)

        mock_link.set_url.assert_called_once_with(link_dict["url"])
        mock_link.set_title.assert_called_once_with(link_dict["title"])
        mock_link.set_link_type.assert_called_once_with(link_dict["type"])
        mock_link.set_description.assert_called_once_with(link_dict["description"])
        assert result == mock_link

    #convert_body_of_attachment
    def test_convert_body_of_attachment_bytes_input(self):
        content = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        body = content.encode('utf-8')
        result = Utils.convert_body_of_attachment(body)

        assert result == body
        assert isinstance(result, bytes)

    def test_convert_body_of_attachment_string_input(self):
        body = f"test content {random.randint(1000, 9999)}"
        result = Utils.convert_body_of_attachment(body)
        expected = body.encode('utf-8')

        assert result == expected
        assert isinstance(result, bytes)

    def test_convert_body_of_attachment_integer_input(self):
        body = random.randint(100, 999999)
        result = Utils.convert_body_of_attachment(body)
        expected = str(body).encode('utf-8')

        assert result == expected
        assert isinstance(result, bytes)

    #convert_value_str_to_bool
    def test_convert_value_str_to_bool_true_string(self):
        result = Utils.convert_value_str_to_bool("true")
        assert result is True

    def test_convert_value_str_to_bool_false_string(self):
        result = Utils.convert_value_str_to_bool("false")
        assert result is False

    def test_convert_value_str_to_bool_other_string(self):
        random_string = ''.join(random.choices(string.ascii_letters, k=5))
        result = Utils.convert_value_str_to_bool(random_string)
        assert result is False

    def test_convert_value_str_to_bool_empty_string(self):
        result = Utils.convert_value_str_to_bool("")
        assert result is False

    def test_convert_value_str_to_bool_none_value(self):
        result = Utils.convert_value_str_to_bool(None)
        assert result is False