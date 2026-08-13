from adapters_api.model.link_api_result import LinkApiResult
from adapters_api.model.link_type import LinkType as ApiLinkType

from testit_python_commons.client.converter import Converter
from testit_python_commons.models.link import Link
from testit_python_commons.models.link_type import LinkType
from testit_python_commons.services.test_run_metadata import parse_test_run_links, parse_test_run_tags


def test_parse_test_run_tags_comma_separated():
    assert parse_test_run_tags('smoke, nightly') == ['smoke', 'nightly']


def test_parse_test_run_tags_json_array():
    assert parse_test_run_tags('["smoke", "nightly"]') == ['smoke', 'nightly']


def test_parse_test_run_tags_invalid_json_returns_empty():
    assert parse_test_run_tags('[smoke') == []


def test_parse_test_run_links_json():
    links = parse_test_run_links(
        '[{"url":"https://ci.example/job/1","title":"CI Job","type":"Related"}]'
    )
    assert len(links) == 1
    assert links[0].get_url() == 'https://ci.example/job/1'
    assert links[0].get_title() == 'CI Job'
    assert links[0].get_link_type() == LinkType.RELATED


def test_parse_test_run_links_skips_items_without_url():
    links = parse_test_run_links('[{"title":"no-url"},{"url":"https://ok"}]')
    assert len(links) == 1
    assert links[0].get_url() == 'https://ok'


def test_create_test_run_model_includes_tags_and_links():
    link = Link().set_url('https://ci.example/job/1').set_title('CI').set_link_type(LinkType.RELATED)
    model = Converter.test_run_to_test_run_short_model(
        'project-id',
        'run-name',
        tags=['smoke'],
        links=[link],
    )
    assert model.tags == ['smoke']
    assert len(model.links) == 1
    assert model.links[0].url == 'https://ci.example/job/1'


def test_build_update_empty_request_without_description_attr(mocker):
    """Adapters TestRunApiResult has no description/launch_source — must not raise."""
    test_run = mocker.Mock(spec=['id', 'name', 'attachments', 'links', 'tags'])
    test_run.id = 'run-id'
    test_run.name = 'name'
    test_run.attachments = []
    test_run.links = []
    test_run.tags = ['ui']
    # Simulate OpenAPI ApiAttributeError on missing fields
    type(test_run).description = property(
        lambda self: (_ for _ in ()).throw(AttributeError('description')))
    type(test_run).launch_source = property(
        lambda self: (_ for _ in ()).throw(AttributeError('launch_source')))

    model = Converter.build_update_empty_request(test_run, tags=['smoke'], links=[])
    assert model.tags == ['ui', 'smoke']
    assert 'description' not in model
    assert 'launch_source' not in model


def test_build_update_empty_request_merges_tags_and_links(mocker):
    existing_link = LinkApiResult(
        id='link-1',
        url='https://existing',
        title='Existing',
        type=ApiLinkType('Related'),
        description=None,
    )
    test_run = mocker.Mock()
    test_run.id = 'run-id'
    test_run.name = 'name'
    test_run.description = None
    test_run.launch_source = None
    test_run.attachments = []
    test_run.links = [existing_link]
    test_run.tags = ['ui']

    new_link = Link().set_url('https://ci.example/job/1').set_link_type(LinkType.RELATED)
    model = Converter.build_update_empty_request(
        test_run,
        tags=['ui', 'smoke'],
        links=[new_link],
    )

    assert model.tags == ['ui', 'smoke']
    assert [link.url for link in model.links] == ['https://existing', 'https://ci.example/job/1']
