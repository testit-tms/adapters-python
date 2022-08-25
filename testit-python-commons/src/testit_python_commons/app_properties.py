import configparser
import os

from testit_python_commons.services.utils import Utils


class AppProperties:
    __default_properties_file = 'connection_config'

    @staticmethod
    def load_properties(option=None):
        properties = AppProperties.load_file_properties()

        if option:
            properties.update(AppProperties.load_cli_properties(option))

        properties.update(AppProperties.load_env_properties())

        AppProperties.__check_properties(properties)

        return properties

    @classmethod
    def load_file_properties(cls, path: str = None):
        properties = {}

        if path is None:
            path = os.path.abspath('')
            root = path[:path.index(os.sep)]

            while not os.path.isfile(
                    path + os.sep + f'{cls.__default_properties_file}.ini') and path != root:
                path = path[:path.rindex(os.sep)]

            path = path + os.sep + f'{cls.__default_properties_file}.ini'

        if os.path.isfile(path):
            parser = configparser.RawConfigParser()

            parser.read(path)

            if parser.has_section('testit'):
                for key, value in parser.items('testit'):
                    properties[key] = Utils.search_in_environ(value)

            if parser.has_section('debug') and parser.has_option('debug', 'testit_proxy'):
                properties['testit_proxy'] = Utils.search_in_environ(
                    parser.get('debug', 'testit_proxy'))

        return properties

    @staticmethod
    def load_cli_properties(option):
        cli_properties = {}

        if hasattr(option, 'set_url') and option.set_url:
            cli_properties['url'] = option.set_url

        if hasattr(option, 'set_privatetoken') and option.set_privatetoken:
            cli_properties['privatetoken'] = option.set_privatetoken

        if hasattr(option, 'set_projectid') and option.set_projectid:
            cli_properties['projectid'] = option.set_projectid

        if hasattr(option, 'set_configurationid') and option.set_configurationid:
            cli_properties['configurationid'] = option.set_configurationid

        if hasattr(option, 'set_testrun') and option.set_testrun:
            cli_properties['testrunid'] = option.set_testrun

        if hasattr(option, 'set_testrun_name') and option.set_testrun_name:
            cli_properties['testrun_name'] = option.set_testrun_name

        if hasattr(option, 'set_testit_proxy') and option.set_testit_proxy:
            cli_properties['testit_proxy'] = option.set_testit_proxy

        return cli_properties

    @staticmethod
    def load_env_properties():
        env_properties = {}

        if 'TESTIT_URL' in os.environ.keys():
            env_properties['url'] = os.environ.get('TESTIT_URL')

        if 'TESTIT_PRIVATE_TOKEN' in os.environ.keys():
            env_properties['privatetoken'] = os.environ.get('TESTIT_PRIVATE_TOKEN')

        if 'TESTIT_PROJECT_ID' in os.environ.keys():
            env_properties['projectid'] = os.environ.get('TESTIT_PROJECT_ID')

        if 'TESTIT_CONFIGURATION_ID' in os.environ.keys():
            env_properties['configurationid'] = os.environ.get('TESTIT_CONFIGURATION_ID')

        if 'TESTIT_TEST_RUN_ID' in os.environ.keys():
            env_properties['testrunid'] = os.environ.get('TESTIT_TEST_RUN_ID')

        if 'TESTIT_TEST_RUN_NAME' in os.environ.keys():
            env_properties['testrun_name'] = os.environ.get('TESTIT_TEST_RUN_NAME')

        if 'TESTIT_PROXY' in os.environ.keys():
            env_properties['testit_proxy'] = os.environ.get('TESTIT_PROXY')

        return env_properties

    @staticmethod
    def __check_properties(properties: dict):
        if properties.get('projectid') is None and\
                properties.get('testrunid') is None:
            print('Project ID and test run ID were not found!')
            raise SystemExit

        if properties.get('url') is None:
            print('URL was not found!')
            raise SystemExit

        if properties.get('privatetoken') is None:
            print('Private token was not found!')
            raise SystemExit

        if properties.get('configurationid') is None:
            print('Configuration ID was not found!')
            raise SystemExit
