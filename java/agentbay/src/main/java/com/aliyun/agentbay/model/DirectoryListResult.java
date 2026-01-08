package com.aliyun.agentbay.model;

import java.util.List;
import java.util.Map;

public class DirectoryListResult extends ApiResponse {
    private boolean success;
    private List<Map<String, Object>> entries;
    private String errorMessage;

    public DirectoryListResult() {
        this("", false, null, "");
    }

    public DirectoryListResult(String requestId, boolean success, List<Map<String, Object>> entries, String errorMessage) {
        super(requestId);
        this.success = success;
        this.entries = entries;
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public List<Map<String, Object>> getEntries() {
        return entries;
    }

    public void setEntries(List<Map<String, Object>> entries) {
        this.entries = entries;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
