package com.aliyun.agentbay.network;

public class NetworkStatusResult {
    private String requestId;
    private boolean success;
    private boolean online;
    private String errorMessage;

    public NetworkStatusResult(String requestId, boolean success, boolean online, String errorMessage) {
        this.requestId = requestId;
        this.success = success;
        this.online = online;
        this.errorMessage = errorMessage;
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

    public boolean isOnline() {
        return online;
    }

    public void setOnline(boolean online) {
        this.online = online;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    @Override
    public String toString() {
        return "NetworkStatusResult{" +
            "requestId='" + requestId + '\'' +
            ", success=" + success +
            ", online=" + online +
            ", errorMessage='" + errorMessage + '\'' +
            '}';
    }
}
