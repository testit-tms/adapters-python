import configparser
import logging
import os
import re
import warnings
import uuid
from urllib.parse import urlparse

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

            parser.read(path, encoding="utf-8")

            if parser.has_section('testit'):
                for key, value in parser.items('testit'):
                    properties[key] = cls.__search_in_environ(value)

            if parser.has_section('debug'):
                if parser.has_option('debug', 'tmsproxy'):
                    properties['tmsproxy'] = cls.__search_in_environ(
                        parser.get('debug', 'tmsproxy'))

                if parser.has_option('debug', '__dev'):
                    properties['logs'] = cls.__search_in_environ(
                        parser.get('debug', '__dev')).lower()

            if 'privatetoken' in properties:
                warnings.warn(
                    'The configuration file specifies a private token. It is not safe.'
                    ' Use TMS_PRIVATE_TOKEN environment variable',
                    category=Warning,
                    stacklevel=2)
                warnings.simplefilter('default', Warning)

        return properties

    @classmethod
    def load_cli_properties(cls, option):
        cli_properties = {}

        if hasattr(option, 'set_url') and cls.__check_property_value(option.set_url):
            cli_properties['url'] = option.set_url

        if hasattr(option, 'set_private_token') and cls.__check_property_value(option.set_private_token):
            cli_properties['privatetoken'] = option.set_private_token

        if hasattr(option, 'set_project_id') and cls.__check_property_value(option.set_project_id):
            cli_properties['projectid'] = option.set_project_id

        if hasattr(option, 'set_configuration_id') and cls.__check_property_value(option.set_configuration_id):
            cli_properties['configurationid'] = option.set_configuration_id

        if hasattr(option, 'set_test_run_id') and cls.__check_property_value(option.set_test_run_id):
            cli_properties['testrunid'] = option.set_test_run_id

        if hasattr(option, 'set_test_run_name') and cls.__check_property_value(option.set_test_run_name):
            cli_properties['testrunname'] = option.set_test_run_name

        if hasattr(option, 'set_tms_proxy') and cls.__check_property_value(option.set_tms_proxy):
            cli_properties['tmsproxy'] = option.set_tms_proxy

        if hasattr(option, 'set_adapter_mode') and cls.__check_property_value(option.set_adapter_mode):
            cli_properties['adaptermode'] = option.set_adapter_mode

        if hasattr(option, 'set_cert_validation') and cls.__check_property_value(option.set_cert_validation):
            cli_properties['certvalidation'] = option.set_cert_validation

        if hasattr(option, 'set_automatic_creation_test_cases') and cls.__check_property_value(
                option.set_automatic_creation_test_cases):
            cli_properties['automaticcreationtestcases'] = option.set_automatic_creation_test_cases

        return cli_properties

    @classmethod
    def load_env_properties(cls):
        env_properties = {}

        if f'{cls.__env_prefix}_URL' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_URL')):
            env_properties['url'] = os.environ.get(f'{cls.__env_prefix}_URL')

        if f'{cls.__env_prefix}_PRIVATE_TOKEN' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_PRIVATE_TOKEN')):
            env_properties['privatetoken'] = os.environ.get(f'{cls.__env_prefix}_PRIVATE_TOKEN')

        if f'{cls.__env_prefix}_PROJECT_ID' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_PROJECT_ID')):
            env_properties['projectid'] = os.environ.get(f'{cls.__env_prefix}_PROJECT_ID')

        if f'{cls.__env_prefix}_CONFIGURATION_ID' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_CONFIGURATION_ID')):
            env_properties['configurationid'] = os.environ.get(f'{cls.__env_prefix}_CONFIGURATION_ID')

        if f'{cls.__env_prefix}_TEST_RUN_ID' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_TEST_RUN_ID')):
            env_properties['testrunid'] = os.environ.get(f'{cls.__env_prefix}_TEST_RUN_ID')

        if f'{cls.__env_prefix}_TEST_RUN_NAME' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_TEST_RUN_NAME')):
            env_properties['testrunname'] = os.environ.get(f'{cls.__env_prefix}_TEST_RUN_NAME')

        if f'{cls.__env_prefix}_PROXY' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_PROXY')):
            env_properties['tmsproxy'] = os.environ.get(f'{cls.__env_prefix}_PROXY')

        if f'{cls.__env_prefix}_ADAPTER_MODE' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_ADAPTER_MODE')):
            env_properties['adaptermode'] = os.environ.get(f'{cls.__env_prefix}_ADAPTER_MODE')

        if f'{cls.__env_prefix}_CERT_VALIDATION' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_CERT_VALIDATION')):
            env_properties['certvalidation'] = os.environ.get(f'{cls.__env_prefix}_CERT_VALIDATION')

        if f'{cls.__env_prefix}_AUTOMATIC_CREATION_TEST_CASES' in os.environ.keys() and cls.__check_property_value(
                os.environ.get(f'{cls.__env_prefix}_AUTOMATIC_CREATION_TEST_CASES')):
            env_properties['automaticcreationtestcases'] = os.environ.get(
                f'{cls.__env_prefix}_AUTOMATIC_CREATION_TEST_CASES')

        return env_properties

    @classmethod
    def __check_properties(cls, properties: dict):
        adapter_mode = properties.get('adaptermode')

        if adapter_mode == AdapterMode.NEW_TEST_RUN:
            try:
                uuid.UUID(str(properties.get('testrunid')))
                logging.error('Adapter mode "2" is enabled. Config should not contains test run id!')
                raise SystemExit
            except ValueError:
                pass

        elif adapter_mode in (
                AdapterMode.RUN_ALL_TESTS,
                AdapterMode.USE_FILTER,
                None):
            try:
                uuid.UUID(str(properties.get('testrunid')))
            except ValueError:
                logging.error(f'Adapter mode "{adapter_mode if adapter_mode else "0"}" is enabled. '
                              f'The test run ID is needed, but it was not found!')
                raise SystemExit
        else:
            logging.error(f'Unknown adapter mode "{adapter_mode}"!')
            raise SystemExit

        try:
            uuid.UUID(str(properties.get('projectid')))
        except ValueError:
            logging.error('Project ID was not found!')
            raise SystemExit

        try:
            url = urlparse(properties.get('url'))
            if not all([url.scheme, url.netloc]):
                raise AttributeError
        except AttributeError:
            logging.error('URL is invalid!')
            raise SystemExit

        if not cls.__check_property_value(properties.get('privatetoken')):
            logging.error('Private token was not found!')
            raise SystemExit

        try:
            uuid.UUID(str(properties.get('configurationid')))
        except ValueError:
            logging.error('Configuration ID was not found!')
            raise SystemExit

        if not cls.__check_property_value(properties.get('certvalidation')):
            properties['certvalidation'] = 'true'

        if not cls.__check_property_value(properties.get('automaticcreationtestcases')):
            properties['automaticcreationtestcases'] = 'false'

    @staticmethod
    def __search_in_environ(var_name: str):
        if re.fullmatch(r'{[a-zA-Z_]\w*}', var_name) and var_name[1:-1] in os.environ:
            return os.environ[var_name[1:-1]]

        return var_name

    @staticmethod
    def __check_property_value(value: str):
        if value is not None and value != "":
            return True

        return False
