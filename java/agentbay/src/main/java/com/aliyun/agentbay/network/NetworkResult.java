package com.aliyun.agentbay.network;

public class NetworkResult {
    private String requestId;
    private boolean success;
    private String networkId;
    private String networkToken;
    private String errorMessage;

    public NetworkResult(String requestId, boolean success, String networkId, String networkToken, String errorMessage) {
        this.requestId = requestId;
        this.success = success;
        this.networkId = networkId;
        this.networkToken = networkToken;
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

    public String getNetworkId() {
        return networkId;
    }

    public void setNetworkId(String networkId) {
        this.networkId = networkId;
    }

    public String getNetworkToken() {
        return networkToken;
    }

    public void setNetworkToken(String networkToken) {
        this.networkToken = networkToken;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    @Override
    public String toString() {
        return "NetworkResult{" +
            "requestId='" + requestId + '\'' +
            ", success=" + success +
            ", networkId='" + networkId + '\'' +
            ", networkToken='" + networkToken + '\'' +
            ", errorMessage='" + errorMessage + '\'' +
            '}';
    }
}
