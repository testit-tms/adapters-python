from typing import List

from testit_python_commons.models.link import Link
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.utils import HtmlEscapeUtils


class TestResult:
    __external_id: str = None
    __autotest_name: str = None
    __outcome: str = None
    __title: str = None
    __description: str = None
    __duration: int = None
    __started_on: str = None
    __completed_on: str = None
    __namespace: str = None
    __classname: str = None
    __message: str = None
    __traces: str = None
    __step_results: List[StepResult] = []
    __setup_results: List[StepResult] = []
    __teardown_results: List[StepResult] = []
    __links: List[Link] = []
    __result_links: List[Link] = []
    __attachments: List[str] = []
    __labels: List[str] = []
    __work_item_ids: List[str] = []
    __parameters: dict = {}
    __properties: dict = {}
    __automatic_creation_test_cases: bool = False
    __external_key: str = None

    @adapter_logger
    def set_external_id(self, external_id: str):
        # don't use escaping for externalId
        # self.__external_id = HtmlEscapeUtils.escape_html_tags(external_id)
        self.__external_id = external_id

        return self

    @adapter_logger
    def get_external_id(self) -> str:
        return self.__external_id

    @adapter_logger
    def set_autotest_name(self, autotest_name: str):
        self.__autotest_name = HtmlEscapeUtils.escape_html_tags(autotest_name)

        return self

    @adapter_logger
    def get_autotest_name(self) -> str:
        return self.__autotest_name

    @adapter_logger
    def set_outcome(self, outcome: str):
        self.__outcome = HtmlEscapeUtils.escape_html_tags(outcome)

        return self

    @adapter_logger
    def get_outcome(self) -> str:
        return self.__outcome

    @adapter_logger
    def set_title(self, title: str):
        self.__title = HtmlEscapeUtils.escape_html_tags(title)

        return self

    @adapter_logger
    def get_title(self) -> str:
        return self.__title

    @adapter_logger
    def set_description(self, description: str):
        self.__description = HtmlEscapeUtils.escape_html_tags(description)

        return self

    @adapter_logger
    def get_description(self) -> str:
        return self.__description

    @adapter_logger
    def set_duration(self, duration: int):
        self.__duration = duration

        return self

    @adapter_logger
    def get_duration(self) -> int:
        return self.__duration

    @adapter_logger
    def set_started_on(self, started_on: str):
        self.__started_on = started_on

        return self

    @adapter_logger
    def get_started_on(self) -> str:
        return self.__started_on

    @adapter_logger
    def set_completed_on(self, completed_on: str):
        self.__completed_on = completed_on

        return self

    @adapter_logger
    def get_completed_on(self) -> str:
        return self.__completed_on

    @adapter_logger
    def set_namespace(self, namespace: str):
        self.__namespace = HtmlEscapeUtils.escape_html_tags(namespace)

        return self

    @adapter_logger
    def get_namespace(self) -> str:
        return self.__namespace

    @adapter_logger
    def set_classname(self, classname: str):
        self.__classname = HtmlEscapeUtils.escape_html_tags(classname)

        return self

    @adapter_logger
    def get_classname(self) -> str:
        return self.__classname

    @adapter_logger
    def set_message(self, message: str):
        self.__message = HtmlEscapeUtils.escape_html_tags(message)

        return self

    @adapter_logger
    def get_message(self) -> str:
        return self.__message

    @adapter_logger
    def set_traces(self, traces: str):
        self.__traces = HtmlEscapeUtils.escape_html_tags(traces)

        return self

    @adapter_logger
    def get_traces(self) -> str:
        return self.__traces

    @adapter_logger
    def set_step_results(self, step_results: list):
        self.__step_results = step_results

        return self

    @adapter_logger
    def get_step_results(self) -> List[StepResult]:
        return self.__step_results

    @adapter_logger
    def set_setup_results(self, setup_results: list):
        self.__setup_results = setup_results

        return self

    @adapter_logger
    def get_setup_results(self) -> List[StepResult]:
        return self.__setup_results

    @adapter_logger
    def set_teardown_results(self, teardown_results: list):
        self.__teardown_results = teardown_results

        return self

    @adapter_logger
    def get_teardown_results(self) -> List[StepResult]:
        return self.__teardown_results

    @adapter_logger
    def set_links(self, links: list):
        self.__links = links

        return self

    @adapter_logger
    def get_links(self) -> list:
        return self.__links

    @adapter_logger
    def set_result_links(self, result_links: list):
        self.__result_links = result_links

        return self

    @adapter_logger
    def get_result_links(self) -> list:
        return self.__result_links

    @adapter_logger
    def set_attachments(self, attachments: list):
        self.__attachments = attachments

        return self

    @adapter_logger
    def get_attachments(self) -> list:
        return self.__attachments

    @adapter_logger
    def set_labels(self, labels: list):
        self.__labels = HtmlEscapeUtils.escape_html_in_object(labels)

        return self

    @adapter_logger
    def get_labels(self) -> list:
        return self.__labels

    @adapter_logger
    def set_work_item_ids(self, work_item_ids: list):
        self.__work_item_ids = work_item_ids

        return self

    @adapter_logger
    def get_work_item_ids(self) -> list:
        return self.__work_item_ids

    @adapter_logger
    def set_parameters(self, parameters: dict):
        self.__parameters = HtmlEscapeUtils.escape_html_in_object(parameters)

        return self

    @adapter_logger
    def get_parameters(self) -> dict:
        return self.__parameters

    @adapter_logger
    def set_properties(self, properties: dict):
        self.__properties = HtmlEscapeUtils.escape_html_in_object(properties)

        return self

    @adapter_logger
    def get_properties(self) -> dict:
        return self.__properties

    @adapter_logger
    def set_automatic_creation_test_cases(self, automatic_creation_test_cases: bool):
        self.__automatic_creation_test_cases = automatic_creation_test_cases

        return self

    @adapter_logger
    def get_automatic_creation_test_cases(self) -> bool:
        return self.__automatic_creation_test_cases

    @adapter_logger
    def set_external_key(self, external_key: str):
        self.__external_key = external_key

        return self

    @adapter_logger
    def get_external_key(self) -> str:
        return self.__external_key
