from adapters_api.model.link_type import LinkType as ApiLinkType

from testit_python_commons.client.api_client import ApiClientWorker
from testit_python_commons.client.converter import Converter
from testit_python_commons.models.link import Link
from testit_python_commons.models.link_type import LinkType


def test_v2_dicts_to_link_api_results():
    links = Converter.v2_dicts_to_link_api_results([
        {
            "id": "l1",
            "url": "https://existing",
            "title": "Existing",
            "type": "Related",
            "description": None,
        },
        {"title": "no-url"},
    ])
    assert len(links) == 1
    assert links[0].id == "l1"
    assert links[0].url == "https://existing"
    assert links[0].type == ApiLinkType("Related")


def test_v2_dicts_to_attachment_stubs():
    stubs = Converter.v2_dicts_to_attachment_stubs([
        {"id": "att-1", "name": "a.txt"},
        {"name": "no-id"},
    ])
    assert len(stubs) == 1
    assert stubs[0].id == "att-1"


def test_v2_test_run_payload_to_model():
    model = Converter.v2_test_run_payload_to_model({
        "id": "run-1",
        "name": "TestRun_1",
        "description": "213123123",
        "launchSource": "Test IT",
        "tags": ["ui", {"name": "smoke"}],
        "links": [{"id": "l1", "url": "https://existing", "type": "Related"}],
        "attachments": [{"id": "att-1"}],
        "testResults": [{"id": "ignore-me"}],
    })
    assert model.id == "run-1"
    assert model.name == "TestRun_1"
    assert model.description == "213123123"
    assert model.launch_source == "Test IT"
    assert model.tags == ["ui", "smoke"]
    assert model.links[0].url == "https://existing"
    assert model.attachments[0].id == "att-1"


def test_build_update_keeps_v2_metadata_when_merging(mocker):
    test_run = Converter.v2_test_run_payload_to_model({
        "id": "run-id",
        "name": "name",
        "description": "desc",
        "launchSource": "Test IT",
        "tags": ["ui"],
        "links": [{"id": "l1", "url": "https://existing", "title": "Existing", "type": "Related"}],
        "attachments": [{"id": "att-1"}],
    })

    new_link = Link().set_url("https://ci.example/job/2").set_link_type(LinkType.RELATED)
    model = Converter.build_update_empty_request(
        test_run,
        tags=["smoke"],
        links=[new_link],
    )

    assert [link.url for link in model.links] == ["https://existing", "https://ci.example/job/2"]
    assert [a.id for a in model.attachments] == ["att-1"]
    assert model.tags == ["ui", "smoke"]
    assert model.description == "desc"
    assert model.launch_source == "Test IT"


class TestGetTestRunV2:
    def test_get_test_run_uses_v2_payload(self, mocker):
        mocker.patch.object(
            ApiClientWorker,
            "_ApiClientWorker__get_status_codes",
            return_value=["PASSED", "FAILED"],
        )
        mocker.patch.object(ApiClientWorker, "_ApiClientWorker__get_api_client_configuration")
        mocker.patch.object(ApiClientWorker, "_ApiClientWorker__get_api_client")
        mocker.patch("testit_python_commons.client.api_client.TestRunsApi")
        mocker.patch("testit_python_commons.client.api_client.AutoTestsApi")
        mocker.patch("testit_python_commons.client.api_client.AttachmentsApi")
        mocker.patch("testit_python_commons.client.api_client.TestResultsApi")
        mocker.patch("testit_python_commons.client.api_client.WorkItemsApi")
        mocker.patch("testit_python_commons.client.api_client.ProjectsApi")
        mocker.patch("testit_python_commons.client.api_client.WorkflowsApi")

        config = mocker.Mock()
        config.get_url.return_value = "https://tms.example"
        config.get_private_token.return_value = "token"
        config.get_cert_validation.return_value = True
        config.get_project_id.return_value = "proj"
        config.get_test_run_id.return_value = "run-1"
        config.get_configuration_id.return_value = "cfg-1"
        config.get_proxy.return_value = None

        worker = ApiClientWorker(config)
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_run_v2_json",
            return_value={
                "id": "run-1",
                "name": "run",
                "description": "desc",
                "launchSource": "Test IT",
                "tags": ["ui"],
                "links": [
                    {"id": "l1", "url": "https://link-1", "title": "L1", "type": "Related"},
                ],
                "attachments": [{"id": "att-1"}],
            },
        )

        result = worker.get_test_run("run-1")

        worker._ApiClientWorker__test_run_api.adapters_test_runs_id_get.assert_not_called()
        assert result.id == "run-1"
        assert result.description == "desc"
        assert result.launch_source == "Test IT"
        assert result.links[0].url == "https://link-1"
        assert result.attachments[0].id == "att-1"
        assert result.tags == ["ui"]
