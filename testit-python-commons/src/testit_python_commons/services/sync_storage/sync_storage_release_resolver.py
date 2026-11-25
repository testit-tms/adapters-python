"""Resolve newest Sync Storage release on the floor's major.minor line and channel."""

from __future__ import annotations

import json
import logging
import urllib.request
from typing import List, Optional

from testit_python_commons.services.sync_storage.sync_storage_version_constraint import (
    SyncStorageVersionConstraint,
    compare_semver,
)

logger = logging.getLogger(__name__)

RELEASES_API_URL = (
    "https://api.github.com/repos/testit-tms/sync-storage-public/releases?per_page=100"
)
_REQUEST_TIMEOUT_SECONDS = 10


def resolve_latest(floor_constraint: str) -> str:
    """
    Return normalized tag to download; floor itself if API/list has no better match.
    """
    floor = SyncStorageVersionConstraint.parse(floor_constraint)
    try:
        tags = fetch_release_tags()
        selected = select_latest(floor, tags)
        if selected is not None:
            channel = f"tms-{floor.tms_channel}" if floor.has_tms_channel() else "numeric"
            logger.info(
                "Sync Storage: resolved %s → %s (channel=%s)",
                floor.normalized_tag(),
                selected,
                channel,
            )
            return selected
        logger.warning(
            "Sync Storage: no matching release for %s, using floor",
            floor.normalized_tag(),
        )
    except Exception as exc:
        logger.warning(
            "Sync Storage: failed to resolve latest release for %s, using floor: %s",
            floor.normalized_tag(),
            exc,
        )
    return floor.normalized_tag()


def select_latest(
    floor: SyncStorageVersionConstraint, tags: List[str]
) -> Optional[str]:
    """Pure selection for tests. Returns None if nothing matches."""
    best: Optional[SyncStorageVersionConstraint] = None
    for tag in tags:
        try:
            candidate = SyncStorageVersionConstraint.parse(tag)
        except ValueError:
            continue
        if not floor.matches_channel(candidate):
            continue
        if not floor.same_minor_line(candidate):
            continue
        if not candidate.is_at_least_floor(floor):
            continue
        if best is None or compare_semver(candidate, best) > 0:
            best = candidate
    return None if best is None else best.normalized_tag()


def fetch_release_tags() -> List[str]:
    request = urllib.request.Request(
        RELEASES_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "testit-python-adapter",
        },
    )
    with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT_SECONDS) as response:
        if response.getcode() != 200:
            raise IOError(f"GitHub releases API HTTP {response.getcode()}")
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list):
        return []
    tags: List[str] = []
    for node in payload:
        if node.get("draft") or node.get("prerelease"):
            continue
        tag = node.get("tag_name")
        if tag:
            tags.append(tag)
    return tags
