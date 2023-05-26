import inspect
import logging
import re
import warnings

from testit_python_commons.models.link import Link
from testit_python_commons.services.logger import adapter_logger


class Utils:
    @staticmethod
    def uuid_check(uuid: str):
        if not re.fullmatch(r'[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}', uuid):
            logging.error(f'The wrong {uuid}!')
            raise SystemExit

        return uuid

    @staticmethod
    def url_check(url: str):
        if not re.fullmatch(
                r"^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)"
                r"([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$",
                url):
            logging.error('The wrong URL!')
            raise SystemExit

        if url[-1] == '/':
            return url[:-1]

        return url

    @staticmethod
    def deprecated(message):
        def deprecated_decorator(func):  # noqa: N802
            def deprecated_func(*args, **kwargs):
                warnings.warn(
                    '"{}" is no longer acceptable to compute time between versions.\n{}'.format(func.__name__, message),
                    category=DeprecationWarning,
                    stacklevel=2)
                warnings.simplefilter('default', DeprecationWarning)
                return func(*args, **kwargs)

            return deprecated_func

        return deprecated_decorator

    @staticmethod
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

    @staticmethod
    @adapter_logger
    def convert_link_dict_to_link_model(link_dict: dict) -> Link:
        link_model = Link()
        link_model.set_url(link_dict['url'])

        if 'title' in link_dict:
            link_model.set_title(link_dict['title'])

        if 'type' in link_dict:
            link_model.set_link_type(link_dict['type'])

        if 'description' in link_dict:
            link_model.set_description(link_dict['description'])

        return link_model
