import hashlib
import logging
import re
import typing
from traceback import format_exception_only
from nose2 import (
    util,
    result
)
import inspect

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.outcome_type import OutcomeType


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

    print(outcome, message, trace)

    return outcome, message, trace


def form_test(test):
    data = {}

    if hasattr(test, "_testFunc"):
        item = test._testFunc

        if not hasattr(item, 'test_external_id'):
            item.test_external_id = get_hash(item.__name__)

        if not hasattr(item, 'test_displayname'):
            item.test_displayname = item.__doc__ if \
                item.__doc__ else item.__name__
        else:
            item.test_displayname = param_attribute_collector(
                item.test_displayname,
                get_params(test))

        data = {
            'externalID': item.test_external_id,
            'autoTestName': item.test_displayname,
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
            'namespace': item.__module__,
            'attachments': [],
            'parameters': get_params(test),
            'properties': get_properties_from(test),
            'classname': get_classname_from(item),
            'title': get_title_from(test),
            'description': get_description_from(test),
            'links': [],
            'labels': [],
            'workItemsID': [],
            'message': None
        }

        if hasattr(item, 'test_links'):
            set_links(test, data)

        if hasattr(item, 'test_labels'):
            set_labels(item, data)

        if hasattr(item, 'test_workitems_id'):
            data['workItemsID'] = item.test_workitems_id
    elif hasattr(test, "_testMethodName"):
        data = {
            'externalID': get_hash(test._testMethodName),
            'autoTestName': test.__doc__ if \
                test.__doc__ else test._testMethodName,
            'parameters': get_params(test)
        }

    return data


def get_properties_from(item):
    if hasattr(item, 'test_properties'):
        return item.test_properties
    return None


def get_classname_from(item):
    i = item.__qualname__.find('.')
    if i != -1:
        return item.__qualname__[:i]
    return None


def set_links(test, data):
    item = test._testFunc
    params = get_params(test)

    if params:
        for link in item.test_links:
            data['links'].append({})
            data['links'][-1]['url'] = param_attribute_collector(
                link['url'],
                params)
            data['links'][-1]['title'] = param_attribute_collector(
                link['title'],
                params) if link['title'] else None
            data['links'][-1]['type'] = param_attribute_collector(
                link['type'],
                params) if link['type'] else None
            data['links'][-1]['description'] = param_attribute_collector(
                link['description'],
                params) if link['description'] else None
    else:
        data['links'] = item.test_links


def get_title_from(test):
    item = test._testFunc

    if not hasattr(item, 'test_title'):
        return None

    params = get_params(test)

    if params:
        return param_attribute_collector(
            item.test_title,
            params)
    return item.test_title


def get_description_from(test):
    item = test._testFunc

    if not hasattr(item, 'test_description'):
        return None

    params = get_params(test)

    if params:
        return param_attribute_collector(
            item.test_description,
            params)
    return item.test_description


def set_labels(item, data):
    if hasattr(item, 'array_parametrize_mark_id'):
        for one_label in item.test_labels:
            result, param_id = mass_param_attribute_collector(
                one_label,
                item.own_markers,
                item.array_parametrize_mark_id,
                item.index)
            if param_id is not None and one_label[1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                for label in result:
                    data['labels'].append({
                        'name': label
                    })
            else:
                data['labels'].append({
                    'name': result
                })
    else:
        for label in item.test_labels:
            data['labels'].append({
                'name': label
            })


def set_workitems_id(item, data):
    if hasattr(item, 'array_parametrize_mark_id'):
        result, param_id = mass_param_attribute_collector(
            item.test_workitems_id[0], item.own_markers,
            item.array_parametrize_mark_id, item.index)
        if param_id is not None and item.test_workitems_id[0][1:-1] in \
                item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                    '-')[param_id]:
            data['workItemsID'] = result
        else:
            data['workItemsID'] = [result]
    else:
        data['workItemsID'] = item.test_workitems_id


def fullname(event):
    if hasattr(event.test, "_testFunc"):
        test_module = event.test._testFunc.__module__
        test_name = event.test._testFunc.__name__
        return f"{test_module}.{test_name}"
    test_id = event.test.id()
    return test_id.split(":")[0]


def get_params(test):
    def _params(names, values):
        return {name if name else f"param{values.index(value)}": value for name, value in zip(names, values)}

    test_id = test.id()

    if len(test_id.split("\n")) > 1:
        if hasattr(test, "_testFunc"):
            wrapper_arg_spec = inspect.getfullargspec(test._testFunc)
            arg_set, obj = wrapper_arg_spec.defaults
            test_arg_spec = inspect.getfullargspec(obj)
            args = test_arg_spec.args

            return _params(args, arg_set)
        elif hasattr(test, "_testMethodName"):
            method = getattr(test, test._testMethodName)
            wrapper_arg_spec = inspect.getfullargspec(method)
            obj, arg_set = wrapper_arg_spec.defaults
            test_arg_spec = inspect.getfullargspec(obj)
            args = test_arg_spec.args

            return _params(args[1:], arg_set)


def param_attribute_collector(attribute, run_param):
    result = attribute
    param_keys = re.findall(r"\{(.*?)\}", attribute)
    if len(param_keys) > 0:
        for param_key in param_keys:
            root_key = param_key
            id_keys = re.findall(r'\[(.*?)\]', param_key)
            if len(id_keys) == 0:
                if root_key in run_param:
                    result = result.replace("{" + root_key + "}", str(run_param[root_key]))
                else:
                    logging.error(f"Parameter {root_key} not found")
            elif len(id_keys) == 1:
                base_key = root_key.replace("[" + id_keys[0] + "]", "")
                id_key = id_keys[0].strip("\'\"")
                if id_key.isdigit() and int(id_key) in range(len(run_param[base_key])):
                    val_key = int(id_key)
                elif id_key.isalnum() and not id_key.isdigit() and id_key in run_param[base_key].keys():
                    val_key = id_key
                else:
                    raise SystemExit(f"Not key: {root_key} in run parameters or other keys problem")
                result = result.replace("{" + root_key + "}", str(run_param[base_key][val_key]))
            else:
                raise SystemExit("For type tuple, list, dict) support only one level!")
    elif len(param_keys) == 0:
        result = attribute
    else:
        raise SystemExit("Collecting parameters error!")
    return result


def mass_param_attribute_collector(attribute, marks, parametrize_id, index):
    for param_index in parametrize_id:
        param_names = []
        for param_name in marks[param_index].args[0].split(','):
            param_names.append(param_name.strip())
        if attribute[1:-1] != '' and attribute[1:-1] in param_names:
            param_id = marks[param_index].args[0].split(', ').index(attribute[1:-1])
            return marks[param_index].args[1][index][param_id], param_id
    return attribute, None


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
