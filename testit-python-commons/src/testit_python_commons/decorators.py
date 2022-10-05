from functools import wraps

from testit_python_commons.services.utils import Utils


def inner(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not hasattr(function, 'test_properties') and kwargs:
            function.test_properties = {}

            for key, property in kwargs.items():
                if hasattr(function,
                           'callspec') and key not in function.callspec.params:
                    function.test_properties[key] = str(property)
        function(*args, **kwargs)
        return function
    return wrapper


@Utils.deprecated('Use "workItemIds" instead.')
def workItemID(*test_workitems_id: int or str):
    def outer(function):
        function.test_workitems_id = []
        for test_workitem_id in test_workitems_id:
            function.test_workitems_id.append(str(test_workitem_id))
        return inner(function)
    return outer


def workItemIds(*test_workitems_id: int or str):
    def outer(function):
        function.test_workitems_id = []
        for test_workitem_id in test_workitems_id:
            function.test_workitems_id.append(str(test_workitem_id))
        return inner(function)
    return outer


def displayName(test_displayname: str):
    def outer(function):
        function.test_displayname = test_displayname
        return inner(function)
    return outer


@Utils.deprecated('Use "externalId" instead.')
def externalID(test_external_id: str):
    def outer(function):
        function.test_external_id = test_external_id
        return inner(function)
    return outer


def externalId(test_external_id: str):
    def outer(function):
        function.test_external_id = test_external_id
        return inner(function)
    return outer


def title(test_title: str):
    def outer(function):
        function.test_title = test_title
        return inner(function)
    return outer


def description(test_description: str):
    def outer(function):
        function.test_description = test_description
        return inner(function)
    return outer


def labels(*test_labels: str):
    def outer(function):
        function.test_labels = test_labels
        return inner(function)
    return outer


@Utils.deprecated('Use "links" instead.')
def link(url: str, title: str = None, type: str = None, description: str = None):
    def outer(function):
        if not hasattr(function, 'test_links'):
            function.test_links = []
        function.test_links.append({'url': url, 'title': title, 'type': type, 'description': description})
        return inner(function)
    return outer


def links(url: str = None, title: str = None, type: str = None, description: str = None, links: list or tuple = None):
    def outer(function):
        if not hasattr(function, 'test_links'):
            function.test_links = []

        if url:
            function.test_links.append({'url': url, 'title': title, 'type': type, 'description': description})
        elif links and (isinstance(links, list) or isinstance(links, tuple)):
            for link in links:
                if isinstance(link, dict) and 'url' in link:
                    function.test_links.append(
                        {'url': link['url'],
                         'title': link['title'] if 'title' in link else None,
                         'type': link['type'] if 'type' in link else None,
                         'description': link['description'] if 'description' in link else None}
                    )
                else:
                    print(f'Link ({link}) can\'t be processed!')
        else:
            print(f'Links for {function.__name__} can\'t be processed!\nPlease, set "url" or "links"!')
        return inner(function)

    return outer
