import pytest

from testit_adapter_pytest.utils import (
    collect_parameters_in_string_attribute,
    get_all_parameters,
    get_parameter,
)


class _FakeItem:
    def __init__(self, callspec_params=None, test_properties=None):
        if callspec_params is not None:
            self.callspec = type('CallSpec', (), {'params': callspec_params})()
        if test_properties is not None:
            self.test_properties = test_properties


def test_expand_dict_keys_from_fixture_params():
    item = _FakeItem(callspec_params={
        'users_prepare_fixture_all_active_param': {
            'user_type': 'viewer',
            'nnumber': 3,
        },
    })
    params = get_all_parameters(item)

    assert params['user_type'] == 'viewer'
    assert params['users_prepare_fixture_all_active_param']['user_type'] == 'viewer'


def test_placeholder_user_type_from_fixture_dict_param():
    item = _FakeItem(callspec_params={
        'users_prepare_fixture_all_active_param': {'user_type': 'consultant'},
    })
    result = collect_parameters_in_string_attribute(
        'Получение Информации о (positive) [{user_type}]',
        get_all_parameters(item),
    )

    assert result == 'Получение Информации о (positive) [consultant]'


def test_bracket_syntax_with_underscore_key():
    params = {'fixture_param': {'user_type': 'admin'}}
    assert get_parameter('fixture_param[user_type]', params) == 'admin'


def test_top_level_param_not_overwritten_by_dict_expand():
    item = _FakeItem(callspec_params={
        'user_type': 'from_parametrize',
        'fixture_param': {'user_type': 'from_dict'},
    })
    params = get_all_parameters(item)

    assert params['user_type'] == 'from_parametrize'
