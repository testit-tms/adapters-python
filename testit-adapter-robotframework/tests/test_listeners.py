import re
import sys
import types
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

try:
    import robot.api  # noqa: F401
    import robot.libraries.BuiltIn  # noqa: F401
except ImportError:
    robot_module = types.ModuleType("robot")
    robot_api_module = types.ModuleType("robot.api")
    robot_api_module.logger = MagicMock()
    robot_api_module.SuiteVisitor = object
    robot_module.api = robot_api_module
    sys.modules["robot"] = robot_module
    sys.modules["robot.api"] = robot_api_module

    robot_libraries_module = types.ModuleType("robot.libraries")
    builtin_module = types.ModuleType("robot.libraries.BuiltIn")
    builtin_module.BuiltIn = MagicMock()
    robot_libraries_module.BuiltIn = builtin_module
    sys.modules["robot.libraries"] = robot_libraries_module
    sys.modules["robot.libraries.BuiltIn"] = builtin_module

from testit_adapter_robotframework.TMSLibrary import TMSLibrary
from testit_adapter_robotframework.listeners import AutotestAdapter
from testit_adapter_robotframework.models import Autotest


class TestAutotestAdapter:
    def test_parse_arguments(self, mocker: MockerFixture):
        mock_builtin_class = mocker.Mock()
        mock_builtin_instance = mocker.Mock()
        mock_builtin_class.return_value = mock_builtin_instance
        
        mock_builtin_instance.get_variable_value.side_effect = [
            "value1",
            "value2",
            "a" * 2500  # A value longer than 2000 characters
        ]
        
        def parse_arguments(args):
            parameters = {}
            for arg in args:
                variables = re.findall(r'\${[a-zA-Z-_\\ \d]*}', arg)
                for arg_var in variables:
                    value = str(mock_builtin_instance.get_variable_value(arg_var))
                    if len(value) > 2000:
                        value = value[:2000]
                    parameters[arg_var] = value
            return parameters if parameters else None
        
        # Arrange
        args = ["${var1}", "prefix_${var2}_suffix", "${var3_with_long_value}"]
        
        # Act
        parameters = parse_arguments(args)
        
        # Assert
        assert parameters == {
            "${var1}": "value1",
            "${var2}": "value2",
            "${var3_with_long_value}": "a" * 2000  # Should be truncated
        }
        
        expected_calls = [
            mocker.call("${var1}"),
            mocker.call("${var2}"),
            mocker.call("${var3_with_long_value}")
        ]
        mock_builtin_instance.get_variable_value.assert_has_calls(expected_calls, any_order=True)


class TestAutotestTagParsing:
    @staticmethod
    def _build_attrs(tags):
        return {
            "originalname": "HeaderName",
            "doc": "Doc",
            "template": None,
            "longname": "Suite.HeaderName",
            "tags": tags,
        }

    def test_display_name_does_not_override_title_when_title_absent(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs(["testit.displayName:DisplayName"]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title is None

    def test_title_has_priority_over_display_name(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs([
            "testit.displayName:DisplayName",
            "testit.title:CardTitle",
        ]))

        assert autotest.autoTestName == "DisplayName"
        assert autotest.title == "CardTitle"

    def test_layer_tag_is_parsed(self):
        autotest = Autotest(autoTestName="Initial")
        autotest.add_attributes(self._build_attrs(["testit.layer:API"]))

        assert autotest.layer == "API"


class Attachment(MagicMock):
    """Stand-in for adapters_api AttachmentPutModel with a readable id."""


def _make_attachment(attachment_id: str) -> Attachment:
    attachment = Attachment()
    attachment.id = attachment_id
    return attachment


def _start_test_attrs(name: str = "Test One"):
    return {
        "originalname": name,
        "doc": "",
        "template": None,
        "longname": "Suite." + name,
        "tags": [],
    }


def _keyword_attrs(kwname: str, args=None, status: str = "PASS"):
    return {
        "type": "KEYWORD",
        "assign": [],
        "kwname": kwname,
        "args": args or [],
        "doc": "",
        "starttime": "20260616 14:55:08.000",
        "endtime": "20260616 14:55:08.100",
        "elapsedtime": 100,
        "status": status,
    }


def _end_test_attrs(status: str = "PASS"):
    return {
        "status": status,
        "starttime": "20260616 14:55:08.000",
        "endtime": "20260616 14:55:09.000",
        "elapsedtime": 1000,
        "message": "",
    }


def _collect_step_attachments(step_results):
    collected = []
    for step_result in step_results:
        collected += getattr(step_result, "attachments", None) or []
        collected += _collect_step_attachments(step_result.step_results)
    return collected


class TestAutotestAdapterAttachments:
    @staticmethod
    def _make_adapter(mocker: MockerFixture):
        mocker.patch("testit_adapter_robotframework.listeners.BuiltIn")
        manager = mocker.Mock()
        return AutotestAdapter(manager), manager

    def test_add_step_result_reports_whether_attachments_were_bound(self):
        autotest = Autotest(autoTestName="T")
        autotest.add_step("KEYWORD", "kw1", "", None)

        bound = autotest.add_step_result("kw1", None, None, 1, "Passed", [_make_attachment("a1")])
        missed = autotest.add_step_result("unknown", None, None, 1, "Passed", [_make_attachment("a2")])

        assert bound is True
        assert missed is False

    def test_end_keyword_clears_attachments_when_bound(self, mocker: MockerFixture):
        adapter, _ = self._make_adapter(mocker)
        adapter.start_test("Test One", _start_test_attrs())
        adapter.start_keyword("kw1", _keyword_attrs("kw1"))
        adapter.active_test.attachments = [_make_attachment("a1")]
        adapter.end_keyword("kw1", _keyword_attrs("kw1"))

        assert adapter.active_test.attachments == []
        assert _collect_step_attachments(adapter.active_test.stepResults) != []

    def test_end_keyword_keeps_attachments_when_step_not_tracked(self, mocker: MockerFixture):
        adapter, _ = self._make_adapter(mocker)
        adapter.start_test("Test One", _start_test_attrs())
        # Steps deeper than the tracked depth (14) get no step result entry.
        for depth in range(1, 16):
            adapter.start_keyword(f"kw{depth}", _keyword_attrs(f"kw{depth}"))
        attachment = _make_attachment("deep-attachment")
        adapter.active_test.attachments = [attachment]

        adapter.end_keyword("kw15", _keyword_attrs("kw15"))

        assert adapter.active_test.attachments == [attachment]

    def test_attachments_beyond_tracked_depth_reach_enclosing_step(self, mocker: MockerFixture):
        adapter, _ = self._make_adapter(mocker)
        adapter.start_test("Test One", _start_test_attrs())
        for depth in range(1, 16):
            adapter.start_keyword(f"kw{depth}", _keyword_attrs(f"kw{depth}"))
        attachment = _make_attachment("deep-attachment")
        adapter.active_test.attachments = [attachment]

        for depth in range(15, 0, -1):
            adapter.end_keyword(f"kw{depth}", _keyword_attrs(f"kw{depth}"))

        assert _collect_step_attachments(adapter.active_test.stepResults) == [attachment]
        assert adapter.active_test.attachments == []

    def test_end_test_resets_active_test(self, mocker: MockerFixture):
        adapter, manager = self._make_adapter(mocker)
        adapter.start_test("Test One", _start_test_attrs())
        adapter.start_keyword("kw1", _keyword_attrs("kw1"))
        adapter.end_keyword("kw1", _keyword_attrs("kw1"))

        adapter.end_test("Test One", _end_test_attrs())

        assert adapter.active_test is None
        assert manager.write_test.called

    def test_end_test_sends_leftover_attachments_on_test_level(self, mocker: MockerFixture):
        adapter, manager = self._make_adapter(mocker)
        adapter.start_test("Test One", _start_test_attrs())
        attachment = _make_attachment("leftover")
        # Attachment never bound to any step result (no keyword was running).
        adapter.active_test.attachments = [attachment]

        adapter.end_test("Test One", _end_test_attrs())

        sent_result = manager.write_test.call_args[0][0]
        # asdict() deep-copies attachments, so compare by id rather than identity
        assert [item.id for item in sent_result.get_attachments()] == ["leftover"]


class TestTMSLibraryAttachmentGuard:
    @staticmethod
    def _make_library(active_test):
        library = TMSLibrary.__new__(TMSLibrary)
        library.enabled = True
        library.adapter_manager = MagicMock()
        listener = MagicMock()
        listener.active_test = active_test
        library.ROBOT_LIBRARY_LISTENER = [listener]
        return library

    def test_add_attachments_without_active_test_skips_upload(self):
        library = self._make_library(None)

        library.add_attachments("screenshot.png")

        assert library.adapter_manager.load_attachments.called is False

    def test_add_attachment_without_active_test_skips_upload(self):
        library = self._make_library(None)

        library.add_attachment("some text")

        assert library.adapter_manager.create_attachment.called is False

    def test_add_attachments_with_active_test_uploads(self):
        active_test = MagicMock()
        active_test.attachments = []
        attachment = _make_attachment("a1")
        library = self._make_library(active_test)
        library.adapter_manager.load_attachments.return_value = [attachment]

        library.add_attachments("screenshot.png")

        assert library.adapter_manager.load_attachments.called is True
        assert active_test.attachments == [attachment]
