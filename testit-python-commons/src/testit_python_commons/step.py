from datetime import datetime
import logging
from functools import wraps
from typing import Any, Callable, TypeVar

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.services import (
    TmsPluginManager,
    Utils
)


Func = TypeVar("Func", bound=Callable[..., Any])


def step(*args, **kwargs):
    if callable(args[0]):
        function = args[0]
        return StepContext(function.__name__, None, {})(function)
    else:
        title = get_title(args, kwargs)
        description = get_description(args, kwargs)

        return StepContext(title, description, {})


def get_title(args: tuple, kwargs: dict):
    if 'title' in kwargs:
        return kwargs['title']

    if len(args) > 0:
        if isinstance(args[0], str):
            return args[0]

        logging.error(f'Cannot to get step title: {args[1]}. The title must be of string type.')


def get_description(args: tuple, kwargs: dict):
    if 'description' in kwargs:
        return kwargs['description']

    if len(args) > 1:
        if isinstance(args[1], str):
            return args[1]
        logging.error(f'Cannot to get step description: {args[1]}. The description must be of string type.')


class StepContext:
    def __init__(self, title, description, parameters):
        self.__title = title
        self.__description = description
        self.__parameters = parameters

    def __enter__(self):
        self.__start_time = round(datetime.utcnow().timestamp() * 1000)
        self.__step_result = StepResult()

        self.__step_result\
            .set_title(self.__title)\
            .set_description(self.__description)\
            .set_parameters(self.__parameters)

        logging.debug(f'Step "{self.__title}" was started')

        TmsPluginManager.get_step_manager().start_step(self.__step_result)

    def __exit__(self, exc_type, exc_val, exc_tb):
        outcome = 'Failed' if exc_type \
            else TmsPluginManager.get_plugin_manager().hook.get_pytest_check_outcome()[0] if \
            hasattr(TmsPluginManager.get_plugin_manager().hook, 'get_pytest_check_outcome') \
            else 'Passed'
        duration = round(datetime.utcnow().timestamp() * 1000) - self.__start_time

        self.__step_result\
            .set_outcome(outcome)\
            .set_duration(duration)

        TmsPluginManager.get_step_manager().stop_step()

    def __call__(self, function: Func) -> Func:
        @wraps(function)
        def impl(*args, **kwargs):
            __tracebackhide__ = True
            parameters = Utils.get_function_parameters(function, *args, **kwargs)

            title = self.__title if self.__title else function.__name__

            with StepContext(title, self.__description, parameters):
                return function(*args, **kwargs)

        return impl
