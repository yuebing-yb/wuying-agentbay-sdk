package com.aliyun.agentbay.service;

import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.Session;

/**
 * Base service class that provides common functionality for all service classes.
 * Similar to Python's BaseService, delegates MCP tool calls to Session.
 */
public class BaseService {
    protected final Session session;

    public BaseService(Session session) {
        this.session = session;
    }

    /**
     * Call an MCP tool and parse the response similar to Python's _call_mcp_tool method.
     * This method delegates to Session.callMcpTool() to unify routing logic (LinkUrl, VPC, API).
     *
     * @param toolName The name of the tool to call
     * @param args     The arguments to pass to the tool
     * @return OperationResult containing the parsed response
     */
    public OperationResult callMcpTool(String toolName, Object args) {
        try {
            // Delegate to Session's unified call_mcp_tool method which handles all routing
            // (LinkUrl, VPC, API) - this is similar to Python's implementation
            return session.callMcpTool(toolName, args);
        } catch (Exception e) {
            return new OperationResult("", false, "", "Unexpected error: " + e.getMessage());
        }
    }
}