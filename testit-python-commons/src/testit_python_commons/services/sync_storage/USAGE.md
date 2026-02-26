# Sync Storage Integration Usage

This document explains how to use the Sync Storage integration in your Test IT Python adapter.

## Overview

The Sync Storage integration allows coordinating test execution across multiple workers in distributed testing environments, similar to the Java adapter implementation.

## Components

1. **SyncStorageRunner** - Main class for managing Sync Storage interactions
2. **TestResultManager** - Handles test result processing with Sync Storage
3. **SyncStorageConfig** - Configuration management for Sync Storage
4. **SyncStorageAdapterInterface** - Interface for framework-specific implementations

## Basic Usage

### 1. Initialize Sync Storage Runner

```python
from testit_python_commons.services.sync_storage import SyncStorageRunner

# Initialize with required parameters
sync_runner = SyncStorageRunner(
    test_run_id="your-test-run-id",
    port="49152",  # Optional, defaults to 49152
    base_url="https://your-testit-instance.com",
    private_token="your-private-token"
)

# Start the service
if sync_runner.start():
    print(f"Sync Storage started successfully. Master worker: {sync_runner.is_master}")
else:
    print("Failed to start Sync Storage")
```

### 2. Handle Test Completion

```python
from testit_python_commons.services.sync_storage import TestResultManager

# Create test result manager
result_manager = TestResultManager(sync_runner)

# When a test completes
test_result = {
    "configurationId": "config-id",
    "autoTestExternalId": "test-external-id",
    "outcome": "Passed",
    "startedOn": "2023-01-01T10:00:00Z",
    "completedOn": "2023-01-01T10:00:05Z",
    "duration": 5000,
    # ... other test result fields
}

# Handle test completion
handled_by_sync_storage = result_manager.handle_test_completion(test_result)

if handled_by_sync_storage:
    print("Test result sent to Sync Storage")
    # Mark test as IN PROGRESS in Test IT
else:
    print("Test result handled normally")
    # Write result normally to Test IT

# After writing to Test IT, finalize handling
result_manager.finalize_test_handling()
```

### 3. Stop Sync Storage

```python
# When finished
sync_runner.stop()
```

## Framework Integration

To integrate with a specific testing framework, implement the `SyncStorageAdapterInterface`:

```python
from testit_python_commons.services.sync_storage import SyncStorageAdapterInterface

class MyFrameworkAdapter(SyncStorageAdapterInterface):
    def initialize_sync_storage(self, config):
        # Initialize Sync Storage with framework config
        self.sync_storage_runner = SyncStorageRunner(
            test_run_id=config["test_run_id"],
            port=config.get("port", "49152"),
            base_url=config["base_url"],
            private_token=config["private_token"]
        )
        return True

    def start_sync_storage(self):
        return self.sync_storage_runner.start()

    def stop_sync_storage(self):
        self.sync_storage_runner.stop()

    def on_test_case_completed(self, test_result):
        # Handle test completion using TestResultManager
        result_manager = TestResultManager(self.sync_storage_runner)
        return result_manager.handle_test_completion(test_result)

    def finalize_test_case_handling(self):
        result_manager = TestResultManager(self.sync_storage_runner)
        result_manager.finalize_test_handling()

# Usage
adapter = MyFrameworkAdapter()
config = {
    "test_run_id": "test-run-123",
    "base_url": "https://testit.example.com",
    "private_token": "token123"
}

if adapter.initialize_sync_storage(config):
    if adapter.start_sync_storage():
        # Run tests...
        adapter.stop_sync_storage()
```

## Configuration

The Sync Storage integration can be configured through:

1. **Direct instantiation** - Pass parameters directly to `SyncStorageRunner`
2. **Application properties** - Use `SyncStorageConfig.from_app_properties()`

```python
from testit_python_commons.services.sync_storage import SyncStorageConfig

# From application properties
properties = {
    "testrunid": "test-run-123",
    "url": "https://testit.example.com",
    "privatetoken": "token123",
    "syncstorage_port": "49152"
}

config = SyncStorageConfig.from_app_properties(properties)

if config.is_valid():
    sync_runner = SyncStorageRunner(
        test_run_id=config.test_run_id,
        port=config.port,
        base_url=config.base_url,
        private_token=config.private_token
    )
```

## Error Handling

The integration includes built-in error handling:

- Network issues are logged as warnings
- Failed registrations are logged as errors
- Service startup timeouts throw exceptions
- All operations gracefully degrade to normal behavior on failure

## Best Practices

1. Always call `stop()` to clean up resources
2. Handle the return values from methods to determine flow control
3. Use `finalize_test_handling()` after writing results to Test IT
4. Check `is_master` to determine worker role
5. Log appropriately for debugging distributed test runs