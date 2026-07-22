from unittest.mock import Mock

from api_client_adapters.models import (
    CreateLinkApiModel,
    LinkCreateApiModel,
    LinkType,
    LinkUpdateApiModel,
    UpdateLinkApiModel,
)

from testit_python_commons.client.converter import Converter
from testit_python_commons.models.link import Link
from testit_python_commons.models.link_type import LinkType as AdapterLinkType


def test_link_to_link_put_model_without_has_info():
    link = (
        Link()
        .set_url('https://example.com')
        .set_title('Example')
        .set_link_type(AdapterLinkType.RELATED)
        .set_description('desc')
    )

    model = Converter.link_to_link_put_model(link)

    assert model == LinkUpdateApiModel(
        url='https://example.com',
        title='Example',
        type=LinkType('Related'),
        description='desc',
    )
    assert not hasattr(model, 'has_info')


def test_link_to_link_create_api_model_without_has_info():
    link = (
        Link()
        .set_url('https://example.com')
        .set_title('Example')
        .set_link_type(AdapterLinkType.RELATED)
    )

    model = Converter.link_to_link_create_api_model(link)

    assert model == LinkCreateApiModel(
        url='https://example.com',
        title='Example',
        type=LinkType('Related'),
        description=None,
    )


def test_build_update_link_api_model_without_has_info():
    link = Mock()
    link.id = 'link-id'
    link.title = 'title'
    link.description = 'description'
    link.type = LinkType('Related')
    link.url = 'https://example.com'

    model = Converter.build_update_link_api_model(link)

    assert model == UpdateLinkApiModel(
        id='link-id',
        title='title',
        description='description',
        type=LinkType('Related'),
        url='https://example.com',
    )


def test_build_create_link_api_model_without_has_info():
    link = Mock()
    link.title = 'title'
    link.description = 'description'
    link.type = LinkType('Related')
    link.url = 'https://example.com'

    model = Converter.build_create_link_api_model(link)

    assert model == CreateLinkApiModel(
        title='title',
        description='description',
        type=LinkType('Related'),
        url='https://example.com',
    )
