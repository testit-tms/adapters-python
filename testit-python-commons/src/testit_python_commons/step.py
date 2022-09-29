import inspect
from datetime import datetime
from functools import wraps

from testit_python_commons.client.converter import Converter
from testit_python_commons.services import TmsPluginManager


class Step:
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

            with Step(name, function.__name__, parameters=parameters):
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

                    with Step(
                            self.args[0], self.args[1], parameters=parameters) if len(self.args) == 2\
                            else Step(self.args[0], parameters=parameters
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
        outcome = 'Failed' if exc_type else TmsPluginManager.get_plugin_manager().hook.get_pytest_check_outcome()[0] if\
            hasattr(TmsPluginManager.get_plugin_manager().hook, 'get_pytest_check_outcome') else 'Passed'
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
                steps_results.append({'step_results': []})
            steps_results[step_stack[0]]['step_results'] = self.result_step_append(
                                                                steps[step_stack[0]]['steps'],
                                                                steps_results[step_stack[0]]['step_results'],
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
        cls.attachments[-1] += TmsPluginManager.get_adapter_manager().load_attachments(attachments_paths)

    @classmethod
    def create_attachment(cls, body, name):
        cls.attachments[-1] += TmsPluginManager.get_adapter_manager().create_attachment(body, name)
