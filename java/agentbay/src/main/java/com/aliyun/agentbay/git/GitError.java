package com.aliyun.agentbay.git;

import com.aliyun.agentbay.exception.AgentBayException;

public class GitError extends AgentBayException {
    private final int exitCode;
    private final String stderr;

    public GitError(String message, int exitCode, String stderr) {
        super(message);
        this.exitCode = exitCode;
        this.stderr = stderr;
    }

    public int getExitCode() {
        return exitCode;
    }

    public String getStderr() {
        return stderr;
    }
}
