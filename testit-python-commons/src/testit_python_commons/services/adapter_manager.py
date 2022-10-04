import os
import uuid

from testit_python_commons.app_properties import AppProperties
import testit_python_commons.client.api_client as api_client
from testit_python_commons.models.adapter_mode import AdapterMode
from testit_python_commons.services.adapter_manager_configuration import AdapterManagerConfiguration


class AdapterManager:

    def __init__(self, option=None):
        app_properties = AppProperties.load_properties(option)
        client_configuration = api_client.ClientConfiguration(app_properties)
        self.__config = AdapterManagerConfiguration(app_properties)

        self.__api_client = api_client.ApiClientWorker(client_configuration)

    def set_test_run_id(self, test_run_id: str):
        self.__config.set_test_run_id(test_run_id)
        self.__api_client.set_test_run_id(test_run_id)

    def get_test_run_id(self):
        if self.__config.get_mode() != AdapterMode.NEW_TEST_RUN:
            return self.__config.get_test_run_id()

        return self.__api_client.create_test_run()

    def get_autotests_for_launch(self):
        if self.__config.get_mode() == AdapterMode.USE_FILTER:
            return self.__api_client.get_autotests_by_test_run_id()

        return

    def write_test(self, test: dict):
        self.__api_client.write_test(test)

    def load_attachments(self, attach_paths: list or tuple):
        return self.__api_client.load_attachments(attach_paths)

    def create_attachment(self, body: str, name: str):
        if name is None:
            name = str(uuid.uuid4()) + '-attachment.txt'

        path = os.path.join(os.path.abspath(''), name)

        with open(path, 'wb') as attached_file:
            attached_file.write(body.encode('utf-8'))

        attachment_id = self.__api_client.load_attachments((path,))

        os.remove(path)

        return attachment_id
