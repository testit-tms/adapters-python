from functools import wraps

from testit_python_commons.services.plugin_manager import TmsPluginManager


def adapter_logger(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        from testit_python_commons.services.utils import Utils

        logger = TmsPluginManager.get_logger()

        parameters = Utils.get_function_parameters(function, *args, **kwargs)

        message = f'Method "{function.__name__}" started'

        if parameters:
            message += f' with parameters: {parameters}'

        logger.debug(message)

        result = function(*args, **kwargs)

        message = f'Method "{function.__name__}" finished'

        if result is not None:
            message += f' with result: {result}'

        logger.debug(message)

        return result
    return wrapper
