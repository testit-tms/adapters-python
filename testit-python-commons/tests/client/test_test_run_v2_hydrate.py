from types import SimpleNamespace

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


def test_build_update_keeps_v2_links_and_attachments_when_merging(mocker):
    existing_link = Converter.v2_dicts_to_link_api_results([
        {"id": "l1", "url": "https://existing", "title": "Existing", "type": "Related"},
    ])[0]
    test_run = mocker.Mock()
    test_run.id = "run-id"
    test_run.name = "name"
    test_run.description = None
    test_run.launch_source = None
    test_run.tags = ["ui"]
    test_run.links = [existing_link]
    test_run.attachments = [SimpleNamespace(id="att-1")]

    new_link = Link().set_url("https://ci.example/job/2").set_link_type(LinkType.RELATED)
    model = Converter.build_update_empty_request(
        test_run,
        tags=["smoke"],
        links=[new_link],
    )

    assert [link.url for link in model.links] == ["https://existing", "https://ci.example/job/2"]
    assert [a.id for a in model.attachments] == ["att-1"]
    assert model.tags == ["ui", "smoke"]


class TestGetTestRunHydrate:
    def test_get_test_run_overlays_links_and_attachments_from_v2(self, mocker):
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
        adapters_run = mocker.Mock(id="run-1", name="run", tags=["ui"], links=[], attachments=[])
        worker._ApiClientWorker__test_run_api.adapters_test_runs_id_get.return_value = adapters_run
        mocker.patch.object(
            worker,
            "_ApiClientWorker__get_test_run_v2_json",
            return_value={
                "links": [
                    {"id": "l1", "url": "https://link-1", "title": "L1", "type": "Related"},
                ],
                "attachments": [{"id": "att-1"}],
            },
        )

        result = worker.get_test_run("run-1")

        assert result is adapters_run
        assert len(result.links) == 1
        assert result.links[0].url == "https://link-1"
        assert [a.id for a in result.attachments] == ["att-1"]
