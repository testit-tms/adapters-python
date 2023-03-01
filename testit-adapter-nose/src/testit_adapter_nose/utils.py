from traceback import format_exception_only
from nose2 import (
    util,
    result
)
import inspect

from testit_python_commons.services.utils import Utils
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
    parameters = get_params(test)

    if hasattr(test, "_testFunc"):
        item = test._testFunc

        if not hasattr(item, 'test_external_id'):
            item.test_external_id = Utils.get_hash(item.__name__)

        if not hasattr(item, 'test_displayname'):
            item.test_displayname = item.__doc__ if \
                item.__doc__ else item.__name__
        else:
            params = Utils.get_params(item)
            item.test_displayname = Utils.param_attribute_collector(
                item.test_displayname,
                params)

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
            'parameters': parameters,
            'properties': get_properties_from(item),
            'classname': get_classname_from(item),
            'title': get_title_from(item),
            'description': get_description_from(item),
            'links': [],
            'labels': [],
            'workItemsID': [],
            'message': None
        }

        if hasattr(item, 'test_links'):
            set_links(item, data)

        if hasattr(item, 'test_labels'):
            set_labels(item, data)

        if hasattr(item, 'test_workitems_id'):
            data['workItemsID'] = item.test_workitems_id
    elif hasattr(test, "_testMethodName"):
        data = {
            'externalID': Utils.get_hash(test._testMethodName),
            'autoTestName': test.__doc__ if \
                test.__doc__ else test._testMethodName,
            'parameters': parameters
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


def set_links(item, data):
    params = Utils.get_params(item)

    if params:
        for link in item.test_links:
            data['links'].append({})
            data['links'][-1]['url'] = Utils.param_attribute_collector(
                link['url'],
                params)
            data['links'][-1]['title'] = Utils.param_attribute_collector(
                link['title'],
                params) if link['title'] else None
            data['links'][-1]['type'] = Utils.param_attribute_collector(
                link['type'],
                params) if link['type'] else None
            data['links'][-1]['description'] = Utils.param_attribute_collector(
                link['description'],
                params) if link['description'] else None
    else:
        data['links'] = item.test_links


def get_title_from(item):
    if not hasattr(item, 'test_title'):
        return None

    params = Utils.get_params(item)

    if params:
        return Utils.param_attribute_collector(
            item.test_title,
            params)
    return item.test_title


def get_description_from(item):
    if not hasattr(item, 'test_description'):
        return None

    params = Utils.get_params(item)

    if params:
        return Utils.param_attribute_collector(
            item.test_description,
            params)
    return item.test_description


def set_labels(item, data):
    if hasattr(item, 'array_parametrize_mark_id'):
        for one_label in item.test_labels:
            result, param_id = Utils.mass_param_attribute_collector(
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
        result, param_id = Utils.mass_param_attribute_collector(
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
