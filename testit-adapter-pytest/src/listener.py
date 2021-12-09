import configparser
import inspect
import os
import pickle
from datetime import datetime

import pytest
import testit_adapter_pytest
from testit_api_client.api import Api
from testit_api_client.json_fixture import JSONFixture
from testit_adapter_pytest.utils import (
    autotests_parser,
    search_in_environ,
    step,
    url_check,
    uuid_check
)


class TestITListener(object):
    # TODO: need to rework for normal read
    def __init__(self, testrun, url, private_token, configuration, proxy=None):
        if testrun:
            self.testrun_id = uuid_check(testrun)

            if not url:
                print('URL was not found!')
                raise SystemExit

            url_check(url)

            if not private_token:
                print('Private token was not found!')
                raise SystemExit

            if not configuration:
                print('Configuration ID was not found!')
                raise SystemExit

            self.configuration_id = uuid_check(configuration)
        else:
            path = os.path.abspath('')
            root = path[:path.index(os.sep)]
            while not os.path.isfile(
                    f'{path}{os.sep}connection_config.ini') and path != root:
                path = path[:path.rindex(os.sep)]
            path = f'{path}{os.sep}connection_config.ini'
            if not os.path.isfile(path):
                print('File connection_config.ini was not found!')
                raise SystemExit
            parser = configparser.RawConfigParser()
            parser.read(path)

            url = url_check(search_in_environ(parser.get('testit',
                                                         'url')))

            private_token = search_in_environ(parser.get('testit',
                                                         'privatetoken'))
            try:
                proxy = search_in_environ(parser.get('debug',
                                                     'testit_proxy'))
            except configparser.NoSectionError as nse:
                print(f"Section not set, cause: {nse}")
            except configparser.NoOptionError as noe:
                print(f"Option not set, cause: {noe}")

            if parser.has_option('testit', 'testrunID'):
                self.testrun_id = uuid_check(search_in_environ(
                    parser.get('testit', 'testrunID')))
            else:
                self.project_id = uuid_check(
                    search_in_environ(parser.get('testit', 'projectID')))
                self.configuration_id = uuid_check(
                    search_in_environ(parser.get('testit', 'configurationID')))

                if parser.has_option('testit', 'testrun_name'):
                    self.testrun_name = parser.get('testit', 'testrun_name')
        self.requests = Api(url, private_token, proxy=proxy)

    @pytest.hookimpl
    def pytest_configure(self, config):
        if not hasattr(config, "workerinput") and not hasattr(self, "testrun_id"):
            config.testrun_id = self.requests.create_testrun(
                JSONFixture.create_testrun(
                    self.project_id,
                    f'{self.testrun_name if hasattr(self, "testrun_name") else "LocalRun"} {datetime.today().strftime("%d %b %Y %H:%M:%S")}'))
            self.requests.testrun_activity(config.testrun_id, 'start')

    @pytest.hookimpl
    def pytest_configure_node(self, node):
        if not hasattr(self, "testrun_id"):
            node.workerinput["testrun_id"] = pickle.dumps(node.config.testrun_id)

    @pytest.hookimpl
    def pytest_collection_modifyitems(self, session, config, items):
        index = 0
        new_items = []
        plugin_info = config.pluginmanager.list_plugin_distinfo()

        for plugin, dist in plugin_info:
            if 'pytest_check' == dist.project_name:
                from pytest_check import check_methods
                self.pytest_check_get_failures = check_methods.get_failures
                break

        if not hasattr(self, "testrun_id"):
            self.testrun_id = pickle.loads(config.workerinput["testrun_id"]) if\
                hasattr(config, 'workerinput') else config.testrun_id

        self.project_id, json_points = self.requests.get_testrun(
            self.testrun_id)

        resolved_autotests = autotests_parser(json_points, self.configuration_id)

        for item in items:
            if hasattr(item.function, 'test_external_id'):
                if item.own_markers:
                    for mark in item.own_markers:
                        if mark.name == 'parametrize':
                            if not hasattr(item, 'array_parametrize_mark_id'):
                                item.array_parametrize_mark_id = []
                            item.array_parametrize_mark_id.append(
                                item.own_markers.index(mark))

                item.test_external_id = self.param_attribute_collector(
                    item.function.test_external_id,
                    item.own_markers,
                    item.array_parametrize_mark_id,
                    index) if hasattr(item,
                                      'array_parametrize_mark_id'
                                      ) else item.function.test_external_id

                item.index = index
                item_id = items.index(item)
                index = index + 1 if item_id + \
                                     1 < len(items) and item.originalname == \
                                     items[item_id + 1].originalname else 0

                if resolved_autotests:
                    if item.test_external_id in resolved_autotests:
                        new_items.append(item)
        if resolved_autotests:
            if not new_items:
                print('The specified tests were not found!')
                raise SystemExit
            session.items = new_items

    @pytest.hookimpl
    def pytest_runtest_protocol(self, item):
        if hasattr(item.function, 'test_external_id'):
            if not hasattr(item.function,
                           'test_displayname') and not item.function.__doc__:
                self.item = None
                raise Exception(
                    f'{item.originalname} must have @testit.displayName or documentation!')
            self.item = item
        else:
            self.item = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef):
        yield
        if hasattr(self, 'item') and self.item:
            steps_data, results_steps_data = step.get_steps_data()
            if fixturedef.scope == 'function':
                if not hasattr(self.item, 'test_method_setup_steps'):
                    self.item.test_method_setup_steps = []
                    self.item.test_method_setup_results_steps = []
                self.item.test_method_setup_steps += steps_data
                self.item.test_method_setup_results_steps += results_steps_data

    @pytest.hookimpl(hookwrapper=True, trylast=True)
    def pytest_runtest_call(self):
        yield
        if hasattr(self, 'item') and not self.item:
            return
        test_steps, test_results_steps = step.get_steps_data()
        self.item.test_steps = test_steps
        self.item.test_results_steps = test_results_steps

    @pytest.hookimpl
    def pytest_fixture_post_finalizer(self, fixturedef):
        if hasattr(self, 'item') and not self.item:
            return
        teardown_steps, teardown_results_steps = step.get_steps_data()
        if fixturedef.scope == 'function':
            if not hasattr(self.item, 'test_method_teardown_steps'):
                self.item.test_method_teardown_steps = []
                self.item.test_method_teardown_results_steps = []
            self.item.test_method_teardown_steps += teardown_steps
            self.item.test_method_teardown_results_steps += teardown_results_steps

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report):
        if hasattr(self, 'item') and self.item:
            if report.failed or hasattr(report, 'wasxfail') \
                    and not report.passed or report.outcome == 'rerun':
                if not hasattr(self.item, 'test_traces'):
                    self.item.test_traces = ''
                self.item.test_traces += (report.longreprtext if report.longreprtext else
                    ''.join(['\n'.join(self.item.old_failures)]) +
                    f'\n{"-" * 60}\nFailed Checks: {len(self.item.old_failures)}') + f'\n{"-" * 60}\n'
                if hasattr(self.item, 'old_failures'):
                    del self.item.old_failures
            if not hasattr(self.item, 'test_duration'):
                self.item.test_duration = 0
            self.item.test_duration += report.duration * 1000

    @pytest.hookimpl
    def pytest_runtest_logfinish(self):
        if not hasattr(self, 'item') or not self.item:
            return
        data_item = self.attribute_collector(self.item)
        if data_item:
            autotest = self.requests.get_autotest(
                data_item['externalID'], self.project_id).json()
            if not autotest:
                autotest_id = self.requests.create_autotest(
                    JSONFixture.create_autotest(
                        data_item['externalID'],
                        self.project_id,
                        data_item['autoTestName'],
                        data_item['steps'],
                        data_item['setUp'],
                        data_item['tearDown'],
                        data_item['namespace'],
                        data_item['classname'],
                        data_item['title'],
                        data_item['description'],
                        data_item['links'],
                        data_item['labels']
                    )
                )
            else:
                autotest_id = autotest[0]['id']
                if data_item['testResult'] == 'Passed':
                    self.requests.update_autotest(
                        JSONFixture.update_autotest(
                            data_item['externalID'],
                            self.project_id,
                            data_item['autoTestName'],
                            autotest_id,
                            data_item['steps'],
                            data_item['setUp'],
                            data_item['tearDown'],
                            data_item['namespace'],
                            data_item['classname'],
                            data_item['title'],
                            data_item['description'],
                            data_item['links'],
                            data_item['labels']
                        )
                    )
                else:
                    self.requests.update_autotest(
                        JSONFixture.update_autotest(
                            data_item['externalID'],
                            self.project_id,
                            autotest[0]['name'],
                            autotest_id,
                            autotest[0]['steps'],
                            autotest[0]['setup'],
                            autotest[0]['teardown'],
                            autotest[0]['namespace'],
                            autotest[0]['classname'],
                            autotest[0]['title'],
                            autotest[0]['description'],
                            autotest[0]['links'],
                            autotest[0]['labels']
                        )
                    )

            for workitem_id in data_item['workItemsID']:
                self.requests.link_autotest(autotest_id, workitem_id)

            self.requests.set_results_for_testrun(
                self.testrun_id,
                [JSONFixture.set_results_for_testrun(
                    data_item['externalID'],
                    self.configuration_id,
                    data_item['testResult'],
                    data_item['stepResults'],
                    data_item['setUpResults'],
                    data_item['tearDownResults'],
                    data_item['traces'],
                    data_item['attachments'],
                    data_item['parameters'],
                    data_item['resultLinks'],
                    data_item['duration'],
                    data_item['failureReasonName'],
                    data_item['message']
                )]
            )

    # TODO: move private methods into separate classes according to the purpose of the object
    @staticmethod
    def _get_steps_from(item):
        if hasattr(item, 'test_steps'):
            return item.test_steps
        return []

    @staticmethod
    def _get_step_results_from(item):
        if hasattr(item, 'test_results_steps'):
            return item.test_results_steps
        return []

    @staticmethod
    def _get_setup_from(item):
        if hasattr(item, 'test_method_setup_steps'):
            method_setup_steps = item.test_method_setup_steps
            del item.test_method_setup_steps
            return method_setup_steps
        return []

    @staticmethod
    def _get_setup_results_from(item):
        if hasattr(item, 'test_method_setup_results_steps'):
            method_setup_results_steps = item.test_method_setup_results_steps
            del item.test_method_setup_results_steps
            return method_setup_results_steps
        return []

    @staticmethod
    def _get_teardown_from(item):
        if hasattr(item, 'test_method_teardown_steps'):
            method_teardown_steps = item.test_method_teardown_steps
            del item.test_method_teardown_steps
            return method_teardown_steps
        return []

    @staticmethod
    def _get_teardown_results_from(item):
        if hasattr(item, 'test_method_teardown_results_steps'):
            method_teardown_results_steps = item.test_method_teardown_results_steps
            del item.test_method_teardown_results_steps
            return method_teardown_results_steps
        return []

    @staticmethod
    def _get_result_links_from(item):
        if hasattr(item, 'result_links'):
            result_links = item.result_links
            del item.result_links
            return result_links
        return []

    @staticmethod
    def _get_duration_from(item):
        if hasattr(item, 'test_duration'):
            test_duration = item.test_duration
            del item.test_duration
            return test_duration
        return None

    @staticmethod
    def _get_traces_from(item):
        if hasattr(item, 'test_traces'):
            test_traces = item.test_traces
            del item.test_traces
            return test_traces
        return None

    @staticmethod
    def _get_attachments_from(item):
        if hasattr(item, 'test_attachments'):
            test_attachments = item.test_attachments
            del item.test_attachments
            return test_attachments
        return []

    @staticmethod
    def _get_parameters_from(item):
        if hasattr(item, 'test_parameters'):
            return item.test_parameters
        return None

    @staticmethod
    def _get_classname_from(item):
        i = item.function.__qualname__.find('.')
        if i != -1:
            return item.function.__qualname__[:i]
        return None

    @staticmethod
    def _set_links(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            for link in item.function.test_links:
                data['links'].append({})
                data['links'][-1]['url'] = TestITListener.attribute_collector_links(
                                                link,
                                                'url',
                                                item.own_markers,
                                                item.array_parametrize_mark_id,
                                                item.index)
                if link['title']:
                    data['links'][-1]['title'] = TestITListener.attribute_collector_links(
                                                    link,
                                                    'title',
                                                    item.own_markers,
                                                    item.array_parametrize_mark_id,
                                                    item.index)
                if link['type']:
                    data['links'][-1]['type'] = TestITListener.attribute_collector_links(
                                                    link,
                                                    'type',
                                                    item.own_markers,
                                                    item.array_parametrize_mark_id,
                                                    item.index)
                if link['description']:
                    data['links'][-1][
                        'description'] = TestITListener.attribute_collector_links(
                                            link,
                                            'description',
                                            item.own_markers,
                                            item.array_parametrize_mark_id,
                                            item.index)
        else:
            data['links'] = item.function.test_links

    @staticmethod
    def _get_title_from(item):
        if not hasattr(item.function, 'test_title'):
            return None
        if hasattr(item, 'array_parametrize_mark_id'):
            return TestITListener.param_attribute_collector(item.function.test_title,
                                                            item.own_markers,
                                                            item.array_parametrize_mark_id,
                                                            item.index)
        return item.function.test_title

    @staticmethod
    def _get_description_from(item):
        if not hasattr(item.function, 'test_description'):
            return None
        if hasattr(item, 'array_parametrize_mark_id'):
            return TestITListener.param_attribute_collector(
                item.function.test_description,
                item.own_markers,
                item.array_parametrize_mark_id,
                item.index)
        return item.function.test_description

    @staticmethod
    def _set_labels(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = TestITListener.mass_param_attribute_collector(
                item.function.test_labels[0],
                item.own_markers,
                item.array_parametrize_mark_id,
                item.index)
            if param_id is not None and item.function.test_labels[0][1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                for label in result:
                    data['labels'].append({
                        'name': label
                    })
            else:
                data['labels'].append({
                    'name': result
                })
        else:
            for label in item.function.test_labels:
                data['labels'].append({
                    'name': label
                })

    @staticmethod
    def _set_workitems_id(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = TestITListener.mass_param_attribute_collector(
                item.function.test_workitems_id[0], item.own_markers,
                item.array_parametrize_mark_id, item.index)
            if param_id is not None and item.function.test_workitems_id[0][
                                        1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                data['workItemsID'] = result
            else:
                data['workItemsID'] = [result]
        else:
            data['workItemsID'] = item.function.test_workitems_id

    @staticmethod
    def attribute_collector(item):
        # TODO: need to refactoring that method
        if not hasattr(item.function, 'test_external_id'):
            return None
        data = {
            'externalID': item.test_external_id,
            'steps': TestITListener._get_steps_from(item),
            'stepResults': TestITListener._get_step_results_from(item),
            'setUp': TestITListener._get_setup_from(item),
            'setUpResults': TestITListener._get_setup_results_from(item),
            'tearDown': TestITListener._get_teardown_from(item),
            'tearDownResults': TestITListener._get_teardown_results_from(
                item),
            'resultLinks': TestITListener._get_result_links_from(item),
            'duration': TestITListener._get_duration_from(item),
            'testResult': 'Failed' if hasattr(item,
                                              'test_traces') else 'Passed',
            'failureReasonName': 'TestDefect' if hasattr(item,
                                                         'test_traces') else 'NoDefect',
            'traces': TestITListener._get_traces_from(item),
            'namespace': item.function.__module__,
            'attachments': TestITListener._get_attachments_from(item),
            'parameters': TestITListener._get_parameters_from(item),
            'classname': TestITListener._get_classname_from(item),
            'title': TestITListener._get_title_from(item),
            'description': TestITListener._get_description_from(item),
            'links': [],
            'labels': [],
            'workItemsID': [],
            'message': None
        }

        if hasattr(item.function, 'test_links'):
            TestITListener._set_links(item, data)

        if hasattr(item.function, 'test_labels'):
            TestITListener._set_labels(item, data)

        if hasattr(item.function, 'test_workitems_id'):
            TestITListener._set_workitems_id(item, data)

        if item.own_markers:
            for mark in item.own_markers:
                if mark.name == 'skip' or mark.name == 'skipif' and mark.args[0]:
                    data['testResult'] = 'Skipped'
                    data['failureReasonName'] = None
                    if mark.kwargs:
                        data['message'] = mark.kwargs['reason']

        if hasattr(item, 'test_message'):
            data['message'] = item.test_message

        if hasattr(item.function, 'test_displayname'):
            if hasattr(item, 'array_parametrize_mark_id'):
                data['autoTestName'] = TestITListener.param_attribute_collector(
                    item.function.test_displayname,
                    item.own_markers,
                    item.array_parametrize_mark_id,
                    item.index)
            else:
                data['autoTestName'] = item.function.test_displayname
        elif item.function.__doc__:
            data['autoTestName'] = item.function.__doc__
        else:
            data['autoTestName'] = 'Test without name'
            data['testResult'] = 'Failed'
            data['failureReasonName'] = 'TestDefect'
            data['traces'] = '>\n{}\nE {} must have @testit.displayName or documentation!\n{}:{}: Exception'.format(
                inspect.getsource(item.function),
                item.originalname,
                item.location[0],
                item.location[1])

        return data

    @staticmethod
    def param_attribute_collector(attribute, marks, parametrize_id, index):
        for ID in parametrize_id:
            if attribute[attribute.find('{') + 1:attribute.rfind('}')] in \
                    marks[ID].args[0]:
                return attribute.split('{')[0] + marks[ID].args[1][index][
                    marks[ID].args[0].split(', ').index(attribute[
                                                        attribute.find(
                                                            '{') + 1:attribute.rfind(
                                                            '}')])] + \
                       attribute.split('}')[1]
        return attribute

    @staticmethod
    def mass_param_attribute_collector(attribute, marks, parametrize_id, index):
        for ID in parametrize_id:
            if attribute[1:-1] != '' and attribute[1:-1] in marks[ID].args[0]:
                param_id = marks[ID].args[0].split(', ').index(attribute[1:-1])
                return marks[ID].args[1][index][param_id], param_id
        return attribute, None

    @staticmethod
    def attribute_collector_links(link, key, marks, parametrize_id, index):
        for ID in parametrize_id:
            if link[key][(link[key].find('{') + 1):(link[key].rfind('}'))] in \
                    marks[ID].args[0]:
                return link[key].split('{')[0] + marks[ID].args[1][index][
                    marks[ID].args[0].split(', ').index(link[key][(
                                                                          link[key].find('{') + 1):
                                                                  (link[key].rfind(
                                                                      '}'))])] + \
                       link[key].split('}')[1]
        return link[key]

    @staticmethod
    def form_tree_steps(item, tree_steps, stage):
        for scope in ('session', 'module', 'class', 'method'):
            if hasattr(item, f'test_{scope}_{stage}_steps'):
                tree_steps[scope] = getattr(
                    item, f'test_{scope}_{stage}_steps')
                tree_steps[f'{scope}_results'] = getattr(
                    item, f'test_{scope}_{stage}_results_steps')
            elif scope not in tree_steps:
                tree_steps[scope] = []
                tree_steps[f'{scope}_results'] = []
        return tree_steps

    @testit_adapter_pytest.hookimpl
    def add_link(self, link_url, link_title, link_type, link_description):
        if not hasattr(self.item, 'result_links'):
            self.item.result_links = []
        self.item.result_links.append(
            {
                'url': link_url,
                'title': link_title,
                'type': link_type,
                'description': link_description
            })

    @testit_adapter_pytest.hookimpl
    def add_message(self, test_message):
        self.item.test_message = str(test_message)

    @testit_adapter_pytest.hookimpl
    def add_attachments(self, attach_paths):
        if not hasattr(self.item, 'test_attachments'):
            self.item.test_attachments = []
        self.item.test_attachments += self.load_attachments(attach_paths)

    @testit_adapter_pytest.hookimpl
    def load_attachments(self, attach_paths):
        attachments = []
        for path in attach_paths:
            if os.path.isfile(path):
                attachments.append(
                    {
                        'id': self.requests.load_attachment(open(path, "rb"))
                    })
            else:
                print(f'File ({path}) not found!')
        return attachments

    @testit_adapter_pytest.hookimpl
    def add_parameters(self, parameters):
        if not hasattr(self.item, 'test_parameters'):
            self.item.test_parameters = {}
            for key, parameter in parameters.items():
                self.item.test_parameters[key] = str(parameter)

    @testit_adapter_pytest.hookimpl
    def get_pytest_check_outcome(self):
        if hasattr(self, 'pytest_check_get_failures'):
            failures = self.pytest_check_get_failures()
            if failures and ((not hasattr(self.item, 'old_failures')) or self.item.old_failures != failures):
                self.item.old_failures = failures[:]
                return 'Failed'
        return 'Passed'
