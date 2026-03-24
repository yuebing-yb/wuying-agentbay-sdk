package com.aliyun.agentbay.browser;

import java.util.HashMap;
import java.util.Map;

/**
 * Options for browser act operations - matches Python ActOptions
 */
public class ActOptions {
    private String action;
    /** Timeout in seconds for the act operation. */
    private Integer timeout;
    private Map<String, String> variables;
    private Boolean useVision;

    public ActOptions(String action) {
        this.action = action;
    }

    public ActOptions(String action, Integer timeout, Map<String, String> variables, Boolean useVision) {
        this.action = action;
        this.timeout = timeout;
        this.variables = variables;
        this.useVision = useVision;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("action", action);
        if (timeout != null) map.put("timeout", timeout);
        if (variables != null) map.put("variables", variables);
        if (useVision != null) map.put("use_vision", useVision);
        return map;
    }

    // Getters and setters
    public String getAction() { return action; }
    public void setAction(String action) { this.action = action; }

    public Integer getTimeout() { return timeout; }
    public void setTimeout(Integer timeout) { this.timeout = timeout; }

    public Map<String, String> getVariables() { return variables; }
    public void setVariables(Map<String, String> variables) { this.variables = variables; }

    public Boolean getUseVision() { return useVision; }
    public void setUseVision(Boolean useVision) { this.useVision = useVision; }
}