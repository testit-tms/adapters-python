import hashlib
import typing
from datetime import datetime

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult


def convert_time(time):
    date = datetime.strptime(time, "%Y%m%d %H:%M:%S.%f")
    date = date.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return date


def convert_executable_test_to_test_result_model(executable_test: dict) -> TestResult:
    return TestResult()\
        .set_external_id(executable_test['externalID'])\
        .set_autotest_name(executable_test['autoTestName'])\
        .set_step_results(
            step_results_to_autotest_steps_model(executable_test['stepResults']))\
        .set_setup_results(
            step_results_to_autotest_steps_model(executable_test['setUpResults']))\
        .set_teardown_results(
            step_results_to_autotest_steps_model(executable_test['tearDownResults']))\
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


def get_hash(value: str):
    md = hashlib.sha256(bytes(value, encoding='utf-8'))
    return md.hexdigest()


STATUSES = {'FAIL': 'Failed', 'PASS': 'Passed', 'SKIP': 'Skipped', 'NOT RUN': 'Skipped'}
