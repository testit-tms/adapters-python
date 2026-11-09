from testit_adapter_behave.models.tags import TagType
from testit_adapter_behave.tags_parser import parse_test_tags


def test_parse_layer_tag():
    parsed = parse_test_tags(['Layer=API'])

    assert parsed[TagType.LAYER] == 'API'
