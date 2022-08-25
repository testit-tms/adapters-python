from testit_python_commons.services.utils import Utils


class ClientConfiguration:

    def __init__(self, app_properties: dict):
        if app_properties.get('testrunid'):
            self.__testrun_id = Utils.uuid_check(app_properties.get('testrunid'))
        else:
            self.__project_id = Utils.uuid_check(app_properties.get('projectid'))

        self.__url = Utils.url_check(app_properties.get('url'))
        self.__private_token = app_properties.get('privatetoken')
        self.__configuration_id = Utils.uuid_check(app_properties.get('configurationid'))
        self.__testrun_name = app_properties.get('testrun_name')
        self.__testit_proxy = app_properties.get('testit_proxy')
        self.__testit_mode = app_properties.get('testit_mode')

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

    def get_testrun_id(self):
        return self.__testrun_id

    def set_testrun_id(self, testrun_id: str):
        self.__testrun_id = testrun_id

    def get_testrun_name(self):
        return self.__testrun_name

    def get_proxy(self):
        return self.__testit_proxy

    def get_mode(self):
        return self.__testit_mode
