import hashlib
import inspect
import logging
import re
import warnings

from testit_python_commons.services.logger import adapter_logger


class Utils:
    @staticmethod
    def uuid_check(uuid: str):
        if not re.fullmatch(r'[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}', uuid):
            logging.error(f'The wrong {uuid}!')
            raise SystemExit

        return uuid

    @staticmethod
    def url_check(url: str):
        if not re.fullmatch(
                r"^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*(:(0-9)*)*(\/?)"
                r"([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%\$#_]*)?$",
                url):
            logging.error('The wrong URL!')
            raise SystemExit

        if url[-1] == '/':
            return url[:-1]

        return url

    @staticmethod
    @adapter_logger
    def form_test(item):
        data = {
            'externalID': Utils.__get_external_id_from(item),
            'autoTestName': Utils.__get_display_name_from(item),
            'steps': [],
            'stepResults': [],
            'setUp': [],
            'setUpResults': [],
            'tearDown': [],
            'tearDownResults': [],
            'resultLinks': [],
            'duration': 0,
            'outcome': None,
            'failureReasonName': None,
            'traces': None,
            'attachments': [],
            'parameters': Utils.__get_parameters_from(item),
            'properties': Utils.__get_properties_from(item),
            'namespace': Utils.__get_namespace_from(item),
            'classname': Utils.__get_class_name_from(item),
            'title': Utils.__get_title_from(item),
            'description': Utils.__get_description_from(item),
            'links': Utils.__get_links_from(item),
            'labels': Utils.__get_labels_from(item),
            'workItemsID': Utils.__get_work_item_ids_from(item),
            'message': None
        }

        if item.own_markers:
            for mark in item.own_markers:
                if mark.name == 'skip' or mark.name == 'skipif':
                    data['outcome'] = 'Skipped'
                    data['failureReasonName'] = None
                    if mark.args:
                        data['message'] = mark.args[0]
                    if mark.kwargs and 'reason' in mark.kwargs:
                        data['message'] = mark.kwargs['reason']
                if mark.name == 'xfail':
                    if mark.args:
                        data['message'] = mark.args[0]
                    if mark.kwargs and 'reason' in mark.kwargs:
                        data['message'] = mark.kwargs['reason']

        return data

    @staticmethod
    @adapter_logger
    def __get_display_name_from(item):
        display_name = Utils.__search_attribute(item, 'test_displayname')

        if not display_name:
            return item.function.__doc__ if \
                item.function.__doc__ else item.function.__name__

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            display_name,
            params)

    @staticmethod
    @adapter_logger
    def __get_external_id_from(item):
        external_id = Utils.__search_attribute(item, 'test_external_id')

        if not external_id:
            return Utils.get_hash(item.nodeid + item.function.__name__)

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            external_id,
            params)

    @staticmethod
    @adapter_logger
    def __get_title_from(item):
        title = Utils.__search_attribute(item, 'test_title')

        if not title:
            return None

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            title,
            params)

    @staticmethod
    @adapter_logger
    def __get_description_from(item):
        description = Utils.__search_attribute(item, 'test_description')

        if not description:
            return None

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            description,
            params)

    @staticmethod
    @adapter_logger
    def __get_namespace_from(item):
        namespace = Utils.__search_attribute(item, 'test_namespace')

        if not namespace:
            return item.function.__module__

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            namespace,
            params)

    @staticmethod
    @adapter_logger
    def __get_class_name_from(item):
        class_name = Utils.__search_attribute(item, 'test_classname')

        if not class_name:
            i = item.function.__qualname__.find('.')

            if i != -1:
                return item.function.__qualname__[:i]

            return None

        params = Utils.get_params(item)

        return Utils.param_attribute_collector(
            class_name,
            params)

    @staticmethod
    @adapter_logger
    def __get_links_from(item):
        links = Utils.__search_attribute(item, 'test_links')

        if not links:
            return []

        params = Utils.get_params(item)

        return Utils.__set_params_in_links(
            links,
            params)

    @staticmethod
    @adapter_logger
    def __get_parameters_from(item):
        if hasattr(item, 'array_parametrize_mark_id'):
            test_parameters = {}
            for key, parameter in item.callspec.params.items():
                test_parameters[key] = str(parameter)
            return test_parameters
        return None

    @staticmethod
    @adapter_logger
    def __get_properties_from(item):
        if hasattr(item, 'test_properties'):
            return item.test_properties
        return None

    @staticmethod
    @adapter_logger
    def __set_params_in_links(links, params):
        if not params:
            return links

        links_with_params = []

        for link in links:
            links_with_params.append(
                {
                    'url': Utils.param_attribute_collector(
                        link['url'],
                        params),
                    'title': Utils.param_attribute_collector(
                        link['title'],
                        params) if link['title'] else None,
                    'type': Utils.param_attribute_collector(
                        link['type'],
                        params) if link['type'] else None,
                    'description': Utils.param_attribute_collector(
                        link['description'],
                        params) if link['description'] else None
                })

        return links_with_params

    # TODO: Need refactor
    @staticmethod
    @adapter_logger
    def __get_labels_from(item):
        test_labels = Utils.__search_attribute(item, 'test_labels')

        if not test_labels:
            return []

        labels = []

        if hasattr(item, 'array_parametrize_mark_id'):
            for one_label in test_labels:
                result, param_id = Utils.mass_param_attribute_collector(
                    one_label,
                    item.own_markers,
                    item.array_parametrize_mark_id,
                    item.index)
                if param_id is not None and one_label[1:-1] in \
                        item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                            '-')[param_id]:
                    for label in result:
                        labels.append({
                            'name': label
                        })
                else:
                    labels.append({
                        'name': result
                    })
        else:
            for label in test_labels:
                labels.append({
                    'name': label
                })

        return labels

    # TODO: Need refactor
    @staticmethod
    @adapter_logger
    def __get_work_item_ids_from(item):
        test_workitems_id = Utils.__search_attribute(item, 'test_workitems_id')

        if not test_workitems_id:
            return []

        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = Utils.mass_param_attribute_collector(
                test_workitems_id[0], item.own_markers,
                item.array_parametrize_mark_id, item.index)
            if param_id is not None and test_workitems_id[0][1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                return result
            else:
                return [result]
        else:
            return test_workitems_id

    @staticmethod
    @adapter_logger
    def param_attribute_collector(attribute, run_param):
        result = attribute
        param_keys = re.findall(r"\{(.*?)\}", attribute)
        if len(param_keys) > 0:
            for param_key in param_keys:
                root_key = param_key
                id_keys = re.findall(r'\[(.*?)\]', param_key)
                if len(id_keys) == 0:
                    if root_key in run_param:
                        result = result.replace("{" + root_key + "}", str(run_param[root_key]))
                    else:
                        logging.error(f"Parameter {root_key} not found")
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
    @adapter_logger
    def mass_param_attribute_collector(attribute, marks, parametrize_id, index):
        for param_index in parametrize_id:
            param_names = []
            for param_name in marks[param_index].args[0].split(','):
                param_names.append(param_name.strip())
            if attribute[1:-1] != '' and attribute[1:-1] in param_names:
                param_id = marks[param_index].args[0].split(', ').index(attribute[1:-1])
                return marks[param_index].args[1][index][param_id], param_id
        return attribute, None

    @staticmethod
    def deprecated(message):
        def deprecated_decorator(func):  # noqa: N802
            def deprecated_func(*args, **kwargs):
                warnings.warn(
                    '"{}" is no longer acceptable to compute time between versions.\n{}'.format(func.__name__, message),
                    category=DeprecationWarning,
                    stacklevel=2)
                warnings.simplefilter('default', DeprecationWarning)
                return func(*args, **kwargs)

            return deprecated_func

        return deprecated_decorator

    @staticmethod
    @adapter_logger
    def get_hash(value: str):
        md = hashlib.sha256(bytes(value, encoding='utf-8'))
        return md.hexdigest()

    @staticmethod
    @adapter_logger
    def get_params(item):
        params = {}

        if hasattr(item, 'test_properties'):
            params.update(item.test_properties)

        if hasattr(item, 'callspec'):
            params.update(item.callspec.params)

        return params

    @staticmethod
    @adapter_logger
    def __search_attribute(item, attribute):
        if hasattr(item.function, attribute):
            return getattr(item.function, attribute)

        if hasattr(item.cls, attribute):
            return getattr(item.cls, attribute)

        return

    @staticmethod
    def get_function_parameters(function, *args, **kwargs):
        parameters = {}
        args_default_values = inspect.getfullargspec(function).defaults

        if args or args_default_values:
            all_keys = inspect.getfullargspec(function).args
            all_args = list(args)

            if args_default_values:
                all_args += list(args_default_values[len(args) - (len(all_keys) - len(args_default_values)):])

            method_args = [arg_name for arg_name in all_keys if arg_name not in list(kwargs)]

            if len(method_args) == len(all_args):
                for index in range(0, len(method_args)):
                    parameters[method_args[index]] = str(all_args[index])

        if kwargs:
            for key, parameter in kwargs.items():
                parameters[key] = str(parameter)

        return parameters
