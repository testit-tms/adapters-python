from testit_python_commons.services import AdapterManager
from testit_python_commons.step import Step
from .utils import (
    form_test,
    get_outcome
)


class AdapterListener(object):
    __executable_test = None

    def __init__(self, adapter_manager: AdapterManager):
        self.__adapter_manager = adapter_manager

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
        self.__executable_test['message'] = message
        self.__executable_test['traces'] = trace

    def stop_test(self):
        test_steps, test_results_steps = Step.get_steps_data()

        self.__executable_test['steps'] = test_steps
        self.__executable_test['stepResults'] = test_results_steps

        self.__adapter_manager.write_test(self.__executable_test)
        self.__executable_test = None
