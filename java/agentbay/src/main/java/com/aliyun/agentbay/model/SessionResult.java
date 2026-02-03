package com.aliyun.agentbay.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.aliyun.agentbay.session.Session;

/**
 * Result of session operations
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class SessionResult extends ApiResponse {
    private boolean success;
    private String errorMessage;
    private Session session;
    @JsonProperty("sessionId")
    private String sessionId;

    @JsonProperty("requestId")
    private String requestId;

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
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

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Session getSession() {
        return session;
    }

    public void setSession(Session session) {
        this.session = session;
    }
}