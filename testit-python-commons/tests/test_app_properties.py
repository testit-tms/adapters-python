import random
import string
import os
import uuid
import pytest

from testit_python_commons.app_properties import AppProperties

class TestAppProperties:
    __properties_file = AppProperties._AppProperties__properties_file
    __env_prefix = AppProperties._AppProperties__env_prefix

    @pytest.fixture
    def create_config_file(self, tmp_path):
        def _create_config_file(filename, content):
            file_path = tmp_path / filename
            file_path.write_text(content, encoding="utf-8")
            return file_path

        return _create_config_file

    @pytest.fixture
    def properties(self):
        return {
            'url': "https://www.example.com",
            'privatetoken': ''.join(random.choices(string.ascii_letters + string.digits, k=24)),
            'projectid': str(uuid.uuid4()),
            'configurationid': str(uuid.uuid4()),
            'testrunid': str(uuid.uuid4()),
            'testrunname': ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            'adaptermode': "2",
            'tmsproxy': ''.join(random.choices(string.ascii_letters + string.digits, k=3)),
            'certvalidation': "false",
            'automaticcreationtestcases': "true",
            'automaticupdationlinkstotestcases': "true",
            'importrealtime': "false"
        }

    def test_load_file_properties_ini_file(self, create_config_file, tmp_path, mocker):
        mocker.patch.object(os.path, 'abspath', return_value=str(tmp_path))
        mocker.patch.dict(os.environ, clear=True)

        properties_testit = {
            'url': 'https://www.example.com',
            'privatetoken': ''.join(random.choices(string.ascii_letters + string.digits, k=24)),
            'projectid': str(uuid.uuid4()),
            'configurationid': str(uuid.uuid4()),
            'testrunid': str(uuid.uuid4()),
            'testrunname': ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
            'adaptermode': "2"
        }

        properties_debug = {
            'tmsproxy': ''.join(random.choices(string.ascii_letters + string.digits, k=3)),
            'logs': 'true'
        }

        config_content = "[testit]\n"
        for property in properties_testit:
            config_content += "%s=%s\n" % (property, properties_testit[property])
        config_content += "[debug]\n"
        config_content += "tmsProxy=%s\n" % properties_debug['tmsproxy']
        config_content += "__dev=%s\n" % properties_debug['logs']

        create_config_file(self.__properties_file, config_content)
        mocker.patch('os.path.isfile', lambda p: p == str(tmp_path / self.__properties_file))
        assert AppProperties.load_file_properties() == {**properties_testit, **properties_debug}

    def test_load_env_properties_all_set(self, properties, mocker):
        env_vars = {
            f"{self.__env_prefix}_URL": properties["url"],
            f"{self.__env_prefix}_PRIVATE_TOKEN": properties["privatetoken"],
            f"{self.__env_prefix}_PROJECT_ID": properties["projectid"],
            f"{self.__env_prefix}_CONFIGURATION_ID": properties["configurationid"],
            f"{self.__env_prefix}_TEST_RUN_ID": properties["testrunid"],
            f"{self.__env_prefix}_TEST_RUN_NAME": properties["testrunname"],
            f"{self.__env_prefix}_ADAPTER_MODE": properties["adaptermode"],
            f"{self.__env_prefix}_PROXY": properties["tmsproxy"],
            f"{self.__env_prefix}_CERT_VALIDATION": properties["certvalidation"],
            f"{self.__env_prefix}_AUTOMATIC_CREATION_TEST_CASES": properties["automaticcreationtestcases"],
            f"{self.__env_prefix}_AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES": properties["automaticupdationlinkstotestcases"],
            f"{self.__env_prefix}_IMPORT_REALTIME": properties["importrealtime"],
        }
        mocker.patch.dict(os.environ, env_vars, clear=True)

        assert AppProperties.load_env_properties() == properties

    def test_load_cli_properties_all_set(self, properties, mocker):
        mock_options = mocker.MagicMock()
        mock_options.set_url = properties["url"]
        mock_options.set_private_token = properties["privatetoken"]
        mock_options.set_project_id = properties["projectid"]
        mock_options.set_configuration_id = properties["configurationid"]
        mock_options.set_test_run_id = properties["testrunid"]
        mock_options.set_test_run_name = properties["testrunname"]
        mock_options.set_adapter_mode = properties["adaptermode"]
        mock_options.set_tms_proxy = properties["tmsproxy"]
        mock_options.set_cert_validation = properties["certvalidation"]
        mock_options.set_automatic_creation_test_cases = properties["automaticcreationtestcases"]
        mock_options.set_automatic_updation_links_to_test_cases = properties["automaticupdationlinkstotestcases"]
        mock_options.set_import_realtime = properties["importrealtime"]

        assert AppProperties.load_cli_properties(mock_options) == properties


