import logging
import re
import inspect

from .models.autotest import Autotest
from .utils import get_hash


class AutotestParser:
    @classmethod
    def parse(cls, test) -> Autotest:
        if hasattr(test, "_testFunc"):
            item = test._testFunc

            if not hasattr(item, 'test_external_id'):
                item.test_external_id = get_hash(item.__name__)

            if not hasattr(item, 'test_displayname'):
                item.test_displayname = item.__doc__ if \
                    item.__doc__ else item.__name__
            else:
                item.test_displayname = cls.__param_attribute_collector(
                    item.test_displayname,
                    cls.__get_params(test))

            autotest = Autotest(
                external_id=item.test_external_id,
                name=item.test_displayname,
                title=cls.__get_title_from(test),
                description=cls.__get_description_from(test),
                namespace=item.__module__,
                classname=cls.__get_classname_from(item),
                parameters=cls.__get_params(test),
                properties=cls.__get_properties_from(test))

            if hasattr(item, 'test_links'):
                cls.__set_links(test, autotest)

            if hasattr(item, 'test_labels'):
                cls.__set_labels(item, autotest)

            if hasattr(item, 'test_workitems_id'):
                cls.__set_workitems_id(item, autotest)
        else:
            autotest = Autotest(
                external_id=get_hash(test._testMethodName),
                name=test.__doc__ if \
                    test.__doc__ else test._testMethodName,
                parameters=cls.__get_params(test))

        return autotest

    @staticmethod
    def __get_properties_from(item):
        if hasattr(item, 'test_properties'):
            return item.test_properties
        return None

    @staticmethod
    def __get_classname_from(item):
        i = item.__qualname__.find('.')
        if i != -1:
            return item.__qualname__[:i]
        return None

    @classmethod
    def __set_links(cls, test, autotest):
        item = test._testFunc
        params = cls.__get_params(test)

        if params:
            for link in item.test_links:
                autotest.links.append({})
                autotest.links[-1]['url'] = cls.__param_attribute_collector(
                    link['url'],
                    params)
                autotest.links[-1]['title'] = cls.__param_attribute_collector(
                    link['title'],
                    params) if link['title'] else None
                autotest.links[-1]['type'] = cls.__param_attribute_collector(
                    link['type'],
                    params) if link['type'] else None
                autotest.links[-1]['description'] = cls.__param_attribute_collector(
                    link['description'],
                    params) if link['description'] else None
        else:
            autotest.links = item.test_links

    @classmethod
    def __get_title_from(cls, test):
        item = test._testFunc

        if not hasattr(item, 'test_title'):
            return None

        params = cls.__get_params(test)

        if params:
            return cls.__param_attribute_collector(
                item.test_title,
                params)
        return item.test_title

    @classmethod
    def __get_description_from(cls, test):
        item = test._testFunc

        if not hasattr(item, 'test_description'):
            return None

        params = cls.__get_params(test)

        if params:
            return cls.__param_attribute_collector(
                item.test_description,
                params)
        return item.test_description

    @classmethod
    def __set_labels(cls, item, autotest):
        if hasattr(item, 'array_parametrize_mark_id'):
            for one_label in item.test_labels:
                result, param_id = cls.__mass_param_attribute_collector(
                    one_label,
                    item.own_markers,
                    item.array_parametrize_mark_id,
                    item.index)
                if param_id is not None and one_label[1:-1] in \
                        item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                            '-')[param_id]:
                    for label in result:
                        autotest.labels.append({
                            'name': label
                        })
                else:
                    autotest.labels.append({
                        'name': result
                    })
        else:
            for label in item.test_labels:
                autotest.labels.append({
                    'name': label
                })

    @classmethod
    def __set_workitems_id(cls, item, autotest):
        if hasattr(item, 'array_parametrize_mark_id'):
            result, param_id = cls.__mass_param_attribute_collector(
                item.test_workitems_id[0], item.own_markers,
                item.array_parametrize_mark_id, item.index)
            if param_id is not None and item.test_workitems_id[0][1:-1] in \
                    item.name[(item.name.find('[') + 1):(item.name.rfind(']'))].split(
                        '-')[param_id]:
                autotest.work_item_ids = result
            else:
                autotest.work_item_ids = [result]
        else:
            autotest.work_item_ids = item.test_workitems_id

    @staticmethod
    def __fullname(event):
        if hasattr(event.test, "_testFunc"):
            test_module = event.test._testFunc.__module__
            test_name = event.test._testFunc.__name__
            return f"{test_module}.{test_name}"
        test_id = event.test.id()
        return test_id.split(":")[0]

    @classmethod
    def __get_params(cls, test):
        def _params(names, values):
            return {name if name else f"param{values.index(value)}": value for name, value in zip(names, values)}

        test_id = test.id()

        if len(test_id.split("\n")) > 1:
            if hasattr(test, "_testFunc"):
                wrapper_arg_spec = inspect.getfullargspec(test._testFunc)
                arg_set, obj = wrapper_arg_spec.defaults
                test_arg_spec = inspect.getfullargspec(obj)
                args = test_arg_spec.args

                return _params(args, arg_set)
            elif hasattr(test, "_testMethodName"):
                method = getattr(test, test._testMethodName)
                wrapper_arg_spec = inspect.getfullargspec(method)
                obj, arg_set = wrapper_arg_spec.defaults
                test_arg_spec = inspect.getfullargspec(obj)
                args = test_arg_spec.args

                return _params(args[1:], arg_set)

    @staticmethod
    def __param_attribute_collector(attribute, run_param):
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
    def __mass_param_attribute_collector(attribute, marks, parametrize_id, index):
        for param_index in parametrize_id:
            param_names = []
            for param_name in marks[param_index].args[0].split(','):
                param_names.append(param_name.strip())
            if attribute[1:-1] != '' and attribute[1:-1] in param_names:
                param_id = marks[param_index].args[0].split(', ').index(attribute[1:-1])
                return marks[param_index].args[1][index][param_id], param_id
        return attribute, None
