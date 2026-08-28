# Sync Storage Integration

This library includes built-in support for Sync Storage, enabling coordinated test execution across multiple workers in distributed testing environments.

See [sync-storage-interaction-spec.md](sync-storage-interaction-spec.md) for the protocol.

**Test result export (POST vs PUT):** [../docs/test-result-export-contract.md](../docs/test-result-export-contract.md)

# How to enable debug logging?
1. Add in **connection_config.ini** file from the root directory of the project:
```
[debug]
__DEV = true
```

## How to install local modified version?
```
cd adapters-python/testit-python-commons
pip install .
```
## How to install version from some branch?
```
git+https://github.com/testit-tms/adapters-python.git@develop#subdirectory=testit-python-commons
```