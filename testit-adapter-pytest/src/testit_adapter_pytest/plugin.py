import pytest

from testit_python_commons.services import TmsPluginManager
from testit_adapter_pytest.listener import TmsListener


def pytest_addoption(parser):
    parser.getgroup('testit').addoption(
        '--testit',
        action='store_true',
        dest="testit_report",
        help='Pytest plugin for Test IT'
    )
    parser.getgroup('testit').addoption(
        '--testit_url',
        action="store",
        dest="set_url",
        metavar="https://demo.testit.software",
        help='Set location of the TMS instance'
    )
    parser.getgroup('testit').addoption(
        '--privatetoken',
        action="store",
        dest="set_private_token",
        metavar="T2lKd2pLZGI4WHRhaVZUejNl",
        help='Set API secret key'
    )
    parser.getgroup('testit').addoption(
        '--projectid',
        action="store",
        dest="set_project_id",
        metavar="15dbb164-c1aa-4cbf-830c-8c01ae14f4fb",
        help='Set project ID'
    )
    parser.getgroup('testit').addoption(
        '--configurationid',
        action="store",
        dest="set_configuration_id",
        metavar="d354bdac-75dc-4e3d-84d4-71186c0dddfc",
        help='Set configuration ID'
    )
    parser.getgroup('testit').addoption(
        '--testrunid',
        action="store",
        dest="set_test_run_id",
        metavar="5236eb3f-7c05-46f9-a609-dc0278896464",
        help='Set test run ID (optional)'
    )
    parser.getgroup('debug').addoption(
        '--testit_proxy',
        action="store",
        dest="set_testit_proxy",
        metavar='{"http":"http://localhost:8888","https":"http://localhost:8888"}',
        help='Set proxy for sending requests (optional)'
    )
    parser.getgroup('testit').addoption(
        '--testrun_name',
        action="store",
        dest="set_test_run_name",
        metavar="Custom name of test run",
        help='Set custom name of test run (optional)'
    )
    parser.getgroup('testit').addoption(
        '--adapter_mode',
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


@pytest.mark.tryfirst
def pytest_cmdline_main(config):
    if config.option.testit_report:
        listener = TmsListener(
            TmsPluginManager.get_adapter_manager(config.option))

        config.pluginmanager.register(listener)
        TmsPluginManager.get_plugin_manager().register(listener)
