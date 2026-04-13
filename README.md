# Test IT Python Integrations
The repository contains new versions of adapters for python test frameworks.

Pytest: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-pytest?style=plastic)](https://pypi.python.org/pypi/testit-adapter-pytest)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-pytest?style=plastic)](https://pypi.python.org/pypi/testit-adapter-pytest)

Behave: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-behave?style=plastic)](https://pypi.python.org/pypi/testit-adapter-behave)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-behave?style=plastic)](https://pypi.python.org/pypi/testit-adapter-behave)

Nose: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-nose?style=plastic)](https://pypi.python.org/pypi/testit-adapter-nose)

Robotframework: [![Release
Status](https://img.shields.io/pypi/v/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)
[![Downloads](https://img.shields.io/pypi/dm/testit-adapter-robotframework?style=plastic)](https://pypi.python.org/pypi/testit-adapter-robotframework)

Commons: [![Release
Status](https://img.shields.io/pypi/v/testit-python-commons?style=plastic)](https://pypi.python.org/pypi/testit-python-commons)
[![Downloads](https://img.shields.io/pypi/dm/testit-python-commons?style=plastic)](https://pypi.python.org/pypi/testit-python-commons)


## Compatibility

| Test IT | Behave         | Nose           | Pytest         | RobotFramework |
|---------|----------------|----------------|----------------|----------------|
| 3.5     | 2.0            | 2.0            | 2.0            | 2.0            |
| 4.0     | 2.1            | 2.1            | 2.1            | 2.1            |
| 4.5     | 2.5            | 2.5            | 2.5            | 2.5            |
| 4.6     | 2.8            | 2.8            | 2.8            | 2.8            |
| 5.0     | 3.2            | 3.2            | 3.2            | 3.2            |
| 5.2     | 3.3            | 3.3            | 3.3            | 3.3            |
| 5.3     | 3.6.1.post530  | 3.6.1.post530  | 3.6.1.post530  | 3.6.1.post530  |
| 5.4     | 3.6.6.post540  | 3.6.6.post540  | 3.6.6.post540  | 3.6.6.post540  |
| 5.5     | 3.10.1.post550 | 3.10.1.post550 | 3.10.1.post550 | 3.10.1.post550 |
| 5.6     | 3.11.1.post560 | 3.11.1.post560 | 3.11.1.post560 | 3.11.1.post560 |
| 5.7     | 4.1.0.post570  | 4.1.0.post570  | 4.1.0.post570  | 4.1.0.post570  |
| Cloud   | 3.12.0 +       | 3.12.0 +       | 3.12.0 +       | 3.12.0 +       |

1. For current versions, see the releases tab. 
2. Starting with 5.2, we have added a TMS postscript, which means that the utility is compatible with a specific enterprise version. 
3. If you are in doubt about which version to use, check with the support staff. support@yoonion.ru


## What's new in 4.0.0?

- New logic with a fix for test results loading
- Added sync-storage subprocess usage for worker synchronization on port **49152** by defailt.
- importRealtime=false is a default mode (previously true)

- **limitations**: 
- The current 4.0.0 version is not compatible with `adapterMode=2` when using parallelization (e.g., `pytest --testit -n 4`). Please use `adapterMode=1`.

### How to run 4.0+ locally?

You can change nothing, it's full compatible with previous versions of adapters for local run on all OS.


### How to run 4.0+ with CI/CD?

For CI/CD pipelines, we recommend starting the sync-storage instance before the adapter and waiting for its completion within the same job.

It can be OK for `adapterMode=2` and automatic creation of new test-run + call for `curl -v http://127.0.0.1:49152/wait-completion || true` in the end.  

There is a guide how to do everything with `adapterMode` `1` or `0`:

You can see how we implement this [here.](https://github.com/testit-tms/adapters-python/tree/main/.github/workflows/test.yml#106) 

- to get the latest version of sync-storage, please use our [script](https://github.com/testit-tms/adapters-python/tree/main/scripts/curl_last_version.sh)

- To download a specific version of sync-storage, use our [script](https://github.com/testit-tms/adapters-python/tree/main/scripts/get_sync_storage.sh) and pass the desired version number as the first parameter. Sync-storage will be downloaded as `.caches/syncstorage-linux-amd64`


1. Create an empty test run using `testit-cli` or use an existing one, and save the `testRunId`.
1.1 (alternative) You can use `curl + jq` to create empty test run, there is an example for github actions:

```bash
mkdir -p "$(dirname "${{ env.TEMP_FILE }}")"
BASE_URL="${{ env.TMS_URL }}"
BASE_URL="${BASE_URL%/}"
BODY=$(jq -nc \
    --arg projectId "${{ env.TMS_PROJECT_ID }}" \
    --arg name "${{ env.TMS_TEST_RUN_NAME }}" \
    '{projectId: $projectId, name: $name}')

curl -sS -f -X POST "${BASE_URL}/api/v2/testRuns" \
    -H "accept: application/json" \
    -H "Content-Type: application/json" \
    -H "Authorization: PrivateToken ${{ env.TMS_PRIVATE_TOKEN }}" \
    -d "$BODY" \
    | jq -er '.id' > "${{ env.TEMP_FILE }}"

echo "TMS_TEST_RUN_ID=$(<${{ env.TEMP_FILE }})" >> $GITHUB_ENV
echo "TMS_TEST_RUN_ID=$(<${{ env.TEMP_FILE }})" >> .env
export TMS_TEST_RUN_ID=$(<${{ env.TEMP_FILE }})
```

2. Start **sync-storage** with the correct parameters as a background process (alternatives to nohup can be used). Stream the log output to the `service.log` file:
```bash
nohup .caches/syncstorage-linux-amd64 --testRunId ${{ env.TMS_TEST_RUN_ID }} --port 49152 \
    --baseURL ${{ env.TMS_URL }} --privateToken ${{ env.TMS_PRIVATE_TOKEN }}  > service.log 2>&1 & 
```
3. Start the adapter using adapterMode=1 or adapterMode=0 for the selected testRunId.
4. Wait for sync-storage to complete background jobs by calling:
```bash
curl -v http://127.0.0.1:49152/wait-completion?testRunId=${{ env.TMS_TEST_RUN_ID }} || true
```
5. You can read the sync-storage logs from the service.log file.


### General

Supported test frameworks:
 1. [Pytest](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-pytest)
 2. [Behave](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-behave)
 3. [RobotFramework](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-robotframework)
 4. [Nose](https://github.com/testit-tms/adapters-python/tree/main/testit-adapter-nose) 

# 🚀 Warning
Since 3.0.0 version:
- If the externalId annotation is not specified, then its contents will be a hash of a fully qualified method name.

<a href='https://coveralls.io/github/testit-tms/adapters-python?branch=main'>
    <img src='https://coveralls.io/repos/github/testit-tms/adapters-python/badge.svg?branch=main' alt='Coverage Status' />
</a>
