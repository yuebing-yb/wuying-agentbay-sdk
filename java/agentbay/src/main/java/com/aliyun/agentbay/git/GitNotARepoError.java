package com.aliyun.agentbay.git;

public class GitNotARepoError extends GitError {
    public GitNotARepoError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
