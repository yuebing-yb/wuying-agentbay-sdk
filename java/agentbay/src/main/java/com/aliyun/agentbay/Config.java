package com.aliyun.agentbay;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Configuration class for AgentBay SDK
 */
public class Config {
    private static final Logger logger = LoggerFactory.getLogger(Config.class);
    // Browser data path constant
    public static final String BROWSER_DATA_PATH = "/tmp/agentbay_browser";

    // Browser fingerprint persistent path constant
    public static final String BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

    // Default configuration values
    private static final String DEFAULT_ENDPOINT = "wuyingai.cn-shanghai.aliyuncs.com";
    private static final int DEFAULT_TIMEOUT_MS = 60000;

    private String regionId;
    private String endpoint;
    private int timeoutMs;

    public Config(String regionId, String endpoint, int timeoutMs) {
        this.regionId = regionId;
        this.endpoint = endpoint;
        this.timeoutMs = timeoutMs;
    }

    public Config(String regionId) {
        this.regionId = regionId;
        this.endpoint = DEFAULT_ENDPOINT;
        this.timeoutMs = DEFAULT_TIMEOUT_MS;
    }

    public Config() {
        this.regionId = loadRegionId();
        this.endpoint = loadEndpoint();
        this.timeoutMs = loadTimeoutMs();
    }

    private String loadRegionId() {
        String envValue = System.getenv("AGENTBAY_REGION_ID");
        return (envValue != null && !envValue.trim().isEmpty()) ? envValue : null;
    }

    private String loadEndpoint() {
        String envValue = System.getenv("AGENTBAY_ENDPOINT");
        return (envValue != null && !envValue.trim().isEmpty()) ? envValue : DEFAULT_ENDPOINT;
    }

    private int loadTimeoutMs() {
        String envValue = System.getenv("AGENTBAY_TIMEOUT_MS");
        if (envValue != null && !envValue.trim().isEmpty()) {
            try {
                return Integer.parseInt(envValue);
            } catch (NumberFormatException e) {
                logger.warn("Invalid AGENTBAY_TIMEOUT_MS value: {}, using default", envValue);
            }
        }
        return DEFAULT_TIMEOUT_MS;
    }

    public String getRegionId() {
        return regionId;
    }

    public void setRegionId(String regionId) {
        this.regionId = regionId;
    }

    public String getEndpoint() {
        return endpoint;
    }

    public void setEndpoint(String endpoint) {
        this.endpoint = endpoint;
    }

    public int getTimeoutMs() {
        return timeoutMs;
    }

    public void setTimeoutMs(int timeoutMs) {
        this.timeoutMs = timeoutMs;
    }
}