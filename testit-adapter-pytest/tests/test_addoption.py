import pytest
from unittest.mock import MagicMock, patch

from testit_adapter_pytest.plugin import (
    _adapter_mode_type,
    _boolean_type,
    _uuid_type,
    _url_type,
    _proxy_type,
    pytest_cmdline_main
)


class TestAdapterModeType:
    
    @pytest.mark.parametrize("valid_mode", ['0', '1', '2'])
    def test_valid_modes(self, valid_mode):
        assert _adapter_mode_type(valid_mode) == valid_mode
    
    @pytest.mark.parametrize("invalid_mode", ['3', '5', '01', '00', 'a', '', None, 'true', 'false'])
    def test_invalid_modes(self, invalid_mode):
        if invalid_mode is None:
            with pytest.raises(ValueError, match=r"Adapter mode cannot be None! Valid modes: 0, 1, 2"):
                _adapter_mode_type(invalid_mode)
        else:
            with pytest.raises(ValueError, match=r"Unknown adapter mode.*Valid modes: 0, 1, 2"):
                _adapter_mode_type(invalid_mode)


class TestBooleanType:
    
    @pytest.mark.parametrize("input_value,expected", [
        ('true', 'true'),
        ('false', 'false'),
        ('TRUE', 'true'),
        ('FALSE', 'false'),
        ('True', 'true'),
        ('False', 'false'),
    ])
    def test_valid_booleans(self, input_value, expected):
        assert _boolean_type(input_value) == expected
    
    @pytest.mark.parametrize("invalid_value", ['yes', 'no', '1', '0', 'on', 'off', 'TrueFalse', '', None])
    def test_invalid_booleans(self, invalid_value):
        if invalid_value is None:
            with pytest.raises(ValueError, match=r"Boolean value cannot be None! Must be 'true' or 'false'"):
                _boolean_type(invalid_value)
        else:
            with pytest.raises(ValueError, match=r"Invalid value.*Must be 'true' or 'false'"):
                _boolean_type(invalid_value)


class TestUUIDType:

    @pytest.mark.parametrize("valid_uuid", [
        '123e4567-e89b-12d3-a456-426614174000',
        '00000000-0000-0000-0000-000000000000',
        'ffffffff-ffff-ffff-ffff-ffffffffffff',
        '15dbb164-c1aa-4cbf-830c-8c01ae14f4fb',
        '5236eb3f-7c05-46f9-a609-dc0278896464',
    ])
    def test_valid_uuids(self, valid_uuid):
        assert _uuid_type(valid_uuid) == valid_uuid
    
    @pytest.mark.parametrize("invalid_uuid", [
        'not-a-uuid',
        '123e4567-e89b-12d3-a456',
        '123e4567-e89b-12d3-a456-42661417400Z',
        '123e4567e89b12d3a456426614174000', 
        '123e4567-e89b-12d3-a456-4266141740000',
        '',
        None,
        'gfffffff-ffff-ffff-ffff-ffffffffffff',
    ])
    def test_invalid_uuids(self, invalid_uuid):
        if invalid_uuid is None:
            with pytest.raises(ValueError, match=r"UUID cannot be None!"):
                _uuid_type(invalid_uuid)
        else:
            with pytest.raises(ValueError, match=r"Invalid UUID format:"):
                _uuid_type(invalid_uuid)


class TestUrlType:

    @pytest.mark.parametrize("valid_url", [
        'https://demo.testit.software',
        'http://localhost',
        'https://example.com',
        'http://127.0.0.1:8000',
        'https://sub.domain.example.com:8080/path?query=1',
    ])
    def test_valid_urls(self, valid_url):
        assert _url_type(valid_url) == valid_url
    
    @pytest.mark.parametrize("invalid_url", [
        'demo.testit.software', 
        'https://', 
        'ftp://example.com', 
        'file:///etc/passwd',
        'http:/example.com', 
        '://example.com', 
        'https://',
        '',
        None,
        'not a url',
    ])
    def test_invalid_urls(self, invalid_url):
        if invalid_url is None:
            with pytest.raises(ValueError, match=r"URL cannot be None!"):
                _url_type(invalid_url)
        else:
            with pytest.raises(ValueError, match=r"Invalid URL format:"):
                _url_type(invalid_url)


class TestProxyType:

    @pytest.mark.parametrize("valid_proxy", [
        '{"http":"http://localhost:8888"}',
        '{"https":"https://proxy.example.com:443"}',
        '{"http":"http://127.0.0.1:8080","https":"https://127.0.0.1:8443"}',
        '{"http":"http://user:pass@proxy:8888"}',
    ])
    def test_valid_proxies(self, valid_proxy):
        assert _proxy_type(valid_proxy) == valid_proxy
    
    @pytest.mark.parametrize("invalid_proxy,error_pattern", [
        ('not json', r"Invalid JSON format for proxy:"),
        ('{"http":123}', r"Proxy URL for 'http' must be string"),
        ('{"ftp":"http://proxy:8888"}', r"Invalid proxy key 'ftp'! Must be 'http' or 'https'"),
        ('[]', r"Proxy must be a JSON object, got list"),
        ('"string"', r"Proxy must be a JSON object, got str"),
        ('42', r"Proxy must be a JSON object, got int"),
        ('{"http":"not-a-url"}', r"Invalid http proxy URL: 'not-a-url'! Must start with http:// or https://"),
        ('{"https":"ftp://proxy:8888"}', r"Invalid https proxy URL: 'ftp://proxy:8888'! Must start with http:// or https://"),
        ('{"http":"http://","https":"https://"}', r"Invalid http proxy URL: 'http://'! Missing hostname"),
        (None, r"Proxy cannot be None!"),
    ])
    def test_invalid_proxies(self, invalid_proxy, error_pattern):
        with pytest.raises(ValueError, match=error_pattern):
            _proxy_type(invalid_proxy)

class TestPytestCmdlineMain:

    @patch('testit_adapter_pytest.plugin.TmsListener')
    @patch('testit_adapter_pytest.plugin.TmsPluginManager')
    def test_cmdline_main_with_tms_report(self, mock_plugin_manager, mock_listener_class):
        mock_config = MagicMock()
        mock_config.option.tms_report = True
        
        mock_adapter_manager = MagicMock()
        mock_step_manager = MagicMock()
        mock_fixture_manager = MagicMock()
        mock_plugin_manager.get_adapter_manager.return_value = mock_adapter_manager
        mock_plugin_manager.get_step_manager.return_value = mock_step_manager
        mock_plugin_manager.get_fixture_manager.return_value = mock_fixture_manager
        
        mock_listener = MagicMock()
        mock_listener_class.return_value = mock_listener
        pytest_cmdline_main(mock_config)

        mock_plugin_manager.get_adapter_manager.assert_called_once_with(mock_config.option)
        mock_plugin_manager.get_step_manager.assert_called_once()
        mock_plugin_manager.get_fixture_manager.assert_called_once()
        mock_listener_class.assert_called_once_with(
            mock_adapter_manager,
            mock_step_manager,
            mock_fixture_manager
        )
        mock_config.pluginmanager.register.assert_called_once_with(mock_listener)
        mock_plugin_manager.get_plugin_manager().register.assert_called_once_with(mock_listener)
    
    @patch('testit_adapter_pytest.plugin.TmsListener')
    @patch('testit_adapter_pytest.plugin.TmsPluginManager')
    def test_cmdline_main_without_tms_report(self, mock_plugin_manager, mock_listener_class):

        mock_config = MagicMock()
        mock_config.option.tms_report = False
        
        pytest_cmdline_main(mock_config)
        mock_plugin_manager.get_adapter_manager.assert_not_called()
        mock_listener_class.assert_not_called()
        mock_config.pluginmanager.register.assert_not_called()


class TestIntegrationWithPytest:
    def test_validator_in_pytest_raises_error(self, mocker):

        from _pytest.config import Config
        mock_config = Config.fromdictargs([], {})
        mock_config.option = mocker.MagicMock()
        mock_config.option.tms_report = True
        mock_config.option.set_adapter_mode = '5'
        mock_config.option.set_url = 'https://example.com'
        mock_config.option.set_private_token = 'token'
        mock_config.option.set_project_id = '123e4567-e89b-12d3-a456-426614174000'
        mock_config.option.set_configuration_id = '123e4567-e89b-12d3-a456-426614174000'
        with pytest.raises(ValueError, match=r"Unknown adapter mode '5'! Valid modes: 0, 1, 2"):
            _adapter_mode_type('5')
    
    def test_validator_accepts_valid_options(self):
        assert _adapter_mode_type('1') == '1'
        assert _url_type('https://example.com') == 'https://example.com'
        assert _uuid_type('123e4567-e89b-12d3-a456-426614174000') == '123e4567-e89b-12d3-a456-426614174000'
        assert _boolean_type('false') == 'false'
        assert _proxy_type('{"http":"http://localhost:8888"}') == '{"http":"http://localhost:8888"}'