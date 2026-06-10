from testit_python_commons.client.converter import Converter
from testit_python_commons.models.outcome_type import OutcomeType
from testit_python_commons.models.step_result import StepResult
from testit_python_commons.models.test_result_with_all_fixture_step_results_model import (
    TestResultWithAllFixtureStepResults,
)


def test_setup_teardown_put_request_does_not_include_step_results():
    test_result = TestResultWithAllFixtureStepResults('result-id')
    parent_step = StepResult().set_title('parent').set_outcome(OutcomeType.PASSED)
    child_step = StepResult().set_title('child').set_outcome(OutcomeType.PASSED)
    parent_step.set_step_results([child_step])
    test_result.set_setup_results([parent_step])

    model = Converter.convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request(
        test_result)

    assert 'step_results' not in model
    assert len(model.setup_results) == 1
    assert len(model.setup_results[0].step_results) == 1
    assert model.setup_results[0].step_results[0].title == 'child'
