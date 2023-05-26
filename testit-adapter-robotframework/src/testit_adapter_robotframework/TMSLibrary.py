from robot.libraries.BuiltIn import BuiltIn

from testit_python_commons.services import TmsPluginManager

from .listeners import AutotestAdapter, TestRunAdapter
from .models import Option


def enabled(func):
    def wrapped(self, *args, **kwargs):
        if self.enabled:
            return func(self, *args, **kwargs)
        else:
            raise ImportError("TestIt module should be enabled. Use '-v testit' CLI option")

    return wrapped


class TMSLibrary:
    """Library for exporting result to TestIt.

        = Table of contents =

        %TOC%

        = Usage =

        This library has several keyword, for example `Add Link`, adding links to result of test in TestIt

        = Examples =

        | `Add Message`      | My message    |                |               |
        | `Add Link`         | http://ya.ru  |                |               |
        | `Add Attachments`  | image.png     | log.txt        | video.gif     |
        """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0'

    def __init__(self):
        built_in = BuiltIn()
        self.enabled = built_in.get_variable_value("${testit}", None) is not None
        if self.enabled:
            cli_params = ["tmsUrl", "tmsPrivateToken", "tmsProjectId",
                          "tmsConfigurationId", "tmsTestRunId", "tmsTestRunName",
                          "tmsAdapterMode", "tmsConfigFile", "tmsCertValidation", "tmsAutomaticCreationTestCases"]
            option = Option(**{param: built_in.get_variable_value(f'${{{param}}}', None) for param in cli_params})
            self.adapter_manager = TmsPluginManager.get_adapter_manager(option)
            pabot_index = built_in.get_variable_value('${PABOTQUEUEINDEX}', None)
            if pabot_index is not None:
                try:
                    from pabot import PabotLib
                    pabot = PabotLib()
                    if int(pabot_index) == 0:
                        test_run_id = self.adapter_manager.get_test_run_id()
                        pabot.set_parallel_value_for_key('test_run_id', test_run_id)
                    else:
                        while True:
                            test_run_id = pabot.get_parallel_value_for_key('test_run_id')
                            if test_run_id:
                                break
                    self.adapter_manager.set_test_run_id(test_run_id)
                except RuntimeError:
                    raise SystemExit
            else:
                self.adapter_manager.set_test_run_id(self.adapter_manager.get_test_run_id())
            self.ROBOT_LIBRARY_LISTENER = [AutotestAdapter(self.adapter_manager), TestRunAdapter(self.adapter_manager)]

    @enabled
    def add_link(self, url, type='Defect', title=None, description=None):  # noqa: A002,VNE003
        """
        Adds link to current test.

        Valid link types are ``Defect``, ``Issue``, ``Related``, ``BlockedBy``, ``Requirement``, ``Repository``.

        """
        from testit_python_commons.models.link import Link

        link = Link()\
            .set_url(url)\
            .set_title(title)\
            .set_link_type(type)\
            .set_description(description)
        self.ROBOT_LIBRARY_LISTENER[0].active_test.resultLinks.append(link)

    @enabled
    def add_links(self, *links):
        """
        Adds several links to current test.

        Every link should be a dict with ``url`` key. See `Add Link` keyword for more information.

        """
        for link in links:
            if isinstance(link, dict):
                self.add_link(**link)

    @enabled
    def add_attachments(self, *paths):
        """
        Adds several attachments to current test.

        """
        attachments = self.adapter_manager.load_attachments(paths)
        self.ROBOT_LIBRARY_LISTENER[0].active_test.attachments.extend(attachments)

    @enabled
    def add_attachment(self, text, filename=None):
        """
        Adds attachment to current test

        """
        attachment = self.adapter_manager.create_attachment(text, filename)
        self.ROBOT_LIBRARY_LISTENER[0].active_test.attachments.extend(attachment)

    @enabled
    def add_message(self, message):
        """
        Adds error message to current test
        """
        self.ROBOT_LIBRARY_LISTENER[0].active_test.message = message
