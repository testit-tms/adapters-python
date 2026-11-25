#!/usr/bin/env bash
# Resolve newest Sync Storage tag on the floor's major.minor line + channel.
# Floor examples: v0.4.4 (numeric only) | v0.4.3-tms-6.0 (only *-tms-6.0)
# On GitHub API failure (403/rate-limit) falls back to floor.
set -euo pipefail

FLOOR="${1:?floor version required, e.g. v0.4.3-tms-6.0}"

normalize_floor() {
  local v="$1"
  [[ "$v" == v* ]] || v="v$v"
  echo "$v"
}

if [[ "$FLOOR" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)(-tms-([0-9.]+))?$ ]]; then
  MAJOR="${BASH_REMATCH[1]}"
  MINOR="${BASH_REMATCH[2]}"
  PATCH="${BASH_REMATCH[3]}"
  TMS_CHANNEL="${BASH_REMATCH[5]:-}"
else
  echo "Unsupported Sync Storage floor: $FLOOR" >&2
  exit 1
fi

FLOOR_NORM="$(normalize_floor "$FLOOR")"

CURL_HEADERS=(
  -H "Accept: application/vnd.github+json"
  -H "User-Agent: testit-python-adapter-ci"
)
# GITHUB_TOKEN is available in Actions; avoids anonymous API 403 rate limits.
TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
if [[ -n "$TOKEN" ]]; then
  CURL_HEADERS+=(-H "Authorization: Bearer ${TOKEN}")
fi

TAGS_JSON=""
if ! TAGS_JSON="$(curl -fsSL "${CURL_HEADERS[@]}" \
  "https://api.github.com/repos/testit-tms/sync-storage-public/releases?per_page=100")"; then
  echo "WARN: GitHub releases API failed; using floor ${FLOOR_NORM}" >&2
  echo "floor=${FLOOR_NORM} resolved=${FLOOR_NORM} channel=${TMS_CHANNEL:-numeric}" >&2
  echo "$FLOOR_NORM"
  exit 0
fi

BEST=""
BEST_PATCH=-1

while IFS= read -r TAG; do
  [[ -z "$TAG" ]] && continue
  if [[ -n "$TMS_CHANNEL" ]]; then
    [[ "$TAG" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)-tms-${TMS_CHANNEL}$ ]] || continue
  else
    [[ "$TAG" =~ ^v?([0-9]+)\.([0-9]+)\.([0-9]+)$ ]] || continue
  fi
  T_MAJOR="${BASH_REMATCH[1]}"
  T_MINOR="${BASH_REMATCH[2]}"
  T_PATCH="${BASH_REMATCH[3]}"
  [[ "$T_MAJOR" == "$MAJOR" && "$T_MINOR" == "$MINOR" ]] || continue
  (( T_PATCH >= PATCH )) || continue
  if (( T_PATCH > BEST_PATCH )); then
    BEST_PATCH="$T_PATCH"
    BEST="v${T_MAJOR}.${T_MINOR}.${T_PATCH}"
    if [[ -n "$TMS_CHANNEL" ]]; then
      BEST="${BEST}-tms-${TMS_CHANNEL}"
    fi
  fi
done < <(echo "$TAGS_JSON" | grep -oE '"tag_name"[[:space:]]*:[[:space:]]*"[^"]+"' | sed -E 's/.*"([^"]+)"/\1/')

if [[ -z "$BEST" ]]; then
  BEST="$FLOOR_NORM"
fi

echo "floor=${FLOOR_NORM} resolved=${BEST} channel=${TMS_CHANNEL:-numeric}" >&2
echo "$BEST"
