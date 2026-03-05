from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils
from testit_python_commons.configurations.properties_names import PropertiesNames

class AdapterManagerConfiguration:
    __test_run_id = None

    def __init__(self, app_properties: dict):
        if app_properties.get(PropertiesNames.TEST_RUN_ID):
            self.__test_run_id = Utils.uuid_check(app_properties.get(PropertiesNames.TEST_RUN_ID))

        self.__adapter_mode = app_properties.get(PropertiesNames.ADAPTER_MODE, AdapterMode.USE_FILTER)
        self.__automatic_creation_test_cases = Utils.convert_value_str_to_bool(
            app_properties.get(PropertiesNames.AUTOMATIC_CREATION_TEST_CASES).lower())

        self.__import_realtime = Utils.convert_value_str_to_bool(app_properties.get(PropertiesNames.IMPORT_REALTIME).lower())
        self.__test_run_name = app_properties.get(PropertiesNames.TEST_RUN_NAME)

    @adapter_logger
    def get_test_run_id(self):
        return self.__test_run_id

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__test_run_id = test_run_id

    @adapter_logger
    def get_test_run_name(self):
        return self.__test_run_name

    @adapter_logger
    def get_mode(self):
        return self.__adapter_mode

    @adapter_logger
    def should_automatic_creation_test_cases(self) -> bool:
        return self.__automatic_creation_test_cases

    @adapter_logger
    def should_import_realtime(self) -> bool:
        return self.__import_realtime
