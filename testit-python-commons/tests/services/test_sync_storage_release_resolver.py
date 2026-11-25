from testit_python_commons.services.sync_storage.sync_storage_release_resolver import (
    resolve_latest,
    select_latest,
)
from testit_python_commons.services.sync_storage.sync_storage_version_constraint import (
    SyncStorageVersionConstraint,
)


TAGS = [
    "v0.4.3-tms-6.0",
    "v0.4.3",
    "v0.4.2-tms-5.8",
    "v0.4.2",
    "v0.4.1-tms-5.8",
    "v0.4.1",
    "v0.4.0-tms-5.8",
    "v0.4.0",
    "v0.3.12-tms-5.8",
    "v0.3.12",
    "v0.3.8-rc-tms-5.7",
]


class TestSelectLatest:
    def test_numeric_floor_picks_latest_numeric_on_minor_line(self):
        floor = SyncStorageVersionConstraint.parse("v0.4.0")
        assert select_latest(floor, TAGS) == "v0.4.3"

    def test_numeric_floor_ignores_tms_tags_and_higher_floor(self):
        floor = SyncStorageVersionConstraint.parse("v0.4.4")
        assert select_latest(floor, TAGS) is None

    def test_tms60_floor_picks_only_tms60(self):
        floor = SyncStorageVersionConstraint.parse("v0.4.0-tms-6.0")
        assert select_latest(floor, TAGS) == "v0.4.3-tms-6.0"

    def test_tms58_floor_does_not_pick_tms60_or_numeric(self):
        floor = SyncStorageVersionConstraint.parse("v0.4.1-tms-5.8")
        assert select_latest(floor, TAGS) == "v0.4.2-tms-5.8"

    def test_does_not_cross_minor_line(self):
        floor = SyncStorageVersionConstraint.parse("v0.3.0")
        assert select_latest(floor, TAGS) == "v0.3.12"

    def test_skips_unparseable_prerelease_tags(self):
        floor = SyncStorageVersionConstraint.parse("v0.3.0-tms-5.7")
        assert select_latest(floor, TAGS) is None


class TestResolveLatestFallback:
    def test_api_failure_falls_back_to_floor(self, mocker):
        mocker.patch(
            "testit_python_commons.services.sync_storage."
            "sync_storage_release_resolver.fetch_release_tags",
            side_effect=OSError("offline"),
        )
        assert resolve_latest("v0.4.3-tms-6.0") == "v0.4.3-tms-6.0"

    def test_no_match_falls_back_to_floor(self, mocker):
        mocker.patch(
            "testit_python_commons.services.sync_storage."
            "sync_storage_release_resolver.fetch_release_tags",
            return_value=["v0.4.3", "v0.4.2-tms-5.8"],
        )
        assert resolve_latest("v0.4.4-tms-6.0") == "v0.4.4-tms-6.0"
