package com.aliyun.agentbay.command;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import java.util.HashMap;
import java.util.Map;

public class Command extends BaseService {
    public Command(Session session) {
        super(session);
    }

    public CommandResult execute(String command) {
        return executeCommand(command, 1000); // Default timeout 1000ms
    }

    public CommandResult execute(String command, String input) {
        // For now, we don't handle input separately, just execute the command
        return executeCommand(command, 1000);
    }

    public CommandResult executeCommand(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs, null, null);
    }

    public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("command", command);
            args.put("timeout_ms", timeoutMs);

            if (cwd != null) {
                args.put("cwd", cwd);
            }

            if (envs != null) {
                for (Map.Entry<String, String> entry : envs.entrySet()) {
                    if (!(entry.getKey() instanceof String) || !(entry.getValue() instanceof String)) {
                        throw new IllegalArgumentException(
                            "Invalid environment variables: all keys and values must be strings."
                        );
                    }
                }
                args.put("envs", envs);
            }

            OperationResult result = callMcpTool("shell", args);

            if (result.isSuccess()) {
                return new CommandResult(result.getRequestId(), true, result.getData(), "", 0);
            } else {
                return new CommandResult(result.getRequestId(), false, "", result.getErrorMessage(), 1);
            }

        } catch (Exception e) {
            return new CommandResult("", false, "", "Unexpected error: " + e.getMessage(), 1);
        }
    }

}