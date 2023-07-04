import pytest

from testit_adapter_pytest.listener import TmsListener

from testit_python_commons.services import TmsPluginManager


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
        metavar="15dbb164-c1aa-4cbf-830c-8c01ae14f4fb",
        help='Set project ID'
    )
    parser.getgroup('testit').addoption(
        '--tmsConfigurationId',
        action="store",
        dest="set_configuration_id",
        metavar="d354bdac-75dc-4e3d-84d4-71186c0dddfc",
        help='Set configuration ID'
    )
    parser.getgroup('testit').addoption(
        '--tmsTestRunId',
        action="store",
        dest="set_test_run_id",
        metavar="5236eb3f-7c05-46f9-a609-dc0278896464",
        help='Set test run ID (optional)'
    )
    parser.getgroup('debug').addoption(
        '--tmsProxy',
        action="store",
        dest="set_tms_proxy",
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
        metavar="false",
        help='Set custom name of configuration file'
    )
    parser.getgroup('testit').addoption(
        '--tmsAutomaticCreationTestCases',
        action="store",
        dest="set_automatic_creation_test_cases",
        metavar="false",
        help="""
        Set mode of automatic creation test cases (optional):
        true - create a test case linked to the created autotest (not to the updated autotest)
        false - not create a test case (Default)
        """
    )


@pytest.mark.tryfirst
def pytest_cmdline_main(config):
    if config.option.tms_report:
        listener = TmsListener(
            TmsPluginManager.get_adapter_manager(config.option),
            TmsPluginManager.get_step_manager())

        config.pluginmanager.register(listener)
        TmsPluginManager.get_plugin_manager().register(listener)
