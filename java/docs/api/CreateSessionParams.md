# CreateSessionParams API 文档

## 概述

`CreateSessionParams` 用于配置会话创建时的各种参数，包括镜像选择、标签、上下文同步、浏览器配置、策略管理、录制设置和高级配置等。

## 类定义

```java
package com.aliyun.agentbay.session;

public class CreateSessionParams {
    private String imageId;
    private Map<String, String> labels;
    private List<ContextSync> contextSyncs;
    private BrowserContext browserContext;
    private String framework;
    private String policyId;                    // 新增
    private Boolean enableBrowserReplay;        // 新增
    private ExtraConfigs extraConfigs;          // 新增
}
```

## 参数说明

### 基础参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `imageId` | String | null | 会话使用的镜像 ID (如 "linux_latest", "mobile_latest", "browser_latest") |
| `labels` | Map<String, String> | null | 自定义标签，用于组织和过滤会话 |
| `framework` | String | null | 框架名称，用于统计追踪 (如 "spring-ai", "langchain4j") |

### 上下文相关参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `contextSyncs` | List<ContextSync> | empty list | 上下文同步配置列表 |
| `browserContext` | BrowserContext | null | 浏览器上下文配置 |

### 新增参数 (v1.x.x+)

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `policyId` | String | null | 应用的策略 ID，用于权限和资源控制 |
| `enableBrowserReplay` | Boolean | null (true) | 是否启用浏览器录制，默认为 true |
| `extraConfigs` | ExtraConfigs | null | 高级配置参数，主要用于移动环境 |

## 构造函数

### CreateSessionParams()
创建默认参数实例。

```java
CreateSessionParams params = new CreateSessionParams();
```

## Getter/Setter 方法

### 基础配置

```java
// Image ID
public String getImageId()
public void setImageId(String imageId)

// Labels
public Map<String, String> getLabels()
public void setLabels(Map<String, String> labels)

// Framework
public String getFramework()
public void setFramework(String framework)
```

### 上下文配置

```java
// Context Syncs
public List<ContextSync> getContextSyncs()
public void setContextSyncs(List<ContextSync> contextSyncs)

// Browser Context
public BrowserContext getBrowserContext()
public void setBrowserContext(BrowserContext browserContext)
```

### 新增配置方法

```java
// Policy ID
public String getPolicyId()
public void setPolicyId(String policyId)

// Browser Replay
public Boolean getEnableBrowserReplay()
public void setEnableBrowserReplay(Boolean enableBrowserReplay)

// Extra Configs
public ExtraConfigs getExtraConfigs()
public void setExtraConfigs(ExtraConfigs extraConfigs)
```

## 使用示例

### 示例 1: 基础会话创建

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("linux_latest");

Map<String, String> labels = new HashMap<>();
labels.put("project", "my-project");
labels.put("environment", "dev");
params.setLabels(labels);

SessionResult result = agentBay.create(params);
```

### 示例 2: 使用自定义策略

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("browser_latest");
params.setPolicyId("production-policy-123");  // 应用自定义策略

SessionResult result = agentBay.create(params);
```

### 示例 3: 禁用浏览器录制

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("browser_latest");
params.setEnableBrowserReplay(false);  // 禁用浏览器录制

SessionResult result = agentBay.create(params);
```

**注意**: 浏览器录制默认是**启用**的。仅当需要禁用时才显式设置为 `false`。

### 示例 4: 移动环境配置

```java
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.mobile.AppManagerRule;
import java.util.Arrays;

// 创建应用白名单
AppManagerRule whitelist = new AppManagerRule(
    "White",
    Arrays.asList("com.android.settings", "com.android.chrome")
);

// 创建移动配置
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setAppManagerRule(whitelist);
mobileConfig.setHideNavigationBar(true);

// 创建 ExtraConfigs
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

// 应用到会话参数
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
```

### 示例 5: 移动设备模拟

```java
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;

// 创建设备模拟配置
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,                              // 启用模拟
    "/tmp/mobile_dev_info",            // 设备信息文件路径
    MobileSimulateMode.ALL,            // 模拟所有属性
    "xiaomi-13-device-context"         // 设备信息的 Context ID
);

// 创建移动配置
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setSimulateConfig(simulateConfig);

// 创建 ExtraConfigs
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

// 应用到会话
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
```

### 示例 6: 组合配置

```java
// 综合使用所有配置选项
AppManagerRule appRule = new AppManagerRule(
    "Black",
    Arrays.asList("com.malicious.app")
);

MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,
    "/tmp/device_info",
    MobileSimulateMode.PROPERTIES_ONLY,
    "device-ctx-id"
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setAppManagerRule(appRule);
mobileConfig.setHideNavigationBar(true);
mobileConfig.setUninstallBlacklist(Arrays.asList("com.android.systemui"));
mobileConfig.setSimulateConfig(simulateConfig);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setPolicyId("comprehensive-policy");
params.setEnableBrowserReplay(false);
params.setExtraConfigs(extraConfigs);
params.setFramework("langchain4j");

Map<String, String> labels = new HashMap<>();
labels.put("environment", "production");
params.setLabels(labels);

SessionResult result = agentBay.create(params);
```

## 配置详解

### policy_id
用于应用预定义的策略配置，控制会话的权限和资源使用。

**使用场景**:
- 生产环境使用受限策略
- 开发环境使用宽松策略
- 不同项目使用不同配置策略

### enable_browser_replay
控制是否启用浏览器操作录制功能。

**特点**:
- **默认启用**: 当参数为 `null` 时，浏览器录制默认启用
- **性能优化**: 禁用录制可提升性能
- **适用场景**: 仅在不需要回放功能时禁用

**注意**: 
- 设置为 `false` 会在创建会话时传递 `enable_record=false` 给 API
- 设置为 `true` 或 `null` 使用默认行为（启用录制）

### extra_configs
提供特殊环境的高级配置，目前主要支持移动环境。

**MobileExtraConfig 配置项**:
- `lockResolution`: 锁定设备分辨率
- `appManagerRule`: 应用白名单/黑名单
- `hideNavigationBar`: 隐藏导航栏
- `uninstallBlacklist`: 卸载保护列表
- `simulateConfig`: 设备属性模拟

## 最佳实践

### 1. 参数验证

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");

// 设置 extra_configs 后进行验证
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
extraConfigs.validate();  // 确保配置有效

params.setExtraConfigs(extraConfigs);
```

### 2. 条件配置

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId(imageId);

// 仅在移动环境时设置 extra_configs
if ("mobile_latest".equals(imageId)) {
    MobileExtraConfig mobileConfig = new MobileExtraConfig();
    mobileConfig.setLockResolution(true);
    params.setExtraConfigs(new ExtraConfigs(mobileConfig));
}

// 仅在浏览器环境时禁用录制
if ("browser_latest".equals(imageId) && skipRecording) {
    params.setEnableBrowserReplay(false);
}
```

### 3. 可重用配置

```java
// 定义可重用的配置模板
public class SessionTemplates {
    public static CreateSessionParams mobileTestTemplate() {
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setHideNavigationBar(true);
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile_latest");
        params.setExtraConfigs(new ExtraConfigs(mobileConfig));
        return params;
    }
    
    public static CreateSessionParams browserTestTemplate() {
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        params.setEnableBrowserReplay(false);  // 测试环境不需要录制
        return params;
    }
}

// 使用模板
CreateSessionParams params = SessionTemplates.mobileTestTemplate();
SessionResult result = agentBay.create(params);
```

## 错误处理

```java
try {
    CreateSessionParams params = new CreateSessionParams();
    params.setImageId("mobile_latest");
    
    // 配置可能抛出验证异常
    MobileExtraConfig mobileConfig = new MobileExtraConfig();
    mobileConfig.setUninstallBlacklist(Arrays.asList("")); // 无效配置
    
    ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
    extraConfigs.validate();  // 会抛出 IllegalArgumentException
    
} catch (IllegalArgumentException e) {
    System.err.println("Invalid configuration: " + e.getMessage());
}
```

## 参考文档

- [ExtraConfigs API](ExtraConfigs.md)
- [MobileExtraConfig API](MobileExtraConfig.md)
- [AgentBay.create() API](common-features/basics/agentbay.md)
- [会话管理指南](../../../docs/guides/common-features/basics/session-management.md)

## 版本历史

- **v1.0.0**: 初始版本，包含基础参数
- **v1.1.0**: 新增 `policyId`, `enableBrowserReplay`, `extraConfigs` 参数

