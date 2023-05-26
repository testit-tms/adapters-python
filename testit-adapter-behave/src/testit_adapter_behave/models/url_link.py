from testit_python_commons.models.link import Link


def get_url_to_link_model(url: str) -> Link:
    return Link() \
        .set_url(url)


def get_dict_to_link_model(link: dict) -> Link:
    return Link() \
        .set_url(link['url']) \
        .set_title(link.get('title', None)) \
        .set_link_type(link.get('type', None)) \
        .set_description(link.get('description', None))
