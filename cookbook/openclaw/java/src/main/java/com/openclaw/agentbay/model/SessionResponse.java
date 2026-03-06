package com.openclaw.agentbay.model;

/**
 * 会话响应
 */
public class SessionResponse {
    private String sessionId;
    private String resourceUrl;
    private String openclawUrl;
    private String username;
    private String createdAt;
    private String status;

    public SessionResponse() {}

    public SessionResponse(String sessionId, String resourceUrl, String openclawUrl,
                           String username, String createdAt, String status) {
        this.sessionId = sessionId;
        this.resourceUrl = resourceUrl;
        this.openclawUrl = openclawUrl;
        this.username = username;
        this.createdAt = createdAt;
        this.status = status;
    }

    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }

    public String getResourceUrl() { return resourceUrl; }
    public void setResourceUrl(String resourceUrl) { this.resourceUrl = resourceUrl; }

    public String getOpenclawUrl() { return openclawUrl; }
    public void setOpenclawUrl(String openclawUrl) { this.openclawUrl = openclawUrl; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
}
