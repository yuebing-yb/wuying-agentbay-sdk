package com.aliyun.agentbay.agent;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.browser.BrowserOption;
import com.aliyun.agentbay.model.ExecutionResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.QueryResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.module.jsonSchema.JsonSchema;
import com.fasterxml.jackson.module.jsonSchema.JsonSchemaGenerator;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

/**
 * An Agent to manipulate applications to complete specific tasks.
 * 
 * <p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
 * we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>
 */
public class Agent extends BaseService {
    private static final Gson gson = new Gson();
    private static final String SERVER_MOBILE_AGENT = "wuying_mobile_agent";
    private static final String SERVER_BROWSER_USE = "wuying_browseruse";
    private static final String SERVER_COMPUTER_AGENT = "wuying_computer_agent";

    private final Computer computer;
    private final Browser browser;
    private final Mobile mobile;

    public Agent(Session session) {
        super(session);
        this.computer = new Computer(session);
        this.browser = new Browser(session);
        this.mobile = new Mobile(session);
    }

    /**
     * Get the Computer agent for desktop task execution.
     *
     * @return Computer agent instance
     */
    public Computer getComputer() {
        return computer;
    }

    /**
     * Get the Browser agent for browser task execution.
     *
     * @return Browser agent instance
     */
    public Browser getBrowser() {
        return browser;
    }

    /**
     * Get the Mobile agent for mobile device task execution.
     *
     * @return Mobile agent instance
     */
    public Mobile getMobile() {
        return mobile;
    }

    public static class SchemaHelper {
        private static final Logger logger = LoggerFactory.getLogger(SchemaHelper.class);
        private static final ObjectMapper mapper = new ObjectMapper();
        private static final JsonSchemaGenerator schemaGenerator = new JsonSchemaGenerator(mapper);

        // Default output schema
        public static class DefaultSchema {
          @JsonProperty(value = "result", required = true)
          private String result;

          public String getResult() { return result; }

          public void setResult(String result) { this.result = result; }
        }

        // 产生一个标准的JsonSchema
        public static String generateJsonSchema(Class<?> schemaClass) {
          if (schemaClass == null) {
            schemaClass = DefaultSchema.class;
          }
          try {
            JsonSchema jsonSchema = schemaGenerator.generateSchema(schemaClass);
            String schemaStr = mapper.writeValueAsString(jsonSchema);
            // 去掉 id 字段并调整 required 字段位置
            JsonNode schemaNode = mapper.readTree(schemaStr);
            if (schemaNode instanceof ObjectNode) {
              ObjectNode rootNode = (ObjectNode)schemaNode;
              // 移除 id 字段
              rootNode.remove("id");

              // 处理 properties，提取 required 字段，组成一个标准的json schema
              JsonNode propertiesNode = rootNode.get("properties");
              if (propertiesNode != null && propertiesNode.isObject()) {
                List<String> requiredFields = new ArrayList<>();
                ObjectNode properties = (ObjectNode)propertiesNode;

                // 遍历所有属性，收集 required 字段
                properties.fields().forEachRemaining(entry -> {
                  String fieldName = entry.getKey();
                  JsonNode fieldNode = entry.getValue();

                  if (fieldNode.isObject()) {
                    ObjectNode fieldObject = (ObjectNode)fieldNode;
                    JsonNode requiredNode = fieldObject.get("required");

                    // 如果该字段标记为 required，添加到列表并从字段中移除
                    if (requiredNode != null && requiredNode.asBoolean()) {
                      requiredFields.add(fieldName);
                      fieldObject.remove("required");
                    }
                  }
                });

                // 在根级别添加 required 数组, 让其变成一个标准的JsonSchema
                if (!requiredFields.isEmpty()) {
                  rootNode.set("required", mapper.valueToTree(requiredFields));
                }
              }
            }

            return mapper.writeValueAsString(schemaNode);
          } catch (Exception e) {
            logger.error("Failed to generate JSON schema: {}", e.getMessage());
            return "schema: null";
          }
        }
    }

    /**
     * Resolves the WebSocket target for the given execute tool name.
     * browser_use -> wuying_browseruse, flux -> wuying_computer_agent, empty -> wuying_mobile_agent.
     */
    private static String resolveAgentTarget(Session session, String executeToolName, String defaultTarget) {
        try {
            String server = session.getMcpServerForTool(executeToolName);
            if (server != null && !server.isEmpty()) {
                return server;
            }
        } catch (Exception e) {
            // fall through to default
        }
        return defaultTarget;
    }

    /**
     * Execute a task via WebSocket streaming channel.
     * Used by Computer, Browser, and Mobile when StreamOptions indicates streaming.
     */
    @SuppressWarnings("unchecked")
    private static ExecutionResult executeTaskStreamWs(
            Session session,
            String executeToolName,
            String defaultTarget,
            Map<String, Object> taskParams,
            int timeout,
            StreamOptions options) {
        Logger streamLogger = LoggerFactory.getLogger(Agent.class);
        try {
            String target = resolveAgentTarget(session, executeToolName, defaultTarget);
            WsClient wsClient = session.getWsClient();

            final List<String> finalContentParts = new ArrayList<>();
            final Map<String, Object>[] lastError = new Map[1];

            StreamOptions opts = options != null ? options : new StreamOptions();
            boolean stream = opts.isStreamBeta();

            Map<String, Object> data = new HashMap<>();
            data.put("method", "exec_task");
            data.put("stream", stream);
            data.put("params", taskParams);

            WsClient.StreamHandle handle = wsClient.callStream(
                    target,
                    data,
                    (_invocationId, eventData) -> {
                        Object eventTypeObj = eventData.get("eventType");
                        String eventType = eventTypeObj != null ? eventTypeObj.toString() : "";
                        Object seqObj = eventData.get("seq");
                        int seq = seqObj instanceof Number ? ((Number) seqObj).intValue() : 0;
                        Object roundObj = eventData.get("round");
                        int round = roundObj instanceof Number ? ((Number) roundObj).intValue() : 0;

                        AgentEvent event = new AgentEvent(eventType, seq, round);

                        if ("reasoning".equals(eventType)) {
                            Object c = eventData.get("content");
                            event.setContent(c != null ? c.toString() : "");
                            dispatchEvent(opts, event, "reasoning");
                        } else if ("content".equals(eventType)) {
                            String contentText = String.valueOf(eventData.getOrDefault("content", ""));
                            finalContentParts.add(contentText);
                            event.setContent(contentText);
                            dispatchEvent(opts, event, "content");
                        } else if ("tool_call".equals(eventType)) {
                            event.setToolCallId(String.valueOf(eventData.getOrDefault("toolCallId", "")));
                            event.setToolName(String.valueOf(eventData.getOrDefault("toolName", "")));
                            Object argsObj = eventData.get("args");
                            event.setArgs(argsObj instanceof Map ? (Map<String, Object>) argsObj : new HashMap<>());
                            dispatchEvent(opts, event, "tool_call");
                        } else if ("tool_result".equals(eventType)) {
                            event.setToolCallId(String.valueOf(eventData.getOrDefault("toolCallId", "")));
                            event.setToolName(String.valueOf(eventData.getOrDefault("toolName", "")));
                            Object resultObj = eventData.get("result");
                            event.setResult(resultObj instanceof Map ? (Map<String, Object>) resultObj : new HashMap<>());
                            dispatchEvent(opts, event, "tool_result");
                        } else if ("error".equals(eventType)) {
                            Object errObj = eventData.get("error");
                            Map<String, Object> errMap = errObj instanceof Map ? (Map<String, Object>) errObj : new HashMap<>();
                            if (errObj != null && !(errObj instanceof Map)) {
                                errMap.put("message", String.valueOf(errObj));
                            }
                            lastError[0] = errMap;
                            event.setError(errMap);
                            dispatchEvent(opts, event, "error");
                        }
                    },
                    (_invocationId, endData) -> { /* onEnd - data captured in waitEnd */ },
                    (_invocationId, err) -> streamLogger.warn("WS stream error: {}", err.getMessage())
            ).join();

            Map<String, Object> endData;
            try {
                endData = handle.waitEnd().get(timeout, TimeUnit.SECONDS);
            } catch (TimeoutException e) {
                try {
                    handle.cancel();
                } catch (Exception ignored) {
                }
                String accumulated = String.join("", finalContentParts);
                return new ExecutionResult(
                        "",
                        false,
                        "Task execution timed out after " + timeout + " seconds.",
                        "",
                        "failed",
                        accumulated.isEmpty() ? "Task execution timed out." : accumulated
                );
            }

            if (lastError[0] != null) {
                String errMsg = String.valueOf(lastError[0].getOrDefault("message", lastError[0]));
                return new ExecutionResult(
                        "",
                        false,
                        errMsg,
                        "",
                        "failed",
                        String.join("", finalContentParts)
                );
            }

            String status = endData != null ? String.valueOf(endData.getOrDefault("status", "finished")) : "finished";
            Object taskResultObj = endData != null ? endData.get("taskResult") : null;
            String taskResult = taskResultObj != null ? taskResultObj.toString() : "";
            if (taskResult.isEmpty()) {
                taskResult = String.join("", finalContentParts);
            }

            return new ExecutionResult(
                    "",
                    "finished".equals(status),
                    "finished".equals(status) ? "" : "Task ended with status: " + status,
                    "",
                    status,
                    taskResult
            );
        } catch (Exception e) {
            return new ExecutionResult(
                    "",
                    false,
                    "Failed to execute: " + e.getMessage(),
                    "",
                    "failed",
                    "Task Failed"
            );
        }
    }

    private static void dispatchEvent(StreamOptions opts, AgentEvent event, String type) {
        try {
            if (opts.getOnEvent() != null) {
                opts.getOnEvent().accept(event);
            }
        } catch (Exception ex) {
            LoggerFactory.getLogger(Agent.class).warn("onEvent callback error: {}", ex.getMessage());
        }
        try {
            java.util.function.Consumer<AgentEvent> cb = null;
            switch (type) {
                case "reasoning": cb = opts.getOnReasoning(); break;
                case "content": cb = opts.getOnContent(); break;
                case "tool_call": cb = opts.getOnToolCall(); break;
                case "tool_result": cb = opts.getOnToolResult(); break;
                default: break;
            }
            if (cb != null) {
                cb.accept(event);
            }
        } catch (Exception ex) {
            LoggerFactory.getLogger(Agent.class).warn("on{} callback error: {}", type, ex.getMessage());
        }
    }

    /**
     * An Agent to perform tasks on the computer.
     * 
     * <p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
     * we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>
     */
    public static class Computer extends BaseService {
        private static final Logger logger = LoggerFactory.getLogger(Computer.class);

        public Computer(Session session) {
            super(session);
        }

        /**
         * Execute a task in human language without waiting for completion (non-blocking).
         *
         * This is a fire-and-return interface that immediately provides a task ID.
         * Call getTaskStatus to check the task status. You can control the timeout
         * of the task execution in your own code by setting the frequency of calling
         * getTaskStatus.
         *
         * @param task Task description in human language
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult executeTask(String task) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);

                OperationResult result = callMcpTool("flux_execute_task", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    String taskId = content.has("task_id") ? content.get("task_id").getAsString() : "";

                    return new ExecutionResult(
                        result.getRequestId(),
                        true,
                        "",
                        taskId,
                        "running"
                    );
                } else {
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute task",
                        "",
                        "failed"
                    );
                }
            } catch (Exception e) {
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to execute: " + e.getMessage(),
                    "",
                    "failed"
                );
            }
        }

        /**
         * Execute a specific task described in human language synchronously.
         *
         * This is a synchronous interface that blocks until the task is completed or
         * an error occurs, or timeout happens. The default polling interval is 3 seconds.
         *
         * @param task Task description in human language
         * @param timeout Maximum time to wait for task completion in seconds
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         *
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);

                OperationResult result = callMcpTool("flux_execute_task", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    String taskId = content.has("task_id") ? content.get("task_id").getAsString() : "";

                    int pollInterval = 3;
                    int maxPollAttempts = timeout / pollInterval;
                    int triedTime = 0;
                    while (triedTime < maxPollAttempts) {
                        QueryResult query = getTaskStatus(taskId);

                        if ("finished".equals(query.getTaskStatus())) {
                            return new ExecutionResult(
                                result.getRequestId(),
                                true,
                                "",
                                taskId,
                                query.getTaskStatus(),
                                query.getTaskProduct()
                            );
                        } else if ("failed".equals(query.getTaskStatus())) {
                            String errorMsg = query.getErrorMessage();
                            if (errorMsg == null || errorMsg.isEmpty()) {
                                errorMsg = "Failed to execute task.";
                            }
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                errorMsg,
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        } else if ("unsupported".equals(query.getTaskStatus())) {
                            String errorMsg = query.getErrorMessage();
                            if (errorMsg == null || errorMsg.isEmpty()) {
                                errorMsg = "Unsupported task.";
                            }
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                errorMsg,
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        }
                        Thread.sleep(3000);
                        triedTime++;
                    }
                    try {
                        ExecutionResult terminateResult = terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            logger.info("✅ Terminate request sent for task {} after timeout", taskId);
                        } else {
                            logger.warn("⚠️ Failed to terminate task {} after timeout: {}", taskId, terminateResult.getErrorMessage());
                        }
                    } catch (Exception e) {
                        logger.warn("⚠️ Exception while terminating task {} after timeout: {}", taskId, e.getMessage());
                    }

                    logger.info("⏳ Waiting for task {} to be fully terminated...", taskId);
                    int terminatePollInterval = 1;
                    int maxTerminatePollAttempts = 30;
                    int terminateTriedTime = 0;
                    boolean taskTerminatedConfirmed = false;

                    while (terminateTriedTime < maxTerminatePollAttempts) {
                        try {
                            QueryResult statusQuery = getTaskStatus(taskId);
                            if (!statusQuery.isSuccess()) {
                                String errorMsg = statusQuery.getErrorMessage() != null ? statusQuery.getErrorMessage() : "";
                                if (errorMsg.startsWith("Task not found or already finished")) {
                                    logger.info("✅ Task {} confirmed terminated (not found or finished)", taskId);
                                    taskTerminatedConfirmed = true;
                                    break;
                                }
                            }
                            Thread.sleep(terminatePollInterval * 1000);
                            terminateTriedTime++;
                        } catch (Exception e) {
                            logger.warn("⚠️ Exception while polling task status during termination: {}", e.getMessage());
                            try {
                                Thread.sleep(terminatePollInterval * 1000);
                            } catch (InterruptedException ie) {
                                Thread.currentThread().interrupt();
                            }
                            terminateTriedTime++;
                        }
                    }

                    if (!taskTerminatedConfirmed) {
                        logger.warn("⚠️ Timeout waiting for task {} to be fully terminated", taskId);
                    }

                    String timeoutErrorMsg = String.format("Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).", timeout, taskId, triedTime, maxPollAttempts);
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        timeoutErrorMsg,
                        taskId,
                        "failed",
                        String.format("Task execution timed out after %d seconds.", timeout)
                    );
                } else {
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute task",
                        "",
                        "failed",
                        "Task Failed"
                    );
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new ExecutionResult(
                    "",
                    false,
                    "Task interrupted: " + e.getMessage(),
                    "",
                    "failed",
                    "Task Failed"
                );
            } catch (Exception e) {
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to execute: " + e.getMessage(),
                    "",
                    "failed",
                    "Task Failed"
                );
            }
        }

        /**
         * Execute a task synchronously with optional WebSocket streaming.
         * When {@code options} is non-null and has streaming params, uses WS streaming for real-time events.
         *
         * @param task Task description in human language
         * @param timeout Maximum time to wait for task completion in seconds
         * @param options StreamOptions for streaming (null to use HTTP polling)
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout, StreamOptions options) {
            if (options != null && options.hasStreamingParams()) {
                Map<String, Object> params = new HashMap<>();
                params.put("task", task);
                return executeTaskStreamWs(session, "flux_execute_task", SERVER_COMPUTER_AGENT, params, timeout, options);
            }
            return executeTaskAndWait(task, timeout);
        }

        /**
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, and error message if any
         *
         */
        public QueryResult getTaskStatus(String taskId) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool("flux_get_task_status", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);

                    return new QueryResult(
                        result.getRequestId(),
                        true,
                        "",
                        content.has("task_id") ? content.get("task_id").getAsString() : taskId,
                        content.has("status") ? content.get("status").getAsString() : "finished",
                        content.has("action") ? content.get("action").getAsString() : "",
                        content.has("product") ? content.get("product").getAsString() : ""
                    );
                } else {
                    return new QueryResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to get task status",
                        taskId,
                        "failed"
                    );
                }
            } catch (Exception e) {
                return new QueryResult(
                    "",
                    false,
                    "Failed to get task status: " + e.getMessage(),
                    taskId,
                    "failed"
                );
            }
        }

        /**
         * Terminate a task with a specified task ID.
         *
         * @param taskId The ID of the running task to terminate
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult terminateTask(String taskId) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool("flux_terminate_task", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    String returnedTaskId = content.has("task_id") ? content.get("task_id").getAsString() : taskId;

                    return new ExecutionResult(
                            result.getRequestId(),
                            true,
                            "",
                            returnedTaskId,
                            content.has("status") ? content.get("status").getAsString() : "finished");
                } else {
                    return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to terminate task",
                            taskId,
                            "failed");
                }
            } catch (Exception e) {
                return new ExecutionResult(
                        "",
                        false,
                        "Failed to terminate: " + e.getMessage(),
                        taskId,
                        "failed");
            }
        }
    }

    /**
     * Browser agent for browser automation with natural language.
     * 
     * <p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
     * we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>
     */
    public static class Browser extends BaseService {
        private static final Logger logger = LoggerFactory.getLogger(Browser.class);
        private boolean initialized = false;

        public Browser(Session session) {
            super(session);
        }

        /**
         * Initialize the browser on which the agent performs tasks.
         * You are supposed to call this API before executeTask is called, but it's not optional.
         * If you want perform a hybrid usage of browser, you must call this API before executeTask is called.
         *
         * @param option the browser initialization options. If {@code null}, default options will be used
         * @return {@code true} if the browser is successfully initialized, {@code false} otherwise
         */
        public boolean initialize(BrowserOption option) {

            if (this.initialized) {
                return true;
            }

            if (option == null) {
                option = new BrowserOption();
            }
            boolean success = session.getBrowser().initialize(option);
            this.initialized = success;
            return success;
        }

        /**
         * Execute a task described in human language on a browser without waiting for completion (non-blocking).
         *
         * This is a fire-and-return interface that immediately provides a task ID.
         * Call get_task_status to check the task status. You can control the timeout
         * of the task execution in your own code by setting the frequency of calling
         * get_task_status.
         *
         * @param task Task description in human language
         * @param useVision Whether to use vision to performe the task
         * @param outputSchema The schema of the structured output
         * @param fullPageScreenShot Whether to take a full page screenshot. This only works when use_vision is true.
         *                           When use_vision is enabled, we need to provide a screenshot of the webpage to the LLM for grounding. There are two ways of screenshot:
         *                           1. Full-page screenshot: Captures the entire webpage content, including parts not currently visible in the viewport.
         *                           2. Viewport screenshot: Captures only the currently visible portion of the webpage.
         *                           The first approach delivers all information to the LLM in one go, which can improve task success rates in certain information extraction scenarios. However, it also results in higher token consumption and increases the LLM's processing time.
         *                           Therefore, we would like to give you the choice—you can decide whether to enable full-page screenshot based on your actual needs.
         * @return ExecutionResult Result object containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult executeTask(String task, boolean useVision,
                Object outputSchema, boolean fullPageScreenShot) {
            if (!this.initialized) {
                logger.info("Browser is not initialized. Initialize browser first.");
                boolean success = initialize(new BrowserOption());
                if (!success) {
                    return new ExecutionResult("", false,
                            "Browser initialization failed.",
                            "", "failed");
                }
            }
            try {
                String schemaJson = "";
                if (outputSchema instanceof String) {
                    System.out.println("-------String schemaJson: " + outputSchema);
                    schemaJson = (String) outputSchema;
                } else if (outputSchema instanceof Class) {
                    schemaJson = SchemaHelper.generateJsonSchema((Class<?>) outputSchema);
                    System.out.println("-------Class schemaJson: " + schemaJson);
                }
                logger.info("Output schema: {}", schemaJson);

                Map<String, Object> args = new HashMap<>();
                args.put("task", task);
                args.put("use_vision", useVision);
                args.put("output_schema", schemaJson);
                args.put("full_page_screenshot", fullPageScreenShot);
                OperationResult result = callMcpTool("browser_use_execute_task", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    String taskId = content.has("task_id")
                            ? content.get("task_id").getAsString()
                            : "";

                    return new ExecutionResult(result.getRequestId(), true, "",
                            taskId, "running");
                } else {
                    return new ExecutionResult(result.getRequestId(), false,
                            result.getErrorMessage() != null
                                    ? result.getErrorMessage()
                                    : "Failed to execute task",
                            "", "failed");
                }
            } catch (Exception e) {
                return new ExecutionResult("", false,
                        "Failed to execute: " + e.getMessage(),
                        "", "failed");
            }
        }

        /**
         * Execute a specific task described in human language synchronously.
         *
         * This is a synchronous interface that blocks until the task is completed or
         * an error occurs, or timeout happens. The default polling interval is 3
         * seconds.
         *
         * @param task               Task description in human language
         * @param timeout            Maximum time to wait for task completion in seconds
         * @param useVision          Whether to use vision in the task
         * @param outputSchema       Optional Zod schema for a structured task output if
         *                           you need
         * @param fullPageScreenShot Whether to take a full page screenshot,
         *                           this only works if useVision is true
         * 
         *                           When use_vision is enabled, we need to provide a
         *                           screenshot of the webpage to the LLM for grounding.
         *                           There are two ways of screenshot:
         *                           1. Full-page screenshot: Captures the entire
         *                           webpage content, including parts not currently
         *                           visible in the viewport.
         *                           2. Viewport screenshot: Captures only the currently
         *                           visible portion of the webpage.
         *                           The first approach delivers all information to the
         *                           LLM in one go, which can improve task success rates
         *                           in certain information extraction scenarios.
         *                           However, it also results in higher token
         *                           consumption and increases the LLM's processing
         *                           time.
         *                           Therefore, we would like to give you the choice—you
         *                           can decide whether to enable full-page screenshot
         *                           based on your actual needs.
         * @return ExecutionResult containing success status, task ID, task status, task
         *         result, and error message if any
         *
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout,
                boolean useVision,
                Object outputSchema, boolean fullPageScreenShot) {
            if (!this.initialized) {
                logger.info("Browser is not initialized. Initialize browser first.");
                boolean success = initialize(new BrowserOption());
                if (!success) {
                    return new ExecutionResult("", false,
                            "Browser initialization failed.",
                            "", "failed");
                }
            }
            try {
                ExecutionResult result = executeTask(task, useVision, outputSchema, fullPageScreenShot);
                if (result.isSuccess()) {
                    String taskId = result.getTaskId();
                    int pollInterval = 3;
                    int maxPollAttempts = timeout / pollInterval;
                    int triedTime = 0;
                    while (triedTime < maxPollAttempts) {
                        QueryResult query = getTaskStatus(taskId);

                        if ("finished".equals(query.getTaskStatus())) {
                            return new ExecutionResult(result.getRequestId(), true, "",
                                    taskId, query.getTaskStatus(),
                                    query.getTaskProduct());
                        } else if ("failed".equals(query.getTaskStatus())) {
                            String errorMsg = query.getErrorMessage();
                            if (errorMsg == null || errorMsg.isEmpty()) {
                                errorMsg = "Failed to execute task.";
                            }
                            return new ExecutionResult(result.getRequestId(), false,
                                    errorMsg, taskId,
                                    query.getTaskStatus(), "");
                        } else if ("unsupported".equals(query.getTaskStatus())) {
                            String errorMsg = query.getErrorMessage();
                            if (errorMsg == null || errorMsg.isEmpty()) {
                                errorMsg = "Unsupported task.";
                            }
                            return new ExecutionResult(result.getRequestId(), false,
                                    errorMsg, taskId,
                                    query.getTaskStatus(), "");
                        }
                        Thread.sleep(3000);
                        triedTime++;
                    }
                    // Automatically terminate the task on timeout
                    try {
                        ExecutionResult terminateResult = terminateTask(taskId);
                        if (terminateResult.isSuccess()) {
                            logger.info("✅ Task {} terminated successfully after timeout",
                                    taskId);
                        } else {
                            logger.warn(
                                    "⚠️ Failed to terminate task {} after timeout: {}",
                                    taskId, terminateResult.getErrorMessage());
                        }
                    } catch (Exception e) {
                        logger.warn(
                                "⚠️ Exception while terminating task {} after timeout: {}",
                                taskId, e.getMessage());
                    }
                    String timeoutErrorMsg = String.format(
                            "Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).",
                            timeout, taskId, triedTime, maxPollAttempts);
                    return new ExecutionResult(
                            result.getRequestId(), false, timeoutErrorMsg, taskId,
                            "failed",
                            String.format("Task execution timed out after %d seconds.",
                                    timeout));
                } else {
                    return result;
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new ExecutionResult("", false,
                        "Task interrupted: " + e.getMessage(),
                        "", "failed", "Task Failed");
            } catch (Exception e) {
                return new ExecutionResult("", false,
                        "Failed to execute: " + e.getMessage(),
                        "", "failed", "Task Failed");
            }
        }

        /**
         * Execute a task synchronously with optional WebSocket streaming.
         * When {@code options} is non-null and has streaming params, uses WS streaming for real-time events.
         *
         * @param task Task description in human language
         * @param timeout Maximum time to wait for task completion in seconds
         * @param useVision Whether to use vision in the task
         * @param outputSchema Optional schema for structured task output
         * @param fullPageScreenShot Whether to take a full page screenshot (when useVision is true)
         * @param options StreamOptions for streaming (null to use HTTP polling)
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout,
                boolean useVision,
                Object outputSchema, boolean fullPageScreenShot,
                StreamOptions options) {
            if (!this.initialized) {
                logger.info("Browser is not initialized. Initialize browser first.");
                boolean success = initialize(new BrowserOption());
                if (!success) {
                    return new ExecutionResult("", false,
                            "Browser initialization failed.",
                            "", "failed");
                }
            }
            if (options != null && options.hasStreamingParams()) {
                String schemaJson = "";
                if (outputSchema instanceof String) {
                    schemaJson = (String) outputSchema;
                } else if (outputSchema instanceof Class) {
                    schemaJson = SchemaHelper.generateJsonSchema((Class<?>) outputSchema);
                }
                Map<String, Object> params = new HashMap<>();
                params.put("task", task);
                params.put("use_vision", useVision);
                params.put("output_schema", schemaJson);
                params.put("full_page_screenshot", fullPageScreenShot);
                return executeTaskStreamWs(session, "browser_use_execute_task", SERVER_BROWSER_USE, params, timeout, options);
            }
            return executeTaskAndWait(task, timeout, useVision, outputSchema, fullPageScreenShot);
        }

        /**
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, and error message if any
         *
         */
        public QueryResult getTaskStatus(String taskId) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool("browser_use_get_task_status", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);

                    return new QueryResult(
                        result.getRequestId(),
                        true,
                        "",
                        content.has("task_id") ? content.get("task_id").getAsString() : taskId,
                        content.has("status") ? content.get("status").getAsString() : "finished",
                        content.has("action") ? content.get("action").getAsString() : "",
                        content.has("product") ? content.get("product").getAsString() : ""
                    );
                } else {
                    return new QueryResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to get task status",
                        taskId,
                        "failed"
                    );
                }
            } catch (Exception e) {
                return new QueryResult(
                    "",
                    false,
                    "Failed to get task status: " + e.getMessage(),
                    taskId,
                    "failed"
                );
            }
        }

        /**
         * Terminate a task with a specified task ID.
         *
         * @param taskId The ID of the running task to terminate
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult terminateTask(String taskId) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool("browser_use_terminate_task", args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    String returnedTaskId = content.has("task_id") ? content.get("task_id").getAsString() : taskId;

                    return new ExecutionResult(
                        result.getRequestId(),
                        true,
                        "",
                        returnedTaskId,
                        content.has("status") ? content.get("status").getAsString() : "finished"
                    );
                } else {
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to terminate task",
                        taskId,
                        "failed"
                    );
                }
            } catch (Exception e) {
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to terminate: " + e.getMessage(),
                    taskId,
                    "failed"
                );
            }
        }
    }

    /**
     * Mobile agent for mobile device automation with natural language.
     * Uses execute_task, get_task_status, terminate_task MCP tools for task execution.
     */
    public static class Mobile extends BaseService {
        private static final Logger logger = LoggerFactory.getLogger(Mobile.class);

        public Mobile(Session session) {
            super(session);
        }

        /**
         * Get the MCP tool name for mobile agent operations.
         *
         * @param action The action name (execute, get_status, terminate)
         * @return The full MCP tool name
         */
        private String getToolName(String action) {
            switch (action) {
                case "execute":
                    return "execute_task";
                case "get_status":
                    return "get_task_status";
                case "terminate":
                    return "terminate_task";
                default:
                    return action;
            }
        }

        /**
         * Execute a mobile task in human language without waiting for completion (non-blocking).
         *
         * This is a fire-and-return interface that immediately provides a task ID.
         * Call getTaskStatus to check the task status. You can control the timeout
         * of the task execution in your own code by setting the frequency of calling
         * getTaskStatus.
         *
         * @param task Task description in human language
         * @param maxSteps Maximum number of steps (clicks/swipes/etc.) allowed
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult executeTask(String task, int maxSteps) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);
                args.put("max_steps", maxSteps);

                OperationResult result = callMcpTool(getToolName("execute"), args);

                if (result.isSuccess()) {
                    try {
                        JsonObject content = gson.fromJson(result.getData(), JsonObject.class);

                        // Check for embedded error in JSON content
                        if (content.has("error")) {
                            String errorMsg = content.get("error").getAsString();
                            logger.error("Task execution failed with embedded error: {}", errorMsg);
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                errorMsg,
                                "",
                                "failed"
                            );
                        }

                        // Support both taskId (camelCase) and task_id (snake_case)
                        String taskId = "";
                        if (content.has("taskId")) {
                            taskId = content.get("taskId").getAsString();
                        } else if (content.has("task_id")) {
                            taskId = content.get("task_id").getAsString();
                        }

                        // Check if taskId is empty
                        if (taskId == null || taskId.isEmpty()) {
                            // 从后端返回的content中提取error信息
                            String errorMsg = "Failed to get task_id from response";
                            if (content.has("error")) {
                                errorMsg = content.get("error").getAsString();
                            }
                            logger.error("Failed to get task_id from response: {}", errorMsg);
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                errorMsg,
                                "",
                                "failed"
                            );
                        }

                        return new ExecutionResult(
                            result.getRequestId(),
                            true,
                            "",
                            taskId,
                            "running"
                        );
                    } catch (Exception e) {
                        logger.error("Failed to parse response", e);
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            "Failed to parse response: " + e.getMessage(),
                            "",
                            "failed"
                        );
                    }
                } else {
                    logger.error("Task execute failed");
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute task",
                        "",
                        "failed"
                    );
                }
            } catch (Exception e) {
                logger.error("Failed to execute task", e);
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to execute: " + e.getMessage(),
                    "",
                    "failed"
                );
            }
        }

        /**
         * Execute a specific mobile task described in human language synchronously.
         *
         * This is a synchronous interface that blocks until the task is completed or
         * an error occurs, or timeout happens. The default polling interval is 3 seconds.
         *
         * @param task Task description in human language
         * @param maxSteps Maximum number of steps (clicks/swipes/etc.) allowed
         * @param timeout Maximum time to wait for task completion in seconds
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         *
         */
        public ExecutionResult executeTaskAndWait(String task, int maxSteps, int timeout) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);
                args.put("max_steps", maxSteps);

                OperationResult result = callMcpTool(getToolName("execute"), args);

                if (!result.isSuccess()) {
                    logger.error("❌ Task execution failed");
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute task",
                        "",
                        "failed",
                        "Task Failed"
                    );
                }

                JsonObject content = gson.fromJson(result.getData(), JsonObject.class);

                // Check for embedded error in JSON content
                if (content.has("error")) {
                    String errorMsg = content.get("error").getAsString();
                    logger.error("Task execution failed with embedded error: {}", errorMsg);
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        errorMsg,
                        "",
                        "failed",
                        "Task Failed"
                    );
                }

                // Support both taskId (camelCase) and task_id (snake_case)
                String taskId = "";
                if (content.has("taskId")) {
                    taskId = content.get("taskId").getAsString();
                } else if (content.has("task_id")) {
                    taskId = content.get("task_id").getAsString();
                }

                if (taskId == null || taskId.isEmpty()) {
                    // 从后端返回的content中提取error信息
                    String errorMsg = "Failed to get task_id from response";
                    if (content.has("error")) {
                        errorMsg = content.get("error").getAsString();
                    }
                    logger.error("Failed to get task_id from response: {}", errorMsg);
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        errorMsg,
                        "",
                        "failed",
                        "Task Failed"
                    );
                }

                int pollInterval = 3;
                int maxPollAttempts = timeout / pollInterval;
                int triedTime = 0;
                java.util.Set<Long> processedTimestamps = new java.util.HashSet<>();
                QueryResult lastQuery = null;

                while (triedTime < maxPollAttempts) {
                    QueryResult query = getTaskStatus(taskId);

                    // Only update lastQuery if stream is not empty
                    if (query.getStream() != null && !query.getStream().isEmpty()) {
                        lastQuery = query;
                    }

                    // Process new stream fragments for real-time output
                    if (query.getStream() != null && !query.getStream().isEmpty()) {
                        for (Map<String, Object> streamItem : query.getStream()) {
                            Object timestampObj = streamItem.get("timestamp_ms");
                            if (timestampObj != null) {
                                long timestamp;
                                if (timestampObj instanceof Number) {
                                    timestamp = ((Number) timestampObj).longValue();
                                } else {
                                    try {
                                        timestamp = Long.parseLong(timestampObj.toString());
                                    } catch (NumberFormatException e) {
                                        continue;
                                    }
                                }
                                // Use timestamp_ms to identify new fragments
                                if (!processedTimestamps.contains(timestamp)) {
                                    processedTimestamps.add(timestamp);

                                    // Output immediately for true streaming effect
                                    Object contentObj = streamItem.get("content");
                                    if (contentObj != null) {
                                        System.out.print(contentObj.toString());
                                        System.out.flush();
                                    }
                                    Object reasoningObj = streamItem.get("reasoning");
                                    if (reasoningObj != null) {
                                        logger.debug("💭 {}", reasoningObj);
                                    }
                                }
                            }
                        }
                    }

                    // Check for error field
                    if (query.getError() != null && !query.getError().isEmpty()) {
                        logger.warn("⚠️ Task error: {}", query.getError());
                    }

                    String taskStatus = query.getTaskStatus();
                    if ("completed".equals(taskStatus)) {
                        return new ExecutionResult(
                            result.getRequestId(),
                            true,
                            "",
                            taskId,
                            query.getTaskStatus(),
                            query.getTaskProduct()
                        );
                    } else if ("failed".equals(taskStatus)) {
                        String errorMsg = query.getError();
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = query.getErrorMessage();
                        }
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = "Failed to execute task.";
                        }
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("cancelled".equals(taskStatus)) {
                        String errorMsg = query.getError();
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = query.getErrorMessage();
                        }
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = "Task was cancelled.";
                        }
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("unsupported".equals(taskStatus)) {
                        String errorMsg = query.getError();
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = query.getErrorMessage();
                        }
                        if (errorMsg == null || errorMsg.isEmpty()) {
                            errorMsg = "Unsupported task.";
                        }
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    }

                    logger.info("⏳ Task {} running 🚀: {}.", taskId, query.getTaskAction());

                    Thread.sleep(pollInterval * 1000);
                    triedTime++;
                }

                logger.warn("⚠️ task execution timeout!");
                try {
                    ExecutionResult terminateResult = terminateTask(taskId);
                    if (terminateResult.isSuccess()) {
                        logger.info("✅ Terminate request sent for task {} after timeout", taskId);
                    } else {
                        logger.warn("⚠️ Failed to terminate task {} after timeout: {}", taskId, terminateResult.getErrorMessage());
                    }
                } catch (Exception e) {
                    logger.warn("⚠️ Exception while terminating task {} after timeout: {}", taskId, e.getMessage());
                }

                logger.info("⏳ Waiting for task {} to be fully terminated...", taskId);
                int terminatePollInterval = 1;
                int maxTerminatePollAttempts = 30;
                int terminateTriedTime = 0;
                boolean taskTerminatedConfirmed = false;

                while (terminateTriedTime < maxTerminatePollAttempts) {
                    try {
                        QueryResult statusQuery = getTaskStatus(taskId);
                        if (!statusQuery.isSuccess()) {
                            String errorMsg = statusQuery.getErrorMessage() != null ? statusQuery.getErrorMessage() : "";
                            if (errorMsg.startsWith("Task not found or already finished")) {
                                logger.info("✅ Task {} confirmed terminated (not found or finished)", taskId);
                                taskTerminatedConfirmed = true;
                                break;
                            }
                        }
                        Thread.sleep(terminatePollInterval * 1000);
                        terminateTriedTime++;
                    } catch (Exception e) {
                        logger.warn("⚠️ Exception while polling task status during termination: {}", e.getMessage());
                        try {
                            Thread.sleep(terminatePollInterval * 1000);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                        }
                        terminateTriedTime++;
                    }
                }

                if (!taskTerminatedConfirmed) {
                    logger.warn("⚠️ Timeout waiting for task {} to be fully terminated", taskId);
                }

                String timeoutErrorMsg = String.format("Task execution timed out after %d seconds. Task ID: %s. Polled %d times (max: %d).", timeout, taskId, triedTime, maxPollAttempts);
                
                // Build task_result with last query status information
                java.util.List<String> taskResultParts = new java.util.ArrayList<>();
                taskResultParts.add(String.format("Task execution timed out after %d seconds.", timeout));
                
                if (lastQuery != null) {
                    // Concatenate stream content from last query
                    if (lastQuery.getStream() != null && !lastQuery.getStream().isEmpty()) {
                        java.util.List<String> streamContentParts = new java.util.ArrayList<>();
                        for (Map<String, Object> streamItem : lastQuery.getStream()) {
                            if (streamItem != null && streamItem.containsKey("content")) {
                                Object contentObj = streamItem.get("content");
                                if (contentObj != null) {
                                    String streamContentItem = contentObj.toString();
                                    if (!streamContentItem.isEmpty()) {
                                        streamContentParts.add(streamContentItem);
                                    }
                                }
                            }
                        }
                        
                        if (!streamContentParts.isEmpty()) {
                            String streamContent = String.join("", streamContentParts);
                            taskResultParts.add("Last task status output: " + streamContent);
                        }
                    }
                    
                    // Also add other status information if available
                    if (lastQuery.getTaskAction() != null && !lastQuery.getTaskAction().isEmpty()) {
                        taskResultParts.add("Last action: " + lastQuery.getTaskAction());
                    }
                    if (lastQuery.getTaskProduct() != null && !lastQuery.getTaskProduct().isEmpty()) {
                        taskResultParts.add("Last result: " + lastQuery.getTaskProduct());
                    }
                    if (lastQuery.getError() != null && !lastQuery.getError().isEmpty()) {
                        taskResultParts.add("Last error: " + lastQuery.getError());
                    }
                    if (lastQuery.getTaskStatus() != null && !lastQuery.getTaskStatus().isEmpty()) {
                        taskResultParts.add("Last status: " + lastQuery.getTaskStatus());
                    }
                }
                
                String taskResult = String.join(" | ", taskResultParts);
                
                return new ExecutionResult(
                    result.getRequestId(),
                    false,
                    timeoutErrorMsg,
                    taskId,
                    "failed",
                    taskResult
                );
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new ExecutionResult(
                    "",
                    false,
                    "Task interrupted: " + e.getMessage(),
                    "",
                    "failed",
                    "Task Failed"
                );
            } catch (Exception e) {
                logger.error("Failed to execute task", e);
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to execute: " + e.getMessage(),
                    "",
                    "failed",
                    "Task Failed"
                );
            }
        }

        /**
         * Execute a task synchronously with optional WebSocket streaming.
         * When {@code options} is non-null and has streaming params, uses WS streaming for real-time events.
         *
         * @param task Task description in human language
         * @param maxSteps Maximum number of steps (clicks/swipes/etc.) allowed
         * @param timeout Maximum time to wait for task completion in seconds
         * @param options StreamOptions for streaming (null to use HTTP polling)
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         */
        public ExecutionResult executeTaskAndWait(String task, int maxSteps, int timeout, StreamOptions options) {
            if (options != null && options.hasStreamingParams()) {
                Map<String, Object> params = new HashMap<>();
                params.put("task", task);
                params.put("max_steps", maxSteps);
                return executeTaskStreamWs(session, getToolName("execute"), SERVER_MOBILE_AGENT, params, timeout, options);
            }
            return executeTaskAndWait(task, maxSteps, timeout);
        }

        /**
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, stream, error, and error message if any
         *
         */
        public QueryResult getTaskStatus(String taskId) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool(getToolName("get_status"), args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);

                    // Support both taskId (camelCase) and task_id (snake_case)
                    String contentTaskId = taskId;
                    if (content.has("taskId")) {
                        contentTaskId = content.get("taskId").getAsString();
                    } else if (content.has("task_id")) {
                        contentTaskId = content.get("task_id").getAsString();
                    }

                    // Prioritize result over product for Mobile Agent
                    String taskProduct = "";
                    if (content.has("result")) {
                        taskProduct = content.get("result").getAsString();
                    } else if (content.has("product")) {
                        taskProduct = content.get("product").getAsString();
                    }

                    // Extract stream array
                    List<Map<String, Object>> stream = new ArrayList<>();
                    if (content.has("stream") && content.get("stream").isJsonArray()) {
                        com.google.gson.JsonArray streamArray = content.get("stream").getAsJsonArray();
                        for (int i = 0; i < streamArray.size(); i++) {
                            JsonObject streamItem = streamArray.get(i).getAsJsonObject();
                            Map<String, Object> streamMap = new HashMap<>();
                            if (streamItem.has("content")) {
                                streamMap.put("content", streamItem.get("content").getAsString());
                            }
                            if (streamItem.has("reasoning")) {
                                streamMap.put("reasoning", streamItem.get("reasoning").getAsString());
                            }
                            if (streamItem.has("timestamp_ms")) {
                                streamMap.put("timestamp_ms", streamItem.get("timestamp_ms").getAsLong());
                            }
                            stream.add(streamMap);
                        }
                    }

                    // Extract error field
                    String error = "";
                    if (content.has("error")) {
                        error = content.get("error").getAsString();
                    }

                    QueryResult queryResult = new QueryResult(
                        result.getRequestId(),
                        true,
                        "",
                        contentTaskId,
                        content.has("status") ? content.get("status").getAsString() : "completed",
                        content.has("action") ? content.get("action").getAsString() : "",
                        taskProduct
                    );
                    queryResult.setStream(stream);
                    queryResult.setError(error);
                    return queryResult;
                } else {
                    return new QueryResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to get task status",
                        taskId,
                        "failed"
                    );
                }
            } catch (Exception e) {
                logger.error("Failed to get task status", e);
                return new QueryResult(
                    "",
                    false,
                    "Failed to get task status: " + e.getMessage(),
                    taskId,
                    "failed"
                );
            }
        }

        /**
         * Terminate a task with a specified task ID.
         *
         * @param taskId The ID of the running task to terminate
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         */
        public ExecutionResult terminateTask(String taskId) {
            logger.info("Terminating task");
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task_id", taskId);

                OperationResult result = callMcpTool(getToolName("terminate"), args);

                if (result.isSuccess()) {
                    JsonObject content = gson.fromJson(result.getData(), JsonObject.class);
                    // Support both taskId (camelCase) and task_id (snake_case)
                    String returnedTaskId = taskId;
                    if (content.has("taskId")) {
                        returnedTaskId = content.get("taskId").getAsString();
                    } else if (content.has("task_id")) {
                        returnedTaskId = content.get("task_id").getAsString();
                    }

                    return new ExecutionResult(
                        result.getRequestId(),
                        true,
                        "",
                        returnedTaskId,
                        content.has("status") ? content.get("status").getAsString() : "cancelling"
                    );
                } else {
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to terminate task",
                        taskId,
                        "failed"
                    );
                }
            } catch (Exception e) {
                logger.error("Failed to terminate task", e);
                return new ExecutionResult(
                    "",
                    false,
                    "Failed to terminate: " + e.getMessage(),
                    taskId,
                    "failed"
                );
            }
        }
    }


}
