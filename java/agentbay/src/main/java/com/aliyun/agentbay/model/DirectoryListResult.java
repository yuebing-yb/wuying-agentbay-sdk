package com.aliyun.agentbay.model;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class DirectoryListResult extends ApiResponse {
    private boolean success;
    private List<Map<String, Object>> _entries;
    private String errorMessage;

    public DirectoryListResult() {
        this("", false, null, "");
    }

    public DirectoryListResult(String requestId, boolean success, List<Map<String, Object>> entries, String errorMessage) {
        super(requestId);
        this.success = success;
        this._entries = entries;
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public List<DirectoryEntry> getEntries() {
        if (_entries == null) {
            return Collections.emptyList();
        }
        return _entries.stream()
                .map(DirectoryEntry::new)
                .collect(Collectors.toList());
    }

    public void setEntries(List<Map<String, Object>> entries) {
        this._entries = entries;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
