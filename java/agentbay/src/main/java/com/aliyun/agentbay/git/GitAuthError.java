package com.aliyun.agentbay.git;

/**
 * Thrown when a git operation fails due to an authentication error.
 *
 * <p>Common triggers include invalid credentials, missing SSH keys,
 * expired tokens, or accessing a private repository without proper
 * authorization.
 */
public class GitAuthError extends GitError {

    /**
     * Constructs a new {@code GitAuthError}.
     *
     * @param message   human-readable error description
     * @param exitCode  the exit code returned by the git command
     * @param stderr    the stderr output from the git command
     */
    public GitAuthError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
