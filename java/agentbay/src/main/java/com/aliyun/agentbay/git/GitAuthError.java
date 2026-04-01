package com.aliyun.agentbay.git;

public class GitAuthError extends GitError {
    public GitAuthError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
