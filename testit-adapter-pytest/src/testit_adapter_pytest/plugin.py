import re
import json
from urllib.parse import urlparse
import pytest

from testit_adapter_pytest.listener import TmsListener
from testit_python_commons.services import TmsPluginManager


def _adapter_mode_type(value):
    if value is None:
        raise ValueError("Adapter mode cannot be None! Valid modes: 0, 1, 2")
    valid_modes = ['0', '1', '2']
    if value not in valid_modes:
        raise ValueError(f"Unknown adapter mode '{value}'! Valid modes: {', '.join(valid_modes)}")
    return value


def _boolean_type(value):
    if value is None:
        raise ValueError("Boolean value cannot be None! Must be 'true' or 'false'")
    valid_values = ['true', 'false']
    if value.lower() not in valid_values:
        raise ValueError(f"Invalid value '{value}'! Must be 'true' or 'false'")
    return value.lower()


def _uuid_type(value):
    if value is None:
        raise ValueError("UUID cannot be None!")
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    if not uuid_pattern.match(value):
        raise ValueError(f"Invalid UUID format: '{value}'!")
    return value


def _url_type(value):
    if value is None:
        raise ValueError("URL cannot be None!")
    if not value.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid URL format: '{value}'!")
    url = urlparse(value)
    if not all([url.scheme, url.netloc]):
        raise ValueError(f"Invalid URL format: '{value}'!")
    return value


def _proxy_type(value):
    if value is None:
        raise ValueError("Proxy cannot be None!")
    try:
        proxy_dict = json.loads(value)
        if not isinstance(proxy_dict, dict):
            raise ValueError(f"Proxy must be a JSON object, got {type(proxy_dict).__name__}")
        
        valid_keys = {'http', 'https'}
        for key in proxy_dict.keys():
            if key not in valid_keys:
                raise ValueError(f"Invalid proxy key '{key}'! Must be 'http' or 'https'")
        
        for key, url in proxy_dict.items():
            if not isinstance(url, str):
                raise ValueError(f"Proxy URL for '{key}' must be string, got {type(url).__name__}")
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid {key} proxy URL: '{url}'! Must start with http:// or https://")
            parsed = urlparse(url)
            if not parsed.netloc:
                raise ValueError(f"Invalid {key} proxy URL: '{url}'! Missing hostname")
        
        return value
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format for proxy: '{value}'!")
    except ValueError as e:
        raise ValueError(str(e))

def pytest_addoption(parser):
    parser.getgroup('testit').addoption(
        '--testit',
        action='store_true',
        dest="tms_report",
        help='Pytest plugin for Test IT'
    )
    parser.getgroup('testit').addoption(
        '--tmsUrl',
        action="store",
        dest="set_url",
        type=_url_type,
        metavar="https://demo.testit.software",
        help='Set location of the TMS instance'
    )
    parser.getgroup('testit').addoption(
        '--tmsPrivateToken',
        action="store",
        dest="set_private_token",
        metavar="T2lKd2pLZGI4WHRhaVZUejNl",
        help='Set API secret key'
    )
    parser.getgroup('testit').addoption(
        '--tmsProjectId',
        action="store",
        dest="set_project_id",
        type=_uuid_type,
        metavar="15dbb164-c1aa-4cbf-830c-8c01ae14f4fb",
        help='Set project ID'
    )
    parser.getgroup('testit').addoption(
        '--tmsConfigurationId',
        action="store",
        dest="set_configuration_id",
        type=_uuid_type,
        metavar="d354bdac-75dc-4e3d-84d4-71186c0dddfc",
        help='Set configuration ID'
    )
    parser.getgroup('testit').addoption(
        '--tmsTestRunId',
        action="store",
        dest="set_test_run_id",
        type=_uuid_type,
        metavar="5236eb3f-7c05-46f9-a609-dc0278896464",
        help='Set test run ID (optional)'
    )
    parser.getgroup('debug').addoption(
        '--tmsProxy',
        action="store",
        dest="set_tms_proxy",
        type=_proxy_type,
        metavar='{"http":"http://localhost:8888","https":"http://localhost:8888"}',
        help='Set proxy for sending requests (optional)'
    )
    parser.getgroup('testit').addoption(
        '--tmsTestRunName',
        action="store",
        dest="set_test_run_name",
        metavar="Custom name of test run",
        help='Set custom name of test run (optional)'
    )
    parser.getgroup('testit').addoption(
        '--tmsAdapterMode',
        action="store",
        type=_adapter_mode_type,
        dest="set_adapter_mode",
        metavar="1",
        help="""
        Set adapter mode with test run (optional):
        0 - with filtering autotests by launch\'s suite in TMS (Default)
        1 - without filtering autotests by launch\'s suite in TMS
        2 - create new test run in TMS
        """
    )
    parser.getgroup('testit').addoption(
        '--tmsConfigFile',
        action="store",
        dest="set_config_file",
        metavar="tmsConfigFile",
        help='Set custom name of configuration file'
    )
    parser.getgroup('testit').addoption(
        '--tmsCertValidation',
        action="store",
        dest="set_cert_validation",
        type=_boolean_type,
        metavar="false",
        help='Set certificate validation (true/false)'
    )
    parser.getgroup('testit').addoption(
        '--tmsAutomaticCreationTestCases',
        action="store",
        dest="set_automatic_creation_test_cases",
        type=_boolean_type,
        metavar="false",
        help="""
        Set mode of automatic creation test cases (optional):
        true - create a test case linked to the created autotest (not to the updated autotest)
        false - not create a test case (Default)
        """
    )
    parser.getgroup('testit').addoption(
        '--tmsAutomaticUpdationLinksToTestCases',
        action="store",
        dest="set_automatic_updation_links_to_test_cases",
        type=_boolean_type,
        metavar="false",
        help="""
        Set mode of automatic updation links to test cases (optional):
        true - update links to test cases
        false - not update links to test cases (Default)
        """
    )
    parser.getgroup('testit').addoption(
        '--tmsImportRealtime',
        action="store",
        dest="set_import_realtime",
        type=_boolean_type,
        metavar="false",
        help="""
        Set mode of import type selection when launching autotests (optional):
        true - the adapter will create/update each autotest in real time (Default)
        false - the adapter will create/update multiple autotests
        """
    )


@pytest.mark.tryfirst
def pytest_cmdline_main(config):
    if config.option.tms_report:
        listener = TmsListener(
            TmsPluginManager.get_adapter_manager(config.option),
            TmsPluginManager.get_step_manager(),
            TmsPluginManager.get_fixture_manager())

        config.pluginmanager.register(listener)
        TmsPluginManager.get_plugin_manager().register(listener)