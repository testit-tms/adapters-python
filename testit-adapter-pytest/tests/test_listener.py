import pytest
from unittest.mock import MagicMock

from testit_adapter_pytest.listener import TmsListener


class TestTmsListener:
    def test_add_link_appends_link(self, mocker):
        # Arrange
        mock_adapter_manager = mocker.MagicMock()
        mock_step_manager = mocker.MagicMock()
        mock_fixture_manager = mocker.MagicMock()

        listener = TmsListener(
            adapter_manager=mock_adapter_manager,
            step_manager=mock_step_manager,
            fixture_manager=mock_fixture_manager
        )

        # Mock the __executable_test attribute
        mock_executable_test = mocker.MagicMock()
        mock_executable_test.result_links = []
        listener._TmsListener__executable_test = mock_executable_test

        test_link = {"url": "http://example.com", "title": "Example"}

        # Act
        listener.add_link(test_link)

        # Assert
        assert len(mock_executable_test.result_links) == 1
        assert mock_executable_test.result_links[0] == test_link

    def test_add_link_does_nothing_if_no_executable_test(self, mocker):
        # Arrange
        mock_adapter_manager = mocker.MagicMock()
        mock_step_manager = mocker.MagicMock()
        mock_fixture_manager = mocker.MagicMock()

        listener = TmsListener(
            adapter_manager=mock_adapter_manager,
            step_manager=mock_step_manager,
            fixture_manager=mock_fixture_manager
        )
        listener._TmsListener__executable_test = None  # Ensure __executable_test is None

        test_link = {"url": "http://example.com", "title": "Example"}

        # Act
        listener.add_link(test_link)

        # Assert
        # No direct assertion on links, but we ensure no error and __executable_test remains None
        # If __executable_test had a result_links attribute, we would check it's still empty.
        # For this case, the main check is that no AttributeError occurs.
        assert listener._TmsListener__executable_test is None 