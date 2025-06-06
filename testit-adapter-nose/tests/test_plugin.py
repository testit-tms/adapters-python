import pytest
from pytest_mock import MockerFixture

from testit_adapter_nose.plugin import TmsPlugin


class TestTmsPlugin:
    def test_handleDir(self, mocker: MockerFixture):
        plugin = TmsPlugin()
        mock_event = mocker.Mock()
        mock_event.topLevelDirectory = "/test/directory"

        assert plugin._TmsPlugin__top_level_directory is None

        plugin.handleDir(mock_event)

        assert plugin._TmsPlugin__top_level_directory == "/test/directory"

        # Calling it again should not change the value
        mock_event_another = mocker.Mock()
        mock_event_another.topLevelDirectory = "/another/directory"
        plugin.handleDir(mock_event_another)

        assert plugin._TmsPlugin__top_level_directory == "/test/directory" 