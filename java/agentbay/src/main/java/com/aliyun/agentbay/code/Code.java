package com.aliyun.agentbay.code;

import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.model.code.*;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;
import java.util.function.Consumer;

/**
 * Handles code execution operations in the AgentBay cloud environment.
 *
 * <p>This service provides methods to execute code in various programming languages
 * (Python, JavaScript, R, Java) within a cloud-based code execution environment.
 * It supports both synchronous and WebSocket-based streaming execution modes.</p>
 *
 */
public class Code extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SERVER_CODESPACE = "wuying_codespace";

    /**
     * Creates a new Code service instance bound to the given session.
     *
     * @param session The session to bind this code execution service to.
     */
    public Code(Session session) {
        super(session);
    }

    /**
     * Parses the response body from the MCP tool, supporting rich output formats.
     *
     * @param responseData The response data map to parse.
     * @return EnhancedCodeExecutionResult containing parsed execution results, logs, and error information.
     * @throws RuntimeException if the response format is unknown or parsing fails.
     */
    private EnhancedCodeExecutionResult parseResponseBody(Map<String, Object> responseData) {
        try {
            if (responseData == null || responseData.isEmpty()) {
                throw new RuntimeException("No data field in response");
            }

            Object contentObj = responseData.get("content");
            if (contentObj instanceof List) {
                List<?> content = (List<?>) contentObj;
                if (!content.isEmpty() && content.get(0) instanceof Map) {
                    Map<?, ?> contentItem = (Map<?, ?>) content.get(0);
                    Object textObj = contentItem.get("text");
                    if (textObj != null) {
                        try {
                            String textString = textObj.toString();
                            Map<String, Object> parsedJson = objectMapper.readValue(textString, Map.class);
                            if (parsedJson.containsKey("result") || parsedJson.containsKey("executionError")) {
                                responseData = parsedJson;
                            }
                        } catch (Exception e) {
                        }
                    }
                }
            }

            if (responseData.containsKey("result") && responseData.get("result") instanceof List) {
                return parseNewJsonFormat(responseData);
            }

            boolean isRich = responseData.containsKey("logs") || responseData.containsKey("results");
            if (isRich) {
                return parseRichFormat(responseData);
            }

            Boolean isError = (Boolean) responseData.get("isError");
            if (isError != null && isError) {
                return parseLegacyErrorFormat(responseData);
            }

            return parseLegacyFormat(responseData);

        } catch (Exception e) {
            throw new RuntimeException("Error parsing response body: " + e.getMessage());
        }
    }

    /**
     * Parses the new JSON format response containing {@code result}, {@code stdout},
     * {@code stderr}, and {@code executionError} fields.
     *
     * @param responseData The response data in new JSON format.
     * @return EnhancedCodeExecutionResult with parsed results and logs.
     * @throws RuntimeException if parsing fails.
     */
    private EnhancedCodeExecutionResult parseNewJsonFormat(Map<String, Object> responseData) {
        try {
            CodeExecutionLogs logs = new CodeExecutionLogs();
            if (responseData.get("stdout") instanceof List) {
                logs.setStdout((List<String>) responseData.get("stdout"));
            }
            if (responseData.get("stderr") instanceof List) {
                logs.setStderr((List<String>) responseData.get("stderr"));
            }

            List<CodeResult> results = new ArrayList<>();
            Object resultObj = responseData.get("result");
            if (resultObj instanceof List) {
                for (Object resItem : (List<?>) resultObj) {
                    Map<String, Object> parsedItem = null;

                    if (resItem instanceof String) {
                        try {
                            Object parsed = objectMapper.readValue((String) resItem, Object.class);
                            if (parsed instanceof String) {
                                try {
                                    parsedItem = objectMapper.readValue((String) parsed, Map.class);
                                } catch (Exception e) {
                                    
                                }
                            } else if (parsed instanceof Map) {
                                parsedItem = (Map<String, Object>) parsed;
                            }
                        } catch (Exception e) {
                            CodeResult result = new CodeResult();
                            result.setText(resItem.toString());
                            results.add(result);
                            continue;
                        }
                    } else if (resItem instanceof Map) {
                        parsedItem = (Map<String, Object>) resItem;
                    }

                    if (parsedItem != null) {
                        CodeResult result = new CodeResult();
                        result.setText(getStringValue(parsedItem, "text/plain", "text"));
                        result.setHtml(getStringValue(parsedItem, "text/html", "html"));
                        result.setMarkdown(getStringValue(parsedItem, "text/markdown", "markdown"));
                        result.setPng(getStringValue(parsedItem, "image/png", "png"));
                        result.setJpeg(getStringValue(parsedItem, "image/jpeg", "jpeg"));
                        result.setSvg(getStringValue(parsedItem, "image/svg+xml", "svg"));
                        result.setJson(parsedItem.get("application/json") != null ? parsedItem.get("application/json") : parsedItem.get("json"));
                        result.setLatex(getStringValue(parsedItem, "text/latex", "latex"));

                        Object chartObj = parsedItem.get("application/vnd.vegalite.v4+json");
                        if (chartObj == null) chartObj = parsedItem.get("application/vnd.vegalite.v5+json");
                        if (chartObj == null) chartObj = parsedItem.get("chart");
                        result.setChart(chartObj);

                        Boolean isMain = (Boolean) parsedItem.get("isMainResult");
                        if (isMain == null) isMain = (Boolean) parsedItem.get("is_main_result");
                        result.setMainResult(isMain != null && isMain);

                        results.add(result);
                    }
                }
            }

            CodeExecutionError error = null;
            Object executionError = responseData.get("executionError");
            if (executionError != null && !executionError.toString().isEmpty()) {
                error = new CodeExecutionError("ExecutionError", executionError.toString(), "");
            }

            EnhancedCodeExecutionResult enhancedResult = new EnhancedCodeExecutionResult();
            enhancedResult.setExecutionCount((Integer) responseData.get("execution_count"));

            Object execTime = responseData.get("execution_time");
            if (execTime instanceof Number) {
                enhancedResult.setExecutionTime(((Number) execTime).doubleValue());
            }

            enhancedResult.setLogs(logs);
            enhancedResult.setResults(results);
            enhancedResult.setError(error);

            Boolean isError = (Boolean) responseData.get("isError");
            enhancedResult.setSuccess(error == null && (isError == null || !isError));

            return enhancedResult;

        } catch (Exception e) {
            throw new RuntimeException("Error parsing new JSON format: " + e.getMessage());
        }
    }

    /**
     * Parses the rich response format containing {@code logs} and {@code results} fields.
     *
     * @param responseData The response data in rich format.
     * @return EnhancedCodeExecutionResult with parsed results and logs.
     * @throws RuntimeException if parsing fails.
     */
    private EnhancedCodeExecutionResult parseRichFormat(Map<String, Object> responseData) {
        try {
            CodeExecutionLogs logs = new CodeExecutionLogs();
            Object logsObj = responseData.get("logs");
            if (logsObj instanceof Map) {
                Map<?, ?> logsData = (Map<?, ?>) logsObj;
                if (logsData.get("stdout") instanceof List) {
                    logs.setStdout((List<String>) logsData.get("stdout"));
                }
                if (logsData.get("stderr") instanceof List) {
                    logs.setStderr((List<String>) logsData.get("stderr"));
                }
            }

            List<CodeResult> results = new ArrayList<>();
            Object resultsObj = responseData.get("results");
            if (resultsObj instanceof List) {
                for (Object resItem : (List<?>) resultsObj) {
                    if (resItem instanceof Map) {
                        Map<?, ?> resData = (Map<?, ?>) resItem;
                        CodeResult result = new CodeResult();
                        result.setText((String) resData.get("text"));
                        result.setHtml((String) resData.get("html"));
                        result.setMarkdown((String) resData.get("markdown"));
                        result.setPng((String) resData.get("png"));
                        result.setJpeg((String) resData.get("jpeg"));
                        result.setSvg((String) resData.get("svg"));
                        result.setJson(resData.get("json"));
                        result.setLatex((String) resData.get("latex"));
                        result.setChart(resData.get("chart"));

                        Boolean isMain = (Boolean) resData.get("is_main_result");
                        result.setMainResult(isMain != null && isMain);

                        results.add(result);
                    }
                }
            }

            CodeExecutionError error = null;
            Object errorObj = responseData.get("error");
            if (errorObj instanceof Map) {
                Map<?, ?> errorData = (Map<?, ?>) errorObj;
                error = new CodeExecutionError(
                    errorData.get("name") != null ? errorData.get("name").toString() : "UnknownError",
                    errorData.get("value") != null ? errorData.get("value").toString() : "",
                    errorData.get("traceback") != null ? errorData.get("traceback").toString() : ""
                );
            }

            EnhancedCodeExecutionResult enhancedResult = new EnhancedCodeExecutionResult();
            enhancedResult.setExecutionCount((Integer) responseData.get("execution_count"));

            Object execTime = responseData.get("execution_time");
            if (execTime instanceof Number) {
                enhancedResult.setExecutionTime(((Number) execTime).doubleValue());
            }

            enhancedResult.setLogs(logs);
            enhancedResult.setResults(results);
            enhancedResult.setError(error);

            Boolean isError = (Boolean) responseData.get("isError");
            enhancedResult.setSuccess(isError == null || !isError);

            return enhancedResult;

        } catch (Exception e) {
            throw new RuntimeException("Error parsing rich format: " + e.getMessage());
        }
    }

    /**
     * Parses the legacy error format response where {@code isError} is true.
     *
     * @param responseData The response data containing error information.
     * @return EnhancedCodeExecutionResult with success set to false and the error message.
     */
    private EnhancedCodeExecutionResult parseLegacyErrorFormat(Map<String, Object> responseData) {
        StringBuilder errorMessage = new StringBuilder();
        Object contentObj = responseData.get("content");
        if (contentObj instanceof List) {
            for (Object item : (List<?>) contentObj) {
                if (item instanceof Map) {
                    Object text = ((Map<?, ?>) item).get("text");
                    if (text != null) {
                        if (errorMessage.length() > 0) errorMessage.append("; ");
                        errorMessage.append(text.toString());
                    }
                }
            }
        }

        EnhancedCodeExecutionResult result = new EnhancedCodeExecutionResult();
        result.setSuccess(false);
        result.setErrorMessage("Error in response: " + errorMessage.toString());
        return result;
    }

    /**
     * Helper method to get a string value from a map with fallback to an alternative key.
     * This mimics Python's dict.get(key1) or dict.get(key2) behavior.
     *
     * @param map The map to search
     * @param key1 The primary key to look for
     * @param key2 The fallback key if key1 is not found
     * @return The string value, or null if neither key exists
     */
    private String getStringValue(Map<String, Object> map, String key1, String key2) {
        Object value = map.get(key1);
        if (value != null) {
            return value.toString();
        }
        value = map.get(key2);
        return value != null ? value.toString() : null;
    }

    /**
     * Parses the legacy response format where result text is in the {@code content} field.
     *
     * @param responseData The response data in legacy format.
     * @return EnhancedCodeExecutionResult wrapping the legacy text content.
     * @throws RuntimeException if the response format is unknown.
     */
    private EnhancedCodeExecutionResult parseLegacyFormat(Map<String, Object> responseData) {
        Object contentObj = responseData.get("content");
        if (contentObj instanceof List) {
            List<?> content = (List<?>) contentObj;
            if (!content.isEmpty() && content.get(0) instanceof Map) {
                Map<?, ?> contentItem = (Map<?, ?>) content.get(0);
                Object textObj = contentItem.get("text");
                if (textObj != null) {
                    String textString = textObj.toString();

                    EnhancedCodeExecutionResult result = new EnhancedCodeExecutionResult();
                    result.setSuccess(true);

                    CodeExecutionLogs logs = new CodeExecutionLogs();
                    logs.getStdout().add(textString);
                    result.setLogs(logs);

                    CodeResult codeResult = new CodeResult();
                    codeResult.setText(textString);
                    codeResult.setMainResult(true);
                    result.getResults().add(codeResult);

                    return result;
                }
            }
        }

        throw new RuntimeException("Unknown response format");
    }

    /**
     * Execute code in the specified language with a timeout.
     *
     * @param code The code to execute.
     * @param language The programming language of the code. Case-insensitive. Supported values: 'python', 'javascript', 'r', 'java'.
     * @param timeoutS The timeout for the code execution in seconds.
     *                 Note: Due to gateway limitations, each request cannot exceed 60 seconds.
     * @return EnhancedCodeExecutionResult containing success status, execution result,
     *         logs, and error message if any.
     */
    public EnhancedCodeExecutionResult runCode(String code, String language, int timeoutS) {
        try {
            String rawLanguage = (language == null) ? "" : language;
            String normalizedLanguage = rawLanguage.trim().toLowerCase();

            Map<String, String> aliases = new HashMap<>();
            aliases.put("py", "python");
            aliases.put("python3", "python");
            aliases.put("js", "javascript");
            aliases.put("node", "javascript");
            aliases.put("nodejs", "javascript");

            String canonicalLanguage = aliases.getOrDefault(normalizedLanguage, normalizedLanguage);

            Set<String> supportedLanguages = new HashSet<>(Arrays.asList("python", "javascript", "r", "java"));
            if (!supportedLanguages.contains(canonicalLanguage)) {
                return new EnhancedCodeExecutionResult("", false,
                    "Unsupported language: " + rawLanguage + ". Supported languages are 'python', 'javascript', 'r', and 'java'");
            }

            language = canonicalLanguage;

            Map<String, Object> args = new HashMap<>();
            args.put("code", code);
            args.put("language", language);
            args.put("timeout_s", timeoutS);
            OperationResult result = callMcpTool("run_code", args);
            if (result.isSuccess()) {
                try {
                    Map<String, Object> responseData = objectMapper.readValue(result.getData(), Map.class);
                    EnhancedCodeExecutionResult enhancedResult = parseResponseBody(responseData);
                    enhancedResult.setRequestId(result.getRequestId());
                    return enhancedResult;
                } catch (Exception e) {
                    EnhancedCodeExecutionResult enhancedResult = new EnhancedCodeExecutionResult();
                    enhancedResult.setRequestId(result.getRequestId());
                    enhancedResult.setSuccess(true);

                    CodeResult codeResult = new CodeResult();
                    codeResult.setText(result.getData());
                    codeResult.setMainResult(true);
                    enhancedResult.getResults().add(codeResult);

                    CodeExecutionLogs logs = new CodeExecutionLogs();
                    logs.getStdout().add(result.getData());
                    enhancedResult.setLogs(logs);

                    return enhancedResult;
                }
            } else {
                return new EnhancedCodeExecutionResult(result.getRequestId(), false,
                    result.getErrorMessage() != null && !result.getErrorMessage().isEmpty()
                        ? result.getErrorMessage() : "Failed to run code");
            }

        } catch (Exception e) {
            return new EnhancedCodeExecutionResult("", false, "Failed to run code: " + e.getMessage());
        }
    }

    // Streaming overload is temporarily disabled in this version.
    // The streaming implementation is preserved in runCodeStreamWs()
    // and will be re-enabled in a future release.

    /**
     * Execute code via WebSocket streaming, delivering stdout/stderr chunks in real-time.
     *
     * @param code The code to execute.
     * @param language The canonical programming language (already normalized).
     * @param timeoutS The timeout for the code execution in seconds.
     * @param onStdout Callback invoked for each stdout chunk. May be null.
     * @param onStderr Callback invoked for each stderr chunk. May be null.
     * @param onError Callback invoked when an error occurs. May be null.
     * @return EnhancedCodeExecutionResult containing success status, execution result,
     *         logs, and error message if any.
     */
    private EnhancedCodeExecutionResult runCodeStreamWs(
        String code,
        String language,
        int timeoutS,
        Consumer<String> onStdout,
        Consumer<String> onStderr,
        Consumer<Object> onError
    ) {
        try {
            String rawLanguage = (language == null) ? "" : language;
            String normalizedLanguage = rawLanguage.trim().toLowerCase();

            Map<String, String> aliases = new HashMap<>();
            aliases.put("py", "python");
            aliases.put("python3", "python");
            aliases.put("js", "javascript");
            aliases.put("node", "javascript");
            aliases.put("nodejs", "javascript");

            String canonicalLanguage = aliases.getOrDefault(normalizedLanguage, normalizedLanguage);

            Set<String> supportedLanguages = new HashSet<>(Arrays.asList("python", "javascript", "r", "java"));
            if (!supportedLanguages.contains(canonicalLanguage)) {
                return new EnhancedCodeExecutionResult("", false,
                    "Unsupported language: " + rawLanguage + ". Supported languages are 'python', 'javascript', 'r', and 'java'");
            }

            String target = SERVER_CODESPACE;
            try {
                String t = this.session.getMcpServerForTool("run_code");
                if (t != null && !t.isEmpty()) {
                    target = t;
                }
            } catch (Exception e) {
            }

            WsClient wsClient = this.session.getWsClient();

            List<String> stdoutChunks = new ArrayList<>();
            List<String> stderrChunks = new ArrayList<>();
            List<CodeResult> results = new ArrayList<>();
            final String[] errorMessage = {""};
            final CodeExecutionError[] errorObj = {null};

            Map<String, Object> data = new HashMap<>();
            data.put("method", "run_code");
            data.put("mode", "stream");
            Map<String, Object> params = new HashMap<>();
            params.put("language", canonicalLanguage);
            params.put("timeoutS", timeoutS);
            params.put("code", code);
            data.put("params", params);

            WsClient.StreamHandle handle = wsClient.callStream(
                target,
                data,
                (_invocationId, eventData) -> {
                    Object eventTypeObj = eventData.get("eventType");
                    String eventType = eventTypeObj != null ? eventTypeObj.toString() : "";
                    if ("stdout".equals(eventType)) {
                        String chunk = String.valueOf(eventData.getOrDefault("chunk", ""));
                        stdoutChunks.add(chunk);
                        if (onStdout != null) onStdout.accept(chunk);
                        return;
                    }
                    if ("stderr".equals(eventType)) {
                        String chunk = String.valueOf(eventData.getOrDefault("chunk", ""));
                        stderrChunks.add(chunk);
                        if (onStderr != null) onStderr.accept(chunk);
                        return;
                    }
                    if ("result".equals(eventType)) {
                        Object rp = eventData.get("result");
                        results.add(parseResultItem(rp));
                        return;
                    }
                    if ("error".equals(eventType)) {
                        String msg = String.valueOf(eventData.getOrDefault("error", ""));
                        errorMessage[0] = msg;
                        errorObj[0] = new CodeExecutionError("ExecutionError", msg, "");
                        if (onError != null) onError.accept(eventData);
                        return;
                    }
                },
                (_invocationId, endData) -> {
                    Object executionError = endData.get("executionError");
                    if (executionError != null && !String.valueOf(executionError).isEmpty() && errorObj[0] == null) {
                        String msg = String.valueOf(executionError);
                        errorMessage[0] = msg;
                        errorObj[0] = new CodeExecutionError("ExecutionError", msg, "");
                    }
                },
                (_invocationId, err) -> {
                    if (onError != null) onError.accept(err);
                }
            ).join();

            Map<String, Object> endData = handle.waitEnd().join();

            CodeExecutionLogs logs = new CodeExecutionLogs();
            logs.getStdout().addAll(stdoutChunks);
            logs.getStderr().addAll(stderrChunks);

            EnhancedCodeExecutionResult result = new EnhancedCodeExecutionResult();
            result.setRequestId(handle.invocationId);
            result.setLogs(logs);
            result.setResults(results);
            result.setError(errorObj[0]);

            Object executionCount = endData.get("executionCount");
            if (executionCount instanceof Number) {
                result.setExecutionCount(((Number) executionCount).intValue());
            }
            Object executionTime = endData.get("executionTime");
            if (executionTime instanceof Number) {
                result.setExecutionTime(((Number) executionTime).doubleValue());
            }

            boolean ok = (errorObj[0] == null) && (endData.get("executionError") == null) && !"failed".equals(String.valueOf(endData.get("status")));
            result.setSuccess(ok);
            result.setErrorMessage(ok ? "" : (errorMessage[0] != null ? errorMessage[0] : "Failed to run code"));
            return result;
        } catch (Exception e) {
            if (onError != null) onError.accept(e);
            return new EnhancedCodeExecutionResult("", false, "Failed to run code: " + e.getMessage());
        }
    }

    /**
     * Parses a single result item from a streaming event payload into a CodeResult.
     *
     * @param payload The result payload, either a Map with MIME-typed fields or a plain value.
     * @return CodeResult containing the parsed result data.
     */
    private CodeResult parseResultItem(Object payload) {
        CodeResult item = new CodeResult();
        if (!(payload instanceof Map)) {
            item.setText(String.valueOf(payload));
            return item;
        }
        Map<?, ?> m = (Map<?, ?>) payload;

        Object isMain = m.get("isMainResult");
        if (isMain instanceof Boolean && (Boolean) isMain) {
            item.setMainResult(true);
        }
        Object isMain2 = m.get("is_main_result");
        if (isMain2 instanceof Boolean && (Boolean) isMain2) {
            item.setMainResult(true);
        }

        Object text = m.get("text/plain");
        if (text != null) item.setText(String.valueOf(text));
        Object html = m.get("text/html");
        if (html != null) item.setHtml(String.valueOf(html));
        Object markdown = m.get("text/markdown");
        if (markdown != null) item.setMarkdown(String.valueOf(markdown));
        Object png = m.get("image/png");
        if (png != null) item.setPng(String.valueOf(png));
        Object jpeg = m.get("image/jpeg");
        if (jpeg != null) item.setJpeg(String.valueOf(jpeg));
        Object svg = m.get("image/svg+xml");
        if (svg != null) item.setSvg(String.valueOf(svg));
        Object latex = m.get("text/latex");
        if (latex != null) item.setLatex(String.valueOf(latex));

        Object jsonObj = m.get("application/json");
        if (jsonObj != null) item.setJson(jsonObj);

        Object chart = m.get("application/vnd.vegalite.v4+json");
        if (chart == null) chart = m.get("application/vnd.vegalite.v5+json");
        if (chart != null) item.setChart(chart);

        if (item.getText() == null && m.get("text") != null) {
            item.setText(String.valueOf(m.get("text")));
        }
        return item;
    }

    /**
     * Alias of runCode with a default timeout of 60 seconds.
     *
     * @param code The code to execute.
     * @param language The programming language of the code.
     * @return EnhancedCodeExecutionResult containing success status and execution result.
     */
    public EnhancedCodeExecutionResult execute(String code, String language) {
        return runCode(code, language, 60);
    }

    /**
     * Alias of runCode with Python as the default language
     * and a default timeout of 60 seconds.
     *
     * @param code The Python code to execute.
     * @return EnhancedCodeExecutionResult containing success status and execution result.
     */
    public EnhancedCodeExecutionResult execute(String code) {
        return execute(code, "python");
    }

    /**
     * Alias of runCode with a default timeout of 60 seconds.
     *
     * @param code The code to execute.
     * @param language The programming language of the code.
     * @return EnhancedCodeExecutionResult containing success status and execution result.
     */
    public EnhancedCodeExecutionResult runCode(String code, String language) {
        return runCode(code, language, 60);
    }

    /**
     * Alias of runCode for better ergonomics and LLM friendliness.
     *
     * @param code The code to execute.
     * @param language The programming language of the code.
     * @param timeoutS The timeout for the code execution in seconds.
     * @return EnhancedCodeExecutionResult containing success status and execution result.
     */
    public EnhancedCodeExecutionResult run(String code, String language, int timeoutS) {
        return runCode(code, language, timeoutS);
    }

    /**
     * Alias of runCode with a default timeout of 60 seconds,
     * for better ergonomics and LLM friendliness.
     *
     * @param code The code to execute.
     * @param language The programming language of the code.
     * @return EnhancedCodeExecutionResult containing success status and execution result.
     */
    public EnhancedCodeExecutionResult run(String code, String language) {
        return runCode(code, language, 60);
    }
}
