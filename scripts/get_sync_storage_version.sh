echo $(grep -o 'SYNC_STORAGE_VERSION = "[^"]*"' testit-python-commons/src/testit_python_commons/services/sync_storage/sync_storage_runner.py | cut -d'"' -f2)
         