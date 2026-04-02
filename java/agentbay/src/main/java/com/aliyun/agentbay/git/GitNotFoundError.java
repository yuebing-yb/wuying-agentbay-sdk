package com.aliyun.agentbay.git;

/**
 * Thrown when the git executable is not found or not installed in the
 * remote session environment.
 *
 * <p>Ensure the session image includes git (e.g., {@code code_latest}).
 */
public class GitNotFoundError extends GitError {

    /**
     * Constructs a new {@code GitNotFoundError}.
     *
     * @param message   human-readable error description
     * @param exitCode  the exit code returned by the git command
     * @param stderr    the stderr output from the git command
     */
    public GitNotFoundError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
