from testit_python_commons.services import TmsPluginManager
from testit_python_commons.step import Step
from testit_python_commons.services.utils import Utils


@Utils.deprecated('Use "addLinks" instead.')
def addLink(url: str, title: str = None, type: str = None, description: str = None):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_link'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_link(
                link_url=url,
                link_title=title,
                link_type=type,
                link_description=description)


def addLinks(url: str = None, title: str = None, type: str = None, description: str = None, links: tuple = None):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_link'):
        if url:
            TmsPluginManager.get_plugin_manager().hook\
                .add_link(
                    link_url=url,
                    link_title=title,
                    link_type=type,
                    link_description=description)
        elif links:
            if isinstance(link, dict) and 'url' in link:
                TmsPluginManager.get_plugin_manager().hook \
                    .add_link(
                    link_url=link['url'],
                    link_title=link['title'] if 'title' in link else None,
                    link_type=link['type'] if 'type' in link else None,
                    link_description=link['description'] if 'description' in link else None)
            else:
                print(f'Link ({link}) can\'t be processed!')
        else:
            print(f'Links can\'t be processed!\nPlease, set "url" or "links"!')


@Utils.deprecated('Use "addMessage" instead.')
def message(test_message: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_message(test_message=test_message)


def addMessage(test_message: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_message(test_message=test_message)


@Utils.deprecated('Use "addAttachments" instead.')
def attachments(*attachments_paths):
    if Step.step_is_active():
        Step.add_attachments(attachments_paths)
    else:
        if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
            TmsPluginManager.get_plugin_manager().hook\
                .add_attachments(attach_paths=attachments_paths)


def addAttachments(data, is_text: bool = False, name: str = None):
    if Step.step_is_active():
        if is_text:
            Step.create_attachment(
                str(data),
                name)
        else:
            if isinstance(data, str):
                Step.add_attachments([data])
            elif isinstance(data, tuple):
                Step.add_attachments(data)
            else:
                print(f'File ({data}) not found!')
    else:
        if is_text and hasattr(TmsPluginManager.get_plugin_manager().hook, 'create_attachment'):
            Step.create_attachment(str(data), name)
            TmsPluginManager.get_plugin_manager().hook \
                .create_attachment(
                    body=str(data),
                    name=name)
        elif hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
            if isinstance(data, str):
                TmsPluginManager.get_plugin_manager().hook \
                    .add_attachments(attach_paths=[data])
            elif isinstance(data, tuple):
                TmsPluginManager.get_plugin_manager().hook \
                    .add_attachments(attach_paths=data)
            else:
                print(f'({data}) is not path!')
