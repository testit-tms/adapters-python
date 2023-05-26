import traceback
from enum import Enum

from testit_python_commons.models.outcome_type import OutcomeType

from .models.tags import TagType
from .tags_parser import parse_tags

STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED,
    'untested': OutcomeType.SKIPPED,
    'undefined': OutcomeType.BLOCKED
}


def parse_scenario(scenario):
    tags = parse_tags(scenario.tags + scenario.feature.tags)

    # TODO: Add model to python-commons; implement via attrs
    executable_test = {
        'externalID': tags[TagType.EXTERNAL_ID] if
        TagType.EXTERNAL_ID in tags and tags[TagType.EXTERNAL_ID] else get_scenario_external_id(scenario),
        'autoTestName': tags[TagType.DISPLAY_NAME] if
        TagType.DISPLAY_NAME in tags and tags[TagType.DISPLAY_NAME] else get_scenario_name(scenario),
        'outcome': None,
        'steps': [],
        'stepResults': [],
        'setUp': [],
        'setUpResults': [],
        'tearDown': [],
        'tearDownResults': [],
        'resultLinks': [],
        'duration': 0,
        'traces': None,
        'message': None,
        'namespace': get_scenario_namespace(scenario),
        'classname': None,
        'attachments': [],
        'parameters': get_scenario_parameters(scenario),
        # TODO: Make optional in Converter python-commons
        'properties': {},
        'title': None,
        'description': None,
        'links': [],
        'labels': [],
        'workItemsID': [],
        # TODO: Add to python-commons
        # 'started_on': '',
        # 'completed_on': None
    }

    if TagType.TITLE in tags:
        executable_test['title'] = tags[TagType.TITLE]

    if TagType.DESCRIPTION in tags:
        executable_test['description'] = tags[TagType.DESCRIPTION]

    if TagType.LINKS in tags:
        executable_test['links'] = tags[TagType.LINKS]

    if TagType.LABELS in tags:
        executable_test['labels'] = tags[TagType.LABELS]

    if TagType.NAMESPACE in tags:
        executable_test['namespace'] = tags[TagType.NAMESPACE]

    if TagType.CLASSNAME in tags:
        executable_test['classname'] = tags[TagType.CLASSNAME]

    if TagType.WORK_ITEM_IDS in tags:
        # TODO: Fix in python-commons to "workItemIds"
        executable_test['workItemsID'] = tags[TagType.WORK_ITEM_IDS]

    return executable_test


def parse_status(status):
    return STATUS[status.name]


def get_scenario_name(scenario):
    return scenario.name if scenario.name else scenario.keyword


def get_scenario_external_id(scenario):
    from .utils import get_hash

    return get_hash(scenario.feature.filename + scenario.name)


def get_scenario_namespace(scenario):
    return scenario.feature.filename


def get_scenario_parameters(scenario):
    row = scenario._row

    return {name: value for name, value in zip(row.headings, row.cells)} if row else {}


def get_scenario_status(scenario):
    for step in scenario.all_steps:
        if get_step_status(step) != 'passed':
            return get_step_status(step)
    return OutcomeType.PASSED


def get_scenario_status_details(scenario):
    for step in scenario.all_steps:
        if get_step_status(step) != 'passed':
            return get_step_status_details(step)


def get_step_status(result):
    if result.exception:
        return get_status(result.exception)
    else:
        if isinstance(result.status, Enum):
            return STATUS.get(result.status.name, None)
        else:
            return STATUS.get(result.status, None)


def get_status(exception):
    if exception and isinstance(exception, AssertionError):
        return OutcomeType.FAILED
    elif exception:
        return OutcomeType.BLOCKED
    return OutcomeType.PASSED


def get_step_status_details(result):
    if result.exception:
        trace = "\n".join(result.exc_traceback) if type(result.exc_traceback) == list else \
            ''.join(traceback.format_tb(result.exc_traceback))
        return trace


def get_step_table(step):
    table = [','.join(step.table.headings)]
    [table.append(','.join(list(row))) for row in step.table.rows]
    return '\n'.join(table)
