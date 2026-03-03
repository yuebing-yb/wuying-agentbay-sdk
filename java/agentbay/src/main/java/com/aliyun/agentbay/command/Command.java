package com.aliyun.agentbay.command;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

/**
 * Async command execution service for session shells in the AgentBay cloud environment.
 * 
 * <p>Use this class for non-blocking command execution; for blocking/synchronous usage,
 * refer to the Command service in the sync API.
 */
public class Command extends BaseService {
    private static final String SERVER_SHELL = "wuying_shell";

    public Command(Session session) {
        super(session);
    }

    /**
     * Execute a shell command with default timeout (50000ms).
     *
     * @param command The shell command to execute
     * @return CommandResult Result object containing execution details
     */
    public CommandResult execute(String command) {
        return executeCommand(command, 50000);
    }

    /**
     * Execute a shell command with default timeout (50000ms).
     * Note: The input parameter is currently not used in the implementation.
     *
     * @param command The shell command to execute
     * @param input Input parameter (currently unused)
     * @return CommandResult Result object containing execution details
     */
    public CommandResult execute(String command, String input) {
        return executeCommand(command, 50000);
    }

    /**
     * Execute a shell command with specified timeout.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     */
    public CommandResult executeCommand(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs, null, null);
    }

    /**
     * Execute a shell command with optional working directory and environment variables.
     *
     * <p>Executes a shell command in the session environment with configurable timeout,
     * working directory, and environment variables. The command runs with session
     * user permissions in a Linux shell environment.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds (default: 50000ms/50s).
     * @param cwd The working directory for command execution. If not specified,
     *            the command runs in the default session directory
     * @param envs Environment variables as a map of key-value pairs.
     *             These variables are set for the command execution only
     * @return CommandResult Result object containing:
     *         <ul>
     *           <li>success: Whether the command executed successfully (exit_code == 0)</li>
     *           <li>output: Command output for backward compatibility (stdout + stderr)</li>
     *           <li>exitCode: The exit code of the command execution (0 for success)</li>
     *           <li>stdout: Standard output from the command execution</li>
     *           <li>stderr: Standard error from the command execution</li>
     *           <li>traceId: Trace ID for error tracking (only present when exit_code != 0)</li>
     *           <li>requestId: Unique identifier for this API request</li>
     *           <li>errorMessage: Error description if execution failed</li>
     *         </ul>
     * @throws IllegalArgumentException If environment variables contain non-string keys or values
     *
     */
    public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        if (envs != null) {
            java.util.List<String> invalidVars = new java.util.ArrayList<>();
            for (Map.Entry<String, String> entry : envs.entrySet()) {
                Object key = entry.getKey();
                Object value = entry.getValue();

                if (!(key instanceof String)) {
                    invalidVars.add(String.format("key '%s' (type: %s)", key, key.getClass().getSimpleName()));
                }
                if (!(value instanceof String)) {
                    invalidVars.add(String.format("value for key '%s' (type: %s)", key, value.getClass().getSimpleName()));
                }
            }

            if (!invalidVars.isEmpty()) {
                throw new IllegalArgumentException(
                    "Invalid environment variables: all keys and values must be strings. " +
                    "Found invalid entries: " + String.join(", ", invalidVars)
                );
            }
        }

        try {
            Map<String, Object> args = new HashMap<>();
            args.put("command", command);
            args.put("timeout_ms", timeoutMs);

            if (cwd != null) {
                args.put("cwd", cwd);
            }

            if (envs != null) {
                args.put("envs", envs);
            }

            OperationResult result = callMcpTool("shell", args);

            if (result.isSuccess()) {
                try {
                    ObjectMapper mapper = new ObjectMapper();
                    JsonNode dataJson;

                    if (result.getData() instanceof String) {
                        dataJson = mapper.readTree((String) result.getData());
                    } else {
                        dataJson = mapper.valueToTree(result.getData());
                    }

                    String stdout = dataJson.has("stdout") ? dataJson.get("stdout").asText() : "";
                    String stderr = dataJson.has("stderr") ? dataJson.get("stderr").asText() : "";
                    int exitCode = dataJson.has("exit_code") ? dataJson.get("exit_code").asInt() : 0;
                    String traceId = dataJson.has("traceId") ? dataJson.get("traceId").asText() : "";

                    boolean success = exitCode == 0;
                    String output = stdout + stderr;

                    return new CommandResult(result.getRequestId(), success, output, "", exitCode,
                            stdout, stderr, traceId);
                } catch (Exception e) {
                    String output = result.getData() instanceof String ? (String) result.getData() : result.getData().toString();
                    return new CommandResult(result.getRequestId(), true, output, "", 0, "", "", "");
                }
            } else {
                try {
                    ObjectMapper mapper = new ObjectMapper();
                    JsonNode errorData;

                    if (result.getErrorMessage() instanceof String) {
                        errorData = mapper.readTree((String) result.getErrorMessage());
                    } else {
                        errorData = mapper.valueToTree(result.getErrorMessage());
                    }

                    if (errorData.isObject()) {
                        String stdout = errorData.has("stdout") ? errorData.get("stdout").asText() : "";
                        String stderr = errorData.has("stderr") ? errorData.get("stderr").asText() : "";
                        int exitCode = errorData.has("exit_code") ? errorData.get("exit_code").asInt()
                                     : errorData.has("errorCode") ? errorData.get("errorCode").asInt() : 0;
                        String traceId = errorData.has("traceId") ? errorData.get("traceId").asText() : "";
                        String output = stdout + stderr;
                        String errorMessage = !stderr.isEmpty() ? stderr
                                            : (result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute command");

                        return new CommandResult(result.getRequestId(), false, output, errorMessage, exitCode,
                                stdout, stderr, traceId);
                    }
                } catch (Exception e) {
                }

                return new CommandResult(result.getRequestId(), false, "",
                        result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to execute command", 1,
                        "", "", "");
            }

        } catch (Exception e) {
            return new CommandResult("", false, "", "Failed to execute command: " + e.getMessage(), 1,
                    "", "", "");
        }
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     * @see #executeCommand(String, int, String, Map)
     */
    public CommandResult run(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @param cwd The working directory for command execution
     * @param envs Environment variables as a map of key-value pairs
     * @return CommandResult Result object containing execution details
     */
    public CommandResult run(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     */
    public CommandResult exec(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @param cwd The working directory for command execution
     * @param envs Environment variables as a map of key-value pairs
     * @return CommandResult Result object containing execution details
     */
    public CommandResult exec(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

}