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

1. Cut model to Sync Storage (final status in the cut for Work X).
2. **Mode 0 only:** `_write_test_realtime_internal` → autotest update + **`sendTestResults`** with **final** status and full steps.
3. Store `externalId → resultId` in `AdapterManager.__test_result_map` (fixtures).
4. Store per-invocation finalize key in `__finalized_result_keys` (`externalKey` or `externalId`+parameters).

**Modes 1 / 2 (not this doc’s primary path):** same cut, but TMS gets **`InProgress`** first; **Work X** applies the final status from the cut. Early adapter finalization above is **mode 0** only.

### End of run — bulk (`write_tests_after_all`)

- If finalize key is already in `__finalized_result_keys` → **skip** `sendTestResults`; refresh autotest metadata if needed.
- Otherwise → bulk `sendTestResults` (including other parametrize iterations that share the same `externalId`).

---

## Flow (mode 0 + Sync Storage + `importRealtime=false`)

```text
Plan start → TMS creates TP-bound InProgress
stopTestCase → SyncStorage cut + sendTestResults (Passed/Failed + full payload)
sessionfinish → bulk skips sendTestResults for tests already in __test_result_map
```

Expected: **one** finalized result row per **test invocation** in the run (parametrize iterations are separate), with steps from the create payload.

---

## Regression checklist

1. Mode 0, one autotest, Sync Storage on, `importRealtime=false`.
2. Log: `Finalized test result via sendTestResults` at test end.
3. Log: `Bulk import: skip sendTestResults …` at run end.
4. `testResults/search`: one hit per `externalId`.

**Bad signs:** two Passed rows for the same `externalId`; bulk `sendTestResults` without skip for an already finalized test.
