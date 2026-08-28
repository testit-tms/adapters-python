# Mode 0: duplicate test results (TP-bound + orphan) — Python adapter

**Related:** [mode0-orphan-testpoint-inprogress.md](./mode0-orphan-testpoint-inprogress.md), [test-result-export-contract.md](./test-result-export-contract.md)  
**Typical setup:** pytest + Sync Storage, `adapterMode=0`, fixed `testRunId`, `importRealtime=false` (default)

Cross-adapter parity: Java [PR #278](https://github.com/testit-tms/adapters-java/pull/278).

---

## Symptom (historical bug)

One autotest from a test plan produced **two** Passed rows in the same run for the same `externalId`:

| Row | `testPointId` | Origin |
|-----|---------------|--------|
| Older | Real plan point UUID | Created by TMS when the run started |
| Newer | Missing / `00000000-…` | **Second** `POST …/testRuns/{id}/test-results` from the adapter |

Root cause: the adapter finalized the test twice — once at **test finish**, again at **run finish** (bulk).

---

## Current behaviour (fixed)

**Rule:** final status goes only through **`sendTestResults`**.  
**PUT** is **not** used to finalize; see [test-result-export-contract.md](./test-result-export-contract.md).

### End of test — Sync Storage master (`importRealtime=false`)

When Sync Storage accepts the cut (`on_master_no_already_in_progress` → true):

1. Cut model to Sync Storage (coordination only).
2. `_write_test_realtime_internal` → autotest update + **`sendTestResults`** with final status and full steps.
3. Store `externalId → resultId` in `AdapterManager.__test_result_map`.

### End of run — bulk (`write_tests_after_all`)

- If `externalId` is already in `__test_result_map` → **skip** `sendTestResults`; refresh autotest metadata if needed.
- Otherwise → bulk `sendTestResults` once (Sync Storage off, or test not sent at finish).

---

## Flow (mode 0 + Sync Storage + `importRealtime=false`)

```text
Plan start → TMS creates TP-bound InProgress
stopTestCase → SyncStorage cut + sendTestResults (Passed/Failed + full payload)
sessionfinish → bulk skips sendTestResults for tests already in __test_result_map
```

Expected: **one** finalized result row per autotest in the run, with steps from the create payload.

---

## Regression checklist

1. Mode 0, one autotest, Sync Storage on, `importRealtime=false`.
2. Log: `Finalized test result via sendTestResults` at test end.
3. Log: `Bulk import: skip sendTestResults …` at run end.
4. `testResults/search`: one hit per `externalId`.

**Bad signs:** two Passed rows for the same `externalId`; bulk `sendTestResults` without skip for an already finalized test.
