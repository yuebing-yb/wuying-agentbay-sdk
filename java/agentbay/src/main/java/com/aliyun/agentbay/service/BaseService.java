package com.aliyun.agentbay.service;

import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import java.util.concurrent.TimeUnit;

/**
 * Base service class that provides common functionality for all service classes.
 * Similar to Python's BaseService, handles MCP tool calls and response parsing.
 */
public class BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(BaseService.class);
    private static final OkHttpClient httpClient = new OkHttpClient.Builder()
        .readTimeout(120, TimeUnit.SECONDS)
        .writeTimeout(120, TimeUnit.SECONDS)
        .connectTimeout(30, TimeUnit.SECONDS)
        .build();
    private static final Random random = new Random();

    protected final Session session;

    public BaseService(Session session) {
        this.session = session;
    }

    /**
     * Call an MCP tool and parse the response similar to Python's _call_mcp_tool method.
     * Routes to VPC or API call based on session configuration.
     *
     * @param toolName The name of the tool to call
     * @param args     The arguments to pass to the tool
     * @return OperationResult containing the parsed response
     */
    protected OperationResult callMcpTool(String toolName, Object args) {
        return callMcpTool(toolName, args, null);
    }

    /**
     * Call an MCP tool with an explicit server name.
     * In LinkUrl mode, serverName is required and will be sent to the link endpoint.
     *
     * @param toolName The name of the tool to call
     * @param args The arguments to pass to the tool
     * @param serverName The MCP server name (e.g. "wuying_filesystem")
     * @return OperationResult containing the parsed response
     */
    protected OperationResult callMcpTool(String toolName, Object args, String serverName) {
        try {
            if (isNotEmpty(session.getLinkUrl()) && isNotEmpty(session.getToken())) {
                return callMcpToolLinkUrl(toolName, args, serverName);
            } else {
                return callMcpToolApi(toolName, args);
            }
        } catch (Exception e) {
            return new OperationResult("", false, "", "Unexpected error: " + e.getMessage());
        }
    }

    /**
     * Check if a string is not null and not empty
     */
    private boolean isNotEmpty(String str) {
        return str != null && !str.isEmpty();
    }

    /**
     * Call MCP tool via traditional API (non-VPC mode)
     */
    private OperationResult callMcpToolApi(String toolName, Object args) {
        try {
            CallMcpToolResponse response = session.callTool(toolName, args);

            if (response == null) {
                return new OperationResult("", false, "", "No response received");
            }

            String requestId = ResponseUtil.extractRequestId(response);

            if (response.getBody() != null && response.getBody().getData() != null) {
                try {
                    String parsedOutput = parseResponseBody(response.getBody().getData());
                    return new OperationResult(requestId, true, parsedOutput, "");
                } catch (RuntimeException e) {
                    if (e.getMessage() != null && e.getMessage().startsWith("MCP tool execution error:")) {
                        String errorMsg = e.getMessage().substring("MCP tool execution error: ".length());
                        String errorWithRequestId = errorMsg;
                        if (requestId != null && !requestId.isEmpty()) {
                            errorWithRequestId = String.format("RequestId=%s, %s", requestId, errorMsg);
                        }
                        return new OperationResult(requestId, false, "", errorWithRequestId);
                    }
                    throw e;
                }
            } else {
                return new OperationResult(requestId, false, "", "Invalid response body");
            }

        } catch (AgentBayException e) {
            return new OperationResult("", false, "", "Failed to call MCP tool " + toolName + ": " + e.getMessage());
        }
    }

    /**
     * Call MCP tool via link url connection
     */
    private OperationResult callMcpToolLinkUrl(String toolName, Object args, String serverName) {
        try {
            if (!isNotEmpty(serverName)) {
                return new OperationResult(
                    "",
                    false,
                    "",
                    "Server name is required for LinkUrl tool call: " + toolName
                );
            }

            String requestId = String.format("link-%d-%09d", System.currentTimeMillis(), random.nextInt(1000000000));

            String linkUrl = session.getLinkUrl();
            if (!isNotEmpty(linkUrl)) {
                return new OperationResult("", false, "",
                    "Link URL not available. Ensure session VPC configuration is complete.");
            }

            String url = linkUrl + "/callTool";

            String token = session.getToken();

            logger.info("🔗 API Call: CallMcpTool(LinkUrl)");
            logger.info("✅ API Response: CallMcpTool(LinkUrl) Request, RequestId={}", requestId);
            logger.info("   └─ tool_name={}", toolName);
            String command = "";
            try {
                if (args instanceof Map) {
                    Object cmd = ((Map<?, ?>) args).get("command");
                    if (cmd != null) {
                        command = cmd.toString();
                    }
                }
            } catch (Exception e) {
            }
            if (command == null || command.isEmpty()) {
                try {
                    command = objectMapper.writeValueAsString(args);
                } catch (Exception e) {
                    command = "";
                }
            }
            if (command != null && command.length() > 500) {
                command = command.substring(0, 500) + "...(truncated)";
            }
            logger.info("   └─ command={}", command);

            Map<String, Object> bodyParams = new HashMap<>();
            bodyParams.put("args", args);
            bodyParams.put("server", serverName);
            bodyParams.put("requestId", requestId);
            bodyParams.put("tool", toolName);
            bodyParams.put("token", token);
            String bodyJson = objectMapper.writeValueAsString(bodyParams);

            RequestBody requestBody = RequestBody.create(bodyJson, MediaType.parse("application/json"));
            Request request = new Request.Builder()
                .url(url)
                .header("Content-Type", "application/json")
                .header("X-Access-Token", token)
                .post(requestBody)
                .build();

            try (Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    return new OperationResult(requestId, false, "",
                        "HTTP request failed with code: " + response.code());
                }

                String responseBody = response.body().string();
                @SuppressWarnings("unchecked")
                Map<String, Object> outerData = objectMapper.readValue(responseBody, Map.class);

                Object dataField = outerData.get("data");
                if (dataField == null) {
                    return new OperationResult(requestId, false, "",
                        "No data field in VPC response");
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
                        "Invalid data field type in VPC response");
                }

                Object resultField = parsedData.get("result");
                if (resultField == null || !(resultField instanceof Map)) {
                    return new OperationResult(requestId, false, "",
                        "No result field in VPC response data");
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
                        if (text != null) {
                            textContent = text.toString();
                        }
                    }
                }

                if (isError != null && isError) {
                    logger.info("✅ API Response: CallMcpTool(LinkUrl) Response, RequestId={}", requestId);
                    logger.info("   └─ http_status={}", response.code());
                    logger.info("   └─ tool_name={}", toolName);
                    String out = textContent != null ? textContent : "";
                    if (out.length() > 800) {
                        out = out.substring(0, 800) + "...(truncated)";
                    }
                    logger.info("   └─ output={}", out);
                    return new OperationResult(requestId, false, "", textContent);
                }

                logger.info("✅ API Response: CallMcpTool(LinkUrl) Response, RequestId={}", requestId);
                logger.info("   └─ http_status={}", response.code());
                logger.info("   └─ tool_name={}", toolName);
                String out = textContent != null ? textContent : "";
                if (out.length() > 800) {
                    out = out.substring(0, 800) + "...(truncated)";
                }
                logger.info("   └─ output={}", out);
                return new OperationResult(requestId, true, textContent, "");
            }

        } catch (IOException e) {
            return new OperationResult("", false, "", "HTTP request failed: " + e.getMessage());
        } catch (Exception e) {
            return new OperationResult("", false, "", "Unexpected error: " + e.getMessage());
        }
    }

    /**
     * Parse MCP tool response body, similar to Python's _parse_response_body method.
     * Extracts text content from body.Data.content[0].text structure.
     *
     * @param responseData The response data to parse
     * @return Parsed text content
     */
    private String parseResponseBody(Object responseData) {
        try {
            if (responseData instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> dataMap = (Map<String, Object>) responseData;

                // Check for error first (similar to Python implementation)
                Boolean isError = (Boolean) dataMap.get("isError");
                if (isError != null && isError) {
                    // Handle error case - extract error message from content
                    Object contentObj = dataMap.get("content");
                    if (contentObj instanceof java.util.List) {
                        @SuppressWarnings("unchecked")
                        java.util.List<Object> content = (java.util.List<Object>) contentObj;
                        if (!content.isEmpty() && content.get(0) instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> contentItem = (Map<String, Object>) content.get(0);
                            Object text = contentItem.get("text");
                            Object blob = contentItem.get("blob");
                            Object data = contentItem.get("data");
                            if (text != null) {
                                throw new RuntimeException("MCP tool execution error: " + text.toString());
                            }
                            if (blob != null) {
                                throw new RuntimeException("MCP tool execution error: " + blob.toString());
                            }
                            if (data != null) {
                                throw new RuntimeException("MCP tool execution error: " + data.toString());
                            }
                        }
                    }
                    throw new RuntimeException("MCP tool execution failed with unknown error");
                }

                // Extract content[0].text like Python implementation
                Object contentObj = dataMap.get("content");
                if (contentObj instanceof java.util.List) {
                    @SuppressWarnings("unchecked")
                    java.util.List<Object> content = (java.util.List<Object>) contentObj;
                    if (!content.isEmpty() && content.get(0) instanceof Map) {
                        @SuppressWarnings("unchecked")
                        Map<String, Object> contentItem = (Map<String, Object>) content.get(0);
                        Object text = contentItem.get("text");
                        if (text != null) {
                            return text.toString();
                        }
                        Object blob = contentItem.get("blob");
                        if (blob != null) {
                            return blob.toString();
                        }
                        Object data = contentItem.get("data");
                        if (data != null) {
                            return data.toString();
                        }
                    }
                }
            }

            // Fallback to JSON representation if possible
            try {
                if (responseData instanceof Map || responseData instanceof java.util.List) {
                    return objectMapper.writeValueAsString(responseData);
                }
            } catch (Exception e) {
            }

            // Final fallback
            return responseData.toString();

        } catch (RuntimeException e) {
            // Re-throw RuntimeExceptions (like MCP tool execution errors) to be handled upstream
            throw e;
        } catch (Exception e) {
            return "Error parsing MCP response: " + e.getMessage();
        }
    }
}