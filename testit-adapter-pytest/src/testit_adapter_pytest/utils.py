import hashlib
import logging
import re
import typing

from testit_python_commons.models.link import Link
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult


def form_test(item):
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
        'parameters': __get_parameters_from(item),
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

    if item.own_markers:
        for mark in item.own_markers:
            if mark.name == 'skip' or mark.name == 'skipif':
                data['outcome'] = 'Skipped'
                data['failureReasonName'] = None
                if mark.args:
                    data['message'] = mark.args[0]
                if mark.kwargs and 'reason' in mark.kwargs:
                    data['message'] = mark.kwargs['reason']
            if mark.name == 'xfail':
                if mark.args:
                    data['message'] = mark.args[0]
                if mark.kwargs and 'reason' in mark.kwargs:
                    data['message'] = mark.kwargs['reason']

    return data


def __get_display_name_from(item):
    display_name = __search_attribute(item, 'test_displayname')

    if not display_name:
        return item.function.__doc__ if \
            item.function.__doc__ else item.function.__name__

    params = get_params(item)

    return param_attribute_collector(
        display_name,
        params)


def __get_external_id_from(item):
    external_id = __search_attribute(item, 'test_external_id')

    if not external_id:
        return get_hash(item.nodeid + item.function.__name__)

    params = get_params(item)

    return param_attribute_collector(
        external_id,
        params)


def __get_title_from(item):
    title = __search_attribute(item, 'test_title')

    if not title:
        return None

    params = get_params(item)

    return param_attribute_collector(
        title,
        params)


def __get_description_from(item):
    description = __search_attribute(item, 'test_description')

    if not description:
        return None

    params = get_params(item)

    return param_attribute_collector(
        description,
        params)


def __get_namespace_from(item):
    namespace = __search_attribute(item, 'test_namespace')

    if not namespace:
        return item.function.__module__

    params = get_params(item)

    return param_attribute_collector(
        namespace,
        params)


def __get_class_name_from(item):
    class_name = __search_attribute(item, 'test_classname')

    if not class_name:
        i = item.function.__qualname__.find('.')

        if i != -1:
            return item.function.__qualname__[:i]

        return None

    params = get_params(item)

    return param_attribute_collector(
        class_name,
        params)


def __get_links_from(item):
    links = __search_attribute(item, 'test_links')

    if not links:
        return []

    params = get_params(item)

    return __set_params_in_links(
        links,
        params)


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


def __set_params_in_links(links, params):
    if not params:
        return links

    links_with_params = []

    for link in links:
        link_with_params = Link()\
            .set_url(
                param_attribute_collector(
                    link.get_url(),
                    params))\
            .set_title(
                param_attribute_collector(
                    link.get_title(),
                    params) if link.get_title() else None)\
            .set_link_type(
                param_attribute_collector(
                    link.get_link_type(),
                    params) if link.get_link_type() else None)\
            .set_description(
                param_attribute_collector(
                    link.get_description(),
                    params) if link.get_description() else None)

        links_with_params.append(link_with_params)

    return links_with_params


# TODO: Need refactor
def __get_labels_from(item):
    test_labels = __search_attribute(item, 'test_labels')

    if not test_labels:
        return []

    labels = []

    if hasattr(item, 'array_parametrize_mark_id'):
        for one_label in test_labels:
            result, param_id = mass_param_attribute_collector(
                one_label,
                item.own_markers,
                item.array_parametrize_mark_id,
                item.index)
            if param_id is not None and one_label[1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                for label in result:
                    labels.append({
                        'name': label
                    })
            else:
                labels.append({
                    'name': result
                })
    else:
        for label in test_labels:
            labels.append({
                'name': label
            })

    return labels


# TODO: Need refactor
def __get_work_item_ids_from(item):
    test_workitems_id = __search_attribute(item, 'test_workitems_id')

    if not test_workitems_id:
        return []

    if hasattr(item, 'array_parametrize_mark_id'):
        result, param_id = mass_param_attribute_collector(
            test_workitems_id[0], item.own_markers,
            item.array_parametrize_mark_id, item.index)

        if param_id is not None and test_workitems_id[0][1:-1] in \
                item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                    '-')[param_id]:
            return result

    return test_workitems_id


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


def get_params(item):
    params = {}

    if hasattr(item, 'test_properties'):
        params.update(item.test_properties)

    if hasattr(item, 'callspec'):
        params.update(item.callspec.params)

    return params


def __search_attribute(item, attribute):
    if hasattr(item.function, attribute):
        return getattr(item.function, attribute)

    if hasattr(item.cls, attribute):
        return getattr(item.cls, attribute)

    return

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

def step_results_to_autotest_steps_model(step_results: dict) -> typing.List[StepResult]:
    autotest_model_steps = []

    for step_result in step_results:
        step_result_model = StepResult()\
            .set_title(step_result['title'])\
            .set_description(step_result['description'])\
            .set_outcome(step_result['outcome'])\
            .set_duration(step_result['duration'])\
            .set_attachments(step_result['attachments'])

        if 'parameters' in step_result:
            step_result_model.set_parameters(step_result['parameters'])

        if 'step_results' in step_result:
            step_result_model.set_step_results(
                step_results_to_autotest_steps_model(step_result['step_results']))

        autotest_model_steps.append(step_result_model)

    return autotest_model_steps
