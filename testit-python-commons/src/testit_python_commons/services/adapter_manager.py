from testit_python_commons.app_properties import AppProperties
import testit_python_commons.client.api_client as api_client


class AdapterManager:

    def __init__(self):
        app_properties = AppProperties.load_properties()
        client_configuration = api_client.ClientConfiguration(app_properties)

        self.__api_client = api_client.ApiClientWorker(client_configuration)

    def start_tests(self):
        self.__api_client.start_launch()

    def write_test(self, test: dict):
        self.__api_client.write_test(test)
