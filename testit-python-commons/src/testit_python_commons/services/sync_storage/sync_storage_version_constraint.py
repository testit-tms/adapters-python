"""Floor version + channel for Sync Storage release selection."""

from __future__ import annotations

import re
from dataclasses import dataclass

_TAG = re.compile(
    r"^v?(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-tms-(?P<tms>[\d.]+))?$"
)


@dataclass(frozen=True)
class SyncStorageVersionConstraint:
    major: int
    minor: int
    patch: int
    # Empty = numeric-only channel.
    tms_channel: str
    raw: str

    @classmethod
    def parse(cls, tag: str) -> "SyncStorageVersionConstraint":
        if tag is None or not str(tag).strip():
            raise ValueError("Sync Storage version is empty")
        trimmed = str(tag).strip()
        match = _TAG.match(trimmed)
        if not match:
            raise ValueError(f"Unsupported Sync Storage version: {trimmed}")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            tms_channel=match.group("tms") or "",
            raw=trimmed if trimmed.startswith("v") else f"v{trimmed}",
        )

    def matches_channel(self, other: "SyncStorageVersionConstraint") -> bool:
        return self.tms_channel == other.tms_channel

    def same_minor_line(self, other: "SyncStorageVersionConstraint") -> bool:
        return self.major == other.major and self.minor == other.minor

    def is_at_least_floor(self, floor: "SyncStorageVersionConstraint") -> bool:
        return compare_semver(self, floor) >= 0

    def normalized_tag(self) -> str:
        base = f"v{self.major}.{self.minor}.{self.patch}"
        if not self.tms_channel:
            return base
        return f"{base}-tms-{self.tms_channel}"

    def has_tms_channel(self) -> bool:
        return bool(self.tms_channel)


def compare_semver(
    a: SyncStorageVersionConstraint, b: SyncStorageVersionConstraint
) -> int:
    if a.major != b.major:
        return (a.major > b.major) - (a.major < b.major)
    if a.minor != b.minor:
        return (a.minor > b.minor) - (a.minor < b.minor)
    return (a.patch > b.patch) - (a.patch < b.patch)
