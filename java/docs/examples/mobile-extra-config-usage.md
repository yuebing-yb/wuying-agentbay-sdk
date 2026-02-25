# MobileExtraConfig 使用指南

## 概述

`MobileExtraConfig` 和 `ExtraConfigs` 提供了移动环境的高级配置能力，使您能够：
- 🔒 锁定设备分辨率
- 📱 控制应用启动权限（白名单/黑名单）
- 🎨 管理导航栏显示
- 🛡️ 保护关键应用不被卸载
- 🎭 模拟真实设备属性

## 快速开始

### 基础配置

```java
import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.session.CreateSessionParams;

// 1. 创建移动配置
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);       // 锁定分辨率
mobileConfig.setHideNavigationBar(true);    // 隐藏导航栏

// 2. 包装为 ExtraConfigs
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

// 3. 创建会话
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

AgentBay agentBay = new AgentBay(apiKey);
SessionResult result = agentBay.create(params);
Session session = result.getSession();
```

## 配置选项详解

### 1. 分辨率锁定 (lock_resolution)

防止应用或系统更改设备分辨率，确保测试一致性。

```java
MobileExtraConfig config = new MobileExtraConfig();
config.setLockResolution(true);  // 启用分辨率锁定
```

**使用场景**:
- UI 自动化测试需要固定分辨率
- 屏幕截图对比测试
- 布局验证测试

### 2. 应用白名单/黑名单 (app_manager_rule)

控制哪些应用可以或不可以启动。

#### 白名单模式

```java
import com.aliyun.agentbay.mobile.AppManagerRule;
import java.util.Arrays;

// 只允许特定应用启动
AppManagerRule whitelist = new AppManagerRule(
    "White",  // 白名单模式
    Arrays.asList(
        "com.android.settings",
        "com.android.chrome",
        "com.example.myapp"
    )
);

MobileExtraConfig config = new MobileExtraConfig();
config.setAppManagerRule(whitelist);
```

**效果**: 只有列表中的应用可以启动，其他应用会被阻止。

#### 黑名单模式

```java
// 阻止特定应用启动
AppManagerRule blacklist = new AppManagerRule(
    "Black",  // 黑名单模式
    Arrays.asList(
        "com.malicious.app",
        "com.unwanted.service"
    )
);

MobileExtraConfig config = new MobileExtraConfig();
config.setAppManagerRule(blacklist);
```

**效果**: 列表中的应用无法启动，其他应用正常运行。

### 3. 导航栏可见性 (hide_navigation_bar)

控制 Android 系统导航栏的显示。

```java
MobileExtraConfig config = new MobileExtraConfig();
config.setHideNavigationBar(true);   // 隐藏导航栏
config.setHideNavigationBar(false);  // 显示导航栏
```

**使用场景**:
- 沉浸式 UI 测试
- 全屏应用测试
- 屏幕截图不包含导航栏

### 4. 卸载保护黑名单 (uninstall_blacklist)

保护关键系统应用不被卸载。

```java
import java.util.Arrays;

MobileExtraConfig config = new MobileExtraConfig();
config.setUninstallBlacklist(Arrays.asList(
    "com.android.systemui",      // 系统UI
    "com.android.settings",      // 设置应用
    "com.google.android.gms"     // Google服务
));
```

**效果**: 列表中的应用无法被 `uninstall_app()` 卸载。

### 5. 设备模拟 (simulate_config) ⭐ 核心功能

模拟真实设备的硬件和软件属性。

```java
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;

// 创建设备模拟配置
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,                              // 启用模拟
    "/tmp/mobile_dev_info",            // 设备信息文件路径
    MobileSimulateMode.ALL,            // 模拟模式
    "device-context-id"                // 设备信息的 Context ID
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setSimulateConfig(simulateConfig);
```

**模拟模式**:
- `PROPERTIES_ONLY`: 仅模拟系统属性（型号、品牌等）
- `SENSORS_ONLY`: 仅模拟传感器数据
- `PACKAGES_ONLY`: 仅模拟已安装应用列表
- `SERVICES_ONLY`: 仅模拟系统服务
- `ALL`: 模拟所有上述内容

**完整示例**:

```java
import com.aliyun.agentbay.mobile.MobileSimulate;

// Step 1: 上传设备信息
MobileSimulate mobileSimulate = agentBay.getMobileSimulate();
mobileSimulate.setSimulateEnable(true);
mobileSimulate.setSimulateMode(MobileSimulateMode.ALL);

String deviceInfoJson = Files.readString(Paths.get("device_info.json"));
MobileSimulateUploadResult uploadResult = 
    mobileSimulate.uploadMobileInfo(deviceInfoJson);

String deviceContextId = uploadResult.getMobileSimulateContextId();

// Step 2: 创建会话时应用设备模拟
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,
    mobileSimulate.getMobileDevInfoPath(),
    MobileSimulateMode.ALL,
    deviceContextId
);

MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setSimulateConfig(simulateConfig);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
Session session = result.getSession();

// Step 3: 验证设备属性
CommandResult modelResult = session.getCommand().executeCommand("getprop ro.product.model");
System.out.println("Device model: " + modelResult.getOutput());
// 输出: 模拟设备的型号，如 "Xiaomi 13"
```

## 组合使用示例

### 示例 1: 移动测试环境完整配置

```java
// 应用黑名单
AppManagerRule blacklist = new AppManagerRule(
    "Black",
    Arrays.asList("com.malicious.app", "com.test.blocker")
);

// 设备模拟
MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
    true,
    "/tmp/xiaomi13_info",
    MobileSimulateMode.ALL,
    "xiaomi-13-ctx"
);

// 完整移动配置
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);
mobileConfig.setAppManagerRule(blacklist);
mobileConfig.setHideNavigationBar(true);
mobileConfig.setUninstallBlacklist(Arrays.asList(
    "com.android.systemui",
    "com.android.settings"
));
mobileConfig.setSimulateConfig(simulateConfig);

// 创建会话
ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
CreateSessionParams params = new CreateSessionParams();
params.setImageId("mobile_latest");
params.setExtraConfigs(extraConfigs);
params.setPolicyId("mobile-test-policy");

SessionResult result = agentBay.create(params);
```

### 示例 2: 浏览器环境性能优化配置

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("browser_latest");
params.setEnableBrowserReplay(false);  // 禁用录制提升性能
params.setPolicyId("performance-optimized");

Map<String, String> labels = new HashMap<>();
labels.put("optimization", "performance");
params.setLabels(labels);

SessionResult result = agentBay.create(params);
```

## 自动应用机制

配置会在会话创建时**自动应用**：

```java
CreateSessionParams params = new CreateSessionParams();
params.setExtraConfigs(extraConfigs);

SessionResult result = agentBay.create(params);
Session session = result.getSession();

// 在 AgentBay.create() 内部会自动调用:
// session.mobile.configure(extraConfigs.getMobile());
// 
// 您无需手动调用 configure()
```

## 常见问题

### Q1: 什么时候需要使用 ExtraConfigs?

**A**: 当您需要：
- 在移动环境中配置特殊设置
- 模拟特定设备型号
- 控制应用启动权限
- 锁定测试环境配置

### Q2: policy_id 和 extra_configs 有什么区别？

**A**: 
- `policy_id`: 应用**预定义的服务端策略**（权限、资源限制等）
- `extra_configs`: 应用**客户端定义的环境配置**（移动设置、设备模拟等）

两者可以同时使用。

### Q3: enable_browser_replay 默认值是什么？

**A**: 默认为 `true` (启用)。仅当显式设置为 `false` 时才会禁用录制。

### Q4: 如何获取设备信息文件？

**A**: 设备信息文件包含真实设备的属性。可以通过：
1. 使用真实设备导出
2. 使用 DumpSDK 工具生成
3. 联系支持团队获取示例文件

### Q5: 配置会立即生效吗？

**A**: 
- `lockResolution`, `appManagerRule`, `hideNavigationBar`, `uninstallBlacklist` 在会话创建后立即生效
- `simulateConfig` 需要等待后台 `wya apply` 命令执行完成（约 5-10 秒）

## 完整示例代码

完整可运行的示例请参考：
- [MobileExtraConfigExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileExtraConfigExample.java)
- [MobileSimulateExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSimulateExample.java)
- [SessionConfigurationExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionConfigurationExample.java)

## 测试用例

参考测试代码：
- [SessionConfigurationIntegration.java](../../agentbay/src/integration-test/java/com/aliyun/agentbay/test/SessionConfigurationIntegrationTest.java)

