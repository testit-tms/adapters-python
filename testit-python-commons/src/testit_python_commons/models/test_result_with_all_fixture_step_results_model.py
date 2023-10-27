import typing

from testit_python_commons.models.step_result import StepResult


class TestResultWithAllFixtureStepResults:
    def __init__(self, test_result_id: str):
        self.__test_result_id = test_result_id
        self.__setup_results = []
        self.__teardown_results = []

    def get_test_result_id(self) -> str:
        return self.__test_result_id

    def set_setup_results(self, setup_results: typing.List[StepResult]):
        self.__setup_results += setup_results

        return self

    def get_setup_results(self) -> typing.List[StepResult]:
        return self.__setup_results

    def set_teardown_results(self, teardown_results: typing.List[StepResult]):
        self.__teardown_results = teardown_results + self.__teardown_results

        return self

    def get_teardown_results(self) -> typing.List[StepResult]:
        return self.__teardown_results
