import hashlib
import typing

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult

from .models.option import Option
from .models.tags import TagType
from .scenario_parser import get_scenario_external_id
from .tags_parser import parse_tags


def parse_userdata(userdata):
    if not userdata:
        return

    option = Option()

    if 'tmsUrl' in userdata:
        option.set_url = userdata['tmsUrl']

    if 'tmsPrivateToken' in userdata:
        option.set_private_token = userdata['tmsPrivateToken']

    if 'tmsProjectId' in userdata:
        option.set_project_id = userdata['tmsProjectId']

    if 'tmsConfigurationId' in userdata:
        option.set_configuration_id = userdata['tmsConfigurationId']

    if 'tmsTestRunId' in userdata:
        option.set_test_run_id = userdata['tmsTestRunId']

    if 'tmsTestRunName' in userdata:
        option.set_test_run_name = userdata['tmsTestRunName']

    if 'tmsProxy' in userdata:
        option.set_tms_proxy = userdata['tmsProxy']

    if 'tmsAdapterMode' in userdata:
        option.set_adapter_mode = userdata['tmsAdapterMode']

    if 'tmsConfigFile' in userdata:
        option.set_config_file = userdata['tmsConfigFile']

    if 'tmsCertValidation' in userdata:
        option.set_cert_validation = userdata['tmsCertValidation']

    if 'tmsAutomaticCreationTestCases' in userdata:
        option.set_automatic_creation_test_cases = userdata['tmsAutomaticCreationTestCases']

    return option


def filter_out_scenarios(tests_for_launch, scenarios):
    if tests_for_launch:
        included_scenarios = []

        for i in range(len(scenarios)):
            tags = parse_tags(scenarios[i].tags + scenarios[i].feature.tags)
            external_id = tags[TagType.EXTERNAL_ID] if \
                TagType.EXTERNAL_ID in tags and tags[TagType.EXTERNAL_ID] else get_scenario_external_id(scenarios[i])

            if external_id in tests_for_launch:
                included_scenarios.append(scenarios[i])

        scenarios = included_scenarios

    return scenarios


# TODO: Add to python-commons
def convert_step_to_step(step, nested_steps):
    return {
        'title': step['title'],
        'description': step['description'],
        'steps': nested_steps,
    }


# TODO: Add to python-commons
def convert_step_to_step_result(step, nested_step_results):
    model = {
        'title': step['title'],
        'description': step['description'],
        'duration': step['duration'],
        'outcome': step['outcome'],
        'parameters': step['parameters'],
        'attachments': step['attachments'],
        # TODO: Add to model
        # started_on: started_on,
        # completed_on: completed_on
    }

    if nested_step_results:
        model['step_results'] = nested_step_results

    return model


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
