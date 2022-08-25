import inspect
import os
import re


class Utils:

    @staticmethod
    def search_in_environ(variable: str):
        if re.fullmatch(r'{[a-zA-Z_]\w*}', variable) and variable[1:-1] in os.environ:
            return os.environ[variable[1:-1]]

        return variable

    @staticmethod
    def autotests_parser(data_autotests: list, configuration: str):
        resolved_autotests = []

        for data_autotest in data_autotests:
            if configuration == data_autotest['configurationId']:
                resolved_autotests.append(data_autotest['autoTest']['externalId'])

        return resolved_autotests

    @staticmethod
    def uuid_check(uuid: str):
        if not re.fullmatch(r'[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}', uuid):
            print(f'The wrong {uuid}!')
            raise SystemExit

        return uuid

    @staticmethod
    def url_check(url: str):
        if not re.fullmatch(r'^(?:(?:(?:https?|ftp):)?//)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-zA-Z0-9\u00a1-\uffff][a-zA-Z0-9\u00a1-\uffff_-]{0,62})?[a-zA-Z0-9\u00a1-\uffff]\.)+(?:[a-zA-Z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$', url):
            print('The wrong URL!')
            raise SystemExit

        if url[-1] == '/':
            return url[:-1]

        return url

    @staticmethod
    def form_test(item):
        data = {
            'externalID': item.test_external_id,
            'steps': [],
            'stepResults': [],
            'setUp': [],
            'setUpResults': [],
            'tearDown': [],
            'tearDownResults': [],
            'resultLinks': [],
            'duration': 0,
            'testResult': 'Failed' if hasattr(item,
                                              'test_traces') else 'Passed',
            'failureReasonName': None,
            'traces': None,
            'namespace': item.function.__module__,
            'attachments': [],
            'parameters': Utils.__get_parameters_from(item),
            'properties': Utils.__get_properties_from(item),
            'classname': Utils.__get_classname_from(item),
            'title': Utils._get_title_from(item),
            'description': Utils.__get_description_from(item),
            'links': [],
            'labels': [],
            'workItemsID': [],
            'message': None
        }

        if hasattr(item.function, 'test_links'):
            Utils.__set_links(item, data)

        if hasattr(item.function, 'test_labels'):
            Utils.__set_labels(item, data)

        if hasattr(item.function, 'test_workitems_id'):
            Utils.__set_workitems_id(item, data)

        if item.own_markers:
            for mark in item.own_markers:
                if mark.name == 'skip' or mark.name == 'skipif' and mark.args[0]:
                    data['testResult'] = 'Skipped'
                    data['failureReasonName'] = None
                    if mark.kwargs:
                        data['message'] = mark.kwargs['reason']

        if hasattr(item.function, 'test_displayname'):
            if hasattr(item, 'array_parametrize_mark_id'):
                data['autoTestName'] = Utils.param_attribute_collector(
                    item.function.test_displayname,
                    item.callspec.params)
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
    def __get_parameters_from(item):
        if hasattr(item, 'array_parametrize_mark_id'):
            test_parameters = {}
            for key, parameter in item.callspec.params.items():
                test_parameters[key] = str(parameter)
            return test_parameters
        return None

    @staticmethod
    def __get_properties_from(item):
        if hasattr(item, 'test_properties'):
            return item.test_properties
        return None

    @staticmethod
    def __get_classname_from(item):
        i = item.function.__qualname__.find('.')
        if i != -1:
            return item.function.__qualname__[:i]
        return None

    @staticmethod
    def __set_links(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            for link in item.function.test_links:
                data['links'].append({})
                data['links'][-1]['url'] = Utils.param_attribute_collector(
                    link['url'],
                    item.callspec.params)
                if link['title']:
                    data['links'][-1]['title'] = Utils.param_attribute_collector(
                        link['title'],
                        item.callspec.params)
                if link['type']:
                    data['links'][-1]['type'] = Utils.param_attribute_collector(
                        link['type'],
                        item.callspec.params)
                if link['description']:
                    data['links'][-1]['description'] = Utils.param_attribute_collector(
                        link['description'],
                        item.callspec.params)
        else:
            data['links'] = item.function.test_links

    @staticmethod
    def _get_title_from(item):
        if not hasattr(item.function, 'test_title'):
            return None
        if hasattr(item, 'array_parametrize_mark_id'):
            return Utils.param_attribute_collector(
                item.function.test_title,
                item.callspec.params)
        return item.function.test_title

    @staticmethod
    def __get_description_from(item):
        if not hasattr(item.function, 'test_description'):
            return None
        if hasattr(item, 'array_parametrize_mark_id'):
            return Utils.param_attribute_collector(
                item.function.test_description,
                item.callspec.params)
        return item.function.test_description

    @staticmethod
    def __set_labels(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = Utils.mass_param_attribute_collector(
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
    def __set_workitems_id(item, data):
        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = Utils.mass_param_attribute_collector(
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
    def param_attribute_collector(attribute, run_param):
        result = attribute
        param_keys = re.findall(r"\{(.*?)\}", attribute)
        if len(param_keys) > 0:
            for param_key in param_keys:
                root_key = param_key
                id_keys = re.findall(r'\[(.*?)\]', param_key)
                if len(id_keys) == 0:
                    base_key = root_key
                    result = result.replace("{" + root_key + "}", str(run_param[base_key]))
                elif len(id_keys) == 1:
                    base_key = root_key.replace("[" + id_keys[0] + "]", "")
                    id_key = id_keys[0].strip("\'\"")
                    if id_key.isdigit() and int(id_key) in range(len(run_param[base_key])):
                        val_key = int(id_key)
                    elif id_key.isalnum() and not id_key.isdigit() and id_key in run_param[base_key].keys():
                        val_key = id_key
                    else:
                        raise SystemExit(f"Not key: {root_key} in run parameters or other keys problem")
                    result = result.replace("{" + root_key + "}", str(run_param[base_key][val_key]))
                else:
                    raise SystemExit("For type tuple, list, dict) support only one level!")
        elif len(param_keys) == 0:
            result = attribute
        else:
            raise SystemExit("Collecting parameters error!")
        return result

    @staticmethod
    def mass_param_attribute_collector(attribute, marks, parametrize_id, index):
        for ID in parametrize_id:
            if attribute[1:-1] != '' and attribute[1:-1] in marks[ID].args[0]:
                param_id = marks[ID].args[0].split(', ').index(attribute[1:-1])
                return marks[ID].args[1][index][param_id], param_id
        return attribute, None