from testit_api_client.models import (
    AutoTestPostModel,
    AutoTestPutModel,
    LinkPostModel,
    LinkPutModel,
    LinkType,
    AutoTestResultsForTestRunModel,
    AttachmentPutModelAutoTestStepResultsModel)


class Converter:

    @classmethod
    def test_result_to_autotest_post_model(
            cls,
            test_result: dict,
            project_id: str):
        return AutoTestPostModel(
            test_result['externalID'],
            project_id,
            test_result['autoTestName'],
            steps=test_result['steps'],
            setup=test_result['setUp'],
            teardown=test_result['tearDown'],
            namespace=test_result['namespace'],
            classname=test_result['classname'],
            title=test_result['title'],
            description=test_result['description'],
            links=cls.links_to_links_post_model(test_result['links']),
            labels=test_result['labels']
        )

    @classmethod
    def test_result_to_autotest_put_model(
            cls,
            test_result: dict,
            project_id: str):
        if test_result['outcome'] == 'Passed':
            return AutoTestPutModel(
                test_result['externalID'],
                project_id,
                test_result['autoTestName'],
                steps=test_result['steps'],
                setup=test_result['setUp'],
                teardown=test_result['tearDown'],
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
                steps=test_result['steps'],
                setup=test_result['setUp'],
                teardown=test_result['tearDown'],
                namespace=test_result['namespace'],
                classname=test_result['classname'],
                title=test_result['title'],
                description=test_result['description'],
                links=cls.links_to_links_put_model(test_result['links']),
                labels=test_result['labels']
            )

    @classmethod
    def test_result_to_testrun_result_post_model(
            cls,
            test_result: dict,
            configuration_id: str):
        return AutoTestResultsForTestRunModel(
            configuration_id,
            test_result['externalID'],
            test_result['outcome'],
            step_results=test_result['stepResults'],
            setup_results=test_result['setUpResults'],
            teardown_results=test_result['tearDownResults'],
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
    def links_to_links_post_model(cls, links: list):
        post_model_links = []

        for link in links:
            post_model_links.append(cls.link_to_link_post_model(
                link['url'],
                link['title'],
                link['type'],
                link['description']
            ))

        return post_model_links

    @classmethod
    def links_to_links_put_model(cls, links: list):
        put_model_links = []

        for link in links:
            put_model_links.append(cls.link_to_link_put_model(
                link['url'],
                link['title'],
                link['type'],
                link['description']
            ))

        return put_model_links

    @staticmethod
    def step_result_to_attachment_put_model_autotest_step_results_model(
            title: str,
            description: str,
            outcome: str,
            duration: str,
            parameters,
            attachments,
            started_on=None,
            completed_on=None):
        return AttachmentPutModelAutoTestStepResultsModel(
            title=title,
            description=description,
            duration=duration,
            outcome=outcome,
            parameters=parameters,
            attachments=attachments,
            started_on=started_on,
            completed_on=completed_on
        )
