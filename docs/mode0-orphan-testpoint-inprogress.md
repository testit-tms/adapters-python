# Mode 0: InProgress slots and test plan runs

How the Python adapter exports results when `adapterMode=0` (test plan / webhook / filter) and TMS already created **InProgress** rows bound to test points.

**Related:** [test-result-export-contract.md](./test-result-export-contract.md), Java `adapters-java/docs/mode0-orphan-testpoint-inprogress.md`.

---

## TMS context

With `adapterMode=0`, the test run is created from a plan. TMS pre-creates one **InProgress** result per test point (`testPointId` set).

The adapter must **finalize** those rows with the real outcome and full payload (steps, parameters, …), not leave them stuck InProgress and not create orphan duplicates.

---

## Correct behaviour (current)

**Finalization uses `sendTestResults` only** (`POST /adapters/testRuns/{id}/test-results`).

- Applies even when an InProgress result already exists for the autotest.
- TMS merges the create payload into the plan-bound row (external id + configuration + parameters).
- The adapter **does not** search InProgress and **does not** PUT final status (removed workaround).

After Sync Storage accepts the cut, the adapter keeps the **final** outcome and calls `_write_test_realtime_internal` → `sendTestResults`.

See [test-result-export-contract.md](./test-result-export-contract.md) and [mode0-duplicate-results-bulk-after-realtime.md](./mode0-duplicate-results-bulk-after-realtime.md).

---

## Historical issues (for context)

### Orphan without `testPointId`

Older behaviour: POST create without matching the plan row → second result (orphan), plan row stayed InProgress.

**Fix:** finalize via `sendTestResults`; TMS updates the existing slot instead of requiring a separate PUT-by-id path.

### Duplicate at bulk (importRealtime=false)

Test finalized at test finish via `sendTestResults`, then bulk at session end sent **again** → orphan duplicate.

**Fix:** skip bulk `sendTestResults` when `externalId` is already in `AdapterManager.__test_result_map`.

### Parametrized tests and many InProgress rows

When several TPs share the same `external_id` with different (or empty) parameters, TMS matching on create uses the payload `parameters`. Adapter sends callspec parameters on `sendTestResults`; each iteration should get its own finalized row without leaving unrelated TPs stuck (TMS-side matching).

Helper `client/helpers/test_result_matching.py` remains for unit tests / future client-side ranking if needed; **`__load_test_result` no longer uses it**.

---

## What PUT is still used for

**Only** after session with `importRealtime=true`: attach pytest fixture **setup/teardown** steps to an already finalized result id. No status, no `stepResults`. See [test-result-export-contract.md](./test-result-export-contract.md).

---

## Note

Sync Storage Work X finalize may still affect nested steps on the **first** held test independently of this export contract; see [realtime-import-spec.md](../testit-python-commons/realtime-import-spec.md) (Cause B).
