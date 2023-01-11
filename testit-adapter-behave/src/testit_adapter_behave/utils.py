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

    return option


def filter_out_scenarios(tests_for_launch, scenarios):
    if tests_for_launch:
        for i in range(len(scenarios)):
            tags = parse_tags(scenarios[i].tags + scenarios[i].feature.tags)
            external_id = tags[TagType.EXTERNAL_ID] if \
                TagType.EXTERNAL_ID in tags and tags[TagType.EXTERNAL_ID] else get_scenario_external_id(scenarios[i])

            if external_id not in tests_for_launch:
                del scenarios[i]

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
