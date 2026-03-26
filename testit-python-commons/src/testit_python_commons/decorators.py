import asyncio
import inspect
import logging
import types
from functools import wraps

from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils


def inner(function):
    def set_properties(kwargs):
        if not hasattr(function, 'test_properties') and kwargs:
            function.test_properties = {}

            for key, value in kwargs.items():
                if hasattr(function,
                           'callspec') and key not in function.callspec.params:
                    function.test_properties[key] = str(value)

    @wraps(function)
    def sync_wrapper(*args, **kwargs):
        set_properties(kwargs)
        function(*args, **kwargs)

    @wraps(function)
    async def async_wrapper(*args, **kwargs):
        set_properties(kwargs)
        await function(*args, **kwargs)

    if isinstance(function, types.FunctionType):
        if inspect.iscoroutinefunction(function):
            return async_wrapper

        return sync_wrapper

    return function


@Utils.deprecated('Use "workItemIds" instead.')
@adapter_logger
def workItemID(*test_workitems_id: int or str):  # noqa: N802
    def outer(function):
        function.test_workitems_id = []
        for test_workitem_id in test_workitems_id:
            function.test_workitems_id.append(str(test_workitem_id))
        return inner(function)

    return outer


@adapter_logger
def workItemIds(*test_workitems_id: int or str):  # noqa: N802
    """
    specifies a method that links autotests with manual tests. Receives the array of manual tests' IDs
    """
    def outer(function):  # noqa: N802
        function.test_workitems_id = []
        for test_workitem_id in test_workitems_id:
            function.test_workitems_id.append(str(test_workitem_id))
        return inner(function)

    return outer


@adapter_logger
def displayName(test_displayname: str):  # noqa: N802
    """
    specifies internal autotest name (used in Test IT)
    """
    def outer(function):
        function.test_displayname = test_displayname
        return inner(function)

    return outer


@adapter_logger
def nameSpace(test_namespace: str):  # noqa: N802
    """
    specifies directory in the TMS system (default - file's name of test)
    """
    def outer(function):
        function.test_namespace = test_namespace
        return inner(function)

    return outer


@adapter_logger
def className(test_classname: str):  # noqa: N802
    """
    specifies subdirectory in the TMS system (default - class's name of test)
    """
    def outer(function):
        function.test_classname = test_classname
        return inner(function)

    return outer


@Utils.deprecated('Use "externalId" instead.')
@adapter_logger
def externalID(test_external_id: str):  # noqa: N802
    def outer(function):
        function.test_external_id = test_external_id
        return inner(function)

    return outer


@adapter_logger
def externalId(test_external_id: str):  # noqa: N802
    """
    specifies unique internal autotest ID (used in Test IT)
    """
    def outer(function):
        function.test_external_id = test_external_id
        return inner(function)

    return outer


@adapter_logger
def title(test_title: str):
    """
    specifies autotest name specified in the autotest card.
    If not specified, the name from the displayName method is used
    """
    def outer(function):
        function.test_title = test_title
        return inner(function)

    return outer


@adapter_logger
def description(test_description: str):
    """
    specifies autotest description specified in the autotest card
    """
    def outer(function):
        function.test_description = test_description
        return inner(function)

    return outer


@Utils.deprecated('Use "tags" instead.')
@adapter_logger
def labels(*test_labels: str):
    """
    specifies labels listed in the autotest card
    """
    def outer(function):
        function.test_labels = test_labels
        return inner(function)

    return outer


@adapter_logger
def tags(*test_tags: str):
    """
    specifies tags listed in the autotest card
    """
    def outer(function):
        function.test_tags = test_tags
        return inner(function)

    return outer


@Utils.deprecated('Use "links" instead.')
@adapter_logger
def link(url: str, title: str = None, type: str = None, description: str = None):  # noqa: A002,VNE003
    def outer(function):
        if not hasattr(function, 'test_links'):
            function.test_links = []

        function.test_links.append(
            Utils.convert_link_dict_to_link_model({
                "url": url,
                "title": title,
                "type": type,
                "description": description}))

        return inner(function)

    return outer


@adapter_logger
def links(url: str = None, title: str = None, type: str = None,  # noqa: A002,VNE003
          description: str = None, links: list or tuple = None):
    """
    specifies links listed in the autotest card
    """
    def outer(function):
        if not hasattr(function, 'test_links'):
            function.test_links = []

        if url:
            function.test_links.append(
                Utils.convert_link_dict_to_link_model({
                    "url": url,
                    "title": title,
                    "type": type,
                    "description": description}))
        elif links and (isinstance(links, list) or isinstance(links, tuple)):
            for link in links:
                if isinstance(link, dict) and 'url' in link:
                    function.test_links.append(
                        Utils.convert_link_dict_to_link_model(link))
                else:
                    logging.warning(f'Link ({link}) can\'t be processed!')
        else:
            logging.warning(f'Links for {function.__name__} can\'t be processed!\nPlease, set "url" or "links"!')
        return inner(function)

    return outer
