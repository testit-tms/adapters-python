"""Match InProgress test results by parameters (parametrized mode 0)."""


def normalize_parameters(parameters) -> dict:
    if not parameters:
        return {}
    if isinstance(parameters, dict):
        return {str(k): "" if v is None else str(v) for k, v in parameters.items()}
    return {}


def parameters_empty(parameters) -> bool:
    return not normalize_parameters(parameters)


def pick_best_in_progress_id(candidates: list, incoming_parameters=None):
    """
    candidates: [{id: str, has_test_point: bool, parameters: dict}, ...]
    Prefer: exact param match > empty TMS params (WI without params) > others skipped if incompatible.
    Among equal match quality: prefer valid testPointId.
    """
    incoming = normalize_parameters(incoming_parameters)
    ranked = []

    for candidate in candidates:
        if not candidate or not candidate.get("id"):
            continue
        cand_params = normalize_parameters(candidate.get("parameters"))
        if cand_params == incoming:
            match_score = 0
        elif parameters_empty(cand_params):
            match_score = 1
        else:
            continue
        tp_score = 0 if candidate.get("has_test_point") else 1
        ranked.append(((match_score, tp_score), candidate["id"]))

    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0])
    return ranked[0][1]
