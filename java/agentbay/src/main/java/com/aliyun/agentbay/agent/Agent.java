package com.aliyun.agentbay.agent;

import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Agent for natural language driven task execution.
 * Provides high-level task automation capabilities for both computer and browser operations.
 */
public class Agent extends BaseService {
    private static final Gson gson = new Gson();

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

    /**
     * Computer agent for desktop automation with natural language.
     * Uses flux_* MCP tools for task execution.
     */
    public static class Computer extends BaseService {
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getComputer().executeTask("Open Chrome browser");
         * System.out.println("Task ID: " + result.getTaskId() + ", Status: " + result.getTaskStatus());
         * QueryResult status = session.getAgent().getComputer().getTaskStatus(result.getTaskId());
         * System.out.println("Task status: " + status.getTaskStatus());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getComputer()
         *     .executeTaskAndWait("Open Chrome browser", 300);
         * System.out.println("Task result: " + result.getTaskResult());
         * </pre>
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
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Failed to execute task.",
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        } else if ("unsupported".equals(query.getTaskStatus())) {
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Unsupported task.",
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        }
                        Thread.sleep(3000);
                        triedTime++;
                    }
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        "Task timeout.",
                        taskId,
                        "failed",
                        "Task timeout."
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
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, and error message if any
         *
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getComputer()
         *     .executeTask("Query the weather in Shanghai with Baidu");
         * QueryResult status = session.getAgent().getComputer().getTaskStatus(result.getTaskId());
         * System.out.println("Status: " + status.getTaskStatus() + ", Action: " + status.getTaskAction());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getComputer()
         *     .executeTask("Query the weather in Shanghai with Baidu");
         * ExecutionResult terminateResult = session.getAgent().getComputer()
         *     .terminateTask(result.getTaskId());
         * System.out.println("Terminated: " + terminateResult.isSuccess());
         * </pre>
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
     * Browser agent for browser automation with natural language.
     * Uses browser_use_* MCP tools for task execution.
     * Still in BETA.
     */
    public static class Browser extends BaseService {
        public Browser(Session session) {
            super(session);
        }

        /**
         * Initialize the browser agent with options.
         *
         * @param options Options for the agent (can be null for default options)
         * @return InitializationResult containing success status and error message if any
         *
         * @example
         * <pre>
         * AgentOptions options = new AgentOptions(false, "");
         * InitializationResult result = session.getAgent().getBrowser().initialize(options);
         * System.out.println("Initialized: " + result.isSuccess());
         * </pre>
         */
        public InitializationResult initialize(AgentOptions options) {
            try {
                Map<String, Object> args = new HashMap<>();
                if (options != null) {
                    args.put("use_vision", options.isUseVision());
                    args.put("output_schema", options.getOutputSchema());
                } else {
                    args.put("use_vision", false);
                    args.put("output_schema", "");
                }

                OperationResult result = callMcpTool("browser_use_initialize", args);

                if (result.isSuccess()) {
                    return new InitializationResult(
                        result.getRequestId(),
                        true,
                        ""
                    );
                } else {
                    return new InitializationResult(
                        result.getRequestId(),
                        false,
                        "Failed to initialize browser use agent"
                    );
                }
            } catch (Exception e) {
                return new InitializationResult(
                    "",
                    false,
                    "Failed to initialize: " + e.getMessage()
                );
            }
        }

        /**
         * Execute a browser task in human language without waiting for completion (non-blocking).
         *
         * This is a fire-and-return interface that immediately provides a task ID.
         * Call getTaskStatus to check the task status. You can control the timeout
         * of the task execution in your own code by setting the frequency of calling
         * getTaskStatus.
         *
         * @param task Task description in human language
         * @return ExecutionResult containing success status, task ID, task status, and error message if any
         *
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTask("Query the weather in Shanghai with Baidu");
         * System.out.println("Task ID: " + result.getTaskId() + ", Status: " + result.getTaskStatus());
         * QueryResult status = session.getAgent().getBrowser().getTaskStatus(result.getTaskId());
         * System.out.println("Task status: " + status.getTaskStatus());
         * </pre>
         */
        public ExecutionResult executeTask(String task) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);

                OperationResult result = callMcpTool("browser_use_execute_task", args);

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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTaskAndWait("Query the weather in Shanghai with Baidu", 300);
         * System.out.println("Task result: " + result.getTaskResult());
         * </pre>
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout) {
            try {
                Map<String, Object> args = new HashMap<>();
                args.put("task", task);

                OperationResult result = callMcpTool("browser_use_execute_task", args);

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
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Failed to execute task.",
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        } else if ("unsupported".equals(query.getTaskStatus())) {
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Unsupported task.",
                                taskId,
                                query.getTaskStatus(),
                                ""
                            );
                        }
                        Thread.sleep(3000);
                        triedTime++;
                    }
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        "Task timeout.",
                        taskId,
                        "failed",
                        "Task timeout."
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
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, and error message if any
         *
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTask("Open Chrome browser");
         * QueryResult status = session.getAgent().getBrowser().getTaskStatus(result.getTaskId());
         * System.out.println("Status: " + status.getTaskStatus() + ", Action: " + status.getTaskAction());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTask("Open Chrome browser");
         * ExecutionResult terminateResult = session.getAgent().getBrowser()
         *     .terminateTask(result.getTaskId());
         * System.out.println("Terminated: " + terminateResult.isSuccess());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * System.out.println("Task ID: " + result.getTaskId() + ", Status: " + result.getTaskStatus());
         * QueryResult status = session.getAgent().getMobile().getTaskStatus(result.getTaskId());
         * System.out.println("Task status: " + status.getTaskStatus());
         * </pre>
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
                            logger.error("Failed to get task_id from response");
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Failed to get task_id from response",
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTaskAndWait("Open WeChat app and send a message", 100, 180);
         * System.out.println("Task result: " + result.getTaskResult());
         * </pre>
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
                    logger.error("Failed to get task_id from response");
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        "Failed to get task_id from response",
                        "",
                        "failed",
                        "Task Failed"
                    );
                }

                int pollInterval = 3;
                int maxPollAttempts = timeout / pollInterval;
                int triedTime = 0;
                java.util.Set<Long> processedTimestamps = new java.util.HashSet<>();

                while (triedTime < maxPollAttempts) {
                    QueryResult query = getTaskStatus(taskId);

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
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Failed to execute task.";
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("cancelled".equals(taskStatus)) {
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Task was cancelled.";
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("unsupported".equals(taskStatus)) {
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Unsupported task.";
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
                return new ExecutionResult(
                    result.getRequestId(),
                    false,
                    "Task timeout.",
                    taskId,
                    "failed",
                    "Task timeout."
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
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, stream, error, and error message if any
         *
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * QueryResult status = session.getAgent().getMobile().getTaskStatus(result.getTaskId());
         * System.out.println("Status: " + status.getTaskStatus() + ", Action: " + status.getTaskAction());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * ExecutionResult terminateResult = session.getAgent().getMobile()
         *     .terminateTask(result.getTaskId());
         * System.out.println("Terminated: " + terminateResult.isSuccess());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * System.out.println("Task ID: " + result.getTaskId() + ", Status: " + result.getTaskStatus());
         * QueryResult status = session.getAgent().getMobile().getTaskStatus(result.getTaskId());
         * System.out.println("Task status: " + status.getTaskStatus());
         * </pre>
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
                            logger.error("Failed to get task_id from response");
                            return new ExecutionResult(
                                result.getRequestId(),
                                false,
                                "Failed to get task_id from response",
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTaskAndWait("Open WeChat app and send a message", 100, 180);
         * System.out.println("Task result: " + result.getTaskResult());
         * </pre>
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
                    logger.error("Failed to get task_id from response");
                    return new ExecutionResult(
                        result.getRequestId(),
                        false,
                        "Failed to get task_id from response",
                        "",
                        "failed",
                        "Task Failed"
                    );
                }

                int pollInterval = 3;
                int maxPollAttempts = timeout / pollInterval;
                int triedTime = 0;
                java.util.Set<Long> processedTimestamps = new java.util.HashSet<>();

                while (triedTime < maxPollAttempts) {
                    QueryResult query = getTaskStatus(taskId);

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
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Failed to execute task.";
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("cancelled".equals(taskStatus)) {
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Task was cancelled.";
                        return new ExecutionResult(
                            result.getRequestId(),
                            false,
                            errorMsg,
                            taskId,
                            query.getTaskStatus()
                        );
                    } else if ("unsupported".equals(taskStatus)) {
                        String errorMsg = query.getError() != null && !query.getError().isEmpty() 
                            ? query.getError() : "Unsupported task.";
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
                return new ExecutionResult(
                    result.getRequestId(),
                    false,
                    "Task timeout.",
                    taskId,
                    "failed",
                    "Task timeout."
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
         * Get the status of the task with the given task ID.
         *
         * @param taskId The ID of the task to query
         * @return QueryResult containing success status, task status, task action, task product, stream, error, and error message if any
         *
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * QueryResult status = session.getAgent().getMobile().getTaskStatus(result.getTaskId());
         * System.out.println("Status: " + status.getTaskStatus() + ", Action: " + status.getTaskAction());
         * </pre>
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
         * @example
         * <pre>
         * ExecutionResult result = session.getAgent().getMobile()
         *     .executeTask("Open WeChat app", 100);
         * ExecutionResult terminateResult = session.getAgent().getMobile()
         *     .terminateTask(result.getTaskId());
         * System.out.println("Terminated: " + terminateResult.isSuccess());
         * </pre>
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
