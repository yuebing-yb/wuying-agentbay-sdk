# Mobile Simulate Example

This example demonstrates how to use the mobile simulate feature to simulate different mobile devices across sessions.

## Features

- Upload mobile device information for simulation
- Create multiple sessions with the same simulated device configuration
- Verify device properties after simulation
- Proper session cleanup

## Prerequisites

- AgentBay API key set as environment variable `AGENTBAY_API_KEY`
- Mobile device information file (contact support team to obtain)

## Usage

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Navigate to the example directory
cd golang/docs/examples/mobile-use/mobile_simulate_basic_usage

# Run the example
go run main.go
```

## What This Example Does

1. **Upload Mobile Info**: Uploads a mobile device information file to create a simulate context
2. **First Session**: Creates a mobile session with the simulated device configuration
3. **Verify Device**: Checks the device model to confirm simulation is working
4. **Second Session**: Creates another session using the same simulated context
5. **Verify Consistency**: Confirms both sessions have the same device properties
6. **Cleanup**: Properly deletes both sessions

## Key Concepts

### Mobile Simulate Service

The `MobileSimulateService` is now part of the main `agentbay` package:

```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

// Create mobile simulate service
simulateService, err := agentbay.NewMobileSimulateService(client)
if err != nil {
    log.Fatalf("Failed to create mobile simulate service: %v", err)
}
```

### Create Session with Mobile Simulate
Creates a session with mobile simulate configuration and the user's context:
```go
params := &agentbay.CreateSessionParams{
    ImageId:      "mobile_latest",
    ContextSyncs: []*agentbay.ContextSync{contextSync},
    ExtraConfigs: &models.ExtraConfigs{
        Mobile: &models.MobileExtraConfig{
            SimulateConfig: simulateService.GetSimulateConfig(),
        },
    },
}
```

### Simulate Modes

- `MobileSimulateModePropertiesOnly`: Only simulate device properties (build.prop)
- `MobileSimulateModeSensorsOnly`: Only simulate sensors information
- `MobileSimulateModePackagesOnly`: Only simulate installed packages
- `MobileSimulateModeServicesOnly`: Only simulate system services
- `MobileSimulateModeAll`: Simulate all aspects

## Output Example

```
=== Mobile Simulate Example ===

AgentBay client initialized
=== First Mobile Session ===
Uploading mobile info file for first time...
Mobile simulate context id uploaded successfully: ctx_abc123
Creating first session...
Session created with ID: sess_xyz789
Waiting for mobile simulate to complete...
Getting device model after mobile simulate...
First session device model: Pixel 6

Deleting first session...
First session deleted successfully (RequestID: req_123)

=== Second Mobile Session ===
Creating second session...
Session created with ID: sess_def456
Waiting for mobile simulate to complete...
Getting device model after mobile simulate...
Second session device model: Pixel 6

Deleting second session...
Second session deleted successfully (RequestID: req_456)

=== Example completed successfully ===
```

## Related Examples

- [Mobile Get ADB URL](../mobile_get_adb_url/README.md) - Get ADB connection URL for mobile sessions
- [Context Management](../../common-features/basics/context_management/README.md) - Learn about context persistence
- [Session Creation](../../common-features/basics/session_creation/README.md) - Basic session creation

## Notes

- The mobile info file path is relative to the example directory
- Wait time after session creation allows the simulation to complete
- The same context ID can be reused across multiple sessions
- Device properties persist across sessions using the same context

