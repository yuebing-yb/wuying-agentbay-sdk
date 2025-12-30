package com.aliyun.agentbay.model;

import java.util.Map;

public class SessionMetricsResult {
    private String requestId;
    private boolean success;
    private SessionMetrics metrics;
    private String errorMessage;
    private Map<String, Object> raw;

    public SessionMetricsResult() {
    }

    public SessionMetricsResult(String requestId, boolean success, SessionMetrics metrics, String errorMessage) {
        this.requestId = requestId;
        this.success = success;
        this.metrics = metrics;
        this.errorMessage = errorMessage;
    }

    public SessionMetricsResult(String requestId, boolean success, SessionMetrics metrics, String errorMessage, Map<String, Object> raw) {
        this.requestId = requestId;
        this.success = success;
        this.metrics = metrics;
        this.errorMessage = errorMessage;
        this.raw = raw;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public SessionMetrics getMetrics() {
        return metrics;
    }

    public void setMetrics(SessionMetrics metrics) {
        this.metrics = metrics;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Map<String, Object> getRaw() {
        return raw;
    }

    public void setRaw(Map<String, Object> raw) {
        this.raw = raw;
    }
}
