import testit_python_commons.services as adapter
from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.services import AdapterManager

from .models.step_result import ScenarioStepResult
from .scenario_parser import (
    ScenarioParser,
    STATUS)
from .utils import convert_executable_test_to_test_result_model


class AdapterListener(object):
    __executable_test = None
    __background_steps_count = 0
    __steps_count = 0

    def __init__(self, adapter_manager: AdapterManager):
        self.__adapter_manager = adapter_manager

    def start_launch(self):
        test_run_id = self.__adapter_manager.get_test_run_id()

        self.__adapter_manager.set_test_run_id(test_run_id)

    def get_tests_for_launch(self):
        return self.__adapter_manager.get_autotests_for_launch()

    def get_scenario(self, scenario):
        self.__executable_test = ScenarioParser.parse(scenario)
        self.__background_steps_count = len(scenario.background_steps)
        self.__steps_count = len(scenario.steps)

    def set_scenario(self):
        self.__adapter_manager.write_test(
            convert_executable_test_to_test_result_model(self.__executable_test))

    def get_step_parameters(self, match):
        scope = self.__get_scope()

        executable_step = ScenarioStepResult()

        for argument in match.arguments:
            name = argument.name if argument.name else 'param' + str(match.arguments.index(argument))
            executable_step.description += f'{name} = {argument.original} '
            executable_step.parameters[name] = argument.original

        if scope.lower() == 'setup':
            self.__executable_test.setup_results.append(executable_step)
        else:
            self.__executable_test.step_results.append(executable_step)

    def get_step_result(self, result):
        scope = self.__get_scope()
        outcome = STATUS[result.status]

        if scope == 'setup':
            active_step = self.__executable_test.setup_results[-1]

            active_step.title = result.name
            active_step.outcome = outcome
            active_step.duration = round(result.duration * 1000)

            self.__executable_test.setup_results[-1] = active_step
        else:
            active_step = self.__executable_test.step_results[-1]

            active_step.title = result.name
            active_step.outcome = outcome
            active_step.duration = round(result.duration * 1000)

            self.__executable_test.step_results[-1] = active_step

        self.__executable_test.duration += result.duration * 1000

        if outcome != OutcomeType.PASSED:
            self.__executable_test.traces = result.error_message
            self.__executable_test.outcome = outcome
            self.set_scenario()
            return

        if scope == 'setup':
            self.__background_steps_count -= 1
            return

        self.__steps_count -= 1

        if self.__steps_count == 0:
            self.__executable_test.outcome = outcome
            self.set_scenario()

    def __get_scope(self):
        if self.__background_steps_count != 0:
            return 'setup'

        return 'steps'

    @adapter.hookimpl
    def add_link(self, link):
        if self.__executable_test:
            self.__executable_test.result_links.append(link)

    @adapter.hookimpl
    def add_message(self, test_message):
        if self.__executable_test:
            self.__executable_test.message = str(test_message)

    @adapter.hookimpl
    def add_attachments(self, attach_paths: list or tuple):
        if self.__executable_test:
            self.__executable_test.attachments += self.__adapter_manager.load_attachments(attach_paths)

    @adapter.hookimpl
    def create_attachment(self, body, name: str):
        if self.__executable_test:
            self.__executable_test.attachments += self.__adapter_manager.create_attachment(body, name)
