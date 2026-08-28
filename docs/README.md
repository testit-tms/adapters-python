# Adapter documentation (Python)

Supplementary docs for behaviour that is not covered in adapter READMEs.

| Document | Topic |
|----------|--------|
| [test-result-export-contract.md](./test-result-export-contract.md) | **Canonical:** `sendTestResults` vs PUT; PUT only for fixture setup/teardown |
| [mode0-duplicate-results-bulk-after-realtime.md](./mode0-duplicate-results-bulk-after-realtime.md) | Mode 0 duplicate Passed (TP + orphan): no second bulk send |
| [mode0-orphan-testpoint-inprogress.md](./mode0-orphan-testpoint-inprogress.md) | Mode 0 + InProgress slots: create path, Sync Storage |
| [test-run-tags-and-links.md](./test-run-tags-and-links.md) | Test run tags & links on create / early merge |

Commons (real-time import, nested steps):

| Document | Topic |
|----------|--------|
| [../testit-python-commons/realtime-import-spec.md](../testit-python-commons/realtime-import-spec.md) | `importRealtime=true`, nested steps, session PUT |
| [../testit-python-commons/sync-storage-interaction-spec.md](../testit-python-commons/sync-storage-interaction-spec.md) | Sync Storage protocol |
