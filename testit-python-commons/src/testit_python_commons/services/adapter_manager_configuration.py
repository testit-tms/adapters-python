from testit_python_commons.services.utils import Utils
from testit_python_commons.models.adapter_mode import AdapterMode


class AdapterManagerConfiguration:
    __test_run_id = None

    def __init__(self, app_properties: dict):
        if app_properties.get('testrunid'):
            self.__test_run_id = Utils.uuid_check(app_properties.get('testrunid'))

        self.__adapter_mode = app_properties.get('adaptermode', AdapterMode.USE_FILTER)

    def get_test_run_id(self):
        return self.__test_run_id

    def set_test_run_id(self, test_run_id: str):
        self.__test_run_id = test_run_id

    def get_mode(self):
        return self.__adapter_mode
