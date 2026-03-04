# Cloud Phone Device Simulation

Make an AgentBay cloud phone look and behave like a real physical Android device — and keep the same device identity across sessions.

## What You'll Build

| | Before Simulation | After Simulation |
|---|---|---|
| `ro.product.model` | Generic cloud phone model | **SM-A505F** (Samsung Galaxy A50) |
| `ro.product.brand` | Generic | **samsung** |
| `ro.product.manufacturer` | Generic | **samsung** |

After completing this example you will be able to:

1. Upload a device info file and create a simulated mobile session
2. Verify the cloud phone reports the simulated device properties
3. Destroy and recreate a session while **keeping the same device identity**

## Use Cases

- **App Compatibility Testing** — simulate different brands and models to verify how your app behaves on each device
- **Automation Reliability** — many apps detect emulators/cloud phones and degrade functionality; device simulation avoids this
- **Consistent Device Identity** — across multiple sessions the device fingerprint stays the same, which is essential for long-running automation workflows

## Prerequisites

1. **AgentBay API Key** — [Get one here](https://agentbay.console.aliyun.com/service-management)
2. **Python 3.8+**
3. **AgentBay SDK**:
   ```bash
   pip install wuying-agentbay-sdk
   ```
4. **Device info file** — a JSON file describing the target device properties. A sample file is provided at `resource/mobile_info_model_a.json` in this repository. Contact the AgentBay team for device info files matching other real-world devices.

## Quick Start

```bash
export AGENTBAY_API_KEY=your_api_key_here
cd cookbook/mobile/device-simulation
python main.py
```

### Expected Output

```
============================================================
Step 1: Upload device info & create first simulated session
============================================================
Loaded device info from: .../resource/mobile_info_model_a.json
Device info uploaded. Context ID: SdkCtx-xxxxx
Creating first session...
Session 1 created: s-xxxxx

============================================================
Step 2: Verify simulated device properties
============================================================
  ro.product.model = SM-A505F
  ro.product.brand = samsung
  ro.product.manufacturer = samsung

============================================================
Step 3: Recreate session with same device identity
============================================================
Deleting session 1...
Session 1 deleted.

Creating second session with same context...
Session 2 created: s-yyyyy

============================================================
Step 4: Verify device identity consistency across sessions
============================================================
  ✓ ro.product.model: SM-A505F (session 1: SM-A505F)
  ✓ ro.product.brand: samsung (session 1: samsung)
  ✓ ro.product.manufacturer: samsung (session 1: samsung)

Device identity is consistent across sessions!
```

## How It Works

### Device Info File

The device info file is a simple JSON describing Android system properties:

```json
{
  "properties": {
    "ro.product.model": "SM-A505F",
    "ro.product.brand": "samsung",
    "ro.product.name": "a505f",
    "ro.product.device": "a505f",
    "ro.product.manufacturer": "samsung"
  }
}
```

When applied, these properties override the cloud phone's default system properties via `setprop`, making the device appear as the specified model to any running application.

### Key API Components

| Component | Role |
|---|---|
| `MobileSimulateService` | Manages device info upload and simulation configuration |
| `MobileSimulateMode` | Controls what gets simulated: `PROPERTIES_ONLY`, `SENSORS_ONLY`, `PACKAGES_ONLY`, `SERVICES_ONLY`, or `ALL` |
| `simulate_context_id` | A persistent identifier for the device info — reuse it across sessions to maintain the same device identity |

### Simulation Modes

| Mode | What It Simulates | When to Use |
|---|---|---|
| `PROPERTIES_ONLY` | Device brand, model, manufacturer, etc. | Most common — sufficient for app compatibility testing |
| `SENSORS_ONLY` | Accelerometer, gyroscope, and other sensor data | When apps check sensor presence for emulator detection |
| `PACKAGES_ONLY` | Installed application list | When apps scan for specific system apps |
| `SERVICES_ONLY` | System services | When apps query running services |
| `ALL` | All of the above | Maximum fidelity — recommended for strict anti-detection scenarios |

### Workflow Overview

```
                    ┌──────────────────┐
                    │  Device Info JSON │
                    └────────┬─────────┘
                             │ upload
                             ▼
                    ┌──────────────────┐
                    │  Context (stored) │ ◄── persistent across sessions
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         Session 1      Session 2      Session N
         SM-A505F       SM-A505F       SM-A505F
         samsung        samsung        samsung
```

## Code Walkthrough

### 1. Configure and Upload Device Info

```python
simulate_service = AsyncMobileSimulateService(agent_bay)
simulate_service.set_simulate_enable(True)
simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)

with open("mobile_info.json", "r") as f:
    mobile_info_content = f.read()

upload_result = await simulate_service.upload_mobile_info(mobile_info_content)
simulate_context_id = upload_result.mobile_simulate_context_id
```

### 2. Create a Simulated Session

```python
params = CreateSessionParams(
    image_id="mobile_latest",
    extra_configs=ExtraConfigs(
        mobile=MobileExtraConfig(
            simulate_config=simulate_service.get_simulate_config()
        )
    ),
)
result = await agent_bay.create(params)
session = result.session
```

### 3. Reuse the Same Device Identity

```python
simulate_service2 = AsyncMobileSimulateService(agent_bay)
simulate_service2.set_simulate_enable(True)
simulate_service2.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
simulate_service2.set_simulate_context_id(simulate_context_id)  # reuse!

params2 = CreateSessionParams(
    image_id="mobile_latest",
    extra_configs=ExtraConfigs(
        mobile=MobileExtraConfig(
            simulate_config=simulate_service2.get_simulate_config()
        )
    ),
)
```

## What's Next

- **[App Login Persistence](../app-login-persistence/)** — combine device simulation with login state persistence for a complete "real device" automation experience
- **[Natural Language Mobile Control](../nl-mobile-control/)** — control the simulated device using natural language commands
- **[MobileSimulate API Reference](../../../python/docs/api/async/async-mobile-simulate.md)** — full API documentation
