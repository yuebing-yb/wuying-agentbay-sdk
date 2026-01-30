package com.aliyun.agentbay.command;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

public class Command extends BaseService {
    private static final String SERVER_SHELL = "wuying_shell";

    public Command(Session session) {
        super(session);
    }

    public CommandResult execute(String command) {
        return executeCommand(command, 50000);
    }

    public CommandResult execute(String command, String input) {
        return executeCommand(command, 50000);
    }

    public CommandResult executeCommand(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs, null, null);
    }

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
            final int MAX_TIMEOUT_MS = 50000;
            if (timeoutMs > MAX_TIMEOUT_MS) {
                timeoutMs = MAX_TIMEOUT_MS;
            }

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

    public CommandResult run(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    public CommandResult run(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

    public CommandResult exec(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    public CommandResult exec(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

}