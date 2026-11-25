#!/usr/bin/env bash
# Download Sync Storage binary for the given (resolved) version tag.
set -euo pipefail

SYNC_STORAGE_VERSION="${1:?sync-storage version tag required}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Callers usually cd into python-examples/<project>; cache next to that cwd.
CACHE_DIR="${SYNC_STORAGE_CACHE_DIR:-.caches}"
mkdir -p "$CACHE_DIR"

ASSET="syncstorage-${SYNC_STORAGE_VERSION}-linux_amd64"
URL="https://github.com/testit-tms/sync-storage-public/releases/download/${SYNC_STORAGE_VERSION}/${ASSET}"
TARGET="${CACHE_DIR}/syncstorage-linux-amd64"
TMP="${TARGET}.tmp"

echo "Downloading Sync Storage ${SYNC_STORAGE_VERSION}"
echo "URL: ${URL}"

HTTP_CODE="$(curl -fsSL -A "testit-python-adapter-ci" -o "${TMP}" -w "%{http_code}" "${URL}" || true)"
if [[ "${HTTP_CODE}" != "200" ]]; then
  rm -f "${TMP}"
  echo "ERROR: failed to download Sync Storage (HTTP ${HTTP_CODE}): ${URL}" >&2
  exit 1
fi

SIZE="$(wc -c < "${TMP}" | tr -d ' ')"
# Real Go binaries are multi-MB; GitHub error pages are tiny.
if [[ "${SIZE}" -lt 1000000 ]]; then
  echo "ERROR: downloaded file too small (${SIZE} bytes), refusing to use it" >&2
  head -c 200 "${TMP}" >&2 || true
  rm -f "${TMP}"
  exit 1
fi

mv -f "${TMP}" "${TARGET}"
chmod +x "${TARGET}"
echo "Sync Storage saved to ${TARGET} (${SIZE} bytes)"
