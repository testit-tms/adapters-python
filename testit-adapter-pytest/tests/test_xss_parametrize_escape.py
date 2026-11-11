"""Ensure pytest parametrize XSS values are escaped in TestResult / API payload."""

from testit_adapter_pytest.models.executable_test import ExecutableTest
from testit_adapter_pytest.utils import convert_executable_test_to_test_result_model
from testit_python_commons.client.converter import Converter
from adapters_api import ApiClient


def test_parametrize_script_payload_escaped_in_parameters_and_external_key():
    payload = '<script>alert("1")</script>'
    executable = ExecutableTest(
        external_id="xss_ext",
        name=f"with xss {payload}",
        duration=1,
        parameters={"description": payload},
        properties={},
        namespace="tests",
        classname=None,
        title=None,
        description=None,
        links=[],
        labels=[],
        tags=[],
        work_item_ids=[],
        node_id=f"tests/test_xss_parametrize.py::test_05_with_chg_xss[{payload}]",
        outcome="Passed",
        status_type="Succeeded",
    )

    test_result = convert_executable_test_to_test_result_model(executable)
    assert test_result.get_parameters()["description"] == '&lt;script&gt;alert("1")&lt;/script&gt;'
    assert "<script>" not in test_result.get_autotest_name()
    assert "&lt;script&gt;" in test_result.get_external_key()

    model = Converter.test_result_to_testrun_result_post_model(
        test_result, "cfg", ["PASSED"])
    body = ApiClient.sanitize_for_serialization(model)
    assert body["parameters"]["description"] == '&lt;script&gt;alert("1")&lt;/script&gt;'
    assert "<script>" not in body["parameters"]["description"]
