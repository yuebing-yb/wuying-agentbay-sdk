package com.aliyun.agentbay.git;

import com.aliyun.agentbay.exception.AgentBayException;

/**
 * Base exception for all git operations.
 *
 * <p>Thrown when a git command executed in the remote session exits with
 * a non-zero status code. Subclasses provide finer-grained error
 * classification (authentication, conflict, etc.).
 *
 * @see GitAuthError
 * @see GitConflictError
 * @see GitNotARepoError
 * @see GitNotFoundError
 */
public class GitError extends AgentBayException {

    /** The exit code returned by the git process. */
    private final int exitCode;

    /** The stderr output captured from the git process. */
    private final String stderr;

    /**
     * Constructs a new {@code GitError}.
     *
     * @param message   human-readable error description
     * @param exitCode  the exit code returned by the git command
     * @param stderr    the stderr output from the git command
     */
    public GitError(String message, int exitCode, String stderr) {
        super(message);
        this.exitCode = exitCode;
        this.stderr = stderr;
    }

    /**
     * Returns the exit code of the failed git command.
     *
     * @return non-zero exit code
     */
    public int getExitCode() {
        return exitCode;
    }

    /**
     * Returns the stderr output of the failed git command.
     *
     * @return stderr text, may be empty but never {@code null}
     */
    public String getStderr() {
        return stderr;
    }
}
