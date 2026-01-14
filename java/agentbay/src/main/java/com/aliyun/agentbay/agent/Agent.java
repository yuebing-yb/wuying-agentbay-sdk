package com.aliyun.agentbay.agent;

import com.aliyun.agentbay.model.*;
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
     * Computer agent for desktop automation with natural language.
     * Uses flux_* MCP tools for task execution.
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
     * Uses browser_use_* MCP tools for task execution.
     * Still in BETA.
     */
    public static class Browser extends BaseService {
        private static final Logger logger = LoggerFactory.getLogger(Browser.class);

        public Browser(Session session) {
            super(session);
        }

        /**
         * Execute a browser task in human language without waiting for
         * completion (non-blocking).
         *
         * This is a fire-and-return interface that immediately provides a task
         * ID. Call getTaskStatus to check the task status. You can control the
         * timeout of the task execution in your own code by setting the
         * frequency of calling getTaskStatus.
         *
         * @param task Task description in human language
         * @param useVision Whether to use vision in the task
         * @param outputSchema Optional Zod schema for a structured task output
         *     if you need
         * @return ExecutionResult containing success status, task ID, task
         *     status, and error message if any
         *
         * @example
         * <pre>
         * public static class WeatherSchema {
         *   @JsonProperty(required = true)
         *   private String city;
         *   private String temperature;
         *   public String getCity() {return city;}
         *   public void setCity(String city) {this.city = city;}
         *   public String getTemperature() {return temperature;}
         *   public void setTemperature(String temperature) {this.temperature = temperature;}
         * }
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTask("Query the weather in Shanghai with Baidu", true, WeatherSchema.class);
         * System.out.println("Task ID: " + result.getTaskId() + ", Status: " +
         * result.getTaskStatus()); QueryResult status =
         * session.getAgent().getBrowser().getTaskStatus(result.getTaskId());
         * System.out.println("Task status: " + status.getTaskStatus());
         * </pre>
         */
        public ExecutionResult executeTask(String task, boolean useVision,
                Class<?> output_schema) {
            try {
                String schemaJson = SchemaHelper.generateJsonSchema(output_schema);
                logger.info("Output schema: {}", schemaJson);
                System.out.println("----------------schemaJson: " + schemaJson);

                Map<String, Object> args = new HashMap<>();
                args.put("task", task);
                args.put("use_vision", useVision);
                args.put("output_schema", schemaJson);
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
         * an error occurs, or timeout happens. The default polling interval is 3 seconds.
         *
         * @param task Task description in human language
         * @param timeout Maximum time to wait for task completion in seconds
         * @param useVision Whether to use vision in the task
         * @param outputSchema Optional Zod schema for a structured task output if you need
         * @return ExecutionResult containing success status, task ID, task status, task result, and error message if any
         *
         * @example
         * <pre>
         *  public static class WeatherSchema {
         *   @JsonProperty(required = true)
         *   private String city;
         *   private String temperature;
         *   public String getCity() {return city;}
         *   public void setCity(String city) {this.city = city;}
         *   public String getTemperature() {return temperature;}
         *   public void setTemperature(String temperature) {this.temperature = temperature;}
         * }
         * ExecutionResult result = session.getAgent().getBrowser()
         *     .executeTaskAndWait("Query the weather in Shanghai with Baidu", 300, true, WeatherSchema.class);
         * System.out.println("Task result: " + result.getTaskResult());
         * </pre>
         */
        public ExecutionResult executeTaskAndWait(String task, int timeout,
                                                  boolean useVision,
                                                  Class<?> output_schema) {
          try {
            ExecutionResult result =
                executeTask(task, useVision, output_schema);
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
