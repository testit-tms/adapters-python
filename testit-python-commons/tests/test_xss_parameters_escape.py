"""Regression: XSS in pytest params must be escaped before TMS API payloads."""

import importlib.util
import unittest
from pathlib import Path

from adapters_api import ApiClient
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_result import TestResult
from testit_python_commons.utils.html_escape_utils import HtmlEscapeUtils


def _load_xss_payloads():
    path = Path(__file__).resolve().parents[2] / "test_files" / "test_xss_parametrize.py"
    spec = importlib.util.spec_from_file_location("test_xss_parametrize", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.XSS_PAYLOADS


class TestXssParametersEscape(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payloads = _load_xss_payloads()

    def test_test_result_parameters_escaped_for_all_payloads(self):
        for payload in self.payloads:
            with self.subTest(payload=payload):
                result = TestResult().set_parameters({"description": payload})
                value = result.get_parameters()["description"]
                if HtmlEscapeUtils._HTML_TAG_PATTERN.search(payload):
                    self.assertNotIn("<script", value.lower().replace("&lt;", ""))
                    self.assertIn("&lt;", value)
                    self.assertNotEqual(value, payload)
                # API model must keep escaped value
                model = Converter.test_result_to_testrun_result_post_model(
                    result.set_external_id("ext").set_outcome("Passed").set_status_type("Succeeded").set_duration(1),
                    "cfg",
                    ["PASSED"],
                )
                self.assertEqual(model.parameters["description"], value)
                serialized = ApiClient.sanitize_for_serialization(model)
                self.assertEqual(serialized["parameters"]["description"], value)

    def test_external_key_with_nodeid_xss_is_escaped(self):
        payload = '<script>alert("1")</script>'
        node_key = f"tests and test_xss_parametrize.py and test_05_with_chg_xss[{payload}]"
        result = TestResult().set_external_key(node_key)
        escaped = result.get_external_key()
        self.assertIn("&lt;script&gt;", escaped)
        self.assertNotIn("<script>", escaped)

    def test_bulk_list_escape_mutates_result_models(self):
        payload = '<script>alert("1")</script>'
        # Simulate model built WITHOUT going through TestResult setters (raw params)
        class FakeResult:
            def __init__(self):
                self.parameters = {"description": payload}
                self.message = payload

        models = [FakeResult(), FakeResult()]
        HtmlEscapeUtils.escape_html_in_object(models)
        for model in models:
            self.assertEqual(
                model.parameters["description"],
                '&lt;script&gt;alert("1")&lt;/script&gt;',
            )
            self.assertEqual(model.message, '&lt;script&gt;alert("1")&lt;/script&gt;')


if __name__ == "__main__":
    unittest.main()
