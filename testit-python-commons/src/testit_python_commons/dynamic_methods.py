from testit_python_commons.services import TmsPluginManager
from testit_python_commons.step import Step


def addLink(url: str, title: str = None, type: str = None, description: str = None):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_link'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_link(
                link_url=url,
                link_title=title,
                link_type=type,
                link_description=description)


def message(test_message: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_message(test_message=test_message)


def addMessage(test_message: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook\
            .add_message(test_message=test_message)


def attachments(*attachments_paths: str):
    if Step.step_is_active():
        Step.add_attachments(attachments_paths)
    else:
        if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
            TmsPluginManager.get_plugin_manager().hook\
                .add_attachments(attach_paths=attachments_paths)
