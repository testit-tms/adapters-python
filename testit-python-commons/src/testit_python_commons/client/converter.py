import typing

from testit_api_client.models import (
    AttachmentPutModelAutoTestStepResultsModel,
    AutoTestPostModel,
    AutoTestPutModel,
    AutoTestResultsForTestRunModel,
    AutoTestStepModel,
    AvailableTestResultOutcome,
    LinkPostModel,
    LinkPutModel,
    LinkType,
    TestRunV2PostShortModel
)

from testit_python_commons.models.link import Link
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.services.logger import adapter_logger


class Converter:
    @classmethod
    @adapter_logger
    def test_run_to_test_run_short_model(cls, project_id, name):
        return TestRunV2PostShortModel(
            project_id=project_id,
            name=name
        )

    @classmethod
    @adapter_logger
    def get_id_from_create_test_run_response(cls, response):
        return response['id']

    @classmethod
    @adapter_logger
    def get_resolved_autotests_from_get_test_run_response(cls, response, configuration: str):
        autotests = response['_data_store']['test_results']

        return cls.__get_resolved_autotests(autotests, configuration)

    @staticmethod
    @adapter_logger
    def __get_resolved_autotests(autotests: list, configuration: str):
        resolved_autotests = []

        for autotest in autotests:
            if configuration == autotest['_data_store']['configuration_id']:
                resolved_autotests.append(autotest._data_store['auto_test']._data_store['external_id'])

        return resolved_autotests

    @classmethod
    @adapter_logger
    def test_result_to_autotest_post_model(
            cls,
            test_result: TestResult,
            project_id: str):
        return AutoTestPostModel(
            test_result.get_external_id(),
            project_id,
            test_result.get_autotest_name(),
            steps=cls.step_results_to_autotest_steps_model(
                test_result.get_step_results()),
            setup=cls.step_results_to_autotest_steps_model(
                test_result.get_setup_results()),
            teardown=cls.step_results_to_autotest_steps_model(
                test_result.get_teardown_results()),
            namespace=test_result.get_namespace(),
            classname=test_result.get_classname(),
            title=test_result.get_title(),
            description=test_result.get_description(),
            links=cls.links_to_links_post_model(test_result.get_links()),
            labels=test_result.get_labels(),
            should_create_work_item=test_result.get_automatic_creation_test_cases()
        )

    @classmethod
    @adapter_logger
    def test_result_to_autotest_put_model(
            cls,
            test_result: TestResult,
            project_id: str):
        if test_result.get_outcome() == 'Passed':
            return AutoTestPutModel(
                test_result.get_external_id(),
                project_id,
                test_result.get_autotest_name(),
                steps=cls.step_results_to_autotest_steps_model(
                    test_result.get_step_results()),
                setup=cls.step_results_to_autotest_steps_model(
                    test_result.get_setup_results()),
                teardown=cls.step_results_to_autotest_steps_model(
                    test_result.get_teardown_results()),
                namespace=test_result.get_namespace(),
                classname=test_result.get_classname(),
                title=test_result.get_title(),
                description=test_result.get_description(),
                links=cls.links_to_links_put_model(test_result.get_links()),
                labels=test_result.get_labels()
            )
        else:
            return AutoTestPutModel(
                test_result.get_external_id(),
                project_id,
                test_result.get_autotest_name(),
                steps=cls.step_results_to_autotest_steps_model(
                    test_result.get_step_results()),
                setup=cls.step_results_to_autotest_steps_model(
                    test_result.get_setup_results()),
                teardown=cls.step_results_to_autotest_steps_model(
                    test_result.get_teardown_results()),
                namespace=test_result.get_namespace(),
                classname=test_result.get_classname(),
                title=test_result.get_title(),
                description=test_result.get_description(),
                links=cls.links_to_links_put_model(test_result.get_links()),
                labels=test_result.get_labels()
            )

    @classmethod
    @adapter_logger
    def test_result_to_testrun_result_post_model(
            cls,
            test_result: TestResult,
            configuration_id: str):
        return AutoTestResultsForTestRunModel(
            configuration_id,
            test_result.get_external_id(),
            AvailableTestResultOutcome(test_result.get_outcome()),
            step_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result.get_step_results()),
            setup_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result.get_setup_results()),
            teardown_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result.get_teardown_results()),
            traces=test_result.get_traces(),
            attachments=test_result.get_attachments(),
            parameters=test_result.get_parameters(),
            properties=test_result.get_properties(),
            links=cls.links_to_links_post_model(
                test_result.get_result_links()),
            duration=round(test_result.get_duration()),
            message=test_result.get_message(),
            started_on=test_result.get_started_on(),
            completed_on=test_result.get_completed_on()
        )

    @staticmethod
    @adapter_logger
    def link_to_link_post_model(link: Link) -> LinkPostModel:
        if link.get_link_type():
            return LinkPostModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description()
            )
        else:
            return LinkPostModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description()
            )

    @staticmethod
    @adapter_logger
    def link_to_link_put_model(link: Link) -> LinkPutModel:
        if link.get_link_type():
            return LinkPutModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description()
            )
        else:
            return LinkPutModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description()
            )

    @classmethod
    @adapter_logger
    def links_to_links_post_model(cls, links: typing.List[Link]):
        post_model_links = []

        for link in links:
            post_model_links.append(
                cls.link_to_link_post_model(link)
            )

        return post_model_links

    @classmethod
    @adapter_logger
    def links_to_links_put_model(cls, links: typing.List[Link]):
        put_model_links = []

        for link in links:
            put_model_links.append(
                cls.link_to_link_put_model(link)
            )

        return put_model_links

    @classmethod
    # @adapter_logger
    def step_results_to_autotest_steps_model(cls, step_results: typing.List[StepResult]):
        autotest_model_steps = []

        for step_result in step_results:
            autotest_model_steps.append(
                AutoTestStepModel(
                    title=step_result.get_title(),
                    description=step_result.get_description(),
                    steps=cls.step_results_to_autotest_steps_model(
                        step_result.get_step_results()))
            )

        return autotest_model_steps

    @classmethod
    @adapter_logger
    def step_results_to_attachment_put_model_autotest_step_results_model(cls, step_results: typing.List[StepResult]):
        autotest_model_step_results = []

        for step_result in step_results:
            autotest_model_step_results.append(
                AttachmentPutModelAutoTestStepResultsModel(
                    title=step_result.get_title(),
                    outcome=AvailableTestResultOutcome(step_result.get_outcome()),
                    description=step_result.get_description(),
                    duration=step_result.get_duration(),
                    parameters=step_result.get_parameters(),
                    attachments=step_result.get_attachments(),
                    started_on=step_result.get_started_on(),
                    completed_on=step_result.get_completed_on(),
                    step_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                        step_result.get_step_results())
                )
            )

        return autotest_model_step_results
