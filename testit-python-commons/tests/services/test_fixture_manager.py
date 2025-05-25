import pytest
import uuid

from testit_python_commons.services.fixture_manager import FixtureManager
from testit_python_commons.models.step_result import StepResult

class TestFixtureManager:
    @pytest.fixture
    def fixture_manager(self):
        manager = FixtureManager()
        manager._items.thread_context.clear()
        return manager

    @pytest.fixture
    def mock_fixture(self, mocker):
        fixture = mocker.MagicMock()
        return fixture

    def test_get_item_existing(self, fixture_manager, mock_fixture):
        test_uuid = str(uuid.uuid4())
        fixture_manager._items[test_uuid] = mock_fixture

        result = fixture_manager.get_item(test_uuid)
        assert result == mock_fixture

    def test_get_last_item_no_type(self, fixture_manager, mock_fixture, mocker):
        uuid1 = str(uuid.uuid4())
        uuid2 = str(uuid.uuid4())
        fixture_manager._items[uuid1] = mocker.MagicMock()
        fixture_manager._items[uuid2] = mock_fixture

        result = fixture_manager.get_last_item()
        assert result == mock_fixture

    def test_get_last_item_with_type(self, fixture_manager, mocker):
        uuid1 = str(uuid.uuid4())
        uuid2 = str(uuid.uuid4())
        uuid3 = str(uuid.uuid4())

        step_result = StepResult()
        fixture_manager._items[uuid1] = mocker.MagicMock()
        fixture_manager._items[uuid2] = step_result
        fixture_manager._items[uuid3] = mocker.MagicMock()

        result = fixture_manager.get_last_item(StepResult)
        assert result == step_result

    def test_start_group(self, fixture_manager, mock_fixture):
        test_uuid = str(uuid.uuid4())
        fixture_manager.start_group(test_uuid, mock_fixture)
        assert fixture_manager._items[test_uuid] == mock_fixture

    def test_stop_group(self, fixture_manager, mock_fixture):
        test_uuid = str(uuid.uuid4())
        fixture_manager._items[test_uuid] = mock_fixture
        fixture_manager.stop_group(test_uuid, status="completed", duration=100)

        assert mock_fixture.status == "completed"
        assert mock_fixture.duration == 100

    def test_update_group(self, fixture_manager, mock_fixture):
        test_uuid = str(uuid.uuid4())
        fixture_manager._items[test_uuid] = mock_fixture
        fixture_manager.update_group(test_uuid, name="UpdatedName")

        assert mock_fixture.name == "UpdatedName"

    def test_start_before_fixture(self, fixture_manager, mock_fixture, mocker):
        parent_uuid = str(uuid.uuid4())
        fixture_uuid = str(uuid.uuid4())

        mock_group = mocker.MagicMock()
        mock_group.befores = []
        fixture_manager._items[parent_uuid] = mock_group

        fixture_manager.start_before_fixture(parent_uuid, fixture_uuid, mock_fixture)
        assert mock_fixture in mock_group.befores
        assert fixture_manager._items[fixture_uuid] == mock_fixture

    def test_stop_before_fixture(self, fixture_manager, mock_fixture):
        fixture_uuid = str(uuid.uuid4())
        fixture_manager._items[fixture_uuid] = mock_fixture

        fixture_manager.stop_before_fixture(fixture_uuid, status="passed")

        assert mock_fixture.status == "passed"
        assert fixture_uuid not in fixture_manager._items

    def test_start_after_fixture(self, fixture_manager, mock_fixture, mocker):
        parent_uuid = str(uuid.uuid4())
        fixture_uuid = str(uuid.uuid4())

        mock_group = mocker.MagicMock()
        mock_group.afters = []
        fixture_manager._items[parent_uuid] = mock_group

        fixture_manager.start_after_fixture(parent_uuid, fixture_uuid, mock_fixture)

        assert mock_fixture in mock_group.afters
        assert fixture_manager._items[fixture_uuid] == mock_fixture

    def test_stop_after_fixture(self, fixture_manager, mock_fixture):
        fixture_uuid = str(uuid.uuid4())
        fixture_manager._items[fixture_uuid] = mock_fixture

        fixture_manager.stop_after_fixture(fixture_uuid, status="failed", error="Test error")

        assert mock_fixture.status == "failed"
        assert mock_fixture.error == "Test error"
        assert fixture_uuid not in fixture_manager._items

    def test_get_all_items(self, fixture_manager, mocker):
        expected_items = {
            str(uuid.uuid4()): mocker.MagicMock(),
            str(uuid.uuid4()): mocker.MagicMock()
        }

        for key, value in expected_items.items():
            fixture_manager._items[key] = value

        result = fixture_manager.get_all_items()

        assert result == expected_items