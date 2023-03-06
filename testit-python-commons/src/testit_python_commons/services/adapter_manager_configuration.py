from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils


class AdapterManagerConfiguration:
    __test_run_id = None

    def __init__(self, app_properties: dict):
        if app_properties.get('testrunid'):
            self.__test_run_id = Utils.uuid_check(app_properties.get('testrunid'))

        self.__adapter_mode = app_properties.get('adaptermode', AdapterMode.USE_FILTER)

        __automatic_creation_test_cases = app_properties.get('automaticcreationtestcases')

        if __automatic_creation_test_cases and __automatic_creation_test_cases == 'true':
            self.__automatic_creation_test_cases = True
        else:
            self.__automatic_creation_test_cases = False

    @adapter_logger
    def get_test_run_id(self):
        return self.__test_run_id

    @adapter_logger
    def set_test_run_id(self, test_run_id: str):
        self.__test_run_id = test_run_id

    @adapter_logger
    def get_mode(self):
        return self.__adapter_mode

    @adapter_logger
    def should_automatic_creation_test_cases(self):
        return self.__automatic_creation_test_cases
