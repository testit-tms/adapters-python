from enum import Enum
import traceback

from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.services.utils import Utils

from .tags_parser import parse_tags
from .tags import TagType

STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED,
    'untested': OutcomeType.SKIPPED,
    'undefined': OutcomeType.BLOCKED
}


def parse_scenario(scenario):
    tags = parse_tags(scenario.tags + scenario.feature.tags)

    return {
        'externalID': tags[TagType.EXTERNAL_ID] if
        tags[TagType.EXTERNAL_ID] else get_scenario_external_id(scenario),
        'autoTestName': tags[TagType.DISPLAY_NAME] if
        tags[TagType.DISPLAY_NAME] else get_scenario_name(scenario),
        'steps': get_step_table(scenario.steps),
        'stepResults': [],
        'setUp': get_step_table(scenario.background_steps),
        'setUpResults': [],
        'resultLinks': [],
        'duration': 0,
        'outcome': get_scenario_status(scenario),
        'traces': get_scenario_status_details(scenario),
        'namespace': get_scenario_namespace(scenario),
        'attachments': [],
        'parameters': get_scenario_parameters(scenario),
        'title': tags[TagType.TITLE],
        'description': tags[TagType.DESCRIPTION],
        'links': tags[TagType.LINKS],
        'labels': tags[TagType.LABELS],
        'workItemIds': tags[TagType.WORK_ITEM_IDS],
    }


def get_scenario_name(scenario):
    return scenario.name if scenario.name else scenario.keyword


def get_scenario_external_id(scenario):
    parts = [scenario.feature.name, scenario.name]

    if scenario._row:
        row = scenario._row
        parts.extend(['{name}={value}'.format(name=name, value=value) for name, value in zip(row.headings, row.cells)])

    return Utils.getHash(*parts)


def get_scenario_namespace(scenario):
    return scenario.feature.filename


def get_scenario_parameters(scenario):
    row = scenario._row

    return {name: value for name, value in zip(row.headings, row.cells)} if row else None


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
