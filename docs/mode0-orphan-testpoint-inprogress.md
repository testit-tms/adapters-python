# Mode 0 orphan InProgress — Python adapter fix

Mirrors the Java/sync-storage contract described in
`adapters-java/docs/mode0-orphan-testpoint-inprogress.md`.

## Problem

With `adapterMode=0`, TMS already creates InProgress **with** `testPointId`.
Previously the Python adapter (after sync-storage accepted the cut) forced
`outcome=InProgress` and called `setAutoTestResultsForTestRun` (create without
`testPointId`) → orphan row; TP stayed InProgress / final status landed on orphan.

## Changes

| File | Change |
|------|--------|
| `services/adapter_manager.py` | After sync success: keep **final** outcome; write via `_write_test_realtime_internal` (no `set_outcome("InProgress")`) |
| `client/api_client.py` | `find_in_progress_test_result_id` + prefer TP via raw `GET /api/v2/testResults/{id}`; `__load_test_result` **PUT**s existing before create |

## Note

Adapters OpenAPI DTOs omit `testPointId` → temporary v2 GET hack (same as Java 5.8).
Sync-storage Work X PUT fix still requires a published binary newer than `v0.3.7-tms-5.7`.
