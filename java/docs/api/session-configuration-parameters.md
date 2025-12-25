# 会话配置参数完整指南

本文档汇总了 `CreateSessionParams` 中新增的配置参数，包括 `policy_id`、`enable_browser_replay` 和 `extra_configs`。

## 参数概览

| 参数名 | 类型 | 默认值 | 版本 | 用途 |
|--------|------|--------|------|------|
| `policyId` | String | null | v1.1.0+ | 应用预定义策略 |
| `enableBrowserReplay` | Boolean | null (true) | v1.1.0+ | 控制浏览器录制 |
| `extraConfigs` | ExtraConfigs | null | v1.1.0+ | 高级环境配置 |

## 快速参考

### policy_id

```java
params.setPolicyId("my-policy-id");
```

**用途**: 应用服务端预定义的策略，控制权限和资源限制。

### enable_browser_replay

```java
params.setEnableBrowserReplay(false);  // 禁用录制
```

**用途**: 控制是否启用浏览器操作录制功能。
**注意**: 默认为 `true`，仅在需要禁用时设置为 `false`。

### extra_configs

```java
MobileExtraConfig mobileConfig = new MobileExtraConfig();
mobileConfig.setLockResolution(true);

ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
params.setExtraConfigs(extraConfigs);
```

**用途**: 提供移动环境的高级配置选项。

## 详细文档

- [ExtraConfigs API 文档](ExtraConfigs.md)
- [MobileExtraConfig API 文档](MobileExtraConfig.md)
- [CreateSessionParams API 文档](CreateSessionParams.md)
- [MobileExtraConfig 使用指南](../examples/mobile-extra-config-usage.md)

## 代码示例

- [MobileExtraConfigExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileExtraConfigExample.java)
- [MobileSimulateExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/MobileSimulateExample.java)
- [SessionConfigurationExample.java](../../agentbay/src/main/java/com/aliyun/agentbay/examples/SessionConfigurationExample.java)

## 测试用例

- [ExtraConfigsTest.java](../../agentbay/src/test/java/com/aliyun/agentbay/test/ExtraConfigsTest.java)
- [CreateSessionParamsTest.java](../../agentbay/src/test/java/com/aliyun/agentbay/test/CreateSessionParamsTest.java)
- [TestSessionConfigurationIntegration.java](../../agentbay/src/test/java/com/aliyun/agentbay/test/TestSessionConfigurationIntegration.java)

