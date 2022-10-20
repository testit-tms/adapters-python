from testit_python_commons.services import AdapterManager
import testit_python_commons.services as adapter
from testit_python_commons.step import Step

from .scenario_parser import parse_scenario


class AdapterListener(object):
    __executable_test = None

    def __init__(self, adapter_manager: AdapterManager):
        self.__adapter_manager = adapter_manager

    def start_launch(self):
        test_run_id = self.__adapter_manager.get_test_run_id()

        self.__adapter_manager.set_test_run_id(test_run_id)

    def get_scenario(self, scenario):
        self.__executable_test = parse_scenario(scenario)

    def set_scenario(self):
        self.__adapter_manager.write_test(self.__executable_test)

    def add_setup(self):
        steps, result_steps = Step.get_steps_data()

        self.__executable_test['setUp'].extend(steps)
        self.__executable_test['setUpResults'].extend(result_steps)

    def add_step(self):
        steps, result_steps = Step.get_steps_data()

        self.__executable_test['steps'].extend(steps)
        self.__executable_test['stepResults'].extend(result_steps)

    @adapter.hookimpl
    def add_link(self, link):
        if self.__executable_test:
            self.__executable_test['resultLinks'].append(link)

    @adapter.hookimpl
    def add_message(self, test_message):
        if self.__executable_test:
            self.__executable_test['message'] = str(test_message)

    @adapter.hookimpl
    def add_attachments(self, attach_paths: list or tuple):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.load_attachments(attach_paths)

    @adapter.hookimpl
    def create_attachment(self, body, name: str):
        if self.__executable_test:
            self.__executable_test['attachments'] += self.__adapter_manager.create_attachment(body, name)
