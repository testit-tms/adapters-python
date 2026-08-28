# Real-Time Import (`importRealtime=true`) Specification

This document describes how the Python adapter imports test results in real time.

**Canonical export rules (POST vs PUT):** [../docs/test-result-export-contract.md](../docs/test-result-export-contract.md)

## Overview

When `importRealtime=true` (CLI: `--testit-import-realtime`, config: `importrealtime`), each test result is sent to Test IT immediately after the test completes via **`sendTestResults`** (POST). At the end of the session, the adapter performs **one allowed PUT**: attach fixture setup/teardown steps only — **not** status, **not** test `stepResults`.

When `importRealtime=false`, all test results are sent once after the session finishes (`write_tests_after_all`), except tests already finalized at test finish (see [../docs/mode0-duplicate-results-bulk-after-realtime.md](../docs/mode0-duplicate-results-bulk-after-realtime.md)).

## Real-Time Flow

1. **Per test** (`pytest_runtest_logfinish` → `AdapterManager.write_test` → `ApiClientWorker.write_test`):
   - Autotest metadata is created or updated (including nested steps in the autotest model).
   - Test result is finalized via **`sendTestResults`** (`POST /adapters/testRuns/{id}/test-results`) with full nested `step_results` (`Converter.test_result_to_testrun_result_post_model`).

2. **After session** (`pytest_sessionfinish` → `AdapterManager.write_tests` → `ApiClientWorker.update_test_results`):
   - **PUT only** fixture `setup_results` / `teardown_results` for tests already sent in real time.
   - PUT body **must not** include `step_results`, `status_code`, or other fields from GET.
   - Test result IDs are stored in `AdapterManager.__test_result_map` during the per-test upload.

## Correct PUT behaviour (session end)

`update_test_results` uses `Converter.convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request`, which builds a PUT request with **only**:

- `setup_results` — recursive `AutoTestStepResultUpdateRequest`
- `teardown_results` — same

Everything else is omitted so nested test steps from the earlier POST are not overwritten.

```python
model = Converter.convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request(
    test_result)
self.__test_results_api.adapters_test_results_id_put(
    id=test_result.get_test_result_id(),
    adapters_test_results_id_put_request=model)
```

Unit test: `tests/client/test_converter_update_test_results.py`.

---

## Historical: Nested Steps Disappeared After Run Completion

The sections below describe **past** bugs and fixes. Current code follows [test-result-export-contract.md](../docs/test-result-export-contract.md).

### Symptoms (historical)

- Nested steps are visible on the **autotest** card (correct).
- Nested steps are visible on the **test result** while the run is still in progress.
- After the run completes, only **top-level** steps remain on the test result.
- Reproducible with `importRealtime=true` (default since adapter 4.x).
- Not reproducible with `importRealtime=false`.
- **With Sync Storage enabled:** only the **first** test in the run is affected (the one held as `InProgress`).
- Tests that are not the first one keep nested steps.
- Without Sync Storage the issue does not reproduce (for the adapter-only PUT bug below).

There are **two independent causes**; both can flatten nested steps on the test result.

---

### Cause A (adapter): final session PUT overwrote `step_results`

At session finish, `update_test_results` used to:

1. `GET` the test result from the API (`get_test_result_by_id`).
2. Build a PUT request from the GET response via `convert_test_result_model_to_test_results_id_put_request`.
3. Overwrite `setup_results` and `teardown_results` with fixture steps.
4. `PUT` the full model back, **including `step_results` from the GET response**.

The problem is a model mismatch:

| Operation | `step_results` model | Nested structure |
|-----------|---------------------|------------------|
| POST (create result) | `AttachmentPutModelAutoTestStepResultsModel` | Full tree via recursive `step_results` |
| GET (read result) | `StepResultApiModel` | References only (`step_id`, `outcome`, …) — **no nested `step_results`** |
| PUT (update result) | `StepResultApiModel` | Same flat reference list |

Re-sending `step_results` from GET in the final PUT replaced the full nested tree (written during real-time import) with a flat list of top-level step references. Autotest steps were unaffected because they are written on a separate API path during `write_test`.

### Fix

The final session update must **not** send `step_results`. It should only attach fixture setup/teardown steps.

**Before:**

```python
test_result_response = self.get_test_result_by_id(test_result.get_test_result_id())
model = Converter.convert_test_result_model_to_test_results_id_put_request(test_result_response)
model.setup_results = Converter.step_results_to_auto_test_step_result_update_request(...)
model.teardown_results = Converter.step_results_to_auto_test_step_result_update_request(...)
self.__test_results_api.api_v2_test_results_id_put(...)
```

**After:**

```python
model = Converter.convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request(
    test_result)
self.__test_results_api.api_v2_test_results_id_put(...)
```

`convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request` builds a PUT request with only:

- `setup_results` — recursive `AutoTestStepResultUpdateRequest` (nested fixture steps preserved)
- `teardown_results` — same

The `step_results` field is omitted, so the nested test steps written during real-time import are not overwritten.

---

### Cause B (Sync Storage + adapter): first test and Work X finalize

When Sync Storage is running and the worker is **master**, the **first** completed test uses `on_master_no_already_in_progress`:

1. Adapter sends **`TestResultCutApiModel`** to Sync Storage (`POST /in_progress_test_result`) — coordination only, no steps.
2. Adapter calls `_write_test_realtime_internal` with the **final** outcome → **`sendTestResults`** with full step tree (no forced InProgress POST to TMS).
3. Stores `externalId → resultId` in `__test_result_map`.

Sync Storage Work X may still finalize the held cut model separately at `wait-completion`; that path is independent of the adapter POST/PUT contract. See Sync Storage docs if nested steps on the **first** test are lost after run completion.

---

### Affected Code (Cause A)

| File | Responsibility |
|------|----------------|
| `services/adapter_manager.py` | Calls `update_test_results` when `importRealtime=true` |
| `client/api_client.py` | `update_test_results` — final PUT after session |
| `client/converter.py` | `convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request` |

### Verification

1. Run pytest with nested `@testit.step` / `with testit.step(...)` and `importRealtime=true`.
2. Confirm nested steps on the test result **during** the run.
3. Wait for session finish (`pytest_sessionfinish`).
4. Confirm nested steps are still present on the test result after the run completes.

Unit test: `tests/client/test_converter_update_test_results.py` — asserts the final PUT model does not include `step_results` and preserves nested setup steps.

## Related Configuration

| Setting | Default (4.x+) | Effect |
|---------|----------------|--------|
| `importRealtime` / `importrealtime` | `false` in config | Per-test `sendTestResults` when enabled; session PUT = fixtures only |
| `adapterMode` | varies | Test run selection; see [../docs/test-result-export-contract.md](../docs/test-result-export-contract.md) |

## See also

- [../docs/test-result-export-contract.md](../docs/test-result-export-contract.md) — POST vs PUT rules
- [../docs/mode0-duplicate-results-bulk-after-realtime.md](../docs/mode0-duplicate-results-bulk-after-realtime.md) — bulk skip after test-finish finalize
