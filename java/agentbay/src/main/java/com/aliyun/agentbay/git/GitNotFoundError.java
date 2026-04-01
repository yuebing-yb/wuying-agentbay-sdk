package com.aliyun.agentbay.git;

public class GitNotFoundError extends GitError {
    public GitNotFoundError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
