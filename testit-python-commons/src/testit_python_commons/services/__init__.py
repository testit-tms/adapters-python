from pluggy import HookimplMarker

from testit_python_commons.services.adapter_manager import AdapterManager
from testit_python_commons.services.fixture_manager import FixtureManager
from testit_python_commons.services.plugin_manager import TmsPluginManager
from testit_python_commons.services.step_manager import StepManager
from testit_python_commons.services.utils import Utils

# Import sync storage components
try:
    from .sync_storage import (
        SyncStorageAdapterInterface,
        SyncStorageConfig,
        SyncStorageRunner,
        TestResultManager,
    )

    __all__ = [
        "AdapterManager",
        "TmsPluginManager",
        "FixtureManager",
        "StepManager",
        "Utils",
        "SyncStorageRunner",
        "TestResultManager",
        "SyncStorageConfig",
        "SyncStorageAdapterInterface",
        "hookimpl",
    ]
except ImportError:
    # Sync storage components not available
    __all__ = [
        "AdapterManager",
        "TmsPluginManager",
        "FixtureManager",
        "StepManager",
        "Utils",
        "hookimpl",
    ]

hookimpl = HookimplMarker("testit")
