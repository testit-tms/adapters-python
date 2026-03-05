# Test IT Adapter Interaction with Sync Storage Specification

This document describes how the Test IT Java adapter interacts with the Sync Storage service. This specification can be used to implement similar functionality in adapters for other programming languages.

## Overview

The Sync Storage is a separate service that manages test execution coordination in distributed testing environments. The Java adapter communicates with it to:

1. Coordinate test execution across multiple workers
2. Send real-time test results during execution
3. Determine which worker acts as the master coordinator

## Initialization Process

### Creating the SyncStorageRunner

1. During adapter initialization, if TMS integration is enabled, the adapter attempts to initialize the Sync Storage:
   - A test run ID is obtained or created via the Test IT API
   - A `SyncStorageRunner` instance is created with:
     - `testRunId`: The ID of the test run
     - `port`: Default port "49152" (can be configured)
     - `baseURL`: Test IT server URL
     - `privateToken`: Authentication token

### Starting the Sync Storage Service

When `SyncStorageRunner.start()` is called:

1. Check if Sync Storage is already running on the specified port
2. If running externally:
   - Mark as external service
   - Attempt to register the worker
3. If not running:
   - Download the appropriate Sync Storage executable for the current OS/architecture
   - Start the Sync Storage process with the provided configuration
   - Wait for the service to start (30-second timeout)
   - Register the worker with the service

### Worker Registration

During registration, the adapter sends a POST request to `/register`:

```
POST http://localhost:{port}/register
Content-Type: application/json

{
  "pid": "worker-{threadId}-{timestamp}",
  "testRunId": "{testRunId}"
}
```

The response indicates whether this worker is the master:

```json
{
  "is_master": true|false
}
```

## Test Execution Flow

### Test Case Completion

When a test case completes (`stopTestCase`):

1. If the current worker is the master AND no test is already in progress:
   - Serialize the test result to JSON
   - Send it to Sync Storage via POST to `/in_progress_test_result`
   - Mark the test as "IN PROGRESS" for Test IT
   - Write the test result in real-time to Test IT
   - Set the "already in progress" flag to prevent duplicate sending
2. Otherwise:
   - Write the test result normally to Test IT

### Sending Test Results to Sync Storage

The adapter sends test results to Sync Storage using:

```
POST http://localhost:{port}/in_progress_test_result?testRunId={testRunId}
Content-Type: application/json

{serialized_test_result_data}
```

The payload is a serialized `AutoTestResultsForTestRunModel` object containing:
- Test execution details
- Status information
- Attachments
- Parameters
- Timing information

## API Endpoints

The Sync Storage service exposes the following endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register a worker and determine master status |
| `/in_progress_test_result` | POST | Receive in-progress test results |

## Error Handling

The adapter handles several error conditions:
- Failed Sync Storage initialization (logs warning and continues)
- Failed worker registration (logs error)
- Failed test result serialization (logs warning)
- Failed HTTP requests to Sync Storage (logs warning)
- Sync Storage startup timeouts (throws exception)

## Implementation Considerations

When implementing this functionality in other languages:

1. **Process Management**: Handle downloading, starting, and monitoring the Sync Storage process
2. **Worker Coordination**: Implement the master/worker election mechanism
3. **HTTP Communication**: Implement RESTful communication with proper timeouts
4. **JSON Serialization**: Ensure compatibility with the expected data models
5. **Error Resilience**: Gracefully handle network issues and service failures
6. **Cross-platform Support**: Account for different OS/architecture combinations when downloading executables

## Configuration

The Sync Storage integration uses these configuration parameters:
- `testRunId`: Test run identifier
- `port`: Port for Sync Storage service (default: 49152)
- `baseURL`: Test IT server URL
- `privateToken`: Authentication token for Test IT API

This specification provides the essential information needed to replicate the Java adapter's Sync Storage interaction in other programming languages.