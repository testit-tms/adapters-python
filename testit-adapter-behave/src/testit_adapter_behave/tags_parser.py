from .models.label import get_label_model
from .models.tags import TagType
from .models.url_link import get_url_link_model


def parse_tags(tags):
    parsed_tags = {
        TagType.LINKS: [],
        TagType.LABELS: [],
        TagType.WORK_ITEM_IDS: []
    }

    for tag in tags:
        if TagType.EXTERNAL_ID in tag:
            parsed_tags[TagType.EXTERNAL_ID] = tag[len(TagType.EXTERNAL_ID):]

        elif TagType.DISPLAY_NAME in tag:
            parsed_tags[TagType.DISPLAY_NAME] = tag[len(TagType.DISPLAY_NAME):]

        elif TagType.LINKS in tag:
            parsed_tags[TagType.LINKS].extend(
                parse_links(
                    tag[len(TagType.LINKS):]))

        elif TagType.TITLE in tag:
            parsed_tags[TagType.TITLE] = tag[len(TagType.TITLE):]

        elif TagType.WORK_ITEM_IDS in tag:
            parsed_tags[TagType.WORK_ITEM_IDS].extend(
                parse_massive(
                    tag[len(TagType.WORK_ITEM_IDS):]))

        elif TagType.DESCRIPTION in tag:
            parsed_tags[TagType.DESCRIPTION] = tag[len(TagType.DESCRIPTION):]

        elif TagType.LABELS in tag:
            parsed_tags[TagType.LABELS].extend(
                parse_labels(
                    tag[len(TagType.LABELS):]))

    return parsed_tags


def parse_massive(tag: str):
    return tag.split(',')


def parse_labels(tag):
    parsed_labels = []

    for label in parse_massive(tag):
        parsed_labels.append(get_label_model(label))

    return parsed_labels


def parse_links(tag: str):
    parsed_links = []
    json_links = parse_json(tag)

    if not json_links:
        for link in parse_massive(tag):
            parsed_links.append(get_url_link_model(link))

    if isinstance(json_links, tuple):
        parsed_links.extend(json_links)

    if isinstance(json_links, dict):
        parsed_links.append(json_links)

    return parsed_links


def parse_json(json_string: str):
    try:
        return eval(json_string)
    except Exception:
        return
