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
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("command", command);
            args.put("timeout_ms", timeoutMs);
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