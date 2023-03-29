from testit_api_client.models import (
    AutoTestStepModel,
    AvailableTestResultOutcome,
    AttachmentPutModelAutoTestStepResultsModel,
    AutoTestPostModel,
    AutoTestPutModel,
    AutoTestResultsForTestRunModel,
    LinkPostModel,
    LinkPutModel,
    LinkType,
    TestRunV2PostShortModel
)
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
            test_result: dict,
            project_id: str):
        return AutoTestPostModel(
            test_result['externalID'],
            project_id,
            test_result['autoTestName'],
            steps=cls.step_results_to_autotest_steps_model(test_result['steps']),
            setup=cls.step_results_to_autotest_steps_model(test_result['setUp']),
            teardown=cls.step_results_to_autotest_steps_model(test_result['tearDown']),
            namespace=test_result['namespace'],
            classname=test_result['classname'],
            title=test_result['title'],
            description=test_result['description'],
            links=cls.links_to_links_post_model(test_result['links']),
            labels=test_result['labels'],
            should_create_work_item=test_result['automaticCreationTestCases']
        )

    @classmethod
    @adapter_logger
    def test_result_to_autotest_put_model(
            cls,
            test_result: dict,
            project_id: str):
        if test_result['outcome'] == 'Passed':
            return AutoTestPutModel(
                test_result['externalID'],
                project_id,
                test_result['autoTestName'],
                steps=cls.step_results_to_autotest_steps_model(test_result['steps']),
                setup=cls.step_results_to_autotest_steps_model(test_result['setUp']),
                teardown=cls.step_results_to_autotest_steps_model(test_result['tearDown']),
                namespace=test_result['namespace'],
                classname=test_result['classname'],
                title=test_result['title'],
                description=test_result['description'],
                links=cls.links_to_links_put_model(test_result['links']),
                labels=test_result['labels']
            )
        else:
            return AutoTestPutModel(
                test_result['externalID'],
                project_id,
                test_result['autoTestName'],
                steps=cls.step_results_to_autotest_steps_model(test_result['steps']),
                setup=cls.step_results_to_autotest_steps_model(test_result['setUp']),
                teardown=cls.step_results_to_autotest_steps_model(test_result['tearDown']),
                namespace=test_result['namespace'],
                classname=test_result['classname'],
                title=test_result['title'],
                description=test_result['description'],
                links=cls.links_to_links_put_model(test_result['links']),
                labels=test_result['labels']
            )

    @classmethod
    @adapter_logger
    def test_result_to_testrun_result_post_model(
            cls,
            test_result: dict,
            configuration_id: str):
        return AutoTestResultsForTestRunModel(
            configuration_id,
            test_result['externalID'],
            AvailableTestResultOutcome(test_result['outcome']),
            step_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result['stepResults']),
            setup_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result['setUpResults']),
            teardown_results=cls.step_results_to_attachment_put_model_autotest_step_results_model(
                test_result['tearDownResults']),
            traces=test_result['traces'],
            attachments=test_result['attachments'],
            parameters=test_result['parameters'],
            properties=test_result['properties'],
            links=cls.links_to_links_post_model(test_result['resultLinks']),
            duration=round(test_result['duration']),
            message=test_result['message'],
            started_on=test_result.get('started_on', None),
            completed_on=test_result.get('completed_on', None)
        )

    @staticmethod
    @adapter_logger
    def link_to_link_post_model(
            url: str,
            title: str,
            url_type: str,
            description: str):
        if url_type:
            return LinkPostModel(
                url,
                title=title,
                type=LinkType(value=url_type),
                description=description
            )
        else:
            return LinkPostModel(
                url,
                title=title,
                description=description
            )

    @staticmethod
    @adapter_logger
    def link_to_link_put_model(
            url: str,
            title: str,
            url_type: str,
            description: str):
        if url_type:
            return LinkPutModel(
                url,
                title=title,
                type=LinkType(value=url_type),
                description=description
            )
        else:
            return LinkPutModel(
                url,
                title=title,
                description=description
            )

    @classmethod
    @adapter_logger
    def links_to_links_post_model(cls, links: list):
        post_model_links = []

        for link in links:
            post_model_links.append(cls.link_to_link_post_model(
                link['url'],
                link.get('title', None),
                link.get('type', None),
                link.get('description', None)
            ))

        return post_model_links

    @classmethod
    @adapter_logger
    def links_to_links_put_model(cls, links: list):
        put_model_links = []

        for link in links:
            put_model_links.append(cls.link_to_link_put_model(
                link['url'],
                link.get('title', None),
                link.get('type', None),
                link.get('description', None)
            ))

        return put_model_links

    @classmethod
    @adapter_logger
    def step_results_to_autotest_steps_model(cls, steps: list):
        autotest_model_steps = []

        for step in steps:
            autotest_model_steps.append(
                cls.step_result_to_autotest_step_model(
                    step['title'],
                    step['description'],
                    cls.step_results_to_autotest_steps_model(
                        step.get('steps', [])
                    )
                )
            )

        return autotest_model_steps

    @staticmethod
    @adapter_logger
    def step_result_to_autotest_step_model(
            title: str,
            description: str = None,
            steps: list = None):
        return AutoTestStepModel(
            title=title,
            description=description,
            steps=steps)

    @classmethod
    @adapter_logger
    def step_results_to_attachment_put_model_autotest_step_results_model(cls, steps: list):
        autotest_model_step_results = []

        for step in steps:
            autotest_model_step_results.append(
                cls.step_result_to_attachment_put_model_autotest_step_results_model(
                    step['title'],
                    step['outcome'],
                    step['description'],
                    step['duration'],
                    step['parameters'],
                    step['attachments'],
                    None,
                    None,
                    cls.step_results_to_attachment_put_model_autotest_step_results_model(
                        step.get('step_results', [])
                    )
                )
            )

        return autotest_model_step_results

    @staticmethod
    @adapter_logger
    def step_result_to_attachment_put_model_autotest_step_results_model(
            title: str,
            outcome: str,
            description: str = None,
            duration: str = None,
            parameters: list = None,
            attachments: list = None,
            started_on: str = None,
            completed_on: str = None,
            step_results: list = None
            ):
        return AttachmentPutModelAutoTestStepResultsModel(
            title=title,
            outcome=AvailableTestResultOutcome(outcome),
            description=description,
            duration=duration,
            parameters=parameters,
            attachments=attachments,
            started_on=started_on,
            completed_on=completed_on,
            step_results=step_results
        )
