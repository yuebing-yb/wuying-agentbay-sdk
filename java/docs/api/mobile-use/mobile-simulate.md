# 🧪 Mobile-simulate API Reference

## Overview

Mobile Simulate helps you apply and persist device simulation settings (properties, sensors, packages, services) by storing a device profile in a context and applying it during session creation.


## 📚 Tutorial

[Mobile Simulate Guide](../../../../docs/guides/mobile-use/mobile-simulate.md)

Use mobile simulate to emulate device properties and persist them with context sync

## MobileSimulate

Service for managing persistent mobile device info and syncing to mobile devices.
Provides methods to upload mobile simulation data and configure simulation settings.

### Constructor

```java
public MobileSimulate(AgentBay agentBay)
```

### Methods

### setSimulateEnable

```java
public void setSimulateEnable(boolean enable)
```

Set the simulate enable flag.

**Parameters:**
- `enable` (boolean): The simulate feature enable flag

### getSimulateEnable

```java
public boolean getSimulateEnable()
```

Get the simulate enable flag.

**Returns:**
- `boolean`: The simulate feature enable flag

### setSimulateMode

```java
public void setSimulateMode(MobileSimulateMode mode)
```

Set the simulate mode.

**Parameters:**
- `mode` (MobileSimulateMode): The simulate mode:
            - PROPERTIES_ONLY: Simulate only device properties
            - SENSORS_ONLY: Simulate only device sensors
            - PACKAGES_ONLY: Simulate only installed packages
            - SERVICES_ONLY: Simulate only system services
            - ALL: Simulate all aspects of the device

### getSimulateMode

```java
public MobileSimulateMode getSimulateMode()
```

Get the simulate mode.

**Returns:**
- `MobileSimulateMode`: The simulate mode

### setSimulateContextId

```java
public void setSimulateContextId(String contextId)
```

Set a previously saved simulate context id.
Please make sure the context id is provided by MobileSimulateService but not user side created context.

**Parameters:**
- `contextId` (String): The context ID of the previously saved mobile simulate context

### getSimulateContextId

```java
public String getSimulateContextId()
```

Get the simulate context id.

**Returns:**
- `String`: The context ID of the mobile simulate context

### getSimulateConfig

```java
public MobileSimulateConfig getSimulateConfig()
```

Get the simulate config.

**Returns:**
- `MobileSimulateConfig`: The MobileSimulateConfig containing:
        - simulate: The simulate feature enable flag
        - simulatePath: The path of the mobile dev info file
        - simulateMode: The simulate mode
        - simulatedContextId: The context ID of the mobile info (defaults to null)

### hasMobileInfo

```java
public boolean hasMobileInfo(ContextSync contextSync)
```

Check if the mobile dev info file exists in one context sync.
This method can only be used when mobile simulate context sync is managed by user side.

**Parameters:**
- `contextSync` (ContextSync): The context sync to check

**Returns:**
- `boolean`: True if the mobile dev info file exists, False otherwise

**Throws:**
- `IllegalArgumentException`: if contextSync is not provided, or contextSync.contextId is not provided, or contextSync.path is not provided

### uploadMobileInfo

```java
public MobileSimulateUploadResult uploadMobileInfo(String mobileDevInfoContent, ContextSync contextSync)
```

```java
public MobileSimulateUploadResult uploadMobileInfo(String mobileDevInfoContent)
```

Upload the mobile simulate dev info.

**Parameters:**
- `mobileDevInfoContent` (String): The mobile simulate dev info content to upload (JSON string)
- `contextSync` (ContextSync): Optional context sync:
                   - If not provided, a new context will be created for the mobile simulate service
                     and this context id will be returned by the MobileSimulateUploadResult.
                     User can use this context id to do persistent mobile simulate across sessions.
                   - If provided, the mobile simulate dev info will be uploaded to the context sync
                     in a specific path.

**Returns:**
- `MobileSimulateUploadResult`: MobileSimulateUploadResult containing the result of the upload operation:
        - success: Whether the operation was successful
        - mobileSimulateContextId: The context ID of the mobile info (defaults to empty string)
        - errorMessage: The error message if the operation failed (defaults to empty string)

**Throws:**
- `IllegalArgumentException`: if mobileDevInfoContent is not provided or not a valid JSON string,
        or if contextSync is provided but contextSync.contextId is missing



## 🔗 Related Resources

- [Mobile API Reference](../../api/mobile-use/mobile.md)
- [Context Sync API Reference](../../api/common-features/basics/context-sync.md)

