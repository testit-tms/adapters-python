import logging
from typing import List

from testit_api_client.models import (
    ApiV2TestResultsSearchPostRequest,
    AutoTestApiResult,
    AttachmentPutModelAutoTestStepResultsModel,
    AutoTestStepResultUpdateRequest,
    CreateAutoTestRequest,
    UpdateAutoTestRequest,
    AutoTestCreateApiModel,
    AutoTestUpdateApiModel,
    AutoTestResultsForTestRunModel,
    AutoTestStepApiModel,
    AvailableTestResultOutcome,
    LinkPostModel,
    LinkCreateApiModel,
    LinkUpdateApiModel,
    LinkType,
    CreateEmptyRequest,
    TestRunV2ApiResult,
    TestResultShortResponse,
    AutoTestSearchApiModelFilter,
    AutoTestSearchApiModelIncludes,
    ApiV2AutoTestsSearchPostRequest,
    ApiV2TestResultsIdPutRequest,
    TestResultResponse,
    AttachmentApiResult,
    AttachmentUpdateRequest,
    UpdateEmptyRequest,
    LinkApiResult,
    UpdateLinkApiModel,
    AssignAttachmentApiModel,
)

from testit_python_commons.models.link import Link
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import TestResultWithAllFixtureStepResults
from testit_python_commons.services.logger import adapter_logger


class Converter:
    @staticmethod
    @adapter_logger
    def test_run_to_test_run_short_model(project_id: str, name: str) -> CreateEmptyRequest:
        return CreateEmptyRequest(
            project_id=project_id,
            name=name
        )

    @staticmethod
    @adapter_logger
    def get_id_from_create_test_run_response(response: TestRunV2ApiResult) -> str:
        return response.id

    @classmethod
    @adapter_logger
    def build_update_empty_request(cls, test_run: TestRunV2ApiResult) -> UpdateEmptyRequest:
        return UpdateEmptyRequest(
            id=test_run.id,
            name=test_run.name,
            description=test_run.description,
            launch_source=test_run.launch_source,
            attachments=list(map(cls.build_assign_attachment_api_model, test_run.attachments)),
            links=list(map(cls.build_update_link_api_model, test_run.links))
        )

    @staticmethod
    @adapter_logger
    def build_update_link_api_model(link: LinkApiResult) -> UpdateLinkApiModel:
        return UpdateLinkApiModel(
            id=link.id,
            title=link.title,
            description=link.description,
            type=link.type,
            url=link.url,
            has_info=link.has_info
        )

    @staticmethod
    @adapter_logger
    def build_assign_attachment_api_model(attachment: AttachmentApiResult) -> AssignAttachmentApiModel:
        return AssignAttachmentApiModel(id=attachment.id)

    @staticmethod
    @adapter_logger
    def project_id_and_external_id_to_auto_tests_search_post_request(
            project_id: str,
            external_id: str
    ) -> ApiV2AutoTestsSearchPostRequest:
        autotests_filter = AutoTestSearchApiModelFilter(
            project_ids=[project_id],
            external_ids=[external_id],
            is_deleted=False)
        autotests_includes = AutoTestSearchApiModelIncludes(
            include_steps=False,
            include_links=False,
            include_labels=False)

        return ApiV2AutoTestsSearchPostRequest(filter=autotests_filter, includes=autotests_includes)

    @staticmethod
    @adapter_logger
    def build_test_results_search_post_request_with_in_progress_outcome(
            testrun_id: str,
            configuration_id: str) -> ApiV2TestResultsSearchPostRequest:
        return ApiV2TestResultsSearchPostRequest(
            test_run_ids=[testrun_id],
            configuration_ids=[configuration_id],
            status_codes=["InProgress"])

    @staticmethod
    @adapter_logger
    def autotest_ids_to_autotests_search_post_request(
            autotest_ids: List[int]) -> ApiV2AutoTestsSearchPostRequest:
        autotests_filter = AutoTestSearchApiModelFilter(
            global_ids=autotest_ids)
        autotests_includes = AutoTestSearchApiModelIncludes(
            include_steps=False,
            include_links=False,
            include_labels=False)

        return ApiV2AutoTestsSearchPostRequest(filter=autotests_filter, includes=autotests_includes)

    @staticmethod
    @adapter_logger
    def get_external_ids_from_autotest_response_list(
            autotests: List[TestResultShortResponse],
            configuration: str) -> List[str]:
        external_ids: List[str] = []

        for autotest in autotests:
            if configuration == autotest.configuration_id:
                external_ids.append(autotest.autotest_external_id)

        return external_ids

    @classmethod
    @adapter_logger
    def test_result_to_autotest_post_model(
            cls,
            test_result: TestResult,
            project_id: str) -> AutoTestCreateApiModel:
        return AutoTestCreateApiModel(
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
            links=cls.links_to_links_create_api_model(test_result.get_links()),
            labels=test_result.get_labels(),
            should_create_work_item=test_result.get_automatic_creation_test_cases(),
            external_key=test_result.get_external_key()
        )

    @classmethod
    @adapter_logger
    def test_result_to_create_autotest_request(
            cls,
            test_result: TestResult,
            project_id: str) -> CreateAutoTestRequest:
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
            links=cls.links_to_links_create_api_model(test_result.get_links()),
            labels=test_result.get_labels(),
            should_create_work_item=test_result.get_automatic_creation_test_cases(),
            external_key=test_result.get_external_key()
        )

    @classmethod
    @adapter_logger
    def test_result_to_autotest_put_model(
            cls,
            test_result: TestResult,
            project_id: str) -> AutoTestUpdateApiModel:
        if test_result.get_outcome() == 'Passed':
            return AutoTestUpdateApiModel(
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
                labels=test_result.get_labels(),
                external_key=test_result.get_external_key()
            )
        else:
            return AutoTestUpdateApiModel(
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
                labels=test_result.get_labels(),
                external_key=test_result.get_external_key()
            )

    @classmethod
    @adapter_logger
    def test_result_to_update_autotest_request(
            cls,
            test_result: TestResult,
            project_id: str) -> UpdateAutoTestRequest:
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
                labels=test_result.get_labels(),
                external_key=test_result.get_external_key()
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
                labels=test_result.get_labels(),
                external_key=test_result.get_external_key()
            )

    @classmethod
    @adapter_logger
    def test_result_to_testrun_result_post_model(
            cls,
            test_result: TestResult,
            configuration_id: str) -> AutoTestResultsForTestRunModel:
        return AutoTestResultsForTestRunModel(
            configuration_id=configuration_id,
            auto_test_external_id=test_result.get_external_id(),
            status_code=test_result.get_outcome(),
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
            test_result: TestResultResponse) -> ApiV2TestResultsIdPutRequest:
        return ApiV2TestResultsIdPutRequest(
            failure_class_ids=test_result.failure_class_ids,
            status_code=test_result.status.code,
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
    def link_to_link_create_api_model(link: Link) -> LinkCreateApiModel:
        if link.get_link_type():
            return LinkCreateApiModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description(),
                has_info=True,
            )
        else:
            return LinkCreateApiModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description(),
                has_info=True,
            )

    @staticmethod
    @adapter_logger
    def link_to_link_put_model(link: Link) -> LinkUpdateApiModel:
        if link.get_link_type():
            return LinkUpdateApiModel(
                url=link.get_url(),
                title=link.get_title(),
                type=LinkType(link.get_link_type()),
                description=link.get_description(),
                has_info=True,
            )
        else:
            return LinkUpdateApiModel(
                url=link.get_url(),
                title=link.get_title(),
                description=link.get_description(),
                has_info=True,
            )

    @classmethod
    @adapter_logger
    def links_to_links_post_model(cls, links: List[Link]) -> List[LinkPostModel]:
        post_model_links = []

        for link in links:
            post_model_links.append(
                cls.link_to_link_post_model(link)
            )

        return post_model_links

    @classmethod
    @adapter_logger
    def links_to_links_create_api_model(cls, links: List[Link]) -> List[LinkCreateApiModel]:
        create_api_model_links = []

        for link in links:
            create_api_model_links.append(
                cls.link_to_link_create_api_model(link)
            )

        return create_api_model_links

    @classmethod
    @adapter_logger
    def links_to_links_put_model(cls, links: List[Link]) -> List[LinkUpdateApiModel]:
        put_model_links = []

        for link in links:
            put_model_links.append(
                cls.link_to_link_put_model(link)
            )

        return put_model_links

    @classmethod
    @adapter_logger
    def attachment_models_to_attachment_put_models(
            cls, attachments: List[AttachmentApiResult]) -> List[AttachmentUpdateRequest]:
        put_model_attachments = []

        for attachment in attachments:
            put_model_attachments.append(
                cls.attachment_model_to_attachment_put_model(attachment)
            )

        return put_model_attachments

    @staticmethod
    @adapter_logger
    def attachment_model_to_attachment_put_model(attachment: AttachmentApiResult) -> AttachmentUpdateRequest:
        return AttachmentUpdateRequest(id=attachment.id)

    @classmethod
    # @adapter_logger
    def step_results_to_autotest_steps_model(
            cls, step_results: List[StepResult]) -> List[AutoTestStepApiModel]:
        autotest_model_steps = []

        for step_result in step_results:
            autotest_model_steps.append(
                AutoTestStepApiModel(
                    title=step_result.get_title(),
                    description=step_result.get_description(),
                    steps=cls.step_results_to_autotest_steps_model(
                        step_result.get_step_results()))
            )

        return autotest_model_steps

    @classmethod
    @adapter_logger
    def step_results_to_attachment_put_model_autotest_step_results_model(
            cls, step_results: List[StepResult]) -> List[AttachmentPutModelAutoTestStepResultsModel]:
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

    @staticmethod
    @adapter_logger
    def fixtures_containers_to_test_results_with_all_fixture_step_results(
            fixtures_containers: dict,
            test_result_ids: dict) -> List[TestResultWithAllFixtureStepResults]:
        test_results_with_all_fixture_step_results = []

        for external_id, test_result_id in test_result_ids.items():
            test_result_with_all_fixture_step_results = TestResultWithAllFixtureStepResults(test_result_id)

            for uuid, fixtures_container in fixtures_containers.items():
                if external_id in fixtures_container.external_ids:
                    if fixtures_container.befores:
                        test_result_with_all_fixture_step_results.set_setup_results(fixtures_container.befores[0].steps)

                    if fixtures_container.afters:
                        test_result_with_all_fixture_step_results.set_teardown_results(
                            fixtures_container.afters[0].steps)

            test_results_with_all_fixture_step_results.append(test_result_with_all_fixture_step_results)

        return test_results_with_all_fixture_step_results

    @classmethod
    @adapter_logger
    def step_results_to_auto_test_step_result_update_request(
            cls, step_results: List[StepResult]) -> List[AutoTestStepResultUpdateRequest]:
        autotest_model_step_results = []

        for step_result in step_results:
            autotest_model_step_results.append(
                AutoTestStepResultUpdateRequest(
                    title=step_result.get_title(),
                    outcome=AvailableTestResultOutcome(step_result.get_outcome()),
                    description=step_result.get_description(),
                    duration=step_result.get_duration(),
                    parameters=step_result.get_parameters(),
                    attachments=step_result.get_attachments(),
                    started_on=step_result.get_started_on(),
                    completed_on=step_result.get_completed_on(),
                    step_results=cls.step_results_to_auto_test_step_result_update_request(
                        step_result.get_step_results())
                )
            )

        return autotest_model_step_results

    @classmethod
    @adapter_logger
    def prepare_to_create_autotest(
            cls,
            test_result: TestResult,
            project_id: str,
            work_item_ids_for_link_with_auto_test: list) -> CreateAutoTestRequest:
        logging.debug('Preparing to create the auto test ' + test_result.get_external_id())

        model = cls.test_result_to_create_autotest_request(
            test_result,
            project_id)
        model.work_item_ids_for_link_with_auto_test = work_item_ids_for_link_with_auto_test

        return model

    @classmethod
    @adapter_logger
    def prepare_to_mass_create_autotest(
            cls,
            test_result: TestResult,
            project_id: str,
            work_item_ids_for_link_with_auto_test: list) -> AutoTestCreateApiModel:
        logging.debug('Preparing to create the auto test ' + test_result.get_external_id())

        model = cls.test_result_to_autotest_post_model(
            test_result,
            project_id)
        model.work_item_ids_for_link_with_auto_test = work_item_ids_for_link_with_auto_test

        return model

    @classmethod
    @adapter_logger
    def prepare_to_update_autotest(
            cls,
            test_result: TestResult,
            autotest: AutoTestApiResult,
            project_id: str) -> UpdateAutoTestRequest:
        logging.debug('Preparing to update the auto test ' + test_result.get_external_id())

        model = cls.test_result_to_update_autotest_request(
            test_result,
            project_id)
        model.is_flaky = autotest.is_flaky
        # TODO: return after fix PUT/api/v2/autoTests
        # model.work_item_ids_for_link_with_auto_test = self.__get_work_item_uuids_for_link_with_auto_test(
        #     test_result.get_work_item_ids(),
        #     str(autotest.global_id))

        return model

    @classmethod
    @adapter_logger
    def prepare_to_mass_update_autotest(
            cls,
            test_result: TestResult,
            autotest: AutoTestApiResult,
            project_id: str) -> AutoTestUpdateApiModel:
        logging.debug('Preparing to update the auto test ' + test_result.get_external_id())

        model = cls.test_result_to_autotest_put_model(
            test_result,
            project_id)
        model.is_flaky = autotest.is_flaky
        # TODO: return after fix PUT/api/v2/autoTests
        # model.work_item_ids_for_link_with_auto_test = self.__get_work_item_uuids_for_link_with_auto_test(
        #     test_result.get_work_item_ids(),
        #     str(autotest.global_id))

        return model
