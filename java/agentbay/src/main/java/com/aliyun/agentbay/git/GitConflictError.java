package com.aliyun.agentbay.git;

/**
 * Thrown when a git operation encounters a merge or rebase conflict.
 *
 * <p>Typically raised during {@code merge}, {@code pull}, or {@code rebase}
 * when conflicting changes cannot be automatically resolved.
 */
public class GitConflictError extends GitError {

    /**
     * Constructs a new {@code GitConflictError}.
     *
     * @param message   human-readable error description
     * @param exitCode  the exit code returned by the git command
     * @param stderr    the stderr output from the git command
     */
    public GitConflictError(String message, int exitCode, String stderr) {
        super(message, exitCode, stderr);
    }
}
