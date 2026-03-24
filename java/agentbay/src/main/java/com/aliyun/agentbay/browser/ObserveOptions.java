package com.aliyun.agentbay.browser;

import java.util.HashMap;
import java.util.Map;

/**
 * Options for browser observe operations - matches Python ObserveOptions
 */
public class ObserveOptions {
    private String instruction;
    private Boolean useVision;
    private String selector;
    /** Timeout in seconds for the observe operation. */
    private Integer timeout;

    public ObserveOptions(String instruction) {
        this.instruction = instruction;
    }

    public ObserveOptions(String instruction, Boolean useVision, String selector, Integer timeout) {
        this.instruction = instruction;
        this.useVision = useVision;
        this.selector = selector;
        this.timeout = timeout;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("instruction", instruction);
        if (useVision != null) map.put("use_vision", useVision);
        if (selector != null) map.put("selector", selector);
        if (timeout != null) map.put("timeout", timeout);
        return map;
    }

    // Getters and setters
    public String getInstruction() { return instruction; }
    public void setInstruction(String instruction) { this.instruction = instruction; }

    public Boolean getUseVision() { return useVision; }
    public void setUseVision(Boolean useVision) { this.useVision = useVision; }

    public String getSelector() { return selector; }
    public void setSelector(String selector) { this.selector = selector; }

    public Integer getTimeout() { return timeout; }
    public void setTimeout(Integer timeout) { this.timeout = timeout; }
}