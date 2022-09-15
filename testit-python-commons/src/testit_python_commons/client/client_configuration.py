from testit_python_commons.services.utils import Utils


class ClientConfiguration:
    __project_id = None
    __test_run_id = None

    def __init__(self, app_properties: dict):
        if app_properties.get('projectid'):
            self.__project_id = Utils.uuid_check(app_properties.get('projectid'))

        if app_properties.get('testrunid'):
            self.__test_run_id = Utils.uuid_check(app_properties.get('testrunid'))

        self.__url = Utils.url_check(app_properties.get('url'))
        self.__private_token = app_properties.get('privatetoken')
        self.__configuration_id = Utils.uuid_check(app_properties.get('configurationid'))
        self.__test_run_name = app_properties.get('testrunname')
        self.__tms_proxy = app_properties.get('tmsproxy')
        self.__adapter_mode = app_properties.get('adaptermode')

    def get_url(self):
        return self.__url

    def get_private_token(self):
        return self.__private_token

    def get_project_id(self):
        return self.__project_id

    def set_project_id(self, project_id: str):
        self.__project_id = project_id

    def get_configuration_id(self):
        return self.__configuration_id

    def get_test_run_id(self):
        return self.__test_run_id

    def set_test_run_id(self, test_run_id: str):
        self.__test_run_id = test_run_id

    def get_test_run_name(self):
        return self.__test_run_name

    def get_proxy(self):
        return self.__tms_proxy

    def get_mode(self):
        return self.__adapter_mode
