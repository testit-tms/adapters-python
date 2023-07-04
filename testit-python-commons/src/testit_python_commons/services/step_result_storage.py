import logging
import typing

from testit_python_commons.models.step_result import StepResult


class StepResultStorage:
    __storage: typing.List[StepResult] = []

    def add(self, step_result: StepResult):
        self.__storage.append(step_result)

    def get_last(self):
        if not self.__storage:
            return

        return self.__storage[-1]

    def remove_last(self):
        try:
            self.__storage.pop()
        except Exception as exc:
            logging.error(f'Cannot remove last step from storage. Storage is empty. {exc}')

    def get_count(self) -> int:
        return len(self.__storage)
