import logging

from testit_python_commons.services import TmsPluginManager
from testit_python_commons.services.logger import adapter_logger
from testit_python_commons.services.utils import Utils


@Utils.deprecated('Use "addLinks" instead.')
@adapter_logger
def addLink(url: str, title: str = None, type: str = None, description: str = None):  # noqa: A002,VNE003,N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_link'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_link(
            link=Utils.convert_link_dict_to_link_model({
                "url": url,
                "title": title,
                "type": type,
                "description": description}))


@adapter_logger
def addLinks(url: str = None, title: str = None, type: str = None, description: str = None,  # noqa: A002,VNE003,N802
             links: list or tuple = None):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_link'):
        if url:
            TmsPluginManager.get_plugin_manager().hook \
                .add_link(
                link=Utils.convert_link_dict_to_link_model({
                    "url": url,
                    "title": title,
                    "type": type,
                    "description": description}))
        elif links and (isinstance(links, list) or isinstance(links, tuple)):
            for link in links:
                if isinstance(link, dict) and 'url' in link:
                    TmsPluginManager.get_plugin_manager().hook \
                        .add_link(link=Utils.convert_link_dict_to_link_model(link))
                else:
                    logging.warning(f'Link ({link}) can\'t be processed!')
        else:
            logging.warning("Links can't be processed!\nPlease, set 'url' or 'links'!")


@Utils.deprecated('Use "addMessage" instead.')
@adapter_logger
def message(test_message: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_message(test_message=test_message)


@adapter_logger
def addMessage(test_message: str):   # noqa: N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_message'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_message(test_message=test_message)


@Utils.deprecated('Use "addAttachments" instead.')
@adapter_logger
def attachments(*attachments_paths):
    active_step = TmsPluginManager.get_step_manager().get_active_step()

    if active_step:
        attachment_ids = TmsPluginManager.get_adapter_manager().load_attachments(attachments_paths)

        active_step.set_attachments(active_step.get_attachments() + attachment_ids)
    else:
        if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
            TmsPluginManager.get_plugin_manager().hook \
                .add_attachments(attach_paths=attachments_paths)


@adapter_logger
def addAttachments(data, is_text: bool = False, name: str = None):   # noqa: N802
    active_step = TmsPluginManager.get_step_manager().get_active_step()

    if active_step:
        add_attachments_to_step(active_step, data, is_text, name)
    else:
        add_attachments_to_test(data, is_text, name)


@adapter_logger
def add_attachments_to_step(step, data, is_text: bool = False, name: str = None):
    if is_text:
        attachment_ids = TmsPluginManager.get_adapter_manager().create_attachment(data, name)
    else:
        if isinstance(data, str):
            attachment_ids = TmsPluginManager.get_adapter_manager().load_attachments([data])
        elif isinstance(data, tuple) or isinstance(data, list):
            attachment_ids = TmsPluginManager.get_adapter_manager().load_attachments(data)
        else:
            logging.warning(f'File ({data}) not found!')
            return

    step.set_attachments(step.get_attachments() + attachment_ids)


@adapter_logger
def add_attachments_to_test(data, is_text: bool = False, name: str = None):
    if is_text and hasattr(TmsPluginManager.get_plugin_manager().hook, 'create_attachment'):
        TmsPluginManager.get_plugin_manager().hook \
            .create_attachment(
            body=data,
            name=name)
    elif hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
        if isinstance(data, str):
            TmsPluginManager.get_plugin_manager().hook \
                .add_attachments(attach_paths=[data])
        elif isinstance(data, tuple) or isinstance(data, list):
            TmsPluginManager.get_plugin_manager().hook \
                .add_attachments(attach_paths=data)
        else:
            logging.warning(f'({data}) is not path!')


@adapter_logger
def addWorkItemIds(*test_work_item_ids: int or str):  # noqa: N802
    if not hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_work_item_id'):
        return

    for test_work_item_id in test_work_item_ids:
        TmsPluginManager.get_plugin_manager().hook.add_work_item_id(test_work_item_id=str(test_work_item_id))


@adapter_logger
def addDisplayName(test_display_name: str):  # noqa: N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_display_name'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_display_name(test_display_name=str(test_display_name))


@adapter_logger
def addNameSpace(test_namespace: str):  # noqa: N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_namespace'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_namespace(test_namespace=str(test_namespace))


@adapter_logger
def addClassName(test_classname: str):  # noqa: N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_classname'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_classname(test_classname=str(test_classname))


@adapter_logger
def addExternalId(test_external_id: str):  # noqa: N802
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_external_id'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_external_id(test_external_id=str(test_external_id))


@adapter_logger
def addTitle(test_title: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_title'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_title(test_title=str(test_title))


@adapter_logger
def addDescription(test_description: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_description'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_description(test_description=str(test_description))


@adapter_logger
def addLabels(*test_labels: str):
    if not hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_label'):
        return

    for test_label in test_labels:
        TmsPluginManager.get_plugin_manager().hook.add_label(test_label=str(test_label))

@adapter_logger
def addParameter(name: str, value: str):
    if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_parameter'):
        TmsPluginManager.get_plugin_manager().hook \
            .add_parameter(name=str(name), value=str(value))
