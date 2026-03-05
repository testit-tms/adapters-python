from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils
from testit_python_commons.configurations.properties_names import PropertiesNames

class ClientConfiguration:
    __project_id = None
    __test_run_id = None

    def __init__(self, app_properties: dict):
        if app_properties.get(PropertiesNames.PROJECT_ID):
            self.__project_id = Utils.uuid_check(app_properties.get(PropertiesNames.PROJECT_ID))

        if app_properties.get(PropertiesNames.TEST_RUN_ID):
            self.__test_run_id = Utils.uuid_check(app_properties.get(PropertiesNames.TEST_RUN_ID))

        self.__url = Utils.url_check(app_properties.get(PropertiesNames.URL))
        self.__private_token = app_properties.get(PropertiesNames.PRIVATE_TOKEN)
        self.__configuration_id = Utils.uuid_check(app_properties.get(PropertiesNames.CONFIGURATION_ID))
        self.__tms_proxy = app_properties.get(PropertiesNames.TMS_PROXY)
        self.__adapter_mode = app_properties.get(PropertiesNames.ADAPTER_MODE)
        self.__cert_validation = Utils.convert_value_str_to_bool(app_properties.get(PropertiesNames.CERT_VALIDATION).lower())
        self.__automatic_updation_links_to_test_cases = Utils.convert_value_str_to_bool(
            app_properties.get(PropertiesNames.AUTOMATIC_UPDATION_LINKS_TO_TEST_CASES).lower())
        self.__sync_storage_port = app_properties.get(PropertiesNames.SYNC_STORAGE_PORT)

    @adapter_logger
    def get_url(self):
        return self.__url

    @adapter_logger
    def get_private_token(self):
        return self.__private_token

    @adapter_logger
    def get_project_id(self):
        return self.__project_id

    @adapter_logger
    def set_project_id(self, project_id: str):
        self.__project_id = project_id

    @adapter_logger
    def get_configuration_id(self):
        return self.__configuration_id

    @adapter_logger
    def get_test_run_id(self):
        return self.__test_run_id

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__test_run_id = test_run_id

    @adapter_logger
    def get_proxy(self):
        return self.__tms_proxy

    @adapter_logger
    def get_mode(self):
        return self.__adapter_mode

    def get_cert_validation(self) -> bool:
        return self.__cert_validation

    def get_automatic_updation_links_to_test_cases(self) -> bool:
        return self.__automatic_updation_links_to_test_cases

    def get_sync_storage_port(self) -> str:
        return self.__sync_storage_port
