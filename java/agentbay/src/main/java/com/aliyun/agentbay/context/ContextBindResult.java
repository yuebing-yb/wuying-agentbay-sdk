package com.aliyun.agentbay.context;

import com.aliyun.agentbay.model.ApiResponse;

/**
 * Result of a bind() operation on contexts.
 */
public class ContextBindResult extends ApiResponse {
    private boolean success;
    private String errorMessage;

    public ContextBindResult(String requestId, boolean success) {
        this(requestId, success, null);
    }

    public ContextBindResult(String requestId, boolean success, String errorMessage) {
        super(requestId);
        this.success = success;
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}
