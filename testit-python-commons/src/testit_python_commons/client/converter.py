import typing

from testit_api_client.models import (
    AttachmentPutModelAutoTestStepResultsModel,
    CreateAutoTestRequest,
    UpdateAutoTestRequest,
    AutoTestResultsForTestRunModel,
    AutoTestStepModel,
    AvailableTestResultOutcome,
    LinkPostModel,
    LinkPutModel,
    LinkType,
    CreateEmptyRequest,
    AutotestsSelectModelFilter,
    AutotestsSelectModelIncludes,
    ApiV2AutoTestsSearchPostRequest,
    ApiV2TestResultsIdPutRequest,
    TestResultModel,
    AttachmentModel,
    AttachmentPutModel
)

from testit_python_commons.models.link import Link
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import TestResultWithAllFixtureStepResults
from testit_python_commons.services.logger import adapter_logger


class Converter:
    @classmethod
    @adapter_logger
    def test_run_to_test_run_short_model(cls, project_id, name):
        return CreateEmptyRequest(
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

    @classmethod
    @adapter_logger
    def project_id_and_external_id_to_auto_tests_search_post_request(cls, project_id: str, external_id: str):
        autotests_filter = AutotestsSelectModelFilter(
            project_ids=[project_id],
            external_ids=[external_id],
            is_deleted=False)
        autotests_includes = AutotestsSelectModelIncludes(
            include_steps=False,
            include_links=False,
            include_labels=False)

        return ApiV2AutoTestsSearchPostRequest(filter=autotests_filter, includes=autotests_includes)

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
        return CreateAutoTestRequest(
            external_id=test_result.get_external_id(),
            project_id=project_id,
            name=test_result.get_autotest_name(),
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
            return UpdateAutoTestRequest(
                external_id=test_result.get_external_id(),
                project_id=project_id,
                name=test_result.get_autotest_name(),
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
            return UpdateAutoTestRequest(
                external_id=test_result.get_external_id(),
                project_id=project_id,
                name=test_result.get_autotest_name(),
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
            configuration_id=configuration_id,
            auto_test_external_id=test_result.get_external_id(),
            outcome=AvailableTestResultOutcome(test_result.get_outcome()),
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

    @classmethod
    @adapter_logger
    def convert_test_result_model_to_test_results_id_put_request(
            cls,
            test_result: TestResultModel) -> ApiV2TestResultsIdPutRequest:
        return ApiV2TestResultsIdPutRequest(
            failure_class_ids=test_result.failure_class_ids,
            outcome=test_result.outcome,
            comment=test_result.comment,
            links=test_result.links,
            step_results=test_result.step_results,
            attachments=cls.attachment_models_to_attachment_put_models(test_result.attachments),
            duration_in_ms=test_result.duration_in_ms,
            step_comments=test_result.step_comments,
            # setup_results=test_result.setup_results,
            # teardown_results=test_result.teardown_results,
            message=test_result.message,
            trace=test_result.traces)

    @classmethod
    @adapter_logger
    def convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request(
            cls,
            test_result: TestResultWithAllFixtureStepResults) -> ApiV2TestResultsIdPutRequest:
        return ApiV2TestResultsIdPutRequest(
            setup_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result.get_setup_results()),
            teardown_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result.get_teardown_results()))

    @classmethod
    @adapter_logger
    def get_test_result_id_from_testrun_result_post_response(cls, response) -> str:
        return response[0]

    @staticmethod
    @adapter_logger
    def link_to_link_post_model(link: Link) -> LinkPostModel:
        if link.get_link_type():
            return LinkPostModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description(),
                has_info=True,
            )
        else:
            return LinkPostModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description(),
                has_info=True,
            )

    @staticmethod
    @adapter_logger
    def link_to_link_put_model(link: Link) -> LinkPutModel:
        if link.get_link_type():
            return LinkPutModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description(),
                has_info=True,
            )
        else:
            return LinkPutModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description(),
                has_info=True,
            )

    @classmethod
    @adapter_logger
    def links_to_links_post_model(cls, links: typing.List[Link]) -> typing.List[LinkPostModel]:
        post_model_links = []

        for link in links:
            post_model_links.append(
                cls.link_to_link_post_model(link)
            )

        return post_model_links

    @classmethod
    @adapter_logger
    def links_to_links_put_model(cls, links: typing.List[Link]) -> typing.List[LinkPutModel]:
        put_model_links = []

        for link in links:
            put_model_links.append(
                cls.link_to_link_put_model(link)
            )

        return put_model_links

    @classmethod
    @adapter_logger
    def attachment_models_to_attachment_put_models(
            cls, attachments: typing.List[AttachmentModel]) -> typing.List[AttachmentPutModel]:
        put_model_attachments = []

        for attachment in attachments:
            put_model_attachments.append(
                cls.attachment_model_to_attachment_put_model(attachment)
            )

        return put_model_attachments

    @staticmethod
    @adapter_logger
    def attachment_model_to_attachment_put_model(attachment: AttachmentModel) -> AttachmentPutModel:
        return AttachmentPutModel(id=attachment.id)

    @classmethod
    # @adapter_logger
    def step_results_to_autotest_steps_model(
            cls, step_results: typing.List[StepResult]) -> typing.List[AutoTestStepModel]:
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
    def step_results_to_attachment_put_model_autotest_step_results_model(
            cls, step_results: typing.List[StepResult]) -> typing.List[AttachmentPutModelAutoTestStepResultsModel]:
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
