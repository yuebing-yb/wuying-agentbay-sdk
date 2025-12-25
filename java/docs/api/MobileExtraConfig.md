# MobileExtraConfig API 文档

## 概述

`MobileExtraConfig` 提供移动环境的高级配置选项，包括分辨率控制、应用管理、导航栏设置、卸载保护和设备模拟等功能。

## 类定义

```java
package com.aliyun.agentbay.mobile;

public class MobileExtraConfig {
    private Boolean lockResolution;
    private AppManagerRule appManagerRule;
    private Boolean hideNavigationBar;
    private List<String> uninstallBlacklist;
    private MobileSimulateConfig simulateConfig;
}
```

## 配置项说明

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `lockResolution` | Boolean | null | 是否锁定设备分辨率 |
| `appManagerRule` | AppManagerRule | null | 应用白名单/黑名单规则 |
| `hideNavigationBar` | Boolean | null | 是否隐藏导航栏 |
| `uninstallBlacklist` | List<String> | null | 禁止卸载的应用包名列表 |
| `simulateConfig` | MobileSimulateConfig | null | 设备模拟配置 |

## 构造函数

### MobileExtraConfig()
创建空配置实例。

```java
MobileExtraConfig config = new MobileExtraConfig();
```

### MobileExtraConfig(所有参数)
使用完整参数创建配置。

```java
MobileExtraConfig config = new MobileExtraConfig(
    true,                    // lockResolution
    appRule,                 // appManagerRule
    true,                    // hideNavigationBar
    blacklist,               // uninstallBlacklist
    simulateConfig           // simulateConfig
);
```

## 方法

### 分辨率锁定

```java
public Boolean getLockResolution()
public void setLockResolution(Boolean lockResolution)
```

**示例**:
```java
config.setLockResolution(true);  // 启用锁定
config.setLockResolution(false); // 禁用锁定
```

### 应用管理规则

```java
public AppManagerRule getAppManagerRule()
public void setAppManagerRule(AppManagerRule appManagerRule)
```

**示例**:
```java
// 白名单
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList("com.android.settings", "com.test.app")
);
config.setAppManagerRule(whitelist);

// 黑名单
AppManagerRule blacklist = new AppManagerRule(
    "Black",
    Arrays.asList("com.malicious.app")
);
config.setAppManagerRule(blacklist);
```

### 导航栏可见性

```java
public Boolean getHideNavigationBar()
public void setHideNavigationBar(Boolean hideNavigationBar)
```

**示例**:
```java
config.setHideNavigationBar(true);   // 隐藏
config.setHideNavigationBar(false);  // 显示
```

### 卸载保护

```java
public List<String> getUninstallBlacklist()
public void setUninstallBlacklist(List<String> uninstallBlacklist)
```

**示例**:
```java
config.setUninstallBlacklist(Arrays.asList(
    "com.android.systemui",
    "com.android.settings"
));
```

### 设备模拟配置

```java
public MobileSimulateConfig getSimulateConfig()
public void setSimulateConfig(MobileSimulateConfig simulateConfig)
```

**示例**:
```java
MobileSimulateConfig simConfig = new MobileSimulateConfig(
    true,                           // 启用模拟
    "/tmp/device_info",             // 设备信息路径
    MobileSimulateMode.ALL,         // 模拟所有属性
    "device-ctx-id"                 // Context ID
);
config.setSimulateConfig(simConfig);
```

### 验证

```java
public void validate()
```

验证配置有效性，抛出 `IllegalArgumentException` 如果无效。

```java
try {
    config.validate();
} catch (IllegalArgumentException e) {
    System.err.println("Invalid config: " + e.getMessage());
}
```

### 序列化

```java
public Map<String, Object> toMap()
public static MobileExtraConfig fromMap(Map<String, Object> map)
```

## 完整使用示例

### 示例 1: 基础配置

```java
MobileExtraConfig config = new MobileExtraConfig();
config.setLockResolution(true);
config.setHideNavigationBar(true);

ExtraConfigs extraConfigs = new ExtraConfigs(config);

CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
```

### 示例 2: 应用白名单配置

```java
// 创建白名单规则
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList(
        "com.android.settings",
        "com.android.chrome",
        "com.example.allowed.app"
    )
);

// 配置移动环境
MobileExtraConfig config = new MobileExtraConfig();
config.setLockResolution(true);
config.setAppManagerRule(whitelist);
config.setUninstallBlacklist(Arrays.asList("com.android.systemui"));

// 应用配置
ExtraConfigs extraConfigs = new ExtraConfigs(config);
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
Session session = result.getSession();

System.out.println("Whitelisted apps can launch normally");
System.out.println("Other apps will be blocked");
```

### 示例 3: 设备模拟完整流程

```java
import com.aliyun.agentbay.mobile.MobileSimulate;
import com.aliyun.agentbay.mobile.MobileSimulateUploadResult;
import java.nio.file.Files;
import java.nio.file.Paths;

// Step 1: 准备设备信息
String deviceInfoPath = "path/to/mobile_info_xiaomi13.json";
String deviceInfoContent = new String(Files.readAllBytes(Paths.get(deviceInfoPath)));

// Step 2: 上传设备信息到 Context
MobileSimulate mobileSimulate = agentBay.getMobileSimulate();
mobileSimulate.setSimulateEnable(true);
mobileSimulate.setSimulateMode(MobileSimulateMode.ALL);

MobileSimulateUploadResult uploadResult = 
    mobileSimulate.uploadMobileInfo(deviceInfoContent);

if (!uploadResult.isSuccess()) {
    throw new RuntimeException("Failed to upload device info");
}

String deviceContextId = uploadResult.getMobileSimulateContextId();

// Step 3: 创建模拟配置
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,
    mobileSimulate.getMobileDevInfoPath(),
    MobileSimulateMode.ALL,
    deviceContextId
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setHideNavigationBar(true);
mobileConfig.setSimulateConfig(simulateConfig);

// Step 4: 创建会话
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
Session session = result.getSession();

// Step 5: 等待模拟完成
Thread.sleep(8000);  // 等待 wya apply 命令完成

// Step 6: 验证设备属性
CommandResult modelResult = session.getCommand()
    .executeCommand("getprop ro.product.model");
System.out.println("Device model: " + modelResult.getOutput().trim());
// 输出: "Xiaomi 13" (模拟的设备型号)

CommandResult brandResult = session.getCommand()
    .executeCommand("getprop ro.product.brand");
System.out.println("Device brand: " + brandResult.getOutput().trim());
// 输出: "Xiaomi" (模拟的设备品牌)
```

### 示例 4: 生产环境最佳实践

```java
/**
 * 创建移动测试会话的工厂方法
 */
public Session createMobileTestSession(
    AgentBay agentBay,
    String deviceContextId,
    List<String> allowedApps
) throws Exception {
    
    // 应用白名单
    AppManagerRule whitelist = new AppManagerRule("White", allowedApps);
    
    // 设备模拟
    MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
        true,
        "/tmp/mobile_dev_info",
        MobileSimulateMode.PROPERTIES_ONLY,  // 只模拟属性，更快
        deviceContextId
    );
    
    // 移动配置
    MobileExtraConfig mobileConfig = new MobileExtraConfig();
    mobileConfig.setLockResolution(true);
    mobileConfig.setAppManagerRule(whitelist);
    mobileConfig.setHideNavigationBar(false);  // 保留导航栏方便调试
    mobileConfig.setUninstallBlacklist(Arrays.asList(
        "com.android.systemui",
        "com.android.settings"
    ));
    mobileConfig.setSimulateConfig(simulateConfig);
    
    // 会话参数
    ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
    CreateSessionParams params = new CreateSessionParams();
    params.setImageId("mobile_latest");
    params.setExtraConfigs(extraConfigs);
    params.setPolicyId("production-mobile-policy");
    params.setFramework("my-automation-framework");
    
    Map<String, String> labels = new HashMap<>();
    labels.put("environment", "production");
    labels.put("device", "simulated");
    params.setLabels(labels);
    
    SessionResult result = agentBay.create(params);
    
    if (!result.isSuccess()) {
        throw new RuntimeException("Failed to create session: " + result.getErrorMessage());
    }
    
    return result.getSession();
}
```

## 性能考虑

1. **设备模拟**: `MobileSimulateMode.ALL` 会模拟所有属性，耗时较长（8-15秒）
   - 如果只需要属性，使用 `PROPERTIES_ONLY`（更快）
   
2. **配置验证**: 在开发时使用 `validate()`，生产环境可跳过以提升性能

3. **应用规则**: 白名单模式比黑名单模式更安全，但可能需要更多配置

## 相关 API

- [ExtraConfigs](ExtraConfigs.md)
- [CreateSessionParams](CreateSessionParams.md)
- [Mobile API](mobile-use/mobile.md)

## 参考示例

完整示例代码：
- [基础配置](../examples/mobile-extra-config-usage.md#基础配置)
- [应用白名单/黑名单](../examples/mobile-extra-config-usage.md#2-应用白名单黑名单-appmanagerrule)
- [设备模拟](../examples/mobile-extra-config-usage.md#5-设备模拟-simulateconfig--核心功能)

