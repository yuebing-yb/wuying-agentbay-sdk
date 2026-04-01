package com.aliyun.agentbay.git;

/**
 * Thrown when a git operation targets a directory that is not a git repository.
 *
 * <p>This typically occurs when a command like {@code status} or {@code log}
 * is run against a path that has not been initialized with {@code git init}
 * or cloned.
 */
public class GitNotARepoError extends GitError {

    /**
     * Constructs a new {@code GitNotARepoError}.
     *
     * @param message   human-readable error description
     * @param exitCode  the exit code returned by the git command
     * @param stderr    the stderr output from the git command
     */
    public GitNotARepoError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
