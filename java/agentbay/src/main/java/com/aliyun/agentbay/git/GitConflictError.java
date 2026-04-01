package com.aliyun.agentbay.git;

public class GitConflictError extends GitError {
    public GitConflictError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
