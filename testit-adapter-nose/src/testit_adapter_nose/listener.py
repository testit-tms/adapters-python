import testit_python_commons.services as adapter
from testit_python_commons.services import (
    AdapterManager,
    StepManager)
from .utils import (
    form_test,
    get_outcome,
    convert_executable_test_to_test_result_model
)


class AdapterListener(object):
    __executable_test = None

    def __init__(self, adapter_manager: AdapterManager, step_manager: StepManager):
        self.__adapter_manager = adapter_manager
        self.__step_manager = step_manager

    def start_launch(self):
        test_run_id = self.__adapter_manager.get_test_run_id()

        self.__adapter_manager.set_test_run_id(test_run_id)

    def get_tests_for_launch(self):
        return self.__adapter_manager.get_autotests_for_launch()

    def start_test(self, test):
        self.__executable_test = form_test(test)

    def set_outcome(self, event):
        outcome, message, trace = get_outcome(event)

        self.__executable_test['outcome'] = outcome
        self.__executable_test['traces'] = trace

        if not self.__executable_test['message']:
            self.__executable_test['message'] = message

    def stop_test(self):
        test_results_steps = self.__step_manager.get_steps_tree()
        self.__executable_test['stepResults'] = test_results_steps

        self.__adapter_manager.write_test(
            convert_executable_test_to_test_result_model(self.__executable_test))
        self.__executable_test = None

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
