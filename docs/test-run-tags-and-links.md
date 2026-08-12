# Test run tags and links

TMS supports **tags** and **links** on a **test run** (not on an individual autotest/result).
Python adapters pass them via config so a CI job URL is visible while the run is still **In progress**.

## Config

| Intent | File / property | Env | CLI |
|--------|-----------------|-----|-----|
| Tags | `testRunTags` | `TMS_TEST_RUN_TAGS` | `tmsTestRunTags` |
| Links | `testRunLinks` | `TMS_TEST_RUN_LINKS` | `tmsTestRunLinks` |

- **Tags:** `smoke,nightly` or `["smoke","nightly"]`
- **Links:** JSON array; `url` required; optional `title`, `description`, `type`
- **Link types:** `Related`, `BlockedBy`, `Defect`, `Issue`, `Requirement`, `Repository`

## Behaviour

| Path | When applied |
|------|----------------|
| Create run (`adapterMode=2`) | On `adapters_test_runs_post` (create body) |
| Existing run (`adapterMode=0` / `1`) | Early merge in `get_test_run_id` (startup), not at session end |

Merge keeps existing UI/API tags and links; adds new ones; skips duplicate tag names and link URLs.

## Example

```ini
[testit]
testRunTags = smoke,nightly
testRunLinks = [{"url":"https://gitlab.example.com/group/project/-/jobs/12345","title":"CI Job","type":"Related"}]
```

```bash
pytest --testit \
  --tmsTestRunTags=smoke,nightly \
  --tmsTestRunLinks='[{"url":"https://ci.example/jobs/1","title":"CI Job","type":"Related"}]'
```

## Scope

Shared in `testit-python-commons`; exposed by pytest / behave / nose / robot adapters.
Out of scope: polling CI until a terminal job status (orchestration/TMS concern).
