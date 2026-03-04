package com.aliyun.agentbay.model;

/**
 * Result of session pause operation (beta feature).
 */
public class SessionPauseResult extends ApiResponse {
    private boolean success;
    private String errorMessage;
    private String status;

    public SessionPauseResult() {
        this("", false, "", "");
    }

    public SessionPauseResult(String requestId, boolean success, String errorMessage) {
        this(requestId, success, errorMessage, "");
    }

    public SessionPauseResult(String requestId, boolean success, String errorMessage, String status) {
        super(requestId);
        this.success = success;
        this.errorMessage = errorMessage;
        this.status = status;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
