# 🧪 Mobile-simulate API Reference

## Overview

Mobile Simulate helps you apply and persist device simulation settings (properties, sensors, packages, services)
by storing a device profile in a context and applying it during session creation.


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
- `mode` (MobileSimulateMode): The simulate mode

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
- `MobileSimulateConfig`: The simulate config

### hasMobileInfo

```java
public boolean hasMobileInfo(ContextSync contextSync)
```

Check if the mobile dev info file exists in one context sync.

**Parameters:**
- `contextSync` (ContextSync): The context sync to check

**Returns:**
- `boolean`: True if the mobile dev info file exists, False otherwise

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
- `contextSync` (ContextSync): Optional context sync. If not provided, a new context will be created

**Returns:**
- `MobileSimulateUploadResult`: MobileSimulateUploadResult containing the result of the upload operation



## 🔗 Related Resources

- [Mobile API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/mobile-use/mobile.md)
- [Context Sync API Reference](/Users/liyuebing/Projects/wuying-agentbay-sdk/java/docs/api/common-features/basics/context-sync.md)

