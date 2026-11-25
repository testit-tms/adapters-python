#!/usr/bin/env bash
# Read floor from SyncStorageRunner and resolve newest patch in the same channel.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

FLOOR="$(grep -o 'SYNC_STORAGE_VERSION = "[^"]*"' \
  "$ROOT/testit-python-commons/src/testit_python_commons/services/sync_storage/sync_storage_runner.py" \
  | cut -d'"' -f2)"

"$SCRIPT_DIR/resolve_sync_storage_version.sh" "$FLOOR"
