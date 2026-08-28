from testit_python_commons.client.helpers.test_result_matching import (
    normalize_parameters,
    parameters_empty,
    pick_best_in_progress_id,
)


class TestParameterMatching:
    def test_normalize_parameters(self):
        assert normalize_parameters(None) == {}
        assert normalize_parameters({}) == {}
        assert normalize_parameters({"a": 1, "b": None}) == {"a": "1", "b": ""}

    def test_parameters_empty(self):
        assert parameters_empty(None)
        assert parameters_empty({})
        assert not parameters_empty({"x": "1"})

    def test_pick_exact_match_over_empty(self):
        candidates = [
            {"id": "empty-tp", "has_test_point": True, "parameters": {}},
            {"id": "exact-tp", "has_test_point": True, "parameters": {"browser": "chrome"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) == "exact-tp"

    def test_pick_empty_fallback_when_no_exact(self):
        candidates = [
            {"id": "empty-tp", "has_test_point": True, "parameters": {}},
            {"id": "other-tp", "has_test_point": True, "parameters": {"browser": "firefox"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) == "empty-tp"

    def test_skip_incompatible_parameters(self):
        candidates = [
            {"id": "ff", "has_test_point": True, "parameters": {"browser": "firefox"}},
        ]
        assert pick_best_in_progress_id(candidates, {"browser": "chrome"}) is None

    def test_prefer_test_point_among_exact(self):
        candidates = [
            {"id": "orphan", "has_test_point": False, "parameters": {"a": "1"}},
            {"id": "bound", "has_test_point": True, "parameters": {"a": "1"}},
        ]
        assert pick_best_in_progress_id(candidates, {"a": "1"}) == "bound"

    def test_non_parametrized_picks_empty_with_tp(self):
        candidates = [
            {"id": "orphan", "has_test_point": False, "parameters": {}},
            {"id": "bound", "has_test_point": True, "parameters": {}},
        ]
        assert pick_best_in_progress_id(candidates, None) == "bound"
