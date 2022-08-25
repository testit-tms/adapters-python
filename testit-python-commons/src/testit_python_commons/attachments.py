from testit_python_commons.services.plugin_manager import TmsPluginManager
from testit_python_commons.step import Step


class AddAttachments:
    def __call__(self, *attachments_paths: str):
        if Step.step_is_active():
            Step.add_attachments(attachments_paths)
        else:
            if hasattr(TmsPluginManager.get_plugin_manager().hook, 'add_attachments'):
                TmsPluginManager.get_plugin_manager().hook\
                    .add_attachments(attach_paths=attachments_paths)

    @staticmethod
    def create(body, name=None):
        if Step.step_is_active():
            Step.create_attachment(body, name)
        else:
            if hasattr(TmsPluginManager.get_plugin_manager().hook, 'create_attachment'):
                TmsPluginManager.get_plugin_manager().hook\
                    .create_attachment(body=body, name=name)
