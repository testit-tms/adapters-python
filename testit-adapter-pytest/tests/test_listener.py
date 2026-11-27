from types import SimpleNamespace

import pytest
from unittest.mock import MagicMock

from testit_adapter_pytest.listener import TmsListener
from testit_adapter_pytest.utils import (
    OUTCOME_XFAILED,
    OUTCOME_XPASSED,
    resolve_xfail_outcome,
)
from testit_python_commons.models.status_type import StatusType


class TestResolveXfailOutcome:
    def test_xfailed_maps_to_succeeded(self):
        report = SimpleNamespace(
            wasxfail='reason',
            passed=False,
            failed=False,
            outcome='skipped',
        )

        result = resolve_xfail_outcome(report)

        assert result.outcome == OUTCOME_XFAILED
        assert result.status_type == StatusType.SUCCEEDED

    def test_xpassed_non_strict_maps_to_failed(self):
        report = SimpleNamespace(
            wasxfail='reason',
            passed=True,
            failed=False,
            outcome='passed',
        )

        result = resolve_xfail_outcome(report)

        assert result.outcome == OUTCOME_XPASSED
        assert result.status_type == StatusType.FAILED

    def test_xpassed_strict_maps_to_failed_not_xfailed(self):
        report = SimpleNamespace(
            wasxfail='reason',
            passed=False,
            failed=True,
            outcome='failed',
        )

        result = resolve_xfail_outcome(report)

        assert result.outcome == OUTCOME_XPASSED
        assert result.status_type == StatusType.FAILED

    def test_without_wasxfail_returns_none(self):
        report = SimpleNamespace(
            passed=True,
            failed=False,
            outcome='passed',
        )

        assert resolve_xfail_outcome(report) is None


class TestPytestRuntestLogreportXfail:
    def _make_listener(self):
        listener = TmsListener(
            adapter_manager=MagicMock(),
            step_manager=MagicMock(),
            fixture_manager=MagicMock(),
        )
        executable_test = MagicMock()
        executable_test.duration = 0
        executable_test.message = None
        listener._TmsListener__executable_test = executable_test
        return listener, executable_test

    def test_logreport_sets_xfailed(self):
        listener, executable_test = self._make_listener()
        report = SimpleNamespace(
            when='call',
            outcome='skipped',
            passed=False,
            failed=False,
            wasxfail='expected',
            duration=0.01,
            longrepr=None,
            longreprtext='xfail traceback',
        )

        listener.pytest_runtest_logreport(report)

        assert executable_test.outcome == OUTCOME_XFAILED
        assert executable_test.status_type == StatusType.SUCCEEDED
        assert executable_test.traces == 'xfail traceback'

    def test_logreport_sets_xpassed_non_strict(self):
        listener, executable_test = self._make_listener()
        report = SimpleNamespace(
            when='call',
            outcome='passed',
            passed=True,
            failed=False,
            wasxfail='expected',
            duration=0.01,
            longrepr=None,
            longreprtext=None,
        )

        listener.pytest_runtest_logreport(report)

        assert executable_test.outcome == OUTCOME_XPASSED
        assert executable_test.status_type == StatusType.FAILED

    def test_logreport_sets_xpassed_strict_over_failed(self):
        listener, executable_test = self._make_listener()
        report = SimpleNamespace(
            when='call',
            outcome='failed',
            passed=False,
            failed=True,
            wasxfail='expected',
            duration=0.01,
            longrepr=None,
            longreprtext='[XPASS(strict)] expected',
        )

        listener.pytest_runtest_logreport(report)

        assert executable_test.outcome == OUTCOME_XPASSED
        assert executable_test.status_type == StatusType.FAILED
        assert executable_test.traces == '[XPASS(strict)] expected'


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