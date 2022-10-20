import json
from .tags import TagType


def parse_tags(tags):
    parsed_tags = {
        TagType.LINKS: [],
        TagType.LABELS: [],
        TagType.WORK_ITEM_IDS: []
    }

    for tag in tags:
        if TagType.EXTERNAL_ID in tag:
            parsed_tags[TagType.EXTERNAL_ID] = tag[:len(TagType.EXTERNAL_ID)]

        elif TagType.DISPLAY_NAME in tag:
            parsed_tags[TagType.DISPLAY_NAME] = tag[:len(TagType.DISPLAY_NAME)]

        elif TagType.LINKS in tag:
            parsed_tags[TagType.LINKS].extend(
                parse_links(
                    tag[:len(TagType.LINKS)]))

        elif TagType.TITLE in tag:
            parsed_tags[TagType.TITLE] = tag[:len(TagType.TITLE)]

        elif TagType.WORK_ITEM_IDS in tag:
            parsed_tags[TagType.WORK_ITEM_IDS].extend(
                parse_massive(
                    tag[:len(TagType.WORK_ITEM_IDS)]))

        elif TagType.DESCRIPTION in tag:
            parsed_tags[TagType.DESCRIPTION] = tag[:len(TagType.DESCRIPTION)]

        elif TagType.LABELS in tag:
            parsed_tags[TagType.LABELS].extend(
                parse_massive(
                    tag[:len(TagType.LABELS)]))


def parse_massive(tag: str):
    return tag.split(',')


def parse_links(tag: str):
    json_links = parse_json(tag)

    if not json_links:
        return tag.split(',')

    return json_links


def parse_json(json_string: str):
    try:
        return json.load(json_string)
    except Exception:
        return
