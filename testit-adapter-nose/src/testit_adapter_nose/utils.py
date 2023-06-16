import hashlib
import typing
from traceback import format_exception_only
from nose2 import (
    util,
    result
)

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.outcome_type import OutcomeType

from .models.autotest import Autotest
from .models.step_result import AutotestStepResult


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



def get_hash(value: str):
    md = hashlib.sha256(bytes(value, encoding='utf-8'))
    return md.hexdigest()


def convert_executable_test_to_test_result_model(executable_test: Autotest) -> TestResult:
    return TestResult()\
        .set_external_id(executable_test.external_id)\
        .set_autotest_name(executable_test.name)\
        .set_step_results(
            step_results_to_autotest_steps_model(executable_test.step_results))\
        .set_setup_results(
            step_results_to_autotest_steps_model(executable_test.setup_results))\
        .set_teardown_results(
            step_results_to_autotest_steps_model(executable_test.teardown_results))\
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


def step_results_to_autotest_steps_model(step_results: typing.List[AutotestStepResult]) -> typing.List[StepResult]:
    autotest_model_steps = []

    for step_result in step_results:
        step_result_model = StepResult()\
            .set_title(step_result.title)\
            .set_description(step_result.description)\
            .set_outcome(step_result.outcome)\
            .set_duration(step_result.duration)\
            .set_attachments(step_result.attachments)\
            .set_parameters(step_result.parameters)\
            .set_step_results(
                step_results_to_autotest_steps_model(step_result.step_results))

        autotest_model_steps.append(step_result_model)

    return autotest_model_steps
