from pluggy import HookimplMarker

__all__ = [
        "AdapterManager",
        "TmsPluginManager",
        "FixtureManager",
        "StepManager",
        "Utils",
        "SyncStorageRunner",
        "hookimpl",
    ]

hookimpl = HookimplMarker("testit")


def __getattr__(name):
    if name == "AdapterManager":
        from testit_python_commons.services.adapter_manager import AdapterManager

        return AdapterManager
    if name == "TmsPluginManager":
        from testit_python_commons.services.plugin_manager import TmsPluginManager

        return TmsPluginManager
    if name == "FixtureManager":
        from testit_python_commons.services.fixture_manager import FixtureManager

        return FixtureManager
    if name == "StepManager":
        from testit_python_commons.services.step_manager import StepManager

        return StepManager
    if name == "Utils":
        from testit_python_commons.services.utils import Utils

        return Utils
    if name == "SyncStorageRunner":
        from testit_python_commons.services.sync_storage import SyncStorageRunner

        return SyncStorageRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
