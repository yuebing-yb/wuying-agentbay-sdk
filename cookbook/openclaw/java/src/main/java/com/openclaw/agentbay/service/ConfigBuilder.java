package com.openclaw.agentbay.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import org.springframework.stereotype.Component;

import java.util.*;

/**
 * OpenClaw 配置文件生成器
 *
 * 根据用户输入的参数，基于默认模板动态生成 openclaw.json 配置。
 * 不硬编码任何 API Key，全部由前端传入。
 */
@Component
public class ConfigBuilder {

    private static final ObjectMapper MAPPER = new ObjectMapper()
            .enable(SerializationFeature.INDENT_OUTPUT);

    /**
     * 生成 openclaw.json 配置内容
     *
     * @param bailianApiKey      百炼 API Key
     * @param dingtalkClientId   钉钉 Client ID (可为 null)
     * @param dingtalkClientSecret 钉钉 Client Secret (可为 null)
     * @param feishuAppId        飞书 App ID (可为 null)
     * @param feishuAppSecret    飞书 App Secret (可为 null)
     * @return 配置文件 JSON 字符串
     */
    public String build(String bailianApiKey,
                        String dingtalkClientId,
                        String dingtalkClientSecret,
                        String feishuAppId,
                        String feishuAppSecret,
                        String modelBaseUrl,
                        String modelId) {
        try {
            Map<String, Object> config = new LinkedHashMap<>();

            // meta
            config.put("meta", Map.of(
                    "lastTouchedVersion", "2026.3.2",
                    "lastTouchedAt", "2026-03-03T09:42:12.612Z"
            ));

            // wizard
            config.put("wizard", Map.of(
                    "lastRunAt", "2026-03-03T09:42:12.553Z",
                    "lastRunVersion", "2026.3.2",
                    "lastRunCommand", "configure",
                    "lastRunMode", "local"
            ));

            // models - 支持自定义 baseUrl 和 modelId
            String actualBaseUrl = isNotBlank(modelBaseUrl) ? modelBaseUrl
                    : "https://dashscope.aliyuncs.com/compatible-mode/v1";
            String actualModelId = isNotBlank(modelId) ? modelId : "qwen3-max-2026-01-23";

            Map<String, Object> modelCost = new LinkedHashMap<>();
            modelCost.put("input", 0.0025);
            modelCost.put("output", 0.01);
            modelCost.put("cacheRead", 0);
            modelCost.put("cacheWrite", 0);

            Map<String, Object> modelDef = new LinkedHashMap<>();
            modelDef.put("id", actualModelId);
            modelDef.put("name", actualModelId);
            modelDef.put("reasoning", false);
            modelDef.put("input", List.of("text"));
            modelDef.put("cost", modelCost);
            modelDef.put("contextWindow", 262144);
            modelDef.put("maxTokens", 65536);

            Map<String, Object> bailianProvider = new LinkedHashMap<>();
            bailianProvider.put("baseUrl", actualBaseUrl);
            bailianProvider.put("apiKey", bailianApiKey);
            bailianProvider.put("api", "openai-completions");
            bailianProvider.put("models", List.of(modelDef));

            config.put("models", Map.of(
                    "mode", "merge",
                    "providers", Map.of("bailian", bailianProvider)
            ));

            // agents
            Map<String, Object> agentDefaults = new LinkedHashMap<>();
            agentDefaults.put("workspace", "/home/wuying/.openclaw/workspace");
            agentDefaults.put("model", Map.of("primary", "bailian/" + actualModelId));
            agentDefaults.put("models", Map.of(
                    "bailian/" + actualModelId, Map.of("alias", actualModelId)
            ));
            agentDefaults.put("compaction", Map.of("mode", "safeguard"));
            agentDefaults.put("maxConcurrent", 4);
            agentDefaults.put("subagents", Map.of("maxConcurrent", 8));
            config.put("agents", Map.of("defaults", agentDefaults));

            // tools, messages, commands, session
            config.put("tools", Map.of("profile", "messaging"));
            config.put("messages", Map.of("ackReactionScope", "group-mentions"));

            Map<String, Object> commands = new LinkedHashMap<>();
            commands.put("native", "auto");
            commands.put("nativeSkills", "auto");
            commands.put("restart", true);
            commands.put("ownerDisplay", "raw");
            config.put("commands", commands);

            config.put("session", Map.of("dmScope", "per-channel-peer"));

            // channels - 根据前端是否传入凭证来决定是否启用
            Map<String, Object> channels = new LinkedHashMap<>();

            // 飞书
            Map<String, Object> feishu = new LinkedHashMap<>();
            boolean feishuEnabled = isNotBlank(feishuAppId) && isNotBlank(feishuAppSecret);
            feishu.put("enabled", feishuEnabled);
            feishu.put("appId", feishuEnabled ? feishuAppId : "feishu_app_id");
            feishu.put("appSecret", feishuEnabled ? feishuAppSecret : "feishu_app_secret");
            feishu.put("connectionMode", "websocket");
            feishu.put("domain", "feishu");
            feishu.put("groupPolicy", "open");
            channels.put("feishu", feishu);

            // 钉钉
            Map<String, Object> dingtalk = new LinkedHashMap<>();
            boolean dingtalkEnabled = isNotBlank(dingtalkClientId) && isNotBlank(dingtalkClientSecret);
            dingtalk.put("enabled", dingtalkEnabled);
            dingtalk.put("clientId", dingtalkEnabled ? dingtalkClientId : "dingxxxx");
            dingtalk.put("clientSecret", dingtalkEnabled ? dingtalkClientSecret : "xxx-xxx-xxx");
            dingtalk.put("dmPolicy", "open");
            dingtalk.put("groupPolicy", "open");
            dingtalk.put("messageType", "markdown");
            channels.put("dingtalk", dingtalk);

            config.put("channels", channels);

            // gateway - 开放策略，支持通过 getLink 访问
            Map<String, Object> gateway = new LinkedHashMap<>();
            gateway.put("port", 30100);
            gateway.put("mode", "local");
            gateway.put("bind", "lan");
            Map<String, Object> controlUi = new LinkedHashMap<>();
            controlUi.put("allowedOrigins", List.of("*"));
            controlUi.put("dangerouslyDisableDeviceAuth", true);
            gateway.put("controlUi", controlUi);
            gateway.put("auth", Map.of(
                    "mode", "token",
                    "token", "4decb1b9ff4997825eb91e37bf28798e0af1f7f00c6b4b1c"
            ));
            gateway.put("tailscale", Map.of("mode", "off", "resetOnExit", false));
            gateway.put("nodes", Map.of("denyCommands", List.of(
                    "camera.snap", "camera.clip", "screen.record",
                    "contacts.add", "calendar.add", "reminders.add", "sms.send"
            )));
            config.put("gateway", gateway);

            // plugins
            Map<String, Object> plugins = new LinkedHashMap<>();
            plugins.put("load", Map.of("paths", List.of("/opt/openclaw/openclaw-channel-dingtalk")));
            plugins.put("entries", Map.of("dingtalk", Map.of("enabled", true)));

            Map<String, Object> dingtalkInstall = new LinkedHashMap<>();
            dingtalkInstall.put("source", "path");
            dingtalkInstall.put("sourcePath", "/opt/openclaw/openclaw-channel-dingtalk");
            dingtalkInstall.put("installPath", "/opt/openclaw/openclaw-channel-dingtalk");
            dingtalkInstall.put("version", "3.1.4");
            dingtalkInstall.put("installedAt", "2026-03-03T09:18:01.176Z");
            plugins.put("installs", Map.of("dingtalk", dingtalkInstall));

            config.put("plugins", plugins);

            return MAPPER.writeValueAsString(config);
        } catch (Exception e) {
            throw new RuntimeException("生成配置文件失败", e);
        }
    }

    private boolean isNotBlank(String s) {
        return s != null && !s.trim().isEmpty();
    }
}
