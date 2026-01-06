package com.aliyun.agentbay.session;

import com.aliyun.agentbay.model.SessionParams;
import com.aliyun.agentbay.mcp.McpTool;

import java.util.List;

public class SessionState {
    private String sessionId;
    private String fileTransferContextId;
    private String httpPort;
    private String token;
    private String linkUrl;
    private long linkUrlTimestamp;
    private List<McpTool> mcpTools;

    public SessionState() {
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getFileTransferContextId() {
        return fileTransferContextId;
    }

    public void setFileTransferContextId(String fileTransferContextId) {
        this.fileTransferContextId = fileTransferContextId;
    }

    public String getHttpPort() {
        return httpPort;
    }

    public void setHttpPort(String httpPort) {
        this.httpPort = httpPort;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getLinkUrl() {
        return linkUrl;
    }

    public void setLinkUrl(String linkUrl) {
        this.linkUrl = linkUrl;
    }

    public long getLinkUrlTimestamp() {
        return linkUrlTimestamp;
    }

    public void setLinkUrlTimestamp(long linkUrlTimestamp) {
        this.linkUrlTimestamp = linkUrlTimestamp;
    }

    public List<McpTool> getMcpTools() {
        return mcpTools;
    }

    public void setMcpTools(List<McpTool> mcpTools) {
        this.mcpTools = mcpTools;
    }
}
