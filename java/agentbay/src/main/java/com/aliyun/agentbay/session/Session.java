package com.aliyun.agentbay.session;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.agent.Agent;
import com.aliyun.agentbay.browser.Browser;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.computer.Computer;
import com.aliyun.agentbay.mobile.Mobile;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.filesystem.FileSystem;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionInfo;
import com.aliyun.agentbay.model.SessionInfoResult;
import com.aliyun.agentbay.model.SessionParams;
import com.aliyun.agentbay.model.SessionMetrics;
import com.aliyun.agentbay.model.SessionMetricsResult;
import com.aliyun.agentbay.oss.OSS;
import com.aliyun.agentbay.code.Code;
import com.aliyun.agentbay.command.Command;
import com.aliyun.agentbay.mcp.McpToolsResult;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

/**
 * Represents a session in the AgentBay cloud environment
 */
public class Session {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(Session.class);

    private final String sessionId;
    private final AgentBay agentBay;
    private final SessionParams params;
    private Agent agent;
    private FileSystem fileSystem;
    private OSS oss;
    private Code code;
    private Command command;
    private ContextManager contextManager;
    private Browser browser;
    private Computer computer;
    public Mobile mobile;
    private String fileTransferContextId;
    private String resourceUrl;
    private String token;
    private String linkUrl;
    private Boolean enableBrowserReplay;
    private String imageId;

    public Session(String sessionId, AgentBay agentBay, SessionParams params) {
        this.sessionId = sessionId;
        this.agentBay = agentBay;
        this.params = params;
        this.agent = new Agent(this);
        this.fileSystem = new FileSystem(this);
        this.oss = new OSS(this);
        this.code = new Code(this);
        this.command = new Command(this);
        this.contextManager = new ContextManager(this);
        this.browser = new Browser(this);
        this.computer = new Computer(this);
        this.mobile = new Mobile(this);
        this.imageId = "";
    }

    /**
     * Constructor compatible with Python SDK style (AgentBay, sessionId)
     */
    public Session(AgentBay agentBay, String sessionId) {
        this(sessionId, agentBay, new SessionParams());
    }

    /**
     * Get the session ID
     *
     * @return Session ID
     */
    public String getSessionId() {
        return sessionId;
    }

    /**
     * Get the AgentBay client
     *
     * @return AgentBay instance
     */
    public AgentBay getAgentBay() {
        return agentBay;
    }

    /**
     * Get session parameters
     *
     * @return SessionParams
     */
    public SessionParams getParams() {
        return params;
    }

    /**
     * Get the agent for this session
     *
     * @return Agent instance
     */
    public Agent getAgent() {
        return agent;
    }

    /**
     * Get the file system for this session
     *
     * @return FileSystem instance
     */
    public FileSystem getFileSystem() {
        return fileSystem;
    }

    public FileSystem fs() {
        return fileSystem;
    }

    public FileSystem getFilesystem() {
        return fileSystem;
    }

    public FileSystem getFiles() {
        return fileSystem;
    }

    /**
     * Call an MCP tool
     *
     * @param toolName Tool name
     * @param args Tool arguments
     * @return CallMcpToolResponse
     * @throws AgentBayException if the call fails
     */
    public CallMcpToolResponse callTool(String toolName, Object args) throws AgentBayException {
        return callTool(toolName, args, null);
    }

    public CallMcpToolResponse callTool(String toolName, Object args, String serverName) throws AgentBayException {
        return agentBay.getApiClient().callMcpTool(sessionId, toolName, args, serverName);
    }

    /**
     * List available tools
     *
     * @return List of available tools
     * @throws AgentBayException if the call fails
     */
    public List<Object> listTools() throws AgentBayException {
        String img = imageId;
        if (img == null || img.isEmpty()) {
            img = "linux_latest";
        }
        ListMcpToolsResponse response = agentBay.getApiClient().listMcpTools(img);

        if (response != null && response.getBody() != null && response.getBody().getData() != null) {
            try {
                String dataJson = response.getBody().getData().toString();
                List<Object> toolsList = objectMapper.readValue(dataJson, List.class);
                return toolsList;
            } catch (Exception e) {
                throw new AgentBayException("Failed to parse tools data", e);
            }
        }
        return new java.util.ArrayList<>();
    }

    /**
     * Get runtime metrics for this session via the MCP get_metrics tool.
     *
     * The underlying MCP tool returns a JSON string. This method parses it and returns structured metrics.
     *
     * @return SessionMetricsResult containing structured metrics data
     */
    public SessionMetricsResult getMetrics() {
        try {
            CallMcpToolResponse toolResponse = callTool("get_metrics", new java.util.HashMap<>(), "wuying_system");

            if (toolResponse == null || toolResponse.getBody() == null) {
                return new SessionMetricsResult("", false, null, "No response from get_metrics tool");
            }

            String requestId = ResponseUtil.extractRequestId(toolResponse);
            Boolean success = toolResponse.getBody().getSuccess();

            if (success == null || !success) {
                String errorMessage = toolResponse.getBody().getMessage();
                return new SessionMetricsResult(requestId, false, null,
                    errorMessage != null ? errorMessage : "get_metrics tool failed");
            }

            Object data = toolResponse.getBody().getData();
            if (data == null) {
                return new SessionMetricsResult(requestId, false, null, "No data in get_metrics response");
            }

            String jsonData;
            if (data instanceof String) {
                jsonData = (String) data;
            } else {
                jsonData = objectMapper.writeValueAsString(data);
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> dataMap = objectMapper.readValue(jsonData, Map.class);

            Boolean isError = (Boolean) dataMap.get("isError");
            if (isError != null && isError) {
                String errorMessage = "Tool returned error";
                Object content = dataMap.get("content");
                if (content instanceof java.util.List && !((java.util.List<?>) content).isEmpty()) {
                    Object firstContent = ((java.util.List<?>) content).get(0);
                    if (firstContent instanceof Map) {
                        Object text = ((Map<?, ?>) firstContent).get("text");
                        if (text != null) {
                            errorMessage = text.toString();
                        }
                    }
                }
                return new SessionMetricsResult(requestId, false, null, errorMessage);
            }

            Object content = dataMap.get("content");
            if (content == null || !(content instanceof java.util.List) || ((java.util.List<?>) content).isEmpty()) {
                return new SessionMetricsResult(requestId, false, null, "No content in get_metrics response");
            }

            Object firstContent = ((java.util.List<?>) content).get(0);
            if (!(firstContent instanceof Map)) {
                return new SessionMetricsResult(requestId, false, null, "Invalid content format in get_metrics response");
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> contentMap = (Map<String, Object>) firstContent;
            Object textObj = contentMap.get("text");
            if (textObj == null) {
                return new SessionMetricsResult(requestId, false, null, "No text in content");
            }

            String metricsJson = textObj.toString();
            @SuppressWarnings("unchecked")
            Map<String, Object> raw = objectMapper.readValue(metricsJson, Map.class);

            SessionMetrics metrics = new SessionMetrics();
            metrics.setCpuCount(getIntValue(raw, "cpu_count"));
            metrics.setCpuUsedPct(getDoubleValue(raw, "cpu_used_pct"));
            metrics.setDiskTotal(getLongValue(raw, "disk_total"));
            metrics.setDiskUsed(getLongValue(raw, "disk_used"));
            metrics.setMemTotal(getLongValue(raw, "mem_total"));
            metrics.setMemUsed(getLongValue(raw, "mem_used"));
            metrics.setRxRateKBps(getDoubleValue(raw, "rx_rate_kbyte_per_s"));
            metrics.setTxRateKBps(getDoubleValue(raw, "tx_rate_kbyte_per_s"));
            metrics.setRxUsedKB(getDoubleValue(raw, "rx_used_kbyte"));
            metrics.setTxUsedKB(getDoubleValue(raw, "tx_used_kbyte"));
            metrics.setTimestamp(getStringValue(raw, "timestamp"));

            return new SessionMetricsResult(requestId, true, metrics, "", raw);

        } catch (Exception e) {
            return new SessionMetricsResult("", false, null,
                "Failed to get metrics: " + e.getMessage());
        }
    }

    private int getIntValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0;
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private long getLongValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0L;
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(value.toString());
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    private double getDoubleValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0.0;
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(value.toString());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    private String getStringValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value != null ? value.toString() : "";
    }

    /**
     * Gets information about this session
     *
     * @return SessionInfoResult containing SessionInfo and request ID
     * @throws AgentBayException if the operation fails
     */
    public SessionInfoResult info() throws AgentBayException {
        try {
            GetMcpResourceRequest request = new GetMcpResourceRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);
            GetMcpResourceResponse response = agentBay.getApiClient().getClient().getMcpResource(request);

            String requestId = ResponseUtil.extractRequestId(response);

            if (response.getBody() != null && response.getBody().getData() != null) {
                // Extract session info from response data
                GetMcpResourceResponseBody.GetMcpResourceResponseBodyData data = response.getBody().getData();

                SessionInfo sessionInfo = new SessionInfo();

                // Set session ID
                if (data.getSessionId() != null) {
                    sessionInfo.setSessionId(data.getSessionId());
                }

                // Set resource URL
                if (data.getResourceUrl() != null) {
                    sessionInfo.setResourceUrl(data.getResourceUrl());
                }

                // Transfer DesktopInfo fields to SessionInfo
                if (data.getDesktopInfo() != null) {
                    GetMcpResourceResponseBody.GetMcpResourceResponseBodyDataDesktopInfo desktopInfo = data.getDesktopInfo();

                    if (desktopInfo.getAppId() != null) {
                        sessionInfo.setAppId(desktopInfo.getAppId());
                    }
                    if (desktopInfo.getAuthCode() != null) {
                        sessionInfo.setAuthCode(desktopInfo.getAuthCode());
                    }
                    if (desktopInfo.getConnectionProperties() != null) {
                        sessionInfo.setConnectionProperties(desktopInfo.getConnectionProperties());
                    }
                    if (desktopInfo.getResourceId() != null) {
                        sessionInfo.setResourceId(desktopInfo.getResourceId());
                    }
                    if (desktopInfo.getResourceType() != null) {
                        sessionInfo.setResourceType(desktopInfo.getResourceType());
                    }
                    if (desktopInfo.getTicket() != null) {
                        sessionInfo.setTicket(desktopInfo.getTicket());
                    }
                }

                return new SessionInfoResult(requestId, true, sessionInfo, "");
            } else {
                return new SessionInfoResult(requestId, false, null, "No session data found");
            }

        } catch (Exception e) {
            throw new AgentBayException("Failed to get session info for session " + sessionId + ": " + e.getMessage(), e);
        }
    }

    /**
     * Get the OSS service for this session
     *
     * @return OSS instance
     */
    public OSS getOss() {
        return oss;
    }

    /**
     * Get the Code service for this session
     *
     * @return Code instance
     */
    public Code getCode() {
        return code;
    }

    /**
     * Get the Command service for this session
     *
     * @return Command instance
     */
    public Command getCommand() {
        return command;
    }

    /**
     * Get the context manager for this session
     *
     * @return ContextManager instance
     */
    public ContextManager getContext() {
        return contextManager;
    }

    /**
     * Get the browser service for this session
     *
     * @return Browser instance
     */
    public Browser getBrowser() {
        return browser;
    }

    /**
     * Get the computer service for this session
     *
     * @return Computer instance
     */
    public Computer getComputer() {
        return computer;
    }


    /**
     * Get the file transfer context ID for this session
     *
     * @return File transfer context ID
     */
    public String getFileTransferContextId() {
        return fileTransferContextId;
    }

    /**
     * Set the file transfer context ID for this session
     *
     * @param fileTransferContextId File transfer context ID
     */
    public void setFileTransferContextId(String fileTransferContextId) {
        this.fileTransferContextId = fileTransferContextId;
    }

    /**
     * Initialize browser instance with the given options
     * This calls the AgentBay cloud service to create a browser instance
     */
    public OperationResult initializeBrowser(BrowserOption option) throws AgentBayException {
        try {
            InitBrowserRequest request = new InitBrowserRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);
            request.setPersistentPath("/tmp/browser_data");  // Default path
            try {
                com.fasterxml.jackson.databind.ObjectMapper objectMapper = new com.fasterxml.jackson.databind.ObjectMapper();
                request.setBrowserOption(objectMapper.writeValueAsString(option.toMap()));
            } catch (Exception e) {
                throw new AgentBayException("Failed to serialize browser option: " + e.getMessage());
            }

            InitBrowserResponse response = agentBay.getClient().initBrowser(request);

            if (response == null || response.getBody() == null) {
                return new OperationResult("", false, "", "Invalid response from init browser API");
            }

            InitBrowserResponseBody.InitBrowserResponseBodyData data = response.getBody().getData();
            if (data != null && data.getPort() != null) {
                return new OperationResult(
                    ResponseUtil.extractRequestId(response),
                    true,
                    "Browser initialized",
                    ""
                );
            } else {
                return new OperationResult("", false, "", "Failed to get browser port from response");
            }
        } catch (Exception e) {
            return new OperationResult("", false, "", "Failed to initialize browser: " + e.getMessage());
        }
    }

    /**
     * Get the API key for this session
     *
     * @return API key
     */
    public String getApiKey() {
        return agentBay.getApiKey();
    }

    /**
     * List MCP tools for this session
     *
     * @return McpToolsResult
     */
    public McpToolsResult listMcpTools() {
        try {
            List<Object> toolsData = listTools();
            McpToolsResult result = new McpToolsResult();
            result.setSuccess(true);

            java.util.List<com.aliyun.agentbay.mcp.McpTool> tools = new java.util.ArrayList<>();
            if (toolsData != null) {
                for (Object toolData : toolsData) {
                    try {
                        if (toolData instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = (Map<String, Object>) toolData;

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        } else if (toolData instanceof String) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = objectMapper.readValue((String) toolData, Map.class);

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        }
                    } catch (Exception e) {
                    }
                }
            }

            result.setTools(tools);
            return result;
        } catch (AgentBayException e) {
            McpToolsResult result = new McpToolsResult();
            result.setSuccess(false);
            result.setErrorMessage(e.getMessage());
            return result;
        }
    }

    /**
     * Set image ID for this session (placeholder method)
     */
    public void setImageId(String imageId) {
        this.imageId = imageId;
    }

    public String getImageId() {
        return imageId;
    }

    /**
     * Get enableBrowserReplay flag
     */
    public Boolean getEnableBrowserReplay() {
        return enableBrowserReplay;
    }

    /**
     * Set enableBrowserReplay flag
     */
    public void setEnableBrowserReplay(Boolean enableBrowserReplay) {
        this.enableBrowserReplay = enableBrowserReplay;
    }

    /**
     * Get the resource URL for accessing the session
     *
     * @return Resource URL
     */
    public String getResourceUrl() {
        return resourceUrl;
    }

    /**
     * Set the resource URL for accessing the session
     *
     * @param resourceUrl Resource URL
     */
    public void setResourceUrl(String resourceUrl) {
        this.resourceUrl = resourceUrl;
    }

    /**
     * Get the token for LinkUrl tool calls.
     */
    public String getToken() {
        return token;
    }

    /**
     * Set the token for LinkUrl tool calls.
     */
    public void setToken(String token) {
        this.token = token;
    }

    /**
     * Get the LinkUrl for direct tool calls.
     */
    public String getLinkUrl() {
        return linkUrl;
    }

    /**
     * Set the LinkUrl for direct tool calls.
     */
    public void setLinkUrl(String linkUrl) {
        this.linkUrl = linkUrl;
    }

    /**
     * Helper method to parse inputSchema which can be a Map, String, or null
     *
     * @param inputSchemaObj The inputSchema object from the tool data
     * @return A Map representing the inputSchema, or an empty Map if parsing fails
     */
    private Map<String, Object> parseInputSchema(Object inputSchemaObj) {
        if (inputSchemaObj == null) {
            return new java.util.HashMap<>();
        }
        
        // If it's already a Map, return it
        if (inputSchemaObj instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> schemaMap = (Map<String, Object>) inputSchemaObj;
            return schemaMap;
        }
        
        // If it's a String, try to parse it as JSON
        if (inputSchemaObj instanceof String) {
            String schemaStr = (String) inputSchemaObj;
            if (schemaStr.isEmpty()) {
                return new java.util.HashMap<>();
            }
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> schemaMap = objectMapper.readValue(schemaStr, Map.class);
                return schemaMap;
            } catch (JsonProcessingException e) {
                logger.warn("Failed to parse inputSchema string as JSON: {}", schemaStr, e);
                return new java.util.HashMap<>();
            }
        }
        
        // For any other type, return empty map
        logger.warn("Unexpected inputSchema type: {}", inputSchemaObj.getClass().getName());
        return new java.util.HashMap<>();
    }

    /**
     * Update MCP tools for this session
     *
     */
    public void updateMcpTools(String dataJson) {
        try {
            List<Object> toolsData = objectMapper.readValue(dataJson, List.class);

            java.util.List<com.aliyun.agentbay.mcp.McpTool> tools = new java.util.ArrayList<>();
            if (toolsData != null) {
                for (Object toolData : toolsData) {
                    try {
                        if (toolData instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = (Map<String, Object>) toolData;

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        } else if (toolData instanceof String) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = objectMapper.readValue((String) toolData, Map.class);

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        }
                    } catch (Exception e) {
                        logger.warn("Failed to parse tool data: {}", toolData, e);
                    }
                }
            }

        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Get a link associated with the current session
     *
     * @param protocolType The protocol type to use for the link (optional)
     * @param port The port to use for the link (optional)
     * @return OperationResult containing the link URL
     * @throws AgentBayException if the request fails
     */
    public OperationResult getLink(String protocolType, Integer port) throws AgentBayException {
        try {
            GetLinkRequest request = new GetLinkRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);
            if (protocolType != null) {
                request.setProtocolType(protocolType);
            }
            if (port != null) {
                request.setPort(port);
            }

            GetLinkResponse response = agentBay.getClient().getLink(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response != null && response.getBody() != null && response.getBody().getData() != null) {
                String url = response.getBody().getData().getUrl();
                return new OperationResult(requestId, true, url, "");
            } else {
                return new OperationResult(requestId, false, "", "No URL in response");
            }
        } catch (Exception e) {
            throw new AgentBayException("Failed to get link: " + e.getMessage(), e);
        }
    }

    /**
     * Get a link associated with the current session with default parameters
     *
     * @return OperationResult containing the link URL
     * @throws AgentBayException if the request fails
     */
    public OperationResult getLink() throws AgentBayException {
        return getLink(null, null);
    }

    /**
     * Dump session state to a JSON string for persistence
     *
     * @return JSON string containing session state
     * @throws AgentBayException if serialization fails
     */
    public String dumpState() throws AgentBayException {
        try {
            SessionState state = new SessionState();
            state.setSessionId(this.sessionId);
            state.setFileTransferContextId(this.fileTransferContextId);
            return objectMapper.writeValueAsString(state);
        } catch (Exception e) {
            throw new AgentBayException("Failed to dump session state: " + e.getMessage(), e);
        }
    }

    /**
     * Restore session from a JSON state string
     *
     * @param agentBay AgentBay client instance
     * @param stateJson JSON string containing session state
     * @return Restored Session object
     * @throws AgentBayException if deserialization or restoration fails
     */
    public static Session restoreState(AgentBay agentBay, String stateJson) throws AgentBayException {
        try {
            SessionState state = objectMapper.readValue(stateJson, SessionState.class);

            Session session = new Session(state.getSessionId(), agentBay, new SessionParams());

            session.setFileTransferContextId(state.getFileTransferContextId());
            return session;
        } catch (Exception e) {
            throw new AgentBayException("Failed to restore session state: " + e.getMessage(), e);
        }
    }

    /**
     * Delete this session
     *
     * @return DeleteResult
     */
    public com.aliyun.agentbay.model.DeleteResult delete() {
        return delete(false);
    }

    /**
     * Delete this session with optional sync context
     *
     * @param syncContext Whether to sync context before deletion
     * @return DeleteResult
     */
    public com.aliyun.agentbay.model.DeleteResult delete(boolean syncContext) {
        try {
            // If sync_context is True, trigger file uploads first
            if (syncContext) {
                // Trigger file upload
                try {
                    ContextSyncResult syncResult = contextManager.sync();
                    if (!syncResult.isSuccess()) {
                    }
                } catch (Exception e) {
                    // Continue with deletion even if sync fails
                }

                // Wait for uploads to complete
                int maxRetries = 150; // Maximum number of retries
                int retryInterval = 2000; // 2 seconds in milliseconds

                for (int retry = 0; retry < maxRetries; retry++) {
                    try {
                        // Get context status data
                        ContextInfoResult infoResult = contextManager.info();

                        // Check if all upload context items have status "Success" or "Failed"
                        boolean allCompleted = true;
                        boolean hasFailure = false;
                        boolean hasUploads = false;

                        for (ContextStatusData item : infoResult.getContextStatusData()) {
                            // We only care about upload tasks
                            if (!"upload".equals(item.getTaskType())) {
                                continue;
                            }

                            hasUploads = true;
                            if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                                allCompleted = false;
                                break;
                            }

                            if ("Failed".equals(item.getStatus())) {
                                hasFailure = true;
                            }
                        }

                        if (allCompleted || !hasUploads) {
                            if (hasFailure) {
                            } else if (hasUploads) {
                            } else {
                            }
                            break;
                        }
                        Thread.sleep(retryInterval);
                    } catch (Exception e) {
                        try {
                            Thread.sleep(retryInterval);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                }
            }

            // Proceed with session deletion
            ReleaseMcpSessionRequest request = new ReleaseMcpSessionRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            ReleaseMcpSessionResponse response = agentBay.getClient().releaseMcpSession(request);

            String requestId = ResponseUtil.extractRequestId(response);

            // Check if the response is successful
            boolean success = true;
            if (response != null && response.getBody() != null) {
                success = response.getBody().getSuccess() != null ? response.getBody().getSuccess() : true;
            }

            if (!success) {
                return new com.aliyun.agentbay.model.DeleteResult(
                    requestId, false, "Failed to delete session");
            }
            return new com.aliyun.agentbay.model.DeleteResult(requestId, true, "");

        } catch (Exception e) {
            return new com.aliyun.agentbay.model.DeleteResult(
                "", false, "Failed to delete session " + sessionId + ": " + e.getMessage());
        }
    }

    /**
     * Set labels for this session
     *
     * @param labels Map of label key-value pairs to set
     * @return OperationResult indicating success or failure
     * @throws AgentBayException if the API call fails
     */
    public OperationResult setLabels(Map<String, String> labels) throws AgentBayException {
        try {
            // Validate labels
            if (labels == null) {
                throw new IllegalArgumentException("Labels cannot be null");
            }

            // Validate label constraints
            if (labels.size() > 20) {
                throw new IllegalArgumentException("Maximum 20 labels allowed");
            }

            for (Map.Entry<String, String> entry : labels.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();

                if (key == null || key.trim().isEmpty()) {
                    throw new IllegalArgumentException("Label key cannot be null or empty");
                }
                if (key.length() > 128) {
                    throw new IllegalArgumentException("Label key cannot exceed 128 characters: " + key);
                }
                if (value != null && value.length() > 256) {
                    throw new IllegalArgumentException("Label value cannot exceed 256 characters for key: " + key);
                }
            }

            // Convert labels to JSON string
            String labelsJson = objectMapper.writeValueAsString(labels);

            // Create request
            SetLabelRequest request = new SetLabelRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);
            request.setLabels(labelsJson);

            // Call API
            SetLabelResponse response = agentBay.getClient().setLabel(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);
            return new OperationResult(requestId, true, labelsJson, "");

        } catch (IllegalArgumentException e) {
            throw new AgentBayException("Invalid labels: " + e.getMessage(), e);
        } catch (Exception e) {
            throw new AgentBayException("Failed to set labels: " + e.getMessage(), e);
        }
    }

    /**
     * Get labels for this session
     *
     * @return OperationResult containing the labels map in the data field
     * @throws AgentBayException if the API call fails
     */
    public OperationResult getLabels() throws AgentBayException {
        try {
            // Create request
            GetLabelRequest request = new GetLabelRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);

            // Call API
            GetLabelResponse response = agentBay.getClient().getLabel(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);

            // Extract labels from response
            Map<String, Object> responseMap = response.toMap();
            Map<String, Object> body = (Map<String, Object>) responseMap.get("body");
            Map<String, Object> data = body != null ? (Map<String, Object>) body.get("Data") : null;
            String labelsJson = data != null ? (String) data.get("Labels") : null;

            Map<String, String> labels = new java.util.HashMap<>();
            if (labelsJson != null && !labelsJson.isEmpty()) {
                labels = objectMapper.readValue(labelsJson,
                    objectMapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
            }

            String labelsJsonResult = objectMapper.writeValueAsString(labels);
            return new OperationResult(requestId, true, labelsJsonResult, "");

        } catch (Exception e) {
            throw new AgentBayException("Failed to get labels: " + e.getMessage(), e);
        }
    }

    @Override
    public String toString() {
        return "Session{" +
                "sessionId='" + sessionId + '\'' +
                ", params=" + params +
                '}';
    }
}