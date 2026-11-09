from unittest.mock import Mock

from adapters_api.models import LayerSource

from testit_python_commons.client.converter import Converter
from testit_python_commons.models.test_layers import TestLayers


def _mock_test_result(**overrides):
    test_result = Mock()
    defaults = {
        'get_external_id': 'ext-1',
        'get_autotest_name': 'test name',
        'get_step_results': [],
        'get_setup_results': [],
        'get_teardown_results': [],
        'get_namespace': 'ns',
        'get_classname': 'cls',
        'get_title': 'title',
        'get_description': None,
        'get_links': [],
        'get_labels': [],
        'get_tags': [],
        'get_automatic_creation_test_cases': False,
        'get_external_key': None,
        'get_layer': None,
    }
    for key, value in defaults.items():
        getter = overrides.pop(key, value)
        getattr(test_result, key).return_value = getter
    return test_result


def test_layer_to_api_model_with_recommended_constant():
    layer = Converter.layer_to_api_model(TestLayers.API)

    assert layer.name == 'API'
    assert layer.source == LayerSource('Run')


def test_layer_to_api_model_with_custom_string():
    layer = Converter.layer_to_api_model('my-custom-layer')

    assert layer.name == 'my-custom-layer'
    assert layer.source == LayerSource('Run')


def test_layer_to_api_model_empty():
    assert Converter.layer_to_api_model(None) is None
    assert Converter.layer_to_api_model('') is None
    assert Converter.layer_to_api_model('   ') is None


def test_create_autotest_request_includes_layer_when_set():
    test_result = _mock_test_result(get_layer='API')

    request = Converter.test_result_to_create_autotest_request(test_result, 'project-id')

    assert request.layer.name == 'API'
    assert request.layer.source == LayerSource('Run')


def test_create_autotest_request_omits_layer_when_not_set():
    test_result = _mock_test_result()

    request = Converter.test_result_to_create_autotest_request(test_result, 'project-id')

    assert 'layer' not in request._data_store


def test_update_autotest_request_includes_layer_and_reset_layer_when_set():
    test_result = _mock_test_result(get_layer='API')

    request = Converter.test_result_to_update_autotest_request(test_result, 'project-id')

    assert request.layer.name == 'API'
    assert request.layer.source == LayerSource('Run')
    assert request.reset_layer is False


def test_update_autotest_request_always_includes_reset_layer_false():
    test_result = _mock_test_result()

    request = Converter.test_result_to_update_autotest_request(test_result, 'project-id')

    assert request.reset_layer is False
    assert 'layer' not in request._data_store


def test_bulk_update_model_includes_reset_layer_false_when_layer_set():
    test_result = _mock_test_result(get_layer='API')

    model = Converter.test_result_to_autotest_put_model(test_result, 'project-id')

    assert model.layer.name == 'API'
    assert model.reset_layer is False


def test_bulk_update_model_always_includes_reset_layer_false():
    test_result = _mock_test_result()

    model = Converter.test_result_to_autotest_put_model(test_result, 'project-id')

    assert model.reset_layer is False
    assert 'layer' not in model._data_store
