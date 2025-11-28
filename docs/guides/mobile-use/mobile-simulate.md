# Mobile Device Simulation

This guide demonstrates how to use the mobile device simulation feature in AgentBay SDK to simulate different mobile devices with specific hardware characteristics and properties across sessions.

## Table of Contents
- [Overview](#overview)
- [What is Mobile Simulate](#what-is-mobile-simulate)
- [Simulation Modes](#simulation-modes)
- [Device Info Format](#device-info-format)
- [Basic Usage](#basic-usage)
- [Using with User Context](#using-with-user-context)
- [Best Practices](#best-practices)

## Overview

Mobile device simulation allows you to:

- **Simulate Real Devices**: Mimic the properties and characteristics of real mobile devices
- **Cross-Session Persistence**: Maintain device identity across multiple sessions
- **Flexible Configuration**: Choose different level simulate mode for device simulation

**Note:** Due to stability reasons, we recommend using mobile simulate feature in Android 12 image but not Android 14 image.

## What is Mobile Simulate

Mobile Simulate is a feature that allows you to configure a mobile session to mimic a specific mobile device. This includes:

- **Device Properties**: Model name, manufacturer, Android version, build information
- **Hardware Characteristics**: Screen resolution, CPU architecture, memory configuration
- **Installed Packages**: Application packages installed on the device
- **System Services**: System-level services running on the device

The mobile device information is stored in a JSON file that can be obtained from:
- Real devices info by using DumpSDK tools
- User maintained mobile info database
**Note:** For more information, please contact AgentBay support team for assistance

## Simulation Modes

AgentBay supports five simulation modes, allowing you to choose the level of device simulation based on your needs:

### Properties Only Mode

Simulates device properties without modifying hardware characteristics. This mode is most recommended.

```python
MobileSimulateMode.PROPERTIES_ONLY
```

### Sensors Only Mode

Simulates only the device sensors information (accelerometer, gyroscope, etc.).

```python
MobileSimulateMode.SENSORS_ONLY
```

### Packages Only Mode

Simulates only the installed packages on the device.

```python
MobileSimulateMode.PACKAGES_ONLY
```

### Services Only Mode

Simulates only the system services running on the device.

```python
MobileSimulateMode.SERVICES_ONLY
```

### All Mode

Provides comprehensive device simulation including all aspects: properties, sensors, packages, and services. This mode offers the most realistic device emulation.

```python
MobileSimulateMode.ALL
```

## Device Info Format

Mobile device information files contain detailed device characteristics in JSON format.

Example device info file structure:
```json
{
    "version": 1,
    "properties": {
        "ro.product.model": "V2429A",
        "ro.xxx": "xxx"
    },
    "packages": []
}
```

## Basic Usage
We can using a persistence mobile simulate context id to simulate mobile devices across sessions. User only need to store persistence the context id.

- using `upload_mobile_info` interface to upload a user device info and a context id will return.
- config `MobileSimulateConfig` for `CreateSessionParams` when create session, we can simulate mobile automaticly.

### Python Example

```python
from agentbay import AgentBay, MobileSimulateService
from agentbay.session_params import CreateSessionParams, ExtraConfigs
from agentbay.api.models import MobileExtraConfig, MobileSimulateMode

# Initialize AgentBay client
agent_bay = AgentBay(api_key="your_api_key")

# Step 1: Create MobileSimulateService and configure
simulate_service = MobileSimulateService(agent_bay)
simulate_service.set_simulate_enable(True)
simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)

# Step 2: Upload mobile device info file
with open("mobile_info_model_a.json", "r") as f:
    mobile_info_content = f.read()

upload_result = simulate_service.upload_mobile_info(mobile_info_content)
if not upload_result.success:
    print(f"Failed to upload: {upload_result.error_message}")
    exit(1)

mobile_sim_context_id = upload_result.mobile_simulate_context_id
print(f"Mobile simulate context ID: {mobile_sim_context_id}")

# Step 3: Create session with mobile simulate configuration
params = CreateSessionParams(
    image_id="mobile_latest",
    extra_configs=ExtraConfigs(
        mobile=MobileExtraConfig(
            simulate_config=simulate_service.get_simulate_config()
        )
    )
)

session_result = agent_bay.create(params)
if not session_result.success:
    print(f"Failed to create session: {session_result.error_message}")
    exit(1)

session = session_result.session
print(f"Session created with ID: {session.session_id}")

# Step 4: Wait for mobile simulate to complete
import time
time.sleep(5)

# Step 5: Verify device simulation
result = session.command.execute_command("getprop ro.product.model")
if result.success:
    print(f"Device model: {result.output.strip()}")

# Step 6: Cleanup
agent_bay.delete(session)
```

### TypeScript Example

```typescript
import { AgentBay, MobileSimulateService, MobileSimulateMode } from 'wuying-agentbay-sdk';
import { readFileSync } from 'fs';

// Initialize AgentBay client
const client = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY! });

// Step 1: Create MobileSimulateService and configure
const simulateService = new MobileSimulateService(client);
simulateService.setSimulateEnable(true);
simulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);

// Step 2: Upload mobile device info file
const mobileInfoContent = readFileSync('mobile_info_model_a.json', 'utf-8');

const uploadResult = await simulateService.uploadMobileInfo(mobileInfoContent);
if (!uploadResult.success) {
  throw new Error(`Failed to upload: ${uploadResult.errorMessage}`);
}

const mobileSimContextId = uploadResult.mobileSimulateContextId!;
console.log(`Mobile simulate context ID: ${mobileSimContextId}`);

// Step 3: Create session with mobile simulate configuration
const sessionResult = await client.create({
  imageId: 'mobile_latest',
  extraConfigs: {
    mobile: {
      simulateConfig: simulateService.getSimulateConfig(),
    },
  },
});

if (!sessionResult.success || !sessionResult.session) {
  throw new Error(`Failed to create session: ${sessionResult.errorMessage}`);
}

const session = sessionResult.session;
console.log(`Session created with ID: ${session.sessionId}`);

// Step 4: Wait for mobile simulate to complete
await new Promise(resolve => setTimeout(resolve, 5000));

// Step 5: Verify device simulation
const result = await session.command.executeCommand('getprop ro.product.model');
if (result.success) {
  console.log(`Device model: ${result.output.trim()}`);
}

// Step 6: Cleanup
await session.delete();
```

### Go Example

```go
package main

import (
	"fmt"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

func main() {
	// Initialize AgentBay client
	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
	if err != nil {
		panic(err)
	}

	// Step 1: Create MobileSimulateService and configure
	simulateService, err := agentbay.NewMobileSimulateService(client)
	if err != nil {
		panic(err)
	}
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	// Step 2: Upload mobile device info file
	mobileInfoContent, err := os.ReadFile("mobile_info_model_a.json")
	if err != nil {
		panic(err)
	}

	uploadResult := simulateService.UploadMobileInfo(string(mobileInfoContent), nil)
	if !uploadResult.Success {
		panic(uploadResult.ErrorMessage)
	}

	mobileSimContextID := uploadResult.MobileSimulateContextID
	fmt.Printf("Mobile simulate context ID: %s\n", mobileSimContextID)

	// Step 3: Create session with mobile simulate configuration
	params := &agentbay.CreateSessionParams{
		ImageId: "mobile_latest",
		ExtraConfigs: &models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		},
	}

	sessionResult, err := client.Create(params)
	if err != nil || !sessionResult.Success {
		panic("Failed to create session")
	}

	session := sessionResult.Session
	fmt.Printf("Session created with ID: %s\n", session.SessionID)

	// Step 4: Wait for mobile simulate to complete
	time.Sleep(5 * time.Second)

	// Step 5: Verify device simulation
	result, err := session.Command.ExecuteCommand("getprop ro.product.model")
	if err == nil && result.Success {
		fmt.Printf("Device model: %s\n", result.Output)
	}

	// Step 6: Cleanup
	session.Delete()
}
```

## Using with User Context

For persistent device simulation across multiple sessions, use user-specific contexts. This approach allows you to:

- Store device information in a user's context
- Reuse device configuration across sessions

### Python Example with Context

```python
from agentbay import AgentBay, MobileSimulateService
from agentbay.context_sync import ContextSync, SyncPolicy, BWList, WhiteList
from agentbay.session_params import CreateSessionParams, ExtraConfigs
from agentbay.api.models import MobileExtraConfig, MobileSimulateMode

# Initialize AgentBay client
agent_bay = AgentBay(api_key="your_api_key")

# Step 1: Get or create user-specific context
context_result = agent_bay.context.get("user_phone_number", create=True)
context = context_result.context

# Step 2: Create context sync configuration
sync_policy = SyncPolicy(
    bw_list=BWList(
        white_lists=[
            WhiteList(path="/com.wuying.devinfo", exclude_paths=[])
        ]
    )
)

context_sync = ContextSync(
    context_id=context.id,
    path="/data/data",
    policy=sync_policy,
)

# Step 3: Create MobileSimulateService and configure
simulate_service = MobileSimulateService(agent_bay)
simulate_service.set_simulate_enable(True)
simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)

# Step 4: Check and upload mobile info if needed
has_mobile_info = simulate_service.has_mobile_info(context_sync)
if not has_mobile_info:
    with open("mobile_info_model_a.json", "r") as f:
        mobile_info_content = f.read()
    
    upload_result = simulate_service.upload_mobile_info(
        mobile_info_content, 
        context_sync
    )
    if not upload_result.success:
        print(f"Failed to upload: {upload_result.error_message}")
        exit(1)
    print("Mobile device info uploaded successfully")
else:
    print("Mobile device info already exists in context")

# Step 5: Create session with context sync
params = CreateSessionParams(
    image_id="mobile_latest",
    context_syncs=[context_sync],
    extra_configs=ExtraConfigs(
        mobile=MobileExtraConfig(
            simulate_config=simulate_service.get_simulate_config()
        )
    )
)

session_result = agent_bay.create(params)
session = session_result.session

# Step 6: Use the session
# Device info is automatically loaded from context
result = session.command.execute_command("getprop ro.product.model")
print(f"Device model: {result.output.strip()}")

# Step 7: Delete session with context sync
agent_bay.delete(session, sync_context=True)
```

### TypeScript Example with Context

```typescript
import { AgentBay, MobileSimulateService, MobileSimulateMode, ContextSync, SyncPolicy } from 'wuying-agentbay-sdk';
import { readFileSync } from 'fs';

const client = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY! });

// Step 1: Get or create user-specific context
const contextResult = await client.context.get('user_phone_number', true);
const context = contextResult.context!;

// Step 2: Create context sync configuration
const syncPolicy: SyncPolicy = {
  bwList: {
    whiteLists: [
      { path: '/com.wuying.devinfo', excludePaths: [] }
    ]
  }
};

const contextSync: ContextSync = {
  contextId: context.id,
  path: '/data/data',
  policy: syncPolicy
};

// Step 3: Create MobileSimulateService and configure
const simulateService = new MobileSimulateService(client);
simulateService.setSimulateEnable(true);
simulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);

// Step 4: Check and upload mobile info if needed
const hasMobileInfo = await simulateService.hasMobileInfo(contextSync);
if (!hasMobileInfo) {
  const mobileInfoContent = readFileSync('mobile_info_model_a.json', 'utf-8');
  
  const uploadResult = await simulateService.uploadMobileInfo(
    mobileInfoContent,
    contextSync
  );
  if (!uploadResult.success) {
    throw new Error(`Failed to upload: ${uploadResult.errorMessage}`);
  }
  console.log('Mobile device info uploaded successfully');
} else {
  console.log('Mobile device info already exists in context');
}

// Step 5: Create session with context sync
const sessionResult = await client.create({
  imageId: 'mobile_latest',
  contextSync: [contextSync],
  extraConfigs: {
    mobile: {
      simulateConfig: simulateService.getSimulateConfig(),
    },
  },
});

const session = sessionResult.session!;

// Step 6: Use the session
const result = await session.command.executeCommand('getprop ro.product.model');
console.log(`Device model: ${result.output.trim()}`);

// Step 7: Delete session with context sync
await session.delete({ syncContext: true });
```

### Go Example with Context

```go
package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

func main() {
	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))

	// Step 1: Get or create user-specific context
	contextResult, _ := client.Context.Get("user_phone_number", true)
	context := contextResult.Context

	// Step 2: Create context sync configuration
	syncPolicy := &agentbay.SyncPolicy{
		BWList: &agentbay.BWList{
			WhiteLists: []*agentbay.WhiteList{
				{Path: "/com.wuying.devinfo", ExcludePaths: []string{}},
			},
		},
	}

	contextSync := &agentbay.ContextSync{
		ContextID: context.ID,
		Path:      "/data/data",
		Policy:    syncPolicy,
	}

	// Step 3: Create MobileSimulateService and configure
	simulateService, _ := agentbay.NewMobileSimulateService(client)
	simulateService.SetSimulateEnable(true)
	simulateService.SetSimulateMode(models.MobileSimulateModePropertiesOnly)

	// Step 4: Check and upload mobile info if needed
	hasMobileInfo, _ := simulateService.HasMobileInfo(contextSync)
	if !hasMobileInfo {
		mobileInfoContent, _ := os.ReadFile("mobile_info_model_a.json")
		uploadResult := simulateService.UploadMobileInfo(
			string(mobileInfoContent),
			contextSync,
		)
		if !uploadResult.Success {
			panic(uploadResult.ErrorMessage)
		}
		fmt.Println("Mobile device info uploaded successfully")
	} else {
		fmt.Println("Mobile device info already exists in context")
	}

	// Step 5: Create session with context sync
	params := &agentbay.CreateSessionParams{
		ImageId:     "mobile_latest",
		ContextSync: []*agentbay.ContextSync{contextSync},
		ExtraConfigs: &models.ExtraConfigs{
			Mobile: &models.MobileExtraConfig{
				SimulateConfig: simulateService.GetSimulateConfig(),
			},
		},
	}

	sessionResult, _ := client.Create(params)
	session := sessionResult.Session

	// Step 6: Use the session
	result, _ := session.Command.ExecuteCommand("getprop ro.product.model")
	fmt.Printf("Device model: %s\n", result.Output)

	// Step 7: Delete session with context sync
	client.Delete(session, true)
}
```


## Best Practices

### 1. Simulation Mode Selection

- **Development**: Use `PROPERTIES_ONLY` mode for faster iteration
- **Production**: Use `FULL` mode for comprehensive simulation

### 2. Verification

- **Always verify**: Check device properties after session creation
- **Wait time**: Allow 5-10 seconds for simulation to complete
- **Multiple checks**: Verify multiple properties to ensure complete simulation

```python
# Verify multiple device properties
properties_to_check = [
    "ro.product.model",
    "ro.product.manufacturer",
    "ro.build.version.release",
    "ro.product.brand"
]

for prop in properties_to_check:
    result = session.command.execute_command(f"getprop {prop}")
    print(f"{prop}: {result.output.strip()}")
```

### 5. Error Handling

Always implement proper error handling:

```python
simulate_service = None
session = None

try:
    # Create and configure simulate service
    simulate_service = MobileSimulateService(agent_bay)
    simulate_service.set_simulate_enable(True)
    simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
    
    # Upload mobile info
    upload_result = simulate_service.upload_mobile_info(mobile_info_content)
    if not upload_result.success:
        raise Exception(f"Upload failed: {upload_result.error_message}")
    
    # Create session
    session_result = agent_bay.create(params)
    if not session_result.success:
        raise Exception(f"Session creation failed: {session_result.error_message}")
    
    session = session_result.session
    # Use session
    # ...
    
except Exception as e:
    print(f"Error: {e}")
    # Cleanup if needed
finally:
    if session:
        agent_bay.delete(session)
```

### 6. Resource Cleanup

Always clean up resources properly:

```python
# Clean up sessions
try:
    agent_bay.delete(session)
except Exception as e:
    print(f"Cleanup error: {e}")
```

## Related Documentation

- [Mobile Session Configuration](./mobile-session-configuration.md) - Additional mobile configuration options
- [Mobile Application Management](./mobile-application-management.md) - Managing mobile applications
- [Mobile UI Automation](./mobile-ui-automation.md) - Automating mobile UI interactions

## Example Code

Complete working examples are available in the SDK repository:

- **Python**: `python/docs/examples/mobile-use/mobile_simulate_basic_usage.py`
- **Python with Context**: `python/docs/examples/mobile-use/mobile_simulate_with_ctx.py`
- **TypeScript**: `typescript/docs/examples/mobile-use/mobile-simulate-basic-usage.ts`
- **TypeScript with Context**: `typescript/docs/examples/mobile-use/mobile-simulate-with-ctx.ts`
- **Go**: `golang/docs/examples/mobile-use/mobile_simulate_basic_usage/main.go`
- **Go with Context**: `golang/docs/examples/mobile-use/mobile_simulate_with_ctx/main.go`

