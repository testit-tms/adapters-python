import hashlib
import logging
import re
import traceback
import typing
import pytest

from traceback import format_exception_only

from testit_python_commons.models.link import Link
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import TestResultWithAllFixtureStepResults

from testit_adapter_pytest.models.executable_test import ExecutableTest


__ARRAY_TYPES = (frozenset, list, set, tuple,)


def form_test(item) -> ExecutableTest:
    executable_test = ExecutableTest(
        external_id=__get_external_id_from(item),
        name=__get_display_name_from(item),
        duration=0,
        parameters=__get_parameters_from(item),
        properties=__get_properties_from(item),
        namespace=__get_namespace_from(item),
        classname=__get_class_name_from(item),
        title=__get_title_from(item),
        description=__get_description_from(item),
        links=__get_links_from(item),
        labels=__get_labels_from(item),
        work_item_ids=__get_work_item_ids_from(item),
        node_id=item.nodeid
    )

    if item.own_markers:
        for mark in item.own_markers:
            if mark.name == 'skip' or mark.name == 'skipif':
                executable_test.outcome = 'Skipped'
                if mark.args:
                    executable_test.message = mark.args[0]
                if mark.kwargs and 'reason' in mark.kwargs:
                    executable_test.message = mark.kwargs['reason']
            if mark.name == 'xfail':
                if mark.args:
                    executable_test.message = mark.args[0]
                if mark.kwargs and 'reason' in mark.kwargs:
                    executable_test.message = mark.kwargs['reason']

    return executable_test


def __get_display_name_from(item):
    display_name = __search_attribute(item, 'test_displayname')

    if not display_name:
        return item.function.__doc__ if \
            item.function.__doc__ else item.function.__name__

    return collect_parameters_in_string_attribute(display_name, get_all_parameters(item))


def __get_external_id_from(item):
    external_id = __search_attribute(item, 'test_external_id')

    if not external_id:
        return get_hash(item.parent.nodeid + item.function.__name__)

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
        return item.function.__module__

    return collect_parameters_in_string_attribute(namespace, get_all_parameters(item))


def __get_class_name_from(item):
    class_name = __search_attribute(item, 'test_classname')

    if not class_name:
        i = item.function.__qualname__.find('.')

        if i != -1:
            return item.function.__qualname__[:i]

        return None

    return collect_parameters_in_string_attribute(class_name, get_all_parameters(item))


def __get_links_from(item):
    links = __search_attribute(item, 'test_links')

    if not links:
        return []

    return __set_parameters_to_links(links, get_all_parameters(item))


def __get_parameters_from(item):
    if hasattr(item, 'callspec'):
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


def get_all_parameters(item):
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


def convert_executable_test_to_test_result_model(executable_test: ExecutableTest) -> TestResult:
    return TestResult()\
        .set_external_id(executable_test.external_id)\
        .set_autotest_name(executable_test.name)\
        .set_step_results(executable_test.step_results)\
        .set_setup_results(executable_test.setup_step_results)\
        .set_teardown_results(executable_test.teardown_step_results)\
        .set_duration(executable_test.duration)\
        .set_outcome(executable_test.outcome)\
        .set_traces(executable_test.traces)\
        .set_attachments(executable_test.attachments)\
        .set_parameters(executable_test.parameters)\
        .set_properties(executable_test.properties)\
        .set_namespace(executable_test.namespace)\
        .set_classname(executable_test.classname)\
        .set_title(executable_test.title)\
        .set_description(executable_test.description)\
        .set_links(executable_test.links)\
        .set_result_links(executable_test.result_links)\
        .set_labels(executable_test.labels)\
        .set_work_item_ids(executable_test.work_item_ids)\
        .set_message(executable_test.message)


def fixtures_containers_to_test_results_with_all_fixture_step_results(
        fixtures_containers: dict,
        test_result_ids: dict) -> typing.List[TestResultWithAllFixtureStepResults]:
    test_results_with_all_fixture_step_results = []

    for node_id, test_result_id in test_result_ids.items():
        test_result_with_all_fixture_step_results = TestResultWithAllFixtureStepResults(test_result_id)

        for uuid, fixtures_container in fixtures_containers.items():
            if node_id in fixtures_container.node_ids:
                if fixtures_container.befores:
                    test_result_with_all_fixture_step_results.set_setup_results(fixtures_container.befores[0].steps)

                if fixtures_container.afters:
                    test_result_with_all_fixture_step_results.set_teardown_results(fixtures_container.afters[0].steps)

        test_results_with_all_fixture_step_results.append(test_result_with_all_fixture_step_results)

    return test_results_with_all_fixture_step_results


def get_status(exception):
    if exception:
        if isinstance(exception, pytest.skip.Exception):
            return "Skipped"
        return "Failed"
    else:
        return "Passed"


def get_outcome_status(outcome):
    _, exception, _ = outcome.excinfo or (None, None, None)
    return get_status(exception)


def get_traceback(exc_traceback):
    return ''.join(traceback.format_tb(exc_traceback)) if exc_traceback else None


def get_message(etype, value):
    return '\n'.join(format_exception_only(etype, value)) if etype or value else None
