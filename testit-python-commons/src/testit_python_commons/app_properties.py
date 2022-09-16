import configparser
import os
import warnings

from testit_python_commons.services.utils import Utils
from testit_python_commons.models.adapter_mode import AdapterMode


class AppProperties:
    __properties_file = 'connection_config'

    @staticmethod
    def load_properties(option=None):
        properties = AppProperties.load_file_properties(
            option.set_config_file if hasattr(option, 'set_config_file') else None)

        if option:
            properties.update(AppProperties.load_cli_properties(option))

        properties.update(AppProperties.load_env_properties())

        AppProperties.__check_properties(properties)

        return properties

    @classmethod
    def load_file_properties(cls, file_name: str = None):
        properties = {}

        path = os.path.abspath('')
        root = path[:path.index(os.sep)]

        if file_name:
            cls.__properties_file = file_name

        if os.environ.get('TMS_CONFIG_FILE'):
            cls.__properties_file = os.environ.get('TMS_CONFIG_FILE')

        while not os.path.isfile(
                path + os.sep + f'{cls.__properties_file}.ini') and path != root:
            path = path[:path.rindex(os.sep)]

        path = path + os.sep + f'{cls.__properties_file}.ini'

        if os.path.isfile(path):
            parser = configparser.RawConfigParser()

            parser.read(path)

            if parser.has_section('testit'):
                for key, value in parser.items('testit'):
                    properties[key] = Utils.search_in_environ(value)

            if 'privatetoken' in properties:
                warnings.warn('The configuration file specifies a private token. It is not safe. Use TMS_PRIVATE_TOKEN environment variable',
                              category=Warning,
                              stacklevel=2)
                warnings.simplefilter('default', Warning)

            if parser.has_section('debug') and parser.has_option('debug', 'testit_proxy'):
                properties['testit_proxy'] = Utils.search_in_environ(
                    parser.get('debug', 'testit_proxy'))

        return properties

    @staticmethod
    def load_cli_properties(option):
        cli_properties = {}

        if hasattr(option, 'set_url') and option.set_url:
            cli_properties['url'] = option.set_url

        if hasattr(option, 'set_private_token') and option.set_private_token:
            cli_properties['privatetoken'] = option.set_private_token

        if hasattr(option, 'set_project_id') and option.set_project_id:
            cli_properties['projectid'] = option.set_project_id

        if hasattr(option, 'set_configuration_id') and option.set_configuration_id:
            cli_properties['configurationid'] = option.set_configuration_id

        if hasattr(option, 'set_test_run_id') and option.set_test_run_id:
            cli_properties['testrunid'] = option.set_test_run_id

        if hasattr(option, 'set_test_run_name') and option.set_test_run_name:
            cli_properties['testrun_name'] = option.set_test_run_name

        if hasattr(option, 'set_testit_proxy') and option.set_testit_proxy:
            cli_properties['testit_proxy'] = option.set_testit_proxy

        if hasattr(option, 'set_adapter_mode') and option.set_adapter_mode:
            cli_properties['adaptermode'] = option.set_testit_mode

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

        if 'ADAPTER_MODE' in os.environ.keys():
            env_properties['adaptermode'] = os.environ.get('ADAPTER_MODE')

        return env_properties

    @staticmethod
    def __check_properties(properties: dict):
        adapter_mode = properties.get('adaptermode')

        if adapter_mode == AdapterMode.NEW_TEST_RUN:
            if properties.get('projectid') is None:
                print('Adapter mode "2" is enabled. The project ID is needed, but it was not found!')
                raise SystemExit
        elif adapter_mode in (
                AdapterMode.RUN_ALL_TESTS,
                AdapterMode.USE_FILTER,
                None):
            if properties.get('testrunid') is None:
                print(f'Adapter mode "{adapter_mode if adapter_mode else "0"}" is enabled. The test run ID is needed, but it was not found!')
                raise SystemExit
        else:
            print(f'Unknown adapter mode "{adapter_mode}"!')
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
