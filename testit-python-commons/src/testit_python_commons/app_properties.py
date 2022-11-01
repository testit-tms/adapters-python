import configparser
import os
import warnings
import logging

from testit_python_commons.services.utils import Utils
from testit_python_commons.models.adapter_mode import AdapterMode


class AppProperties:
    __properties_file = 'connection_config'
    __env_prefix = 'TMS'

    @staticmethod
    def load_properties(option=None):
        properties = AppProperties.load_file_properties(
            option.set_config_file if hasattr(option, 'set_config_file') else None)

        properties.update(AppProperties.load_env_properties())

        if option:
            properties.update(AppProperties.load_cli_properties(option))

        AppProperties.__check_properties(properties)

        return properties

    @classmethod
    def load_file_properties(cls, file_name: str = None):
        properties = {}

        path = os.path.abspath('')
        root = path[:path.index(os.sep)]

        if file_name:
            cls.__properties_file = file_name

        if os.environ.get(f'{cls.__env_prefix}_CONFIG_FILE'):
            cls.__properties_file = os.environ.get(f'{cls.__env_prefix}_CONFIG_FILE')

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

            if parser.has_section('debug') and parser.has_option('debug', 'tmsproxy'):
                properties['tmsproxy'] = Utils.search_in_environ(
                    parser.get('debug', 'tmsproxy'))

            if 'privatetoken' in properties:
                warnings.warn('The configuration file specifies a private token. It is not safe. Use TMS_PRIVATE_TOKEN environment variable',
                              category=Warning,
                              stacklevel=2)
                warnings.simplefilter('default', Warning)

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
            cli_properties['testrunname'] = option.set_test_run_name

        if hasattr(option, 'set_tms_proxy') and option.set_tms_proxy:
            cli_properties['tmsproxy'] = option.set_tms_proxy

        if hasattr(option, 'set_adapter_mode') and option.set_adapter_mode:
            cli_properties['adaptermode'] = option.set_adapter_mode

        return cli_properties

    @classmethod
    def load_env_properties(cls):
        env_properties = {}

        if f'{cls.__env_prefix}_URL' in os.environ.keys():
            env_properties['url'] = os.environ.get(f'{cls.__env_prefix}_URL')

        if f'{cls.__env_prefix}_PRIVATE_TOKEN' in os.environ.keys():
            env_properties['privatetoken'] = os.environ.get(f'{cls.__env_prefix}_PRIVATE_TOKEN')

        if f'{cls.__env_prefix}_PROJECT_ID' in os.environ.keys():
            env_properties['projectid'] = os.environ.get(f'{cls.__env_prefix}_PROJECT_ID')

        if f'{cls.__env_prefix}_CONFIGURATION_ID' in os.environ.keys():
            env_properties['configurationid'] = os.environ.get(f'{cls.__env_prefix}_CONFIGURATION_ID')

        if f'{cls.__env_prefix}_TEST_RUN_ID' in os.environ.keys():
            env_properties['testrunid'] = os.environ.get(f'{cls.__env_prefix}_TEST_RUN_ID')

        if f'{cls.__env_prefix}_TEST_RUN_NAME' in os.environ.keys():
            env_properties['testrunname'] = os.environ.get(f'{cls.__env_prefix}_TEST_RUN_NAME')

        if f'{cls.__env_prefix}_PROXY' in os.environ.keys():
            env_properties['tmsproxy'] = os.environ.get(f'{cls.__env_prefix}_PROXY')

        if f'{cls.__env_prefix}_ADAPTER_MODE' in os.environ.keys():
            env_properties['adaptermode'] = os.environ.get(f'{cls.__env_prefix}_ADAPTER_MODE')

        return env_properties

    @staticmethod
    def __check_properties(properties: dict):
        adapter_mode = properties.get('adaptermode')

        if adapter_mode == AdapterMode.NEW_TEST_RUN:
            if properties.get('projectid') is None:
                logging.error('Adapter mode "2" is enabled. The project ID is needed, but it was not found!')
                raise SystemExit
        elif adapter_mode in (
                AdapterMode.RUN_ALL_TESTS,
                AdapterMode.USE_FILTER,
                None):
            if properties.get('testrunid') is None:
                logging.error(f'Adapter mode "{adapter_mode if adapter_mode else "0"}" is enabled. The test run ID is needed, but it was not found!')
                raise SystemExit
        else:
            logging.error(f'Unknown adapter mode "{adapter_mode}"!')
            raise SystemExit

        if properties.get('url') is None:
            logging.error('URL was not found!')
            raise SystemExit

        if properties.get('privatetoken') is None:
            logging.error('Private token was not found!')
            raise SystemExit

        if properties.get('configurationid') is None:
            logging.error('Configuration ID was not found!')
            raise SystemExit
