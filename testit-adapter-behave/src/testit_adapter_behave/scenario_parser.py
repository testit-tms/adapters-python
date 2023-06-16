import traceback
from enum import Enum

from testit_python_commons.models.outcome_type import OutcomeType

from .models.tags import TagType
from .models.autotest import Autotest
from .tags_parser import parse_tags
from .utils import get_hash


STATUS = {
    'passed': OutcomeType.PASSED,
    'failed': OutcomeType.FAILED,
    'skipped': OutcomeType.SKIPPED,
    'untested': OutcomeType.SKIPPED,
    'undefined': OutcomeType.BLOCKED
}


class ScenarioParser:
    @classmethod
    def parse(cls, scenario) -> Autotest:
        tags = parse_tags(scenario.tags + scenario.feature.tags)

        external_id = tags[TagType.EXTERNAL_ID] if \
            TagType.EXTERNAL_ID in tags and tags[TagType.EXTERNAL_ID] else cls.__get_scenario_external_id(scenario)
        autotest_name = tags[TagType.DISPLAY_NAME] if \
            TagType.DISPLAY_NAME in tags and tags[TagType.DISPLAY_NAME] else cls.__get_scenario_name(scenario)
        namespace = tags[TagType.NAMESPACE] if \
            TagType.NAMESPACE in tags else cls.__get_scenario_namespace(scenario)
        parameters = cls.__get_scenario_namespace(scenario)

        executable_test = Autotest(
            external_id=external_id,
            name=autotest_name,
            namespace=namespace,
            parameters=parameters)

        if TagType.TITLE in tags:
            executable_test.title = tags[TagType.TITLE]

        if TagType.DESCRIPTION in tags:
            executable_test.description =tags[TagType.DESCRIPTION]

        if TagType.LINKS in tags:
            executable_test.links = tags[TagType.LINKS]

        if TagType.LABELS in tags:
            executable_test.labels = tags[TagType.LABELS]

        if TagType.CLASSNAME in tags:
            executable_test.classname = tags[TagType.CLASSNAME]

        if TagType.WORK_ITEM_IDS in tags:
            executable_test.work_item_ids = tags[TagType.WORK_ITEM_IDS]

        return executable_test

    @staticmethod
    def __get_scenario_name(scenario) -> str:
        return scenario.name if scenario.name else scenario.keyword

    @staticmethod
    def __get_scenario_external_id(scenario):
        return get_hash(scenario.feature.filename + scenario.name)

    @staticmethod
    def __get_scenario_namespace(scenario):
        return scenario.feature.filename

    @staticmethod
    def __get_scenario_parameters(scenario):
        row = scenario._row

        return {name: value for name, value in zip(row.headings, row.cells)} if row else {}

    @classmethod
    def __get_scenario_status(cls, scenario):
        for step in scenario.all_steps:
            if cls.__get_step_status(step) != 'passed':
                return cls.__get_step_status(step)
        return OutcomeType.PASSED

    @classmethod
    def __get_scenario_status_details(cls, scenario):
        for step in scenario.all_steps:
            if cls.__get_step_status(step) != 'passed':
                return cls.__get_step_status_details(step)

    @classmethod
    def __get_step_status(cls, result):
        if result.exception:
            return cls.__get_status(result.exception)
        else:
            if isinstance(result.status, Enum):
                return STATUS.get(result.status.name, None)
            else:
                return STATUS.get(result.status, None)

    @staticmethod
    def __get_status(exception):
        if exception and isinstance(exception, AssertionError):
            return OutcomeType.FAILED
        elif exception:
            return OutcomeType.BLOCKED
        return OutcomeType.PASSED

    @staticmethod
    def __get_step_status_details(result):
        if result.exception:
            trace = "\n".join(result.exc_traceback) if type(result.exc_traceback) == list else \
                ''.join(traceback.format_tb(result.exc_traceback))
            return trace

    @staticmethod
    def __get_step_table(step):
        table = [','.join(step.table.headings)]
        [table.append(','.join(list(row))) for row in step.table.rows]
        return '\n'.join(table)
