from testit_python_commons.services.logger import adapter_logger


class StepResult:
    __title: str = None
    __outcome: str = None
    __description: str = None
    __duration: int = None
    __started_on: str = None
    __completed_on: str = None
    __step_results: list = []
    __attachments: list = []
    __parameters: dict = {}

    @adapter_logger
    def set_title(self, title: str):
        self.__title = title

        return self

    @adapter_logger
    def get_title(self) -> str:
        return self.__title

    @adapter_logger
    def set_outcome(self, outcome: str):
        self.__outcome = outcome

        return self

    @adapter_logger
    def get_outcome(self) -> str:
        return self.__outcome

    @adapter_logger
    def set_description(self, description: str):
        self.__description = description

        return self

    @adapter_logger
    def get_description(self) -> str:
        return self.__description

    @adapter_logger
    def set_duration(self, duration: int):
        self.__duration = duration

        return self

    @adapter_logger
    def get_duration(self) -> int:
        return self.__duration

    @adapter_logger
    def set_started_on(self, started_on: str):
        self.__started_on = started_on

        return self

    @adapter_logger
    def get_started_on(self) -> str:
        return self.__started_on

    @adapter_logger
    def set_completed_on(self, completed_on: str):
        self.__completed_on = completed_on

        return self

    @adapter_logger
    def get_completed_on(self) -> str:
        return self.__completed_on

    @adapter_logger
    def set_step_results(self, step_results: list):
        self.__step_results = step_results

        return self

    @adapter_logger
    def get_step_results(self) -> list:
        return self.__step_results

    @adapter_logger
    def set_attachments(self, attachments: list):
        self.__attachments = attachments

        return self

    @adapter_logger
    def get_attachments(self) -> list:
        return self.__attachments

    @adapter_logger
    def set_parameters(self, parameters: dict):
        self.__parameters = parameters

        return self

    @adapter_logger
    def get_parameters(self) -> dict:
        return self.__parameters
