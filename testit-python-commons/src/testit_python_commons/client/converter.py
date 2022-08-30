from testit_api_client import JSONFixture


class Converter:

    @staticmethod
    def test_result_to_autotest_post_model(
            test_result: dict,
            project_id: str):
        return JSONFixture.create_autotest(
            test_result['externalID'],
            project_id,
            test_result['autoTestName'],
            test_result['steps'],
            test_result['setUp'],
            test_result['tearDown'],
            test_result['namespace'],
            test_result['classname'],
            test_result['title'],
            test_result['description'],
            test_result['links'],
            test_result['labels'])

    @staticmethod
    def test_result_to_autotest_put_model(
            autotest: dict,
            test_result: dict,
            project_id: str):
        if test_result['testResult'] == 'Passed':
            return JSONFixture.update_autotest(
                test_result['externalID'],
                project_id,
                test_result['autoTestName'],
                autotest['id'],
                test_result['steps'],
                test_result['setUp'],
                test_result['tearDown'],
                test_result['namespace'],
                test_result['classname'],
                test_result['title'],
                test_result['description'],
                test_result['links'],
                test_result['labels'])
        else:
            return JSONFixture.update_autotest(
                test_result['externalID'],
                project_id,
                autotest['name'],
                autotest['id'],
                autotest['steps'],
                autotest['setup'],
                autotest['teardown'],
                autotest['namespace'],
                autotest['classname'],
                autotest['title'],
                autotest['description'],
                test_result['links'],
                autotest['labels'])

    @staticmethod
    def test_result_to_testrun_result_post_model(
            test_result: dict,
            configuration_id: str):
        return [JSONFixture.set_results_for_testrun(
            test_result['externalID'],
            configuration_id,
            'Failed' if test_result['traces'] else 'Passed',
            test_result['stepResults'],
            test_result['setUpResults'],
            test_result['tearDownResults'],
            test_result['traces'],
            test_result['attachments'],
            test_result['parameters'],
            test_result['properties'],
            test_result['resultLinks'],
            test_result['duration'],
            test_result['failureReasonName'],
            test_result['message'])]
