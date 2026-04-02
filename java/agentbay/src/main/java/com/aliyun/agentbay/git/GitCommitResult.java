package com.aliyun.agentbay.git;

/**
 * Result of a {@code git commit} operation.
 *
 * <p>Contains the hash of the newly created commit.
 */
public class GitCommitResult {

    /** The SHA-1 hash of the created commit, or {@code null} if it could not be parsed. */
    private final String commitHash;

    /**
     * Constructs a new {@code GitCommitResult}.
     *
     * @param commitHash the SHA-1 hash of the created commit
     */
    public GitCommitResult(String commitHash) {
        this.commitHash = commitHash;
    }

    /**
     * Returns the SHA-1 hash of the created commit.
     *
     * @return commit hash string, or {@code null} if unavailable
     */
    public String getCommitHash() {
        return commitHash;
    }
}
