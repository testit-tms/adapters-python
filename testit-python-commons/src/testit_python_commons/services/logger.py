import inspect

from functools import wraps

from testit_python_commons.services.plugin_manager import TmsPluginManager


def adapter_logger(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        logger = TmsPluginManager.get_logger()

        parameters = get_function_parameters(function, *args, **kwargs)

        message = f'Method "{function.__name__}" started'

        if parameters:
            message += f' with parameters: {parameters}'

        logger.debug(message)

        result = function(*args, **kwargs)

        message = f'Method "{function.__name__}" finished'

        if result:
            message += f' with result: {result}'

        logger.debug(message)

        return result
    return wrapper

def get_function_parameters(function, *args, **kwargs):
    parameters = {}
    args_default_values = inspect.getfullargspec(function).defaults

    if args or args_default_values:
        all_keys = inspect.getfullargspec(function).args
        all_args = list(args)

        if args_default_values:
            all_args += list(args_default_values[len(args) - (len(all_keys) - len(args_default_values)):])

        method_args = [arg_name for arg_name in all_keys if arg_name not in list(kwargs)]

        if len(method_args) == len(all_args):
            for index in range(0, len(method_args)):
                parameters[method_args[index]] = str(all_args[index])

    if kwargs:
        for key, parameter in kwargs.items():
            parameters[key] = str(parameter)

    return parameters
