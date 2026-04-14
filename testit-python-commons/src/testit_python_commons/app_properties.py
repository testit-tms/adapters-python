import configparser
import logging
import os
import warnings
import uuid
import re
from urllib.parse import urlparse
import tomli

from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.configurations.properties_names import PropertiesNames, ENV_TO_PROPERTY, OPTION_TO_PROPERTY


class AppProperties:
    __toml_extension = '.toml'
    __ini_extension = '.ini'
    __project_metadata_file = 'pyproject' + __toml_extension
    __tms_config_file = 'connection_config' + __ini_extension
    __properties_file = __tms_config_file
    __available_extensions = [__toml_extension, __ini_extension]

    ENV_CONFIG_FILE = 'TMS_CONFIG_FILE'
    __config_section_name = 'testit'
    __debug_section_name = 'debug'

    @staticmethod
    def load_properties(option=None):
        properties = AppProperties.load_file_properties(
            option.set_config_file if hasattr(option, 'set_config_file') else None)

        AppProperties.__check_token_property(properties)

        properties.update(AppProperties.load_env_properties())
        
        if option:
            properties.update(AppProperties.load_cli_properties(option))

        AppProperties.__check_properties(properties)

        return properties

    @classmethod
    def load_file_properties(cls, cli_file_path: str = None):
        if os.path.isfile(cls.__project_metadata_file):
            # https://peps.python.org/pep-0621/
            cls.__properties_file = cls.__project_metadata_file

        path = os.path.abspath('')
        root = path[:path.index(os.sep)]

        while not os.path.isfile(
                path + os.sep + cls.__tms_config_file) and path != root:
            path = path[:path.rindex(os.sep)]

        path = path + os.sep + cls.__tms_config_file

        if os.path.isfile(path):
            cls.__properties_file = cls.__tms_config_file

        if os.environ.get(cls.ENV_CONFIG_FILE):
            cls.__properties_file = cls.__tms_config_file
            path = os.environ.get(cls.ENV_CONFIG_FILE)

        if cli_file_path:
            cls.__properties_file = cls.__tms_config_file
            path = cli_file_path

        _, extension = os.path.splitext(cls.__properties_file)
        if extension not in cls.__available_extensions:
            raise FileNotFoundError(
                f'{cls.__properties_file} is not a valid file ({_, extension}). Available extensions: {cls.__available_extensions}'
            )

        if extension == cls.__toml_extension:
            return cls.__load_file_properties_from_toml()

        return cls.__load_file_properties_from_ini(path)

    @classmethod
    def load_cli_properties(cls, option):
        # Формируем словарь `cli_properties` с помощью генератора
        return {
            prop: getattr(option, option_attr)
            for option_attr, prop in OPTION_TO_PROPERTY.items()
            if hasattr(option, option_attr) and cls.__check_property_value(getattr(option, option_attr))
        }

    @classmethod
    def map_env_to_properties(cls) -> dict:
        env_properties = {}
        for env_key, property_name in ENV_TO_PROPERTY.items():
            if env_key in os.environ and cls.__check_property_value(os.environ.get(env_key)):
                env_properties[property_name] = os.environ.get(env_key)
        return env_properties

    @classmethod
    def load_env_properties(cls):
        env_properties = cls.map_env_to_properties()
        return env_properties

    @classmethod
    def __check_properties(cls, properties: dict):
        adapter_mode = properties.get(PropertiesNames.ADAPTER_MODE)

        if adapter_mode == AdapterMode.NEW_TEST_RUN:
            try:
                uuid.UUID(str(properties.get(PropertiesNames.TEST_RUN_ID)))
                logging.error('Adapter mode "2" is enabled. Config should not contains test run id!')
                raise SystemExit
            except ValueError:
                pass

        elif adapter_mode in (
                AdapterMode.RUN_ALL_TESTS,
                AdapterMode.USE_FILTER,
                None):
            try:
                uuid.UUID(str(properties.get(PropertiesNames.TEST_RUN_ID)))
            except ValueError:
                logging.error(f'Adapter mode "{adapter_mode if adapter_mode else "0"}" is enabled. '
                              f'The test run ID is needed, but it was not found!')
                raise SystemExit
        else:
            logging.error(f'Unknown adapter mode "{adapter_mode}"!')
            raise SystemExit

        try:
            uuid.UUID(str(properties.get(PropertiesNames.PROJECT_ID)))
        except ValueError:
            logging.error('Project ID was not found!')
            raise SystemExit

        try:
            url = urlparse(properties.get(PropertiesNames.URL))
            if not all([url.scheme, url.netloc]):
                raise AttributeError
        except AttributeError:
            logging.error('URL is invalid!')
            raise SystemExit

        if not cls.__check_property_value(properties.get(PropertiesNames.PRIVATE_TOKEN)):
            logging.error('Private token was not found!')
            raise SystemExit

        try:
            uuid.UUID(str(properties.get(PropertiesNames.CONFIGURATION_ID)))
        except ValueError:
            logging.error('Configuration ID was not found!')
            raise SystemExit

        if not cls.__check_property_value(properties.get(PropertiesNames.CERT_VALIDATION)):
            properties[PropertiesNames.CERT_VALIDATION] = 'true'

        if not cls.__check_property_value(properties.get(PropertiesNames.AUTOMATIC_CREATION_TEST_CASES)):
            properties[PropertiesNames.AUTOMATIC_CREATION_TEST_CASES] = 'false'

        if not cls.__check_property_value(properties.get(PropertiesNames.AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES)):
            properties[PropertiesNames.AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES] = 'false'

        if not cls.__check_property_value(properties.get(PropertiesNames.IMPORT_REALTIME)):
            # import realtime false by default
            properties[PropertiesNames.IMPORT_REALTIME] = 'false'

        if not cls.__check_property_value(properties.get(PropertiesNames.SYNC_STORAGE_PORT)):
            # import realtime false by default
            properties[PropertiesNames.SYNC_STORAGE_PORT] = '49152'

    @classmethod
    def __load_file_properties_from_toml(cls) -> dict:
        properties = {}

        with open(cls.__project_metadata_file, "rb+") as file:
            toml_dict = tomli.load(file)

            if not cls.__check_toml_section(toml_dict, cls.__config_section_name):
                logging.error(f'Config section in "{cls.__properties_file}" file was not found!')
                raise SystemExit

            config_section = toml_dict.get(cls.__config_section_name)

            for key, value in config_section.items():
                properties[key.lower()] = cls.__search_in_environ(str(value))

            if cls.__check_toml_section(toml_dict, cls.__debug_section_name):
                debug_section = toml_dict.get(cls.__debug_section_name)

                for key, value in debug_section.items():
                    if key == PropertiesNames.TMS_PROXY:
                        properties[PropertiesNames.TMS_PROXY] = cls.__search_in_environ(str(value))

                    if key == '__dev':
                        properties['logs'] = cls.__search_in_environ(str(value)).lower()

        return properties

    @classmethod
    def __load_file_properties_from_ini(cls, path: str) -> dict:
        properties = {}
        parser = configparser.RawConfigParser()

        parser.read(path, encoding="utf-8")

        if parser.has_section(cls.__config_section_name):
            for key, value in parser.items(cls.__config_section_name):
                properties[key] = cls.__search_in_environ(value)

        if parser.has_section('debug'):
            if parser.has_option('debug', PropertiesNames.TMS_PROXY):
                properties[PropertiesNames.TMS_PROXY] = cls.__search_in_environ(
                    parser.get('debug', PropertiesNames.TMS_PROXY))

            if parser.has_option('debug', '__dev'):
                properties['logs'] = cls.__search_in_environ(
                    parser.get('debug', '__dev')).lower()

        return properties

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

    @staticmethod
    def __check_toml_section(toml_dict: dict, section_name: str) -> bool:
        if section_name not in toml_dict.keys():
            return False
        if not type(toml_dict.get(section_name)) is dict:
            return False

        return True

    @staticmethod
    def __check_token_property(properties: dict):
        if PropertiesNames.PRIVATE_TOKEN in properties:
            warnings.warn(
                'The configuration file specifies a private token. It is not safe.'
                ' Use TMS_PRIVATE_TOKEN environment variable',
                category=Warning,
                stacklevel=2)
            warnings.simplefilter('default', Warning)
