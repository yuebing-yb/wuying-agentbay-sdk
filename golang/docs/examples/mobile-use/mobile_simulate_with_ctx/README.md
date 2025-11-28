# Mobile Simulate with User Specific Context Example

This example demonstrates how to use the mobile simulate feature with a user specific context to simulate mobile devices across sessions.

## Overview

This example shows:
1. Getting a user specific context
2. Checking if the mobile dev info file exists in user's specific context
3. Uploading mobile dev info file to user's specific context if not exists
4. Creating a session with mobile simulate configuration and user's specific context
5. Waiting for mobile simulate to complete
6. Getting device model after mobile simulate
7. Deleting session with context sync

## Prerequisites

- Go 1.16 or higher
- AgentBay API key
- Mobile info file (contact support team for details)

## Setup

1. Set your API key as an environment variable:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Ensure you have the mobile info file at `resource/mobile_info_model_a.json`

## Running the Example

```bash
cd golang/docs/examples/mobile-use/mobile_simulate_with_ctx
go run main.go
```

## What This Example Does

### 1. Create Mobile Simulate Service

The `MobileSimulateService` is now part of the main `agentbay` package:

```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

// Create mobile simulate service
simulateService, err := agentbay.NewMobileSimulateService(client)
if err != nil {
    log.Fatalf("Failed to create mobile simulate service: %v", err)
}
```

### 2. Get User Specific Context
The example first gets or creates a user-specific context using a phone number as identifier:
```go
contextResult, err := client.Context.Get("13000000002", true)
```

### 3. Create Context Sync Configuration
Creates a context sync with a white list policy to sync specific paths:
```go
syncPolicy := &agentbay.SyncPolicy{
    BWList: &agentbay.BWList{
        WhiteLists: []*agentbay.WhiteList{
            {
                Path:         "/com.wuying.devinfo",
                ExcludePaths: []string{},
            },
        },
    },
}

contextSync := &agentbay.ContextSync{
    ContextID: context.ID,
    Path:      "/data/data",
    Policy:    syncPolicy,
}
```

### 4. Check and Upload Mobile Info
Checks if mobile dev info exists in the context, and uploads it if not:
```go
hasMobileInfo, err := simulateService.HasMobileInfo(contextSync)
if err != nil {
    log.Fatalf("Failed to check mobile info: %v", err)
}

if !hasMobileInfo {
    uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), contextSync)
    if !uploadResult.Success {
        log.Fatalf("Failed to upload mobile info: %s", uploadResult.ErrorMessage)
    }
}
```

### 5. Configure Mobile Simulate
Set up the simulate service with desired configuration:
```go
simulateService.SetSimulateEnable(true)
simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)
```

### 6. Create Session with Mobile Simulate
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

### 7. Verify Mobile Simulate
Verifies the mobile simulate by checking the device model:
```go
result, err := session.Command.ExecuteCommand("getprop ro.product.model")
```

### 8. Delete Session with Context Sync
Deletes the session and syncs the context back:
```go
deleteResult, err := session.Delete(&agentbay.DeleteSessionParams{
    SyncContext: true,
})
```

## Expected Output

```
=== Mobile Simulate with User Specific Context Example ===

AgentBay client initialized
Getting a user specific context...
context.id = <context_id>, context.name = 13000000000
Checking or uploading mobile dev info file...
Mobile dev info uploaded successfully
Creating session...
Session created with ID: <session_id>
Session: <session_details>
Waiting 5 seconds for mobile simulate to complete...
Getting device model after mobile simulate...
Session device model: <device_model>

Deleting session...
Session deleted successfully (RequestID: <request_id>)

=== Example completed successfully ===
```

## Key Concepts

### User Specific Context
- Allows persisting mobile device information across sessions
- Identified by a unique identifier (e.g., phone number)
- Can be reused across multiple sessions

### Context Sync
- Synchronizes specific paths between local and remote contexts
- Uses white list policy to control what gets synced
- Supports sync on session creation and deletion

### Mobile Simulate Modes
- `PropertiesOnly`: Only simulates device properties
- `Full`: Full device simulation including hardware characteristics

## Notes

- The mobile info file contains device-specific information
- Contact the support team for guidance on obtaining mobile info files
- The context sync ensures device information persists across sessions
- Use `SyncContext: true` when deleting to save changes back to context

## Related Examples

- [Mobile Simulate Basic Usage](../mobile_simulate_basic_usage/README.md) - Basic mobile simulate without user context
- [Mobile Get ADB URL](../mobile_get_adb_url/README.md) - Getting ADB connection URL

