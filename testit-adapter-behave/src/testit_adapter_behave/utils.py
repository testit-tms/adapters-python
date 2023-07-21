import hashlib
import logging
import re
import typing

from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult

from .models.option import Option
from .models.tags import TagType
from .scenario_parser import get_scenario_external_id, get_scenario_parameters
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
            if scenarios[i].keyword == 'Scenario Outline' and hasattr(scenarios[i], 'scenarios'):
                scenarios_outline = filter_out_scenarios(tests_for_launch, scenarios[i].scenarios)

                if len(scenarios_outline) != 0:
                    for unmatched_scenario in set(scenarios[i].scenarios).symmetric_difference(set(scenarios_outline)):
                        scenarios[i].scenarios.remove(unmatched_scenario)

                    included_scenarios.append(scenarios[i])
            else:
                if validate_scenario(scenarios[i], tests_for_launch):
                    included_scenarios.append(scenarios[i])

        scenarios = included_scenarios

    return scenarios


def validate_scenario(scenario, tests_for_launch) -> bool:
    tags = parse_tags(scenario.tags + scenario.feature.tags)
    external_id = tags[TagType.EXTERNAL_ID] if \
        TagType.EXTERNAL_ID in tags and tags[TagType.EXTERNAL_ID] else get_scenario_external_id(scenario)

    if scenario.keyword == 'Scenario Outline':
        external_id = param_attribute_collector(external_id, get_scenario_parameters(scenario))

    return external_id in tests_for_launch


def param_attribute_collector(attribute, run_param):
    result = attribute
    param_keys = re.findall(r"\{'<(.*?)>'\}", attribute)
    if len(param_keys) > 0:
        for param_key in param_keys:
            root_key = param_key
            id_keys = re.findall(r'\[(.*?)\]', param_key)
            if len(id_keys) == 0:
                if root_key in run_param:
                    result = result.replace("{'<" + root_key + ">'}", str(run_param[root_key]))
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
                result = result.replace("{'<" + root_key + ">'}", str(run_param[base_key][val_key]))
            else:
                raise SystemExit("For type tuple, list, dict) support only one level!")
    elif len(param_keys) == 0:
        result = attribute
    else:
        raise SystemExit("Collecting parameters error!")
    return result


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


def convert_step_to_step_result_model(step: dict, nested_step_results: typing.List[StepResult]) -> StepResult:
    step_result_model = StepResult()\
        .set_title(step['title'])\
        .set_description(step['description'])\
        .set_outcome(step['outcome'])\
        .set_duration(step['duration'])\
        .set_attachments(step['attachments'])

    if 'parameters' in step:
        step_result_model.set_parameters(step['parameters'])

    if nested_step_results:
        step_result_model.set_step_results(nested_step_results)

    return step_result_model


def get_hash(value: str):
    md = hashlib.sha256(bytes(value, encoding='utf-8'))
    return md.hexdigest()
