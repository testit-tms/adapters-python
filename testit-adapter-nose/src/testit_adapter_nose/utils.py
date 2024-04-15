import hashlib
import logging
import re
from traceback import format_exception_only
from nose2 import (
    util,
    result
)
import inspect

from testit_python_commons.models.link import Link
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.outcome_type import OutcomeType


__ARRAY_TYPES = (frozenset, list, set, tuple,)


def status_details(event):
    message, trace = None, None
    if event.exc_info:
        exc_type, value, _ = event.exc_info
        message = '\n'.join(format_exception_only(exc_type, value)) if exc_type or value else None
        trace = ''.join(util.exc_info_to_string(event.exc_info, event.test))
    elif event.reason:
        message = event.reason

    return message, trace


def update_attrs(test, name, values):
    if type(values) in (list, tuple, str) and name.isidentifier():
        attrib = getattr(test, name, values)
        if attrib and attrib != values:
            attrib = sum(
                [tuple(i) if type(i) in (tuple, list) else (i,) for i in (attrib, values)],
                ()
            )
        setattr(test, name, attrib)


def get_outcome(event):
    outcome = None
    message = None
    trace = None

    if event.outcome == result.PASS and event.expected:
        outcome = OutcomeType.PASSED
    elif event.outcome == result.PASS and not event.expected:
        outcome = OutcomeType.PASSED
        message = "test passes unexpectedly"
    elif event.outcome == result.FAIL and not event.expected:
        outcome = OutcomeType.FAILED
        message, trace = status_details(event)
    elif event.outcome == result.ERROR:
        outcome = OutcomeType.BLOCKED
        message, trace = status_details(event)
    elif event.outcome == result.SKIP:
        outcome = OutcomeType.SKIPPED
        message, trace = status_details(event)

    return outcome, message, trace


def form_test(item):
    data = {}

    if hasattr(item, "_testFunc"):
        data = {
            'externalID': __get_external_id_from(item),
            'autoTestName': __get_display_name_from(item),
            'steps': [],
            'stepResults': [],
            'setUp': [],
            'setUpResults': [],
            'tearDown': [],
            'tearDownResults': [],
            'resultLinks': [],
            'duration': 0,
            'outcome': None,
            'failureReasonName': None,
            'traces': None,
            'attachments': [],
            'parameters': get_all_parameters(item),
            'properties': __get_properties_from(item),
            'namespace': __get_namespace_from(item),
            'classname': __get_class_name_from(item),
            'title': __get_title_from(item),
            'description': __get_description_from(item),
            'links': __get_links_from(item),
            'labels': __get_labels_from(item),
            'workItemsID': __get_work_item_ids_from(item),
            'message': None
        }

    elif hasattr(item, "_testMethodName"):
        data = {
            'externalID': get_hash(item._testMethodName),
            'autoTestName': item.__doc__ if item.__doc__ else item._testMethodName,
            'parameters': get_all_parameters(item)
        }

    return data


def __get_display_name_from(item):
    display_name = __search_attribute(item, 'test_displayname')

    if not display_name:
        return item._testFunc.__doc__ if \
            item._testFunc.__doc__ else item._testFunc.__name__

    return collect_parameters_in_string_attribute(display_name, get_all_parameters(item))


def __get_external_id_from(item):
    external_id = __search_attribute(item, 'test_external_id')

    if not external_id:
        return get_hash(item._testFunc.__qualname__ + item._testFunc.__name__)

    return collect_parameters_in_string_attribute(external_id, get_all_parameters(item))


def __get_title_from(item):
    title = __search_attribute(item, 'test_title')

    if not title:
        return None

    return collect_parameters_in_string_attribute(title, get_all_parameters(item))


def __get_description_from(item):
    description = __search_attribute(item, 'test_description')

    if not description:
        return None

    return collect_parameters_in_string_attribute(description, get_all_parameters(item))


def __get_namespace_from(item):
    namespace = __search_attribute(item, 'test_namespace')

    if not namespace:
        return item._testFunc.__module__

    return collect_parameters_in_string_attribute(namespace, get_all_parameters(item))


def __get_class_name_from(item):
    class_name = __search_attribute(item, 'test_classname')

    if not class_name:
        i = item._testFunc.__qualname__.find('.')

        if i != -1:
            return item._testFunc.__qualname__[:i]

        return None

    return collect_parameters_in_string_attribute(class_name, get_all_parameters(item))


def __get_links_from(item):
    links = __search_attribute(item, 'test_links')

    if not links:
        return []

    return __set_parameters_to_links(links, get_all_parameters(item))


def __get_parameters_from(item):
    if hasattr(item, 'array_parametrize_mark_id'):
        test_parameters = {}
        for key, parameter in item.callspec.params.items():
            test_parameters[key] = str(parameter)
        return test_parameters
    return None


def __get_properties_from(item):
    if hasattr(item, 'test_properties'):
        return item.test_properties
    return None


def __set_parameters_to_links(links, all_parameters):
    if not all_parameters:
        return links

    links_with_parameters = []

    for link in links:
        links_with_parameters.append(
            Link()
            .set_url(
                collect_parameters_in_string_attribute(
                    link.get_url(),
                    all_parameters))
            .set_title(
                collect_parameters_in_string_attribute(
                    link.get_title(),
                    all_parameters) if link.get_title() else None)
            .set_link_type(
                collect_parameters_in_string_attribute(
                    link.get_link_type(),
                    all_parameters) if link.get_link_type() else None)
            .set_description(
                collect_parameters_in_string_attribute(
                    link.get_description(),
                    all_parameters) if link.get_description() else None))

    return links_with_parameters


def __get_labels_from(item):
    test_labels = __search_attribute(item, 'test_labels')

    if not test_labels:
        return []

    labels = []

    for label in test_labels:
        result = collect_parameters_in_mass_attribute(
            label,
            get_all_parameters(item))

        if isinstance(result, __ARRAY_TYPES):
            for label in result:
                labels.append({
                    'name': str(label)
                })
        else:
            labels.append({
                'name': str(result)
            })

    return labels


def __get_work_item_ids_from(item):
    test_workitems_id = __search_attribute(item, 'test_workitems_id')

    if not test_workitems_id:
        return []

    all_parameters = get_all_parameters(item)

    if not all_parameters:
        return test_workitems_id

    result = collect_parameters_in_mass_attribute(test_workitems_id[0], all_parameters)

    return map(str, result) if isinstance(result, __ARRAY_TYPES) else [str(result)]


def fullname(event):
    if hasattr(event.test, "_testFunc"):
        test_module = event.test._testFunc.__module__
        test_name = event.test._testFunc.__name__
        return f"{test_module}.{test_name}"
    test_id = event.test.id()
    return test_id.split(":")[0]


def __search_attribute(item, attribute):
    if hasattr(item._testFunc, attribute):
        return getattr(item._testFunc, attribute)

    return


def get_all_parameters(item):
    def _params(names, values):
        return {name: str(value) for name, value in zip(names, values)}

    test_id = item.id()

    if len(test_id.split("\n")) > 1:
        if hasattr(item, "_testFunc"):
            wrapper_arg_spec = inspect.getfullargspec(item._testFunc)
            arg_set, obj = wrapper_arg_spec.defaults
            args = inspect.signature(obj).parameters.keys()

            return _params(args, arg_set)
        elif hasattr(item, "_testMethodName"):
            method = getattr(item, item._testMethodName)
            wrapper_arg_spec = inspect.getfullargspec(method)
            obj, arg_set = wrapper_arg_spec.defaults
            test_arg_spec = inspect.getfullargspec(obj)
            args = test_arg_spec.args

            return _params(args[1:], arg_set)


def collect_parameters_in_string_attribute(attribute, all_parameters):
    param_keys = re.findall(r"\{(.*?)\}", attribute)

    if len(param_keys) > 0:
        for param_key in param_keys:
            parameter = get_parameter(param_key, all_parameters)

            if parameter is not None:
                attribute = attribute.replace("{" + param_key + "}", str(parameter))

    return attribute


def collect_parameters_in_mass_attribute(attribute, all_parameters):
    param_keys = re.findall(r"\{(.*?)\}", attribute)

    if len(param_keys) == 1:
        parameter = get_parameter(param_keys[0], all_parameters)

        if parameter is not None:
            return parameter

    if len(param_keys) > 1:
        logging.error(f'(For type tuple, list, set) support only one key!')

    return attribute


def get_parameter(key_for_parameter, all_parameters):
    id_keys_in_parameter = re.findall(r'\[(.*?)\]', key_for_parameter)

    if len(id_keys_in_parameter) > 1:
        logging.error("(For type tuple, list, set, dict) support only one level!")

        return

    if len(id_keys_in_parameter) == 0:
        if key_for_parameter not in all_parameters:
            logging.error(f"Key for parameter {key_for_parameter} not found")

            return

        return all_parameters[key_for_parameter]

    parameter_key = key_for_parameter.replace("[" + id_keys_in_parameter[0] + "]", "")
    id_key_in_parameter = id_keys_in_parameter[0].strip("\'\"")

    if id_key_in_parameter.isdigit() and int(id_key_in_parameter) in range(len(all_parameters[parameter_key])):
        return all_parameters[parameter_key][int(id_key_in_parameter)]

    if id_key_in_parameter.isalnum() and id_key_in_parameter in all_parameters[parameter_key].keys():
        return all_parameters[parameter_key][id_key_in_parameter]

    logging.error(f"Not key: {key_for_parameter} in run parameters or other keys problem")


def get_hash(value: str):
    md = hashlib.sha256(bytes(value, encoding='utf-8'))
    return md.hexdigest()


def convert_executable_test_to_test_result_model(executable_test: dict) -> TestResult:
    return TestResult()\
        .set_external_id(executable_test['externalID'])\
        .set_autotest_name(executable_test['autoTestName'])\
        .set_step_results(executable_test['stepResults'])\
        .set_setup_results(executable_test['setUpResults'])\
        .set_teardown_results(executable_test['tearDownResults'])\
        .set_duration(executable_test['duration'])\
        .set_outcome(executable_test['outcome'])\
        .set_traces(executable_test['traces'])\
        .set_attachments(executable_test['attachments'])\
        .set_parameters(executable_test['parameters'])\
        .set_properties(executable_test['properties'])\
        .set_namespace(executable_test['namespace'])\
        .set_classname(executable_test['classname'])\
        .set_title(executable_test['title'])\
        .set_description(executable_test['description'])\
        .set_links(executable_test['links'])\
        .set_result_links(executable_test['resultLinks'])\
        .set_labels(executable_test['labels'])\
        .set_work_item_ids(executable_test['workItemsID'])\
        .set_message(executable_test['message'])
