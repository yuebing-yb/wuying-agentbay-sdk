# ExtraConfigs API 文档

## 概述

`ExtraConfigs` 提供高级配置参数，用于在创建会话时进行特殊环境配置。目前主要支持移动环境的配置选项。

## 类定义

```java
package com.aliyun.agentbay.model;

public class ExtraConfigs {
    private MobileExtraConfig mobile;
}
```

## 构造函数

### ExtraConfigs()
创建一个空的 ExtraConfigs 实例。

```java
ExtraConfigs extraConfigs = new ExtraConfigs();
```

### ExtraConfigs(MobileExtraConfig mobile)
使用移动配置创建 ExtraConfigs 实例。

**参数**:
- `mobile` - 移动环境配置

```java
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
```

## 方法

### getMobile()
获取移动环境配置。

**返回**: `MobileExtraConfig` - 移动配置，如果未设置则返回 null

```java
MobileExtraConfig mobileConfig = extraConfigs.getMobile();
```

### setMobile(MobileExtraConfig mobile)
设置移动环境配置。

**参数**:
- `mobile` - 移动环境配置

```java
MobileExtraConfig mobileConfig = new MobileExtraConfig();
extraConfigs.setMobile(mobileConfig);
```

### validate()
验证配置的有效性。

**抛出**: `IllegalArgumentException` - 如果配置无效

```java
extraConfigs.validate();
```

### toMap()
转换为 Map 格式供 API 请求使用。

**返回**: `Map<String, Object>` - Map 表示

```java
Map<String, Object> map = extraConfigs.toMap();
```

### fromMap(Map<String, Object> map)
从 Map 创建 ExtraConfigs 实例。

**参数**:
- `map` - Map 表示

**返回**: `ExtraConfigs` 实例

```java
ExtraConfigs restored = ExtraConfigs.fromMap(map);
```

## 使用场景

### 1. 移动环境配置

```java
import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.session.CreateSessionParams;

// 创建移动配置
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setHideNavigationBar(true);

// 创建 ExtraConfigs
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

// 应用到会话创建
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

AgentBay agentBay = new AgentBay(apiKey);
SessionResult result = agentBay.create(params);
```

### 2. 应用白名单配置

```java
import com.aliyun.agentbay.mobile.AppManagerRule;
import java.util.Arrays;

// 创建应用白名单
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList(
        "com.android.settings",
        "com.android.chrome"
    )
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setAppManagerRule(whitelist);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
```

### 3. 设备模拟配置

```java
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;

// 创建设备模拟配置
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,                              // 启用模拟
    "/tmp/mobile_dev_info",            // 设备信息路径
    MobileSimulateMode.ALL,            // 模拟所有属性
    "device-context-id"                // 设备信息的 Context ID
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setSimulateConfig(simulateConfig);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
```

### 4. 完整配置示例

```java
import com.aliyun.agentbay.mobile.*;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

// 创建完整的移动配置
AppManagerRule appRule = new AppManagerRule(
    "Black",
    Arrays.asList("com.unwanted.app")
);

MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,
    "/tmp/device_info",
    MobileSimulateMode.PROPERTIES_ONLY,
    "xiaomi-13-context"
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setAppManagerRule(appRule);
mobileConfig.setHideNavigationBar(true);
mobileConfig.setUninstallBlacklist(Arrays.asList("com.android.systemui"));
mobileConfig.setSimulateConfig(simulateConfig);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

// 创建会话
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);
params.setPolicyId("my-policy");
params.setEnableBrowserReplay(false);

Map<String, String> labels = new HashMap<>();
labels.put("project", "mobile-automation");
params.setLabels(labels);

AgentBay agentBay = new AgentBay(apiKey);
SessionResult result = agentBay.create(params);
Session session = result.getSession();
```

## 相关类

- [MobileExtraConfig](MobileExtraConfig.md) - 移动环境配置
- [CreateSessionParams](CreateSessionParams.md) - 会话创建参数

## 注意事项

1. **验证配置**: 在使用前调用 `validate()` 确保配置有效
2. **移动环境**: `extra_configs` 主要用于 `mobile_latest` 镜像
3. **自动应用**: 配置会在会话创建时自动应用
4. **JSON 序列化**: 使用 Jackson 注解确保正确的 API 调用格式

## 完整示例

参考示例代码：
- [MobileExtraConfig 使用指南](../examples/mobile-extra-config-usage.md)

