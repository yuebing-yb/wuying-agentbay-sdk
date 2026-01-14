package com.aliyun.agentbay.client;

import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.ApiException;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * API client wrapper for WuyingAI client
 */
public class ApiClient {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Client client;
    private final String apiKey;

    public ApiClient(Client client, String apiKey) {
        this.client = client;
        this.apiKey = apiKey;
    }

    /**
     * Call an MCP tool
     *
     * @param sessionId The session ID
     * @param toolName The tool name
     * @param args The tool arguments
     * @return CallMcpToolResponse
     * @throws AgentBayException if the call fails
     */
    public CallMcpToolResponse callMcpTool(String sessionId, String toolName, Object args) throws AgentBayException {
        try {
            CallMcpToolRequest request = new CallMcpToolRequest();
            request.authorization = "Bearer " + apiKey;
            request.sessionId = sessionId;

            // Use 'name' field like Python version, with plain tool name
            request.name = toolName;

            // Properly serialize arguments to JSON
            String argsJson;
            if (args == null) {
                argsJson = "{}";
            } else {
                try {
                    argsJson = objectMapper.writeValueAsString(args);
                } catch (Exception e) {
                    argsJson = args.toString();
                }
            }
            request.args = argsJson;

            CallMcpToolResponse response = client.callMcpTool(request);

            return response;
        } catch (Exception e) {
            throw new ApiException(String.format(
                    "Failed to call MCP tool '%s' for session '%s': %s",
                    toolName,
                    sessionId,
                    e.getMessage()
            ), e);
        }
    }

    /**
     * List available MCP tools
     *
     * @param imageId The image ID
     * @return ListMcpToolsResponse
     * @throws AgentBayException if the call fails
     */
    public ListMcpToolsResponse listMcpTools(String imageId) throws AgentBayException {
        try {
            ListMcpToolsRequest request = new ListMcpToolsRequest();
            request.authorization = "Bearer " + apiKey;
            if (imageId != null && !imageId.isEmpty()) {
                request.imageId = imageId;
            }

            ListMcpToolsResponse response = client.listMcpTools(request);

            return response;
        } catch (Exception e) {
            throw new ApiException("Failed to list MCP tools", e);
        }
    }

    /**
     * Get ADB connection link for mobile sessions
     *
     * @param sessionId The session ID
     * @param adbkeyPub The ADB public key
     * @return GetAdbLinkResponse
     * @throws AgentBayException if the call fails
     */
    public GetAdbLinkResponse getAdbLink(String sessionId, String adbkeyPub) throws AgentBayException {
        try {
            GetAdbLinkRequest request = new GetAdbLinkRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setSessionId(sessionId);
            
            // Build options JSON with adbkey_pub
            String optionsJson = String.format("{\"adbkey_pub\":\"%s\"}", adbkeyPub);
            request.setOption(optionsJson);

            GetAdbLinkResponse response = client.getAdbLink(request);

            return response;
        } catch (Exception e) {
            throw new ApiException(String.format(
                    "Failed to get ADB link for session '%s': %s",
                    sessionId,
                    e.getMessage()
            ), e);
        }
    }

    /**
     * Simple session deletion - stub implementation
     *
     * @param sessionId The session ID
     * @throws AgentBayException if the call fails
     */
    public void deleteSession(String sessionId) throws AgentBayException {
        // In a real implementation, this would call the appropriate API
    }

    /**
     * Get the underlying client
     *
     * @return Client instance
     */
    public Client getClient() {
        return client;
    }
}