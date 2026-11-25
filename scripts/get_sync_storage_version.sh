#!/usr/bin/env bash
# Read floor from SyncStorageRunner and resolve newest patch in the same channel.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FLOOR="$(grep -o 'SYNC_STORAGE_VERSION = "[^"]*"' \
  "$ROOT/testit-python-commons/src/testit_python_commons/services/sync_storage/sync_storage_runner.py" \
  | cut -d'"' -f2)"

if [[ -z "${FLOOR}" ]]; then
  echo "ERROR: could not read SYNC_STORAGE_VERSION floor from SyncStorageRunner" >&2
  exit 1
fi

# bash … so missing +x on resolve script does not break CI
RESOLVED="$(bash "$SCRIPT_DIR/resolve_sync_storage_version.sh" "$FLOOR")"
if [[ -z "${RESOLVED}" ]]; then
  echo "ERROR: resolve_sync_storage_version.sh returned empty tag" >&2
  exit 1
fi

echo "${RESOLVED}"
