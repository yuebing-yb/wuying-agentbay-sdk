# Mobile Use Examples

This directory contains Java examples demonstrating mobile device automation capabilities of the AgentBay SDK.

## Examples

### 1. MobileUiAutomationExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileUiAutomationExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileUiAutomationExample.java)

Basic mobile UI automation:
- Tapping on screen coordinates
- Swiping gestures
- Text input
- Taking screenshots

**Key features demonstrated:**
```java
// Tap at coordinates
session.getMobile().tap(500, 800);

// Swipe gesture
session.getMobile().swipe(500, 1000, 500, 500, 500);

// Input text
session.getMobile().inputText("Hello World");

// Screenshot
session.getMobile().screenshot("/tmp/screenshot.png");
```

### 2. MobileAppOperationsExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileAppOperationsExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileAppOperationsExample.java)

Application lifecycle management:
- Starting applications
- Stopping applications
- Managing app states
- App package handling

**Key features demonstrated:**
```java
// Start an application
session.getMobile().startApp("com.android.chrome");

// Stop an application
session.getMobile().stopApp("com.android.chrome");

// Check app status
boolean isRunning = session.getMobile().isAppRunning("com.android.chrome");
```

### 3. MobileSystemExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSystemExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSystemExample.java)

System-level mobile operations:
- Send key events
- System UI interactions
- Device information
- System settings

**Key features demonstrated:**
```java
// Send key event (e.g., home button)
session.getMobile().sendKey(KeyEvent.KEYCODE_HOME);

// Back button
session.getMobile().sendKey(KeyEvent.KEYCODE_BACK);

// Get device info
DeviceInfo info = session.getMobile().getDeviceInfo();
```

### 4. MobileGetAdbUrlExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileGetAdbUrlExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileGetAdbUrlExample.java)

ADB connection and debugging:
- Getting ADB connection URL
- Remote ADB access
- Debugging mobile sessions

**Key features demonstrated:**
```java
// Get ADB connection URL
String adbUrl = session.getMobile().getAdbUrl();
System.out.println("ADB URL: " + adbUrl);

// Use with local ADB
// adb connect <adb-url>
```

### 5. MobileSimulateExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSimulateExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSimulateExample.java)

Device simulation and fingerprinting:
- Upload device information
- Simulate specific device models
- Device fingerprinting
- Anti-detection techniques

**Key features demonstrated:**
```java
// Upload device info
session.getMobileSimulate().uploadMobileInfo("/path/to/device_info.json");

// Set simulation mode
session.getMobileSimulate().setSimulateMode(MobileSimulateMode.ALL);
```

### 6. MobileExtraConfigExample.java
**Source**: [`../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileExtraConfigExample.java`](../../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileExtraConfigExample.java)

Advanced mobile session configuration:
- Lock resolution settings
- App manager rules (whitelist/blacklist)
- Hide navigation bar
- Uninstall protection
- Simulation configuration

**Key features demonstrated:**
```java
// Create app whitelist
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList("com.android.settings", "com.android.chrome")
);

// Configure mobile session
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setAppManagerRule(whitelist);
mobileConfig.setHideNavigationBar(true);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

Session session = agentBay.create(params).getSession();
```

## Running the Examples

### Prerequisites

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Use mobile image for session:
```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
```

### Running from Maven

```bash
cd java/agentbay
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.MobileUiAutomationExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.MobileAppOperationsExample"
mvn compile exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.MobileExtraConfigExample"
```

## Common Patterns

### Basic Mobile Session
```java
// Create mobile session
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");

Session session = agentBay.create(params).getSession();

// Interact with device
session.getMobile().tap(500, 800);
session.getMobile().swipe(500, 1000, 500, 500, 500);
```

### App Management
```java
// Start app
session.getMobile().startApp("com.example.app");

// Perform operations
session.getMobile().tap(500, 800);
session.getMobile().inputText("test");

// Stop app
session.getMobile().stopApp("com.example.app");
```

### Device Simulation
```java
// Create simulation config
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,                              // Enable simulation
    "/tmp/device_info.json",           // Device info path
    MobileSimulateMode.ALL,            // Simulate all properties
    "device-context-id"                // Context ID for device info
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setSimulateConfig(simulateConfig);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);
```

### App Whitelist/Blacklist
```java
// Create whitelist (only allow these apps)
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList("com.android.settings", "com.android.chrome")
);

// Or create blacklist (block these apps)
AppManagerRule blacklist = new AppManagerRule(
    "Black",
    Arrays.asList("com.malicious.app")
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setAppManagerRule(whitelist);
```

## Related Documentation

- [Mobile API](../../api/mobile-use/mobile.md)
- [MobileSimulate API](../../api/mobile-use/mobile-simulate.md)

## Troubleshooting

**Mobile operations fail:**
- Ensure image is "mobile_latest"
- Check session is active
- Verify coordinates are within screen bounds

**App start fails:**
- Check app package name is correct
- Verify app is installed in the image
- Check app is not in blacklist

**ADB connection issues:**
- Get fresh ADB URL with `getAdbUrl()`
- Check network connectivity
- Verify ADB is installed locally

**Simulation not working:**
- Upload device info before starting session
- Check simulation mode is set correctly
- Verify device info format is valid

**App manager rules not applied:**
- Set rules in `ExtraConfigs` before session creation
- Cannot modify rules after session is created
- Check package names are correct
