package com.aliyun.agentbay.git;

/**
 * Result of a {@code git init} operation.
 *
 * <p>Contains the path of the newly initialized repository.
 */
public class GitInitResult {

    /** The directory path of the initialized repository. */
    private final String path;

    /**
     * Constructs a new {@code GitInitResult}.
     *
     * @param path the directory path of the initialized repository
     */
    public GitInitResult(String path) {
        this.path = path;
    }

    /**
     * Returns the directory path of the initialized repository.
     *
     * @return repository path
     */
    public String getPath() {
        return path;
    }
}
