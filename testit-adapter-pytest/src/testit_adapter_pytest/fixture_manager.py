from testit_adapter_pytest.fixture_storage import ThreadContextFixtures
from testit_adapter_pytest.models.fixture import FixtureResult


class FixtureManager:
    def __init__(self):
        self._items = ThreadContextFixtures()
        self._orphan_items = []

    def _update_item(self, uuid, **kwargs):
        item = self._items[uuid] if uuid else self._items[next(reversed(self._items))]
        for name, value in kwargs.items():
            attr = getattr(item, name)
            if isinstance(attr, list):
                attr.append(value)
            else:
                setattr(item, name, value)

    def _last_executable(self):
        for _uuid in reversed(self._items):
            if isinstance(self._items[_uuid], FixtureResult):
                return _uuid

    def get_item(self, uuid):
        return self._items.get(uuid)

    def get_last_item(self, item_type=None):
        for _uuid in reversed(self._items):
            if item_type is None:
                return self._items.get(_uuid)
            if type(self._items[_uuid]) == item_type:
                return self._items.get(_uuid)

    def start_group(self, uuid, group):
        self._items[uuid] = group

    def stop_group(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)

    def update_group(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)

    def start_before_fixture(self, parent_uuid, uuid, fixture):
        self._items.get(parent_uuid).befores.append(fixture)
        self._items[uuid] = fixture

    def stop_before_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        self._items.pop(uuid)

    def start_after_fixture(self, parent_uuid, uuid, fixture):
        self._items.get(parent_uuid).afters.append(fixture)
        self._items[uuid] = fixture

    def stop_after_fixture(self, uuid, **kwargs):
        self._update_item(uuid, **kwargs)
        self._items.pop(uuid)

    def get_all_items(self):
        return self._items.get_all()
