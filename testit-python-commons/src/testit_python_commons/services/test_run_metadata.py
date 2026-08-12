import json
import logging
from typing import List, Optional

from testit_python_commons.models.link import Link
from testit_python_commons.services.utils import Utils


def parse_test_run_tags(raw: Optional[str]) -> List[str]:
    if not raw or not str(raw).strip():
        return []

    value = str(raw).strip()
    if value.startswith('['):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            logging.warning('Invalid test run tags JSON: %s', value)
            return []
        if not isinstance(parsed, list):
            logging.warning('Test run tags JSON must be an array: %s', value)
            return []
        return [str(tag).strip() for tag in parsed if str(tag).strip()]

    return [tag.strip() for tag in value.split(',') if tag.strip()]


def parse_test_run_links(raw: Optional[str]) -> List[Link]:
    if not raw or not str(raw).strip():
        return []

    value = str(raw).strip()
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        logging.warning('Invalid test run links JSON: %s', value)
        return []

    if not isinstance(parsed, list):
        logging.warning('Test run links JSON must be an array: %s', value)
        return []

    links = []
    for item in parsed:
        if not isinstance(item, dict) or not item.get('url'):
            logging.warning('Skipping invalid test run link (url is required): %s', item)
            continue
        links.append(Utils.convert_link_dict_to_link_model(item))

    return links
