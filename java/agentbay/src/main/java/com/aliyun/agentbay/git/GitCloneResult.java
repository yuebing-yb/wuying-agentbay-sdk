package com.aliyun.agentbay.git;

/**
 * Result of a {@code git clone} operation.
 *
 * <p>Contains the local path where the repository was cloned to.
 */
public class GitCloneResult {

    /** The local directory path of the cloned repository. */
    private final String path;

    /**
     * Constructs a new {@code GitCloneResult}.
     *
     * @param path the local directory path of the cloned repository
     */
    public GitCloneResult(String path) {
        this.path = path;
    }

    /**
     * Returns the local directory path of the cloned repository.
     *
     * @return repository path
     */
    public String getPath() {
        return path;
    }
}
