package com.openclaw.agentbay.model;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.session.Session;

/**
 * 内部会话信息 (含 SDK 对象引用，用于后续操作和销毁)
 */
public class SessionInfo {
    private String sessionId;
    private String resourceUrl;
    private String openclawUrl;
    private String username;
    private String createdAt;
    private String status;
    /** AgentBay 客户端引用 */
    private transient AgentBay agentBay;
    /** Session 对象引用 */
    private transient Session session;

    public SessionInfo() {}

    public SessionInfo(String sessionId, String resourceUrl, String openclawUrl, String username,
                       String createdAt, String status, AgentBay agentBay, Session session) {
        this.sessionId = sessionId;
        this.resourceUrl = resourceUrl;
        this.openclawUrl = openclawUrl;
        this.username = username;
        this.createdAt = createdAt;
        this.status = status;
        this.agentBay = agentBay;
        this.session = session;
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

    public AgentBay getAgentBay() { return agentBay; }
    public void setAgentBay(AgentBay agentBay) { this.agentBay = agentBay; }

    public Session getSession() { return session; }
    public void setSession(Session session) { this.session = session; }
}
