import inspect
import os
import re
from datetime import datetime
from functools import wraps

from testit_adapter_pytest import TestITPluginManager


def inner(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if hasattr(TestITPluginManager.get_plugin_manager().hook, 'add_properties') and kwargs:
            TestITPluginManager.get_plugin_manager().hook.add_properties(properties=kwargs)
        function(*args, **kwargs)
        return function
    return wrapper


def workItemID(*test_workitems_id: int or str):
    def outer(function):
        function.test_workitems_id = []
        for test_workitem_id in test_workitems_id:
            function.test_workitems_id.append(str(test_workitem_id))
        return inner(function)
    return outer


def displayName(test_displayname: str):
    def outer(function):
        function.test_displayname = test_displayname
        return inner(function)
    return outer


def externalID(test_external_id: str):
    def outer(function):
        function.test_external_id = test_external_id
        return inner(function)
    return outer


def title(test_title: str):
    def outer(function):
        function.test_title = test_title
        return inner(function)
    return outer


def description(test_description: str):
    def outer(function):
        function.test_description = test_description
        return inner(function)
    return outer


def labels(*test_labels: str):
    def outer(function):
        function.test_labels = test_labels
        return inner(function)
    return outer


def link(url: str, title: str = None, type: str = None, description: str = None):
    def outer(function):
        if not hasattr(function, 'test_links'):
            function.test_links = []
        function.test_links.append({'url': url, 'title': title, 'type': type, 'description': description})
        return inner(function)
    return outer


class LinkType:
    RELATED = 'Related'
    BLOCKED_BY = 'BlockedBy'
    DEFECT = 'Defect'
    ISSUE = 'Issue'
    REQUIREMENT = 'Requirement'
    REPOSITORY = 'Repository'


def addLink(url: str, title: str = None, type: str = None, description: str = None):
    if hasattr(TestITPluginManager.get_plugin_manager().hook, 'add_link'):
        TestITPluginManager.get_plugin_manager().hook.add_link(link_url=url, link_title=title, link_type=type, link_description=description)


def message(test_message: str):
    if hasattr(TestITPluginManager.get_plugin_manager().hook, 'add_message'):
        TestITPluginManager.get_plugin_manager().hook.add_message(test_message=test_message)


def attachments(*attachments_paths: str):
    if step.step_is_active():
        step.add_attachments(attachments_paths)
    else:
        if hasattr(TestITPluginManager.get_plugin_manager().hook, 'add_attachments'):
            TestITPluginManager.get_plugin_manager().hook.add_attachments(attach_paths=attachments_paths)


class step:
    step_stack = []
    steps_data = []
    steps_data_results = []
    attachments = []

    def __init__(self, *args, **kwargs):
        self.args = args
        if 'parameters' in kwargs and kwargs['parameters']:
            self.parameters = kwargs['parameters']

    def __call__(self, *args, **kwargs):
        parameters = {}
        if self.args and callable(self.args[0]):
            function = self.args[0]

            if self.step_stack:
                name = f'Step {str(self.step_stack[0] + 1)}'
                steps = self.steps_data[self.step_stack[0]]['steps']
                for step_id in self.step_stack[1:]:
                    name += f'.{step_id + 1}'
                    steps = steps[step_id]['steps']
                name += f'.{len(steps) + 1}'
            else:
                name = f'Step {str(len(self.steps_data) + 1)}'

            args_default_values = inspect.getfullargspec(function).defaults
            if args or args_default_values:
                if args_default_values:
                    args += args_default_values

                function_args_name = inspect.getfullargspec(function).args
                step_args = [arg_name for arg_name in function_args_name if arg_name not in list(kwargs)]

                for id in range(0, len(step_args)):
                    parameters[step_args[id]] = str(args[id])
            if kwargs:
                for key, parameter in kwargs.items():
                    parameters[key] = str(parameter)

            with step(name, function.__name__, parameters=parameters):
                return function(*args, **kwargs)
        else:
            function = args[0]

            @wraps(function)
            def step_wrapper(*a, **kw):
                if self.args:
                    args_default_values = inspect.getfullargspec(function).defaults
                    if a or args_default_values:
                        if args_default_values:
                            a += args_default_values

                        function_args_name = inspect.getfullargspec(function).args
                        step_args = [arg_name for arg_name in function_args_name if arg_name not in list(kw)]

                        for id in range(0, len(step_args)):
                            parameters[step_args[id]] = str(a[id])
                    if kw:
                        for key, parameter in kw.items():
                            parameters[key] = str(parameter)

                    with step(
                            self.args[0], self.args[1], parameters=parameters) if len(self.args) == 2\
                            else step(self.args[0], parameters=parameters
                        ):
                        return function(*a, **kw)
            return step_wrapper

    def __enter__(self):
        self.start_time = round(datetime.utcnow().timestamp() * 1000)
        self.steps_data = self.step_append(
                            self.steps_data,
                            self.step_stack,
                            self.args[0],
                            self.args[1] if len(self.args) == 2 else None)

    def __exit__(self, exc_type, exc_value, tb):
        outcome = 'Failed' if exc_type else TestITPluginManager.get_plugin_manager().hook.get_pytest_check_outcome()[0] if\
            hasattr(TestITPluginManager.get_plugin_manager().hook, 'get_pytest_check_outcome') else 'Passed'
        duration = round(datetime.utcnow().timestamp() * 1000) - self.start_time
        self.steps_data_results = self.result_step_append(
                                    self.steps_data,
                                    self.steps_data_results,
                                    self.step_stack,
                                    outcome,
                                    duration)

    def step_append(self, steps, step_stack, step_title, step_description):
        if steps and step_stack:
            steps[step_stack[0]]['steps'] = self.step_append(steps[step_stack[0]]['steps'], step_stack[1:], step_title, step_description)
        else:
            steps.append({'title': step_title, 'description': step_description, 'steps': []})
            self.step_stack.append(len(steps) - 1)
            self.attachments.append([])
        return steps

    def result_step_append(self, steps, steps_results, step_stack, outcome, duration):
        if steps and len(step_stack) == 1:
            while len(steps_results) < step_stack[0] + 1:
                steps_results.append({})
            steps_results[step_stack[0]]['title'] = steps[step_stack[0]]['title']
            steps_results[step_stack[0]]['description'] = steps[step_stack[0]]['description']
            steps_results[step_stack[0]]['outcome'] = outcome
            steps_results[step_stack[0]]['duration'] = duration
            steps_results[step_stack[0]]['parameters'] = self.parameters if hasattr(self, 'parameters') else None
            steps_results[step_stack[0]]['attachments'] = self.attachments[-1]
            del self.step_stack[-1]
            del self.attachments[-1]
        else:
            while len(steps_results) < step_stack[0] + 1:
                steps_results.append({'stepResults': []})
            steps_results[step_stack[0]]['stepResults'] = self.result_step_append(
                                                                steps[step_stack[0]]['steps'],
                                                                steps_results[step_stack[0]]['stepResults'],
                                                                step_stack[1:],
                                                                outcome,
                                                                duration)
        return steps_results

    @classmethod
    def get_steps_data(cls):
        data = cls.steps_data
        result_data = cls.steps_data_results
        cls.steps_data = []
        cls.steps_data_results = []
        return data, result_data

    @classmethod
    def step_is_active(cls):
        return len(cls.step_stack) != 0

    @classmethod
    def add_attachments(cls, attachments_paths):
        if hasattr(TestITPluginManager.get_plugin_manager().hook, 'load_attachments'):
            cls.attachments[-1] += TestITPluginManager.get_plugin_manager().hook.load_attachments(attach_paths=attachments_paths)[0]


def search_in_environ(variable):
    if re.fullmatch(r'{[a-zA-Z_]\w*}', variable) and variable[1:-1] in os.environ:
        return os.environ[variable[1:-1]]
    return variable


def autotests_parser(data_autotests, configuration):
    resolved_autotests = []
    for data_autotest in data_autotests:
        if configuration == data_autotest['configurationId']:
            resolved_autotests.append(data_autotest['autoTest']['externalId'])
    return resolved_autotests


def uuid_check(uuid):
    if not re.fullmatch(r'[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}', uuid):
        print(f'The wrong {uuid}!')
        raise SystemExit
    return uuid


def url_check(url):
    if not re.fullmatch(r'^(?:(?:(?:https?|ftp):)?//)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-zA-Z0-9\u00a1-\uffff][a-zA-Z0-9\u00a1-\uffff_-]{0,62})?[a-zA-Z0-9\u00a1-\uffff]\.)+(?:[a-zA-Z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$', url):
        print('The wrong URL!')
        raise SystemExit
    if url[-1] == '/':
        return url[:-1]
    return url
