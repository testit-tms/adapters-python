import typing

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.services.step_result_storage import StepResultStorage


class StepManager:
    __steps_tree: typing.List[StepResult] = []

    def __init__(self):
        self.__storage = StepResultStorage()

    def start_step(self, step: StepResult):
        if self.__storage.get_count():
            parent_step: StepResult = self.__storage.get_last()

            step_results_from_parent_step = parent_step.get_step_results()
            step_results_from_parent_step.append(step)
            parent_step.set_step_results(step_results_from_parent_step)

        self.__storage.add(step)

    def stop_step(self):
        if self.__storage.get_count() == 1:
            self.__steps_tree.append(self.__storage.get_last())

        self.__storage.remove_last()

    def get_active_step(self) -> StepResult:
        return self.__storage.get_last()

    def get_steps_tree(self) -> typing.List[StepResult]:
        steps_tree = self.__steps_tree.copy()
        self.__steps_tree.clear()

        return steps_tree
