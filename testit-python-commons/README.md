# Sync Storage Integration

This library includes built-in support for Sync Storage, enabling coordinated test execution across multiple workers in distributed testing environments.

See [SYNC_STORAGE_INTEGRATION.md](SYNC_STORAGE_INTEGRATION.md) for detailed documentation on how the integration works.

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