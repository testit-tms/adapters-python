from types import SimpleNamespace

import pytest

from testit_adapter_pytest.utils import __get_layer_from


class _FakeMarker:
    def __init__(self, args=(), kwargs=None):
        self.args = args
        self.kwargs = kwargs or {}


class _FakeItem:
    def __init__(self, markers=None, function=None, cls=None):
        self._markers = markers or []
        self.function = function or SimpleNamespace()
        self.cls = cls

    def iter_markers(self, name=None):
        for marker in self._markers:
            if name is None or marker.name == name:
                yield marker


def test_get_layer_from_pytest_mark():
    item = _FakeItem(markers=[SimpleNamespace(name='layer', args=('API',), kwargs={})])

    assert __get_layer_from(item) == 'API'


def test_get_layer_from_decorator_attribute():
    function = SimpleNamespace(test_layer='UI')
    item = _FakeItem(function=function)

    assert __get_layer_from(item) == 'UI'


def test_get_layer_from_missing_returns_none():
    item = _FakeItem()

    assert __get_layer_from(item) is None
