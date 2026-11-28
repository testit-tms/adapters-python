---
name: sync-storage-python
description: >-
  Sync-storage rules for adapters-python (testit-python-commons SyncStorageRunner).
  Use when changing sync-storage start/stop, ports, keep-alive, wait-completion,
  atexit/shutdown hooks, xdist/CI pipelines, or porting Java sync-storage fixes to Python.
---

# Sync-storage in adapters-python

## Hard rules

- Do **not** finalize test-result status via `PUT /api/v2/testResults/{id}`. Finals = Work X / send-test-result.
- Prefer port bump (`preferred .. +SYNC_STORAGE_PORT_MAX_BUMP`) over fail-fast / silent “no sync-storage” when the preferred port has another `testRunId` or start/register loses a race.

## atexit — known CI/CD problems (do not reintroduce)

**с atexit были проблемы в CI/CD.**

History in this repo (`fb30546` / prior `atexit` + `terminate`):

- Sync-storage is started with `start_new_session=True` (detached) so Work X can outlive the test runner.
- An `atexit` hook that **terminated** the child broke CI/CD pipes / xdist-style runs: SS died before external `wait-completion`, Work X could not finish.
- Blocking `atexit` on `/wait-completion` is also unsafe (hangs runner exit, bad with multiple workers).

**Do not** register `atexit` (or similar process-exit hooks) to kill sync-storage or to block on `/wait-completion` in the Python adapter.

### Correct Python lifecycle

| Concern | Approach |
|---------|----------|
| Spawn | `subprocess.Popen(..., start_new_session=True)`, log to `syncstorage.log` |
| Kill on adapter exit | **No** — leave detached SS alive |
| Wait for Work X | **External / CI**: `GET /wait-completion?testRunId=...` (see README); health-before-wait |
| Worker `completed` | Stop keep-alive only — **no** wait-completion mid-run |
| Foreign port / race | Try `port+1` …; cleanup failed spawn; do not silently drop SS when another port is free |

Java may use a JVM shutdown-hook that waits then destroys an **owned** child. That pattern does **not** map 1:1 onto Python’s detached + CI wait model.

## Touchpoints

- `testit-python-commons/.../sync_storage/sync_storage_runner.py`
- Docs: `docs/sync-storage-port-bump-and-wait-completion.md`, `docs/sync-storage-verification-checklist.md`
- CI/README: curl/`wait-completion` after tests
