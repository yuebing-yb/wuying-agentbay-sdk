package com.aliyun.agentbay.session;

import com.aliyun.agentbay.mcp.McpTool;

import java.util.List;

public class SessionState {
    private String sessionId;
    private String fileTransferContextId;
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

    public List<McpTool> getMcpTools() {
        return mcpTools;
    }

    public void setMcpTools(List<McpTool> mcpTools) {
        this.mcpTools = mcpTools;
    }
}
