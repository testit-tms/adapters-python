from unittest.mock import Mock

from api_client_adapters.models import LabelApiModel

from testit_python_commons.client.converter import Converter


def test_labels_to_label_api_models_from_string():
    result = Converter.labels_to_label_api_models(['smoke', 'regression'])

    assert len(result) == 2
    assert result[0] == LabelApiModel(name='smoke', global_id=0)
    assert result[1] == LabelApiModel(name='regression', global_id=0)


def test_labels_to_label_api_models_from_dict():
    result = Converter.labels_to_label_api_models([
        {'name': 'smoke'},
        {'name': 'regression', 'global_id': 42},
        {'name': 'legacy', 'globalId': 7},
    ])

    assert result == [
        LabelApiModel(name='smoke', global_id=0),
        LabelApiModel(name='regression', global_id=42),
        LabelApiModel(name='legacy', global_id=7),
    ]


def test_labels_to_label_api_models_empty():
    assert Converter.labels_to_label_api_models([]) is None
    assert Converter.labels_to_label_api_models(None) is None


def test_create_autotest_request_accepts_labels_from_adapter():
    test_result = Mock()
    test_result.get_external_id.return_value = 'ext-1'
    test_result.get_autotest_name.return_value = 'test name'
    test_result.get_step_results.return_value = []
    test_result.get_setup_results.return_value = []
    test_result.get_teardown_results.return_value = []
    test_result.get_namespace.return_value = 'ns'
    test_result.get_classname.return_value = 'cls'
    test_result.get_title.return_value = 'title'
    test_result.get_description.return_value = None
    test_result.get_links.return_value = []
    test_result.get_labels.return_value = [{'name': 'smoke'}]
    test_result.get_tags.return_value = []
    test_result.get_automatic_creation_test_cases.return_value = False
    test_result.get_external_key.return_value = None

    request = Converter.test_result_to_create_autotest_request(test_result, 'project-id')

    assert request.labels == [LabelApiModel(name='smoke', global_id=0)]
