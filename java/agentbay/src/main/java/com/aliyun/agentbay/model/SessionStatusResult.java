package com.aliyun.agentbay.model;

/**
 * Result class for session status operations.
 * Contains basic session status information (status only, no extra detail fields).
 */
public class SessionStatusResult {
    private String requestId;
    private int httpStatusCode;
    private String code;
    private boolean success;
    private String status;
    private String errorMessage;

    public SessionStatusResult() {
    }

    public SessionStatusResult(String requestId, int httpStatusCode, String code, boolean success, String status, String errorMessage) {
        this.requestId = requestId;
        this.httpStatusCode = httpStatusCode;
        this.code = code;
        this.success = success;
        this.status = status;
        this.errorMessage = errorMessage;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public int getHttpStatusCode() {
        return httpStatusCode;
    }

    public void setHttpStatusCode(int httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    @Override
    public String toString() {
        return "SessionStatusResult{" +
                "requestId='" + requestId + '\'' +
                ", httpStatusCode=" + httpStatusCode +
                ", code='" + code + '\'' +
                ", success=" + success +
                ", status='" + status + '\'' +
                ", errorMessage='" + errorMessage + '\'' +
                '}';
    }
}
