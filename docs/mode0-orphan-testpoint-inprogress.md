# Mode 0: InProgress matching (orphan TP + parametrized)

How the Python adapter finds and **updates** an existing InProgress test result
instead of creating a new one when `adapterMode=0` (test plan / webhook / filter).

Related: Java/sync-storage contract in
`adapters-java/docs/mode0-orphan-testpoint-inprogress.md`.

---

## Problem 1 — orphan InProgress (no `testPointId`)

With `adapterMode=0`, TMS already creates InProgress results **bound to a test point**
(`testPointId` set).

Previously the Python adapter (after sync-storage accepted the cut) forced
`outcome=InProgress` and called create (`setAutoTestResultsForTestRun`) **without**
`testPointId`. That produced a second row (orphan). The TP-bound result stayed
InProgress forever; the final status landed on the orphan.

**Fix:** keep the final outcome after sync; before create, search InProgress by
`autotest_external_id`, prefer a result with a valid `testPointId`, then **PUT**
that result instead of posting a new one.

---

## Problem 2 — parametrized pytest leaves many InProgress forever

### What happens in practice

1. A test plan / filter creates many InProgress rows (one per test point).
2. The same autotest is parametrized (`@pytest.mark.parametrize`). Iterations often
   share one `external_id` (name template without `{param}`).
3. Work items / test points frequently have **empty parameters**, while the adapter
   sends **callspec parameters** on create.
4. The first matching logic used only `external_id`. The first TP-bound InProgress
   was always chosen (or create ran when params on TMS did not “fit” create semantics).
5. Result: one empty TP might get updated once; other iterations **POST new results**
   with parameters; remaining empty InProgress rows stay InProgress forever.

Root cause: mismatch between WI parameters and
autotest/result parameters, plus search that ignores parameters.

### Why short search is not enough

`TestResultShortResponse` (search) has **no `parameters`**. Full / v2 payload does.
Adapters OpenAPI models also omit `testPointId` on short DTOs → temporary
`GET /api/v2/testResults/{id}` for both `testPointId` and `parameters`.

---

## Solution (parameter-aware pick + claim)

| File | Role |
|------|------|
| `client/helpers/test_result_matching.py` | Pure ranking: exact params > empty TMS params; prefer valid TP |
| `client/api_client.py` | `find_in_progress_test_result_id(external_id, parameters)`; claim chosen ids; `__load_test_result` passes `get_parameters()` |
| `services/adapter_manager.py` | After sync: keep **final** outcome; realtime write without forcing InProgress |

### Matching rules

For candidates with the same `external_id` (and not yet claimed in this process):

1. **Exact parameter match** (normalized string key/value) — best.
2. Else **empty / missing parameters on TMS** — fallback for WI without params
   (typical test-plan case).
3. Else **skip** if TMS has non-empty parameters that differ from the incoming ones
   (do not overwrite the wrong callspec’s TP).
4. Among equal match quality, prefer a valid `testPointId`.
5. **Claim** the chosen result id so the next parametrize iteration does not reuse
   the same empty TP.

If nothing matches → create (previous behaviour for genuinely new results).

Non-parametrized tests (`parameters` empty/`None`) still pick the empty-params
TP-bound InProgress first — same as the original orphan fix.

### What we do **not** change

- Adapters PUT body still cannot set `parameters` (OpenAPI PUT has no field) —
  we complete the existing TP-bound row (outcome / duration / message / trace).
- Cloud-side “better” filling of WI params remains a TMS concern; the adapter only
  stops creating endless orphans and stuck InProgress.

---

## Note

Sync-storage Work X PUT fix still requires a published binary newer than
`v0.3.7-tms-5.7` for nested-step finalize issues unrelated to this matching.
