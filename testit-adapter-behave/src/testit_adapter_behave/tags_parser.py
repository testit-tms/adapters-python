from .models.label import get_label_model
from .models.tags import TagType
from .models.url_link import get_url_to_link_model, get_dict_to_link_model


def parse_test_tags(tags):
    parsed_tags = {
        TagType.LINKS: [],
        TagType.TAGS: [],
        TagType.WORK_ITEM_IDS: []
    }

    for tag in tags:
        if TagType.EXTERNAL_ID in tag:
            parsed_tags[TagType.EXTERNAL_ID] = __parse_space_in_tag(tag[len(TagType.EXTERNAL_ID):])

        elif TagType.DISPLAY_NAME in tag:
            parsed_tags[TagType.DISPLAY_NAME] = __parse_space_in_tag(tag[len(TagType.DISPLAY_NAME):])

        elif TagType.LINKS in tag:
            parsed_tags[TagType.LINKS].extend(
                __parse_links(
                    tag[len(TagType.LINKS):]))

        elif TagType.TITLE in tag:
            parsed_tags[TagType.TITLE] = __parse_space_in_tag(tag[len(TagType.TITLE):])

        elif TagType.WORK_ITEM_IDS in tag:
            parsed_tags[TagType.WORK_ITEM_IDS].extend(
                __parse_massive(
                    tag[len(TagType.WORK_ITEM_IDS):]))

        elif TagType.DESCRIPTION in tag:
            parsed_tags[TagType.DESCRIPTION] = __parse_space_in_tag(tag[len(TagType.DESCRIPTION):])

        elif TagType.LABELS in tag:
            parsed_tags[TagType.LABELS].extend(
                __parse_labels(
                    tag[len(TagType.LABELS):]))

        elif TagType.TAGS in tag:
            parsed_tags[TagType.TAGS].extend(
                __parse_tags(
                    tag[len(TagType.TAGS):]))

        elif TagType.NAMESPACE in tag:
            parsed_tags[TagType.NAMESPACE] = __parse_space_in_tag(tag[len(TagType.NAMESPACE):])

        elif TagType.CLASSNAME in tag:
            parsed_tags[TagType.CLASSNAME] = __parse_space_in_tag(tag[len(TagType.CLASSNAME):])

    return parsed_tags


def __parse_massive(tag: str):
    return tag.split(',')


def __parse_labels(tag):
    parsed_labels = []

    for label in __parse_massive(tag):
        parsed_labels.append(get_label_model(label))

    return parsed_labels


def __parse_tags(tag):
    parsed_tags = []

    for tms_tag in __parse_massive(tag):
        parsed_tags.append(tms_tag)

    return parsed_tags


def __parse_links(tag: str):
    parsed_links = []
    json_links = __parse_json(tag)

    if not json_links:
        for url in __parse_massive(tag):
            parsed_links.append(get_url_to_link_model(url))

    if isinstance(json_links, tuple):
        for url in json_links:
            parsed_links.append(get_url_to_link_model(url))

    if isinstance(json_links, dict):
        parsed_links.append(get_dict_to_link_model(json_links))

    return parsed_links


def __parse_json(json_string: str):
    try:
        return eval(json_string)
    except Exception:
        return


def __parse_space_in_tag(tag: str) -> str:
    return tag.replace('\\_', ' ')
