from testit_python_commons.models.link import Link
from testit_python_commons.models.link_type import LinkType



def get_url_to_link_model(url: str) -> Link:
    return Link() \
        .set_url(url) \
        .set_link_type(LinkType.RELATED)


def get_dict_to_link_model(link: dict) -> Link:
    return Link() \
        .set_url(link['url']) \
        .set_title(link.get('title', None)) \
        .set_link_type(link.get('type', LinkType.RELATED)) \
        .set_description(link.get('description', None))
