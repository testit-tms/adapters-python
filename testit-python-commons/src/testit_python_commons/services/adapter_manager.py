import os
import uuid

from testit_python_commons.app_properties import AppProperties
import testit_python_commons.client.api_client as api_client


class AdapterManager:

    def __init__(self, option=None):
        app_properties = AppProperties.load_properties(option)
        client_configuration = api_client.ClientConfiguration(app_properties)

        self.__api_client = api_client.ApiClientWorker(client_configuration)

    def start_tests(self):
        return self.__api_client.start_launch()

    def write_test(self, test: dict):
        self.__api_client.write_test(test)

    def load_attachments(self, attach_paths: tuple):
        return self.__api_client.load_attachments(attach_paths)

    def create_attachment(self, body: str, name: str):
        if name is None:
            name = str(uuid.uuid4()) + '-attachment.txt'

        if not os.path.isdir('files'):
            os.mkdir('files')

        path = os.path.abspath('') + f'{os.sep}files{os.sep}{name}'

        with open(path, 'wb') as attached_file:
            attached_file.write(body.encode('utf-8'))

        return self.__api_client.load_attachments([path])
