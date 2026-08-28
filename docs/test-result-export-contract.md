# Test result export contract (Python adapter)

Canonical rules for how the Python adapter sends test results to TMS.  
Aligned with Java adapters [PR #278](https://github.com/testit-tms/adapters-java/pull/278) (TMS-41083).

**Related:** [realtime-import-spec.md](../testit-python-commons/realtime-import-spec.md), [mode0-duplicate-results-bulk-after-realtime.md](./mode0-duplicate-results-bulk-after-realtime.md)

---

## API methods

| TMS operation | Adapter API | When used |
|---------------|-------------|-----------|
| **Send test results** | `POST /adapters/testRuns/{id}/test-results` (`adapters_test_runs_id_test_results_post`, Java: `sendTestResults`) | **Final** test result: status, steps, parameters, message, attachments |
| **Update test result** | `PUT /adapters/testResults/{id}` (`adapters_test_results_id_put`) | **Only** fixture `setupResults` / `teardownResults` after session (see below) |

---

## Rules (correct behaviour)

### 1. Finalization = `sendTestResults` only

- Every finalized test result (Passed, Failed, Skipped, …) is sent via **`sendTestResults`**, including when TMS already has an **InProgress** row from a test plan (`adapterMode=0` / `1`).
- TMS merges/enriches the existing InProgress slot on create; the adapter **must not** finalize via PUT.
- Full nested `stepResults` use `AttachmentPutModelAutoTestStepResultsModel` on the POST path (`Converter.test_result_to_testrun_result_post_model`).

**Entry point:** `ApiClientWorker.__load_test_result` → always POST.

Debug log:

```text
Finalized test result via sendTestResults for <externalId> (resultId=<uuid>)
```

### 2. PUT = fixture setup/teardown only (`importRealtime=true`)

After the session, when tests were already sent per-test:

1. `AdapterManager.write_tests` → `ApiClientWorker.update_test_results`
2. PUT body contains **only** `setupResults` and `teardownResults` (`Converter.convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request`)
3. **Must not** include: `stepResults`, `statusCode`, `duration`, `message`, `trace`, or fields copied from GET

Rationale: GET returns flat `StepResultApiModel` references without nested children. Re-sending them in PUT would **overwrite** the full step tree written during POST.

Unit test: `tests/client/test_converter_update_test_results.py`.

### 3. Never use PUT to change final status

- Do not PUT `statusCode` / outcome to finalize a test.
- Do not implement `findInProgress` → PUT finalize (removed; was a workaround before TMS/create merge was reliable).

### 4. Bulk at run end must not double-send

When `importRealtime=false` and a test was already finalized at test finish (e.g. Sync Storage master path stores `externalId → resultId` in `AdapterManager.__test_result_map`):

- `write_tests(..., finalized_external_ids=...)` **skips** `sendTestResults` for those external IDs
- Optionally refreshes autotest metadata only

Info log:

```text
Bulk import: skip sendTestResults for <externalId> (already finalized at test finish)
```

See [mode0-duplicate-results-bulk-after-realtime.md](./mode0-duplicate-results-bulk-after-realtime.md).

---

## Flow summary

### `importRealtime=true` (per-test upload)

```text
pytest_runtest_logfinish
  → write_test → write_test (autotest) + __load_test_result (sendTestResults)

pytest_sessionfinish
  → update_test_results → PUT setup/teardown only (no stepResults, no status)
```

### `importRealtime=false` (bulk at end)

```text
pytest_runtest_logfinish → buffer in AdapterManager.__test_results
  (Sync Storage master: sendTestResults immediately + store in __test_result_map)

pytest_sessionfinish
  → write_tests → sendTestResults for buffered tests
  → skip sendTestResults for keys already in __test_result_map
```

---

## Affected code

| File | Role |
|------|------|
| `client/api_client.py` | `__load_test_result` (POST), `update_test_results` (PUT fixtures), `write_tests` (bulk + skip) |
| `client/converter.py` | `test_result_to_testrun_result_post_model`, `convert_test_result_with_all_setup_and_teardown_steps_to_test_results_id_put_request` |
| `services/adapter_manager.py` | `__test_result_map`, `write_tests` / `__write_tests_after_all` |

---

## Regression checklist

**Good:**

- Log `Finalized test result via sendTestResults` at test finish
- With `importRealtime=true`: nested steps still on test result after session (PUT did not touch `stepResults`)
- With bulk + Sync Storage: log `Bulk import: skip sendTestResults` for tests finalized at test finish
- One finalized row per autotest per run (no TP + orphan duplicate)

**Bad (bug is back):**

- `Updated existing test result` / PUT with final status at test finish
- PUT body includes `stepResults` from GET in `update_test_results`
- Second `sendTestResults` for the same test in one run without skip
