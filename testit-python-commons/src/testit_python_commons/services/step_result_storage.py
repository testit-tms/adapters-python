import logging
import typing

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.services.logger import adapter_logger


class StepResultStorage:
    __storage: typing.List[StepResult] = []

    @adapter_logger
    def add(self, step_result: StepResult):
        self.__storage.append(step_result)

    @adapter_logger
    def get_last(self) -> StepResult:
        try:
            return self.__storage[-1]
        except Exception as exc:
            logging.error(f'Cannot get last step from storage. Storage is empty. {exc}')

    @adapter_logger
    def remove_last(self):
        try:
            self.__storage.pop()
        except Exception as exc:
            logging.error(f'Cannot remove last step from storage. Storage is empty. {exc}')

    @adapter_logger
    def get_count(self) -> int:
        return len(self.__storage)
