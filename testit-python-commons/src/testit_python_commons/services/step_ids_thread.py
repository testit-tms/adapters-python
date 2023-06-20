import typing

from testit_python_commons.services.logger import adapter_logger


class StepIdsThread:
    __storage: typing.List[str] = []

    @adapter_logger
    def get_current(self) -> str | None:
        return self.__storage[-1] if len(self.__storage) else None

    @adapter_logger
    def start(self, uuid: str):
        self.__storage.append(uuid)

    @adapter_logger
    def stop(self) -> str | None:
        return self.__storage.pop() if len(self.__storage) else None

    @adapter_logger
    def clear(self):
        self.__storage.clear()
