package com.aliyun.agentbay.model;

/**
 * Result of session resume operation (beta feature).
 */
public class SessionResumeResult extends ApiResponse {
    private boolean success;
    private String errorMessage;
    private String status;

    public SessionResumeResult() {
        this("", false, "", "");
    }

    public SessionResumeResult(String requestId, boolean success, String errorMessage) {
        this(requestId, success, errorMessage, "");
    }

    public SessionResumeResult(String requestId, boolean success, String errorMessage, String status) {
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
