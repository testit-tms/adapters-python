import pytest

from testit_python_commons.services.step_manager import StepManager
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.services.step_result_storage import StepResultStorage

class TestStepManager:
    @pytest.fixture
    def step_manager(self, mock_step_result_storage):
        return StepManager()

    @pytest.fixture
    def mock_step_result(self, mocker):
        step = mocker.Mock(spec=StepResult)
        step.get_step_results.return_value = []
        step.set_step_results.return_value = step
        return step

    @pytest.fixture
    def mock_step_result_storage(self, mocker):
        mock_storage = mocker.Mock(spec=StepResultStorage)
        mocker.patch('testit_python_commons.services.step_manager.StepResultStorage', return_value=mock_storage)
        return mock_storage

    def test_start_step_with_empty_storage(self, step_manager, mock_step_result, mock_step_result_storage):
        mock_step_result_storage.get_count.return_value = 0
        step_manager.start_step(mock_step_result)
        mock_step_result_storage.get_count.assert_called_once()
        mock_step_result_storage.add.assert_called_once_with(mock_step_result)
        mock_step_result.get_step_results.assert_not_called()

    def test_stop_step_when_not_last_step(self, step_manager, mock_step_result_storage):
        mock_step_result_storage.get_count.return_value = 2
        step_manager.stop_step()
        mock_step_result_storage.get_count.assert_called_once()
        mock_step_result_storage.remove_last.assert_called_once()
        mock_step_result_storage.get_last.assert_not_called()

    def test_get_active_step_returns_last_step(self, step_manager, mock_step_result, mock_step_result_storage):
        mock_step_result_storage.get_last.return_value = mock_step_result
        result = step_manager.get_active_step()
        mock_step_result_storage.get_last.assert_called_once()
        assert result == mock_step_result

    def test_get_steps_tree_returns_copy_and_clears(self, step_manager, mocker):
        mock_step1 = mocker.Mock(spec=StepResult)
        mock_step2 = mocker.Mock(spec=StepResult)
        step_manager._StepManager__steps_tree = [mock_step1, mock_step2]
        result = step_manager.get_steps_tree()
        assert len(result) == 2
        assert mock_step1 in result
        assert mock_step2 in result

        assert len(step_manager._StepManager__steps_tree) == 0