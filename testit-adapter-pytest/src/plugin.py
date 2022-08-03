import testit_adapter_pytest
import pytest
from testit_adapter_pytest.listener import TestITListener


def pytest_addoption(parser):
    parser.getgroup('testit').addoption(
        '--testit',
        action='store_true',
        dest="testit_report",
        help='Pytest plugin for Test IT'
    )
    parser.getgroup('testit').addoption(
        '--testrunid',
        action="store",
        dest="set_testrun",
        metavar="5236eb3f-7c05-46f9-a609-dc0278896464",
        help='Set Test-run ID'
    )
    parser.getgroup('testit').addoption(
        '--testit_url',
        action="store",
        dest="set_url",
        metavar="https://demo.testit.software",
        help='Set location of the Test IT instance'
    )
    parser.getgroup('testit').addoption(
        '--privatetoken',
        action="store",
        dest="set_privatetoken",
        metavar="T2lKd2pLZGI4WHRhaVZUejNl",
        help='Set API secret key'
    )
    parser.getgroup('testit').addoption(
        '--projectid',
        action="store",
        dest="set_projectid",
        metavar="15dbb164-c1aa-4cbf-830c-8c01ae14f4fb",
        help='Set Project ID'
    )
    parser.getgroup('testit').addoption(
        '--configurationid',
        action="store",
        dest="set_configurationid",
        metavar="d354bdac-75dc-4e3d-84d4-71186c0dddfc",
        help='Set Configuration ID'
    )
    parser.getgroup('debug').addoption(
        '--testit_proxy',
        action="store",
        dest="set_testit_proxy",
        metavar='{"http":"http://localhost:8888","https":"http://localhost:8888"}',
        help='Set proxy for sending requests'
    )
    parser.getgroup('testit').addoption(
        '--testrun_name',
        action="store",
        dest="set_testrun_name",
        metavar="Custom name of Test-run",
        help='Set custom name of Test-run'
    )


@pytest.mark.tryfirst
def pytest_cmdline_main(config):
    if config.option.testit_report:
        listener = TestITListener(config.option.set_testrun,
                                  config.option.set_url,
                                  config.option.set_privatetoken,
                                  config.option.set_projectid,
                                  config.option.set_configurationid,
                                  config.option.set_testit_proxy,
                                  config.option.set_testrun_name)
        config.pluginmanager.register(listener)
        testit_adapter_pytest.TestITPluginManager.get_plugin_manager().register(listener)
