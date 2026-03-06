package com.openclaw.agentbay.model;

/**
 * 创建会话请求 - 所有参数由前端传入
 */
public class CreateSessionRequest {
    /** AgentBay API Key (必填) */
    private String agentbayApiKey;
    /** 百炼 API Key (必填) */
    private String bailianApiKey;
    /** 用户名称 (必填) */
    private String username;
    /** 钉钉 Client ID (可选) */
    private String dingtalkClientId;
    /** 钉钉 Client Secret (可选) */
    private String dingtalkClientSecret;
    /** 飞书 App ID (可选) */
    private String feishuAppId;
    /** 飞书 App Secret (可选) */
    private String feishuAppSecret;
    /** 模型 Base URL (可选，默认百炼) */
    private String modelBaseUrl;
    /** 模型 ID (可选，默认 qwen3-max) */
    private String modelId;

    public CreateSessionRequest() {}

    public String getAgentbayApiKey() { return agentbayApiKey; }
    public void setAgentbayApiKey(String agentbayApiKey) { this.agentbayApiKey = agentbayApiKey; }

    public String getBailianApiKey() { return bailianApiKey; }
    public void setBailianApiKey(String bailianApiKey) { this.bailianApiKey = bailianApiKey; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getDingtalkClientId() { return dingtalkClientId; }
    public void setDingtalkClientId(String dingtalkClientId) { this.dingtalkClientId = dingtalkClientId; }

    public String getDingtalkClientSecret() { return dingtalkClientSecret; }
    public void setDingtalkClientSecret(String dingtalkClientSecret) { this.dingtalkClientSecret = dingtalkClientSecret; }

    public String getFeishuAppId() { return feishuAppId; }
    public void setFeishuAppId(String feishuAppId) { this.feishuAppId = feishuAppId; }

    public String getFeishuAppSecret() { return feishuAppSecret; }
    public void setFeishuAppSecret(String feishuAppSecret) { this.feishuAppSecret = feishuAppSecret; }

    public String getModelBaseUrl() { return modelBaseUrl; }
    public void setModelBaseUrl(String modelBaseUrl) { this.modelBaseUrl = modelBaseUrl; }

    public String getModelId() { return modelId; }
    public void setModelId(String modelId) { this.modelId = modelId; }
}
