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
import com.aliyun.agentbay.model.SessionMetrics;
import com.aliyun.agentbay.model.SessionMetricsResult;
import com.aliyun.agentbay.model.SessionStatusResult;
import com.aliyun.agentbay.oss.OSS;
import com.aliyun.agentbay.code.Code;
import com.aliyun.agentbay.command.Command;
import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.mcp.McpToolsResult;
import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

public class Session {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(Session.class);

    private final String sessionId;
    private final AgentBay agentBay;
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
    private String wsUrl;
    private WsClient wsClient;
    private Boolean enableBrowserReplay;
    private String imageId;
    private List<McpTool> mcpTools = new java.util.ArrayList<>();

    /**
     * Creates a new Session instance.
     * 
     * <p>Initializes all service instances (Agent, FileSystem, OSS, Code, Command, 
     * ContextManager, Browser, Computer, Mobile) for this session.</p>
     * 
     * @param agentBay The AgentBay client instance
     * @param sessionId The unique identifier for this session
     */
    public Session(AgentBay agentBay, String sessionId) {
        this.sessionId = sessionId;
        this.agentBay = agentBay;
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
        this.wsUrl = "";
    }

    public String getWsUrl() {
        return wsUrl;
    }

    public void setWsUrl(String wsUrl) {
        this.wsUrl = wsUrl;
    }

    /**
     * Internal: get or create a session-scoped WS client.
     * 
     * <p>This method is internal API by convention. The WS client is lazily initialized
     * and cached for the lifetime of this session. Callers are responsible for calling
     * connect() on the returned client if needed.</p>
     * 
     * @return The WsClient instance for this session
     * @throws RuntimeException if wsUrl or token is not available
     */
    public synchronized WsClient getWsClient() {
        if (this.wsUrl == null || this.wsUrl.trim().isEmpty()) {
            throw new RuntimeException("wsUrl is not available for this session");
        }
        if (this.token == null || this.token.trim().isEmpty()) {
            throw new RuntimeException("token is not available for WS connection");
        }
        if (this.wsClient == null) {
            this.wsClient = new WsClient(this.wsUrl, this.token);
        }
        return this.wsClient;
    }

    /**
     * Creates a new Session instance with alternative parameter order.
     * 
     * <p>This constructor provides backward compatibility for code that uses
     * the (String, AgentBay) parameter order.</p>
     * 
     * @param sessionId The unique identifier for this session
     * @param agentBay The AgentBay client instance
     */
    public Session(String sessionId, AgentBay agentBay) {
        this(agentBay, sessionId);
    }

    /**
     * Get the session ID.
     *
     * @return The unique identifier for this session
     */
    public String getSessionId() {
        return sessionId;
    }

    /**
     * Get basic session status.
     *
     * <p>This method calls the GetSessionDetail API and returns status only.</p>
     *
     * @return SessionStatusResult containing session status information
     */
    public SessionStatusResult getStatus() {
        try {
            logger.debug("Calling GetSessionDetail API for session: {}", sessionId);
            
            GetSessionDetailRequest request = new GetSessionDetailRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            GetSessionDetailResponse response = agentBay.getClient().getSessionDetail(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new SessionStatusResult(requestId, 0, "", false, "", "Invalid response from GetSessionDetail API");
            }

            GetSessionDetailResponseBody body = response.getBody();
            Integer httpStatusCode = body.getHttpStatusCode() != null ? body.getHttpStatusCode() : 0;
            String code = body.getCode() != null ? body.getCode() : "";
            Boolean success = body.getSuccess() != null ? body.getSuccess() : false;
            String message = body.getMessage() != null ? body.getMessage() : "";

            if (requestId == null || requestId.isEmpty()) {
                requestId = body.getRequestId() != null ? body.getRequestId() : "";
            }

            if (!success && !code.isEmpty()) {
                String errorMessage = message != null && !message.isEmpty() ? message : "Unknown error";
                if (!code.isEmpty()) {
                    errorMessage = "[" + code + "] " + errorMessage;
                }
                return new SessionStatusResult(requestId, httpStatusCode, code, false, "", errorMessage);
            }

            String status = "";
            if (body.getData() != null) {
                GetSessionDetailResponseBody.GetSessionDetailResponseBodyData data = body.getData();
                logger.info("GetSessionDetail API call successful: {}", data);
                status = data.getStatus() != null ? data.getStatus() : "";
            }

            logger.debug("GetSessionDetail API response - RequestId: {}, Success: {}, Status: {}", 
                        requestId, success, status);

            return new SessionStatusResult(requestId, httpStatusCode, code, success, status, "");

        } catch (Exception e) {
            String errorStr = e.getMessage() != null ? e.getMessage() : e.toString();
            
            // Check for NotFound error
            if (errorStr.contains("InvalidMcpSession.NotFound") || errorStr.contains("NotFound")) {
                logger.info("Session not found: {}", sessionId);
                logger.debug("GetSessionDetail error details: {}", errorStr);
                return new SessionStatusResult("", 400, "InvalidMcpSession.NotFound", false, "", 
                                              "Session " + sessionId + " not found");
            }

            logger.error("Error calling GetSessionDetail: {}", errorStr, e);
            return new SessionStatusResult("", 0, "", false, "", 
                                          "Failed to get session status " + sessionId + ": " + errorStr);
        }
    }

    /**
     * Refresh the backend idle timer for this session.
     *
     * <p>This method calls the RefreshSessionIdleTime API to prevent the session
     * from being automatically terminated due to inactivity.</p>
     *
     * @return OperationResult containing request ID and success status
     */
    public OperationResult keepAlive() {
        try {
            RefreshSessionIdleTimeRequest request = new RefreshSessionIdleTimeRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            RefreshSessionIdleTimeResponse response = agentBay.getClient().refreshSessionIdleTime(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new OperationResult(requestId, false, "", "Invalid response from RefreshSessionIdleTime API");
            }

            Boolean success = response.getBody().getSuccess();
            if (success == null || !success) {
                String code = response.getBody().getCode();
                String message = response.getBody().getMessage();
                String err = message != null && !message.isEmpty() ? message : "Unknown error";
                if (code != null && !code.isEmpty()) {
                    err = "[" + code + "] " + err;
                }
                return new OperationResult(requestId, false, "", err);
            }

            return new OperationResult(requestId, true, "", "");
        } catch (Exception e) {
            return new OperationResult("", false, "", "Failed to keep session alive: " + e.getMessage());
        }
    }

    /**
     * Get the AgentBay client.
     *
     * @return The AgentBay client instance associated with this session
     */
    public AgentBay getAgentBay() {
        return agentBay;
    }

    /**
     * Get the agent for this session.
     *
     * @return The Agent instance for AI-powered automation
     */
    public Agent getAgent() {
        return agent;
    }

    /**
     * Get the file system for this session.
     *
     * @return The FileSystem instance for file operations
     */
    public FileSystem getFileSystem() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides a shorthand way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem fs() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides an alternative way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem getFilesystem() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides a shorthand way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem getFiles() {
        return fileSystem;
    }

    /**
     * Call an MCP tool (legacy method, returns raw API response).
     *
     * @param toolName Tool name
     * @param args Tool arguments
     * @return CallMcpToolResponse Raw API response
     * @throws AgentBayException if the call fails
     */
    public CallMcpToolResponse callTool(String toolName, Object args) throws AgentBayException {
        // Server name is optional for API-based tool calls.
        // Some environments do not return ToolList in CreateSession, and the backend
        // can resolve the server by tool name.
        String serverName = getMcpServerForTool(toolName);
        if (serverName == null || serverName.isEmpty()) {
            serverName = null;
        }
        return agentBay.getApiClient().callMcpTool(sessionId, toolName, args, serverName);
    }

    /**
     * Call an MCP tool and return structured OperationResult.
     * 
     * <p>This is the preferred method for calling MCP tools as it provides unified routing logic
     * (LinkUrl, VPC, API) and consistent error handling.</p>
     *
     * @param toolName Tool name
     * @param args Tool arguments
     * @return OperationResult containing parsed response with request ID, success status, and data
     */
    public OperationResult callMcpTool(String toolName, Object args) {
        try {
            String serverName = getMcpServerForTool(toolName);

            // LinkUrl route requires explicit server name. If it's not available,
            // fall back to API-based call to let backend resolve the server.
            if (isNotEmpty(linkUrl) && isNotEmpty(token) && isNotEmpty(serverName)) {
                return callMcpToolLinkUrl(toolName, args, serverName);
            }

            // Fall back to API route
            return callMcpToolApi(toolName, args, serverName);

        } catch (Exception e) {
            return new OperationResult("", false, "",
                "Failed to call MCP tool " + toolName + ": " + e.getMessage());
        }
    }

    /**
     * Checks if a string is not null and not empty.
     * 
     * @param str The string to check
     * @return true if the string is not null and not empty, false otherwise
     */
    private boolean isNotEmpty(String str) {
        return str != null && !str.isEmpty();
    }

    /**
     * Calls an MCP tool via the traditional API route.
     * 
     * This method makes an HTTP API call to invoke the MCP tool and returns
     * the result as an OperationResult. It handles response parsing, error checking,
     * and data extraction.
     * 
     * @param toolName The name of the MCP tool to call
     * @param args The arguments to pass to the tool
     * @param serverName The MCP server name (can be null for server-side resolution)
     * @return OperationResult containing the tool call result
     */
    private OperationResult callMcpToolApi(String toolName, Object args, String serverName) {
        try {
            if (serverName == null || serverName.isEmpty()) {
                serverName = null;
            }

            CallMcpToolResponse response = agentBay.getApiClient().callMcpTool(sessionId, toolName, args, serverName);

            if (response == null || response.getBody() == null) {
                return new OperationResult("", false, "", "No response from MCP tool");
            }

            String requestId = ResponseUtil.extractRequestId(response);
            Boolean success = response.getBody().getSuccess();

            if (success == null || !success) {
                String errorMessage = response.getBody().getMessage();
                return new OperationResult(requestId, false, "",
                    errorMessage != null ? errorMessage : "MCP tool call failed");
            }

            Object data = response.getBody().getData();
            if (data == null) {
                return new OperationResult(requestId, false, "", "No data in response");
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
                String errorMessage = extractErrorMessageFromContent(dataMap);
                return new OperationResult(requestId, false, "", errorMessage);
            }

            String textContent = extractTextContentFromData(dataMap);
            return new OperationResult(requestId, true, textContent, "");

        } catch (Exception e) {
            return new OperationResult("", false, "",
                "Failed to call MCP tool via API: " + e.getMessage());
        }
    }

    /**
     * Calls an MCP tool via the LinkUrl route (VPC mode).
     * 
     * This method makes a direct HTTP call to the LinkUrl endpoint for faster
     * tool execution in VPC environments. It requires both token and linkUrl to be set.
     * 
     * @param toolName The name of the MCP tool to call
     * @param args The arguments to pass to the tool
     * @param serverName The MCP server name (required for LinkUrl route)
     * @return OperationResult containing the tool call result
     */
    private OperationResult callMcpToolLinkUrl(String toolName, Object args, String serverName) {
        try {
            if (!isNotEmpty(serverName)) {
                return new OperationResult("", false, "",
                    "Server name is required for LinkUrl tool call: " + toolName);
            }

            String requestId = String.format("link-%d-%09d",
                System.currentTimeMillis(),
                new java.util.Random().nextInt(1000000000));

            if (!isNotEmpty(linkUrl) || !isNotEmpty(token)) {
                return new OperationResult(requestId, false, "", "LinkUrl/token not available");
            }

            String url = linkUrl.endsWith("/") ? linkUrl + "callTool" : linkUrl + "/callTool";

            Map<String, Object> bodyParams = new java.util.HashMap<>();
            bodyParams.put("args", args);
            bodyParams.put("server", serverName);
            bodyParams.put("requestId", requestId);
            bodyParams.put("tool", toolName);
            bodyParams.put("token", token);
            String bodyJson = objectMapper.writeValueAsString(bodyParams);

            okhttp3.RequestBody requestBody = okhttp3.RequestBody.create(
                bodyJson,
                okhttp3.MediaType.parse("application/json")
            );

            okhttp3.OkHttpClient httpClient = new okhttp3.OkHttpClient.Builder()
                .readTimeout(900, java.util.concurrent.TimeUnit.SECONDS)
                .writeTimeout(900, java.util.concurrent.TimeUnit.SECONDS)
                .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                .build();

            okhttp3.Request request = new okhttp3.Request.Builder()
                .url(url)
                .header("Content-Type", "application/json")
                .header("X-Access-Token", token)
                .post(requestBody)
                .build();

            try (okhttp3.Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    String respBody = "";
                    try {
                        if (response.body() != null) {
                            respBody = response.body().string();
                        }
                    } catch (Exception ignored) {
                    }
                    logger.error("❌ API Response Failed: CallMcpTool(LinkUrl) Response, RequestId={}", requestId);
                    logger.error("📥 Response: {}", respBody);
                    return new OperationResult(requestId, false, "",
                        "HTTP request failed with code: " + response.code());
                }

                String responseBody = response.body() != null ? response.body().string() : "";
                @SuppressWarnings("unchecked")
                Map<String, Object> outerData = objectMapper.readValue(responseBody, Map.class);

                Object dataField = outerData.get("data");
                if (dataField == null) {
                    return new OperationResult(requestId, false, "", "No data field in LinkUrl response");
                }

                Map<String, Object> parsedData;
                if (dataField instanceof String) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> parsed = objectMapper.readValue((String) dataField, Map.class);
                    parsedData = parsed;
                } else if (dataField instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> casted = (Map<String, Object>) dataField;
                    parsedData = casted;
                } else {
                    return new OperationResult(requestId, false, "",
                        "Invalid data field type in LinkUrl response");
                }

                Object resultField = parsedData.get("result");
                if (!(resultField instanceof Map)) {
                    return new OperationResult(requestId, false, "",
                        "No result field in LinkUrl response data");
                }

                @SuppressWarnings("unchecked")
                Map<String, Object> resultData = (Map<String, Object>) resultField;
                Boolean isError = (Boolean) resultData.get("isError");
                Object contentObj = resultData.get("content");

                String textContent = "";
                if (contentObj instanceof java.util.List) {
                    java.util.List<?> content = (java.util.List<?>) contentObj;
                    if (!content.isEmpty() && content.get(0) instanceof Map) {
                        Map<?, ?> firstContent = (Map<?, ?>) content.get(0);
                        Object text = firstContent.get("text");
                        Object blob = firstContent.get("blob");
                        Object data = firstContent.get("data");
                        if (text != null) {
                            textContent = text.toString();
                        } else if (blob != null) {
                            textContent = blob.toString();
                        } else if (data != null) {
                            textContent = data.toString();
                        }
                    }
                }

                if (isError != null && isError) {
                    return new OperationResult(requestId, false, "", textContent);
                }
                return new OperationResult(requestId, true, textContent, "");
            }
        } catch (java.io.IOException e) {
            return new OperationResult("", false, "", "HTTP request failed: " + e.getMessage());
        } catch (Exception e) {
            return new OperationResult("", false, "", "Unexpected error in LinkUrl call: " + e.getMessage());
        }
    }

    /**
     * Extracts error message from the content field of an MCP tool response.
     * 
     * @param dataMap The response data map
     * @return The extracted error message, or a default error message if not found
     */
    private String extractErrorMessageFromContent(Map<String, Object> dataMap) {
        Object content = dataMap.get("content");
        if (content instanceof java.util.List && !((java.util.List<?>) content).isEmpty()) {
            Object firstContent = ((java.util.List<?>) content).get(0);
            if (firstContent instanceof Map) {
                Object text = ((Map<?, ?>) firstContent).get("text");
                if (text != null) {
                    return text.toString();
                }
            }
        }
        return "MCP tool execution error";
    }

    /**
     * Extracts text content from the data field of an MCP tool response.
     * 
     * This method looks for text, blob, or data fields in the content array
     * and returns the first non-null value found.
     * 
     * @param dataMap The response data map
     * @return The extracted text content as a string
     */
    private String extractTextContentFromData(Map<String, Object> dataMap) {
        Object content = dataMap.get("content");
        if (content instanceof java.util.List && !((java.util.List<?>) content).isEmpty()) {
            Object firstContent = ((java.util.List<?>) content).get(0);
            if (firstContent instanceof Map) {
                Map<?, ?> contentMap = (Map<?, ?>) firstContent;
                Object text = contentMap.get("text");
                if (text != null) {
                    return text.toString();
                }
                Object blob = contentMap.get("blob");
                if (blob != null) {
                    return blob.toString();
                }
                Object data = contentMap.get("data");
                if (data != null) {
                    return data.toString();
                }
            }
        }
        try {
            return objectMapper.writeValueAsString(dataMap);
        } catch (Exception e) {
            return dataMap.toString();
        }
    }

    /**
     * List available tools
     *
     * @return List of available tools
     * @throws AgentBayException if the call fails
     */
    private List<Object> listTools() throws AgentBayException {
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
            OperationResult result = callMcpTool("get_metrics", new java.util.HashMap<>());

            if (!result.isSuccess()) {
                return new SessionMetricsResult(result.getRequestId(), false, null, result.getErrorMessage());
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> raw = objectMapper.readValue(result.getData(), Map.class);

            SessionMetrics metrics = parseMetrics(raw);
            return new SessionMetricsResult(result.getRequestId(), true, metrics, "", raw);

        } catch (Exception e) {
            return new SessionMetricsResult("", false, null,
                "Failed to get metrics: " + e.getMessage());
        }
    }

    /**
     * Parses raw metrics data from the MCP get_metrics tool response.
     * 
     * This method extracts various metrics including CPU, memory, disk, and network
     * statistics from the raw data map and populates a SessionMetrics object.
     * 
     * @param raw The raw metrics data map from the MCP tool response
     * @return A populated SessionMetrics object
     */
    private SessionMetrics parseMetrics(Map<String, Object> raw) {
        SessionMetrics metrics = new SessionMetrics();
        metrics.setCpuCount(getIntValue(raw, "cpu_count"));
        metrics.setCpuUsedPct(getDoubleValue(raw, "cpu_used_pct"));
        metrics.setDiskTotal(getLongValue(raw, "disk_total"));
        metrics.setDiskUsed(getLongValue(raw, "disk_used"));
        metrics.setMemTotal(getLongValue(raw, "mem_total"));
        metrics.setMemUsed(getLongValue(raw, "mem_used"));

        metrics.setRxRateKBps(getDoubleValueWithFallback(raw,
            "rx_rate_kbyte_per_s", "rx_rate_kbps", "rx_rate_KBps"));
        metrics.setTxRateKBps(getDoubleValueWithFallback(raw,
            "tx_rate_kbyte_per_s", "tx_rate_kbps", "tx_rate_KBps"));
        metrics.setRxUsedKB(getDoubleValueWithFallback(raw,
            "rx_used_kbyte", "rx_used_kb", "rx_used_KB"));
        metrics.setTxUsedKB(getDoubleValueWithFallback(raw,
            "tx_used_kbyte", "tx_used_kb", "tx_used_KB"));

        metrics.setTimestamp(getStringValue(raw, "timestamp"));
        return metrics;
    }

    /**
     * Gets a double value from a map with fallback keys.
     * 
     * Tries each key in order until a non-null value is found, then converts it to double.
     * 
     * @param map The map to search
     * @param keys The keys to try in order
     * @return The first non-null value converted to double, or 0.0 if none found
     */
    private double getDoubleValueWithFallback(Map<String, Object> map, String... keys) {
        for (String key : keys) {
            Object value = map.get(key);
            if (value != null) {
                if (value instanceof Number) {
                    return ((Number) value).doubleValue();
                }
                try {
                    return Double.parseDouble(value.toString());
                } catch (NumberFormatException e) {
                    // Try next key
                }
            }
        }
        return 0.0;
    }

    /**
     * Gets an integer value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The integer value, or 0 if not found or conversion fails
     */
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

    /**
     * Gets a long value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The long value, or 0L if not found or conversion fails
     */
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

    /**
     * Gets a double value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The double value, or 0.0 if not found or conversion fails
     */
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

    /**
     * Gets a string value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The string value, or empty string if not found
     */
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
     * Get the mobile service for this session
     *
     * @return Mobile instance
     */
    public Mobile getMobile() {
        return mobile;
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
     * Initializes a browser instance with the given options.
     * 
     * This method calls the AgentBay cloud service to create a browser instance for web automation and testing. The browser is initialized with a persistent path for storing browser data.
     * 
     * @param option Browser configuration options including browser type, headless mode, etc.
     * @return OperationResult containing the initialization result
     * @throws AgentBayException if browser initialization fails
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
     * Lists all available MCP tools for this session.
     * 
     * This method retrieves the list of MCP tools that can be called in this session,including their names, descriptions, input schemas, and server information.
     * 
     * @return McpToolsResult containing the list of available tools
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
     * Sets the image ID for this session.
     * This is used to specify the base image for the session environment.
     * 
     * @param imageId The image ID to set
     */
    public void setImageId(String imageId) {
        this.imageId = imageId;
    }

    /**
     * Gets the image ID for this session.
     * 
     * @return The image ID, or empty string if not set
     */
    public String getImageId() {
        return imageId;
    }

    /**
     * Gets the enableBrowserReplay flag.
     * This flag determines whether browser recording is enabled for this session.
     * 
     * @return true if browser replay is enabled, false otherwise
     */
    public Boolean getEnableBrowserReplay() {
        return enableBrowserReplay;
    }

    /**
     * Sets the enableBrowserReplay flag.
     * This flag determines whether browser recording is enabled for this session.
     * 
     * @param enableBrowserReplay true to enable browser replay, false to disable
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
     * Gets the token for LinkUrl tool calls.
     * This token is used for authentication when calling MCP tools via the LinkUrl route.
     * 
     * @return The authentication token
     */
    public String getToken() {
        return token;
    }

    /**
     * Sets the token for LinkUrl tool calls.
     * This token is used for authentication when calling MCP tools via the LinkUrl route.
     * 
     * @param token The authentication token to set
     */
    public void setToken(String token) {
        this.token = token;
    }

    /**
     * Gets the LinkUrl for direct tool calls.
     * This URL is used for calling MCP tools via the LinkUrl route in VPC environments.
     * 
     * @return The LinkUrl, or empty string if not set
     */
    public String getLinkUrl() {
        return linkUrl == null ? "" : linkUrl;
    }

    /**
     * Sets the LinkUrl for direct tool calls.
     * This URL is used for calling MCP tools via the LinkUrl route in VPC environments.
     * 
     * @param linkUrl The LinkUrl to set
     */
    public void setLinkUrl(String linkUrl) {
        this.linkUrl = linkUrl == null ? "" : linkUrl;
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
     * Updates the MCP tools list for this session from a JSON string.
     * 
     * This method parses the JSON string and updates the mcpTools list with
     * the new tool definitions. It handles both Map and String representations
     * of tool data.
     * 
     * @param dataJson JSON string containing the tool definitions
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
                            tool.setName((String) (toolMap.get("name") != null ? toolMap.get("name") : toolMap.get("Name")));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            Object server = toolMap.get("server");
                            if (server == null) {
                                server = toolMap.get("serverName");
                            }
                            if (server == null) {
                                server = toolMap.get("Server");
                            }
                            tool.setServer((String) server);
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        } else if (toolData instanceof String) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = objectMapper.readValue((String) toolData, Map.class);

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) (toolMap.get("name") != null ? toolMap.get("name") : toolMap.get("Name")));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            Object server = toolMap.get("server");
                            if (server == null) {
                                server = toolMap.get("serverName");
                            }
                            if (server == null) {
                                server = toolMap.get("Server");
                            }
                            tool.setServer((String) server);
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        }
                    } catch (Exception e) {
                        logger.warn("Failed to parse tool data: {}", toolData, e);
                    }
                }
            }

            this.mcpTools = tools;

        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Gets the list of MCP tools available for this session.
     * 
     * @return List of McpTool instances
     */
    public List<McpTool> getMcpTools() {
        return mcpTools;
    }

    /**
     * Sets the list of MCP tools for this session.
     * 
     * @param mcpTools The list of McpTool instances to set
     */
    public void setMcpTools(List<McpTool> mcpTools) {
        this.mcpTools = mcpTools != null ? mcpTools : new java.util.ArrayList<>();
    }

    /**
     * Gets the MCP server name for a specific tool.
     * 
     * This method searches through the available MCP tools to find the server that provides the specified tool.
     * 
     * @param toolName The name of the tool to look up
     * @return The server name, or empty string if not found
     */
    public String getMcpServerForTool(String toolName) {
        if (toolName == null || toolName.isEmpty()) {
            return "";
        }
        for (McpTool tool : mcpTools) {
            if (tool != null && toolName.equals(tool.getName())) {
                String server = tool.getServer();
                if (server != null && !server.isEmpty()) {
                    return server;
                }
            }
        }
        return "";
    }

    /**
     * Gets a connection link for the current session with specified parameters.
     * 
     * This method generates a connection URL that can be used to access the session via the specified protocol and port.
     * 
     * @param protocolType The protocol type to use for the link (e.g., "https")
     * @param port The port number to use for the connection
     * @return OperationResult containing the connection link URL
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
     * Gets a connection link for the current session with default parameters.
     * 
     * This method generates a connection URL using the default protocol and port.
     * 
     * @return OperationResult containing the connection link URL
     * @throws AgentBayException if the request fails
     */
    public OperationResult getLink() throws AgentBayException {
        return getLink(null, null);
    }


    /**
     * Deletes this session.
     * 
     * This method releases the cloud resources associated with this session.
     * Context synchronization is not performed before deletion.
     * 
     * @return DeleteResult containing the deletion result
     */
    public com.aliyun.agentbay.model.DeleteResult delete() {
        return delete(false);
    }

    /**
     * Deletes this session with optional context synchronization.
     * 
     * This method releases the cloud resources associated with this session.
     * If syncContext is true, it will first synchronize the context (upload files)
     * before deleting the session, waiting for all uploads to complete.
     * 
     * @param syncContext Whether to synchronize context before deletion
     * @return DeleteResult containing the deletion result
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
     * Sets labels for this session.
     * 
     * Labels are key-value pairs that can be used to organize and filter sessions.
     * All keys and values must be non-empty strings.
     * 
     * @param labels Map of label key-value pairs to set
     * @return OperationResult indicating success or failure
     * @throws AgentBayException if the API call fails or validation fails
     * @throws IllegalArgumentException if labels are null or contain invalid keys/values
     */
    public OperationResult setLabels(Map<String, String> labels) throws AgentBayException {
        try {
            // Validate labels
            if (labels == null) {
                throw new IllegalArgumentException("Labels cannot be null");
            }

            // Validate label keys and values
            for (Map.Entry<String, String> entry : labels.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();

                if (key == null || key.trim().isEmpty()) {
                    throw new IllegalArgumentException("Label key cannot be null or empty");
                }
                if (value == null || value.trim().isEmpty()) {
                    throw new IllegalArgumentException("Label value cannot be null or empty");
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
     * Gets the labels for this session.
     * 
     * This method retrieves all labels that have been set for this session.
     * 
     * @return OperationResult containing the labels map as JSON string in the data field
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

    /**
     * Returns a string representation of this session.
     * 
     * @return A string containing the session ID and parameters
     */
    @Override
    public String toString() {
        return "Session{" +
                "sessionId='" + sessionId + '\'' +
                '}';
    }
}