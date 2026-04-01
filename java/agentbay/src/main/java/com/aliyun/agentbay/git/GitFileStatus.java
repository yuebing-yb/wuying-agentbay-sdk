package com.aliyun.agentbay.git;

/**
 * Status information for a single file in a git repository.
 *
 * <p>Parsed from the {@code git status --porcelain=1} output. Each entry
 * describes the index and working-tree status of one file.
 */
public class GitFileStatus {

    /** Path of the file relative to the repository root. */
    private final String path;

    /** Normalized status string (e.g., {@code "modified"}, {@code "added"}, {@code "untracked"}). */
    private final String status;

    /** Index (staging area) status character from porcelain output. */
    private final String indexStatus;

    /** Working-tree status character from porcelain output. */
    private final String workTreeStatus;

    /** Whether the change is staged for the next commit. */
    private final boolean staged;

    /** Original path before rename, or {@code null} if the file was not renamed. */
    private final String renamedFrom;

    /**
     * Constructs a new {@code GitFileStatus}.
     *
     * @param path           file path relative to the repository root
     * @param status         normalized status string
     * @param indexStatus    index status character
     * @param workTreeStatus working-tree status character
     * @param staged         whether the change is staged
     * @param renamedFrom    original path before rename, or {@code null}
     */
    public GitFileStatus(String path, String status, String indexStatus, String workTreeStatus, boolean staged, String renamedFrom) {
        this.path = path;
        this.status = status;
        this.indexStatus = indexStatus;
        this.workTreeStatus = workTreeStatus;
        this.staged = staged;
        this.renamedFrom = renamedFrom;
    }

    /**
     * Returns the file path relative to the repository root.
     *
     * @return file path
     */
    public String getPath() {
        return path;
    }

    /**
     * Returns the normalized status string.
     *
     * @return one of {@code "modified"}, {@code "added"}, {@code "deleted"},
     *         {@code "renamed"}, {@code "copied"}, {@code "untracked"},
     *         {@code "conflict"}, {@code "typechange"}, or {@code "unknown"}
     */
    public String getStatus() {
        return status;
    }

    /**
     * Returns the index (staging area) status character.
     *
     * @return single-character status code
     */
    public String getIndexStatus() {
        return indexStatus;
    }

    /**
     * Returns the working-tree status character.
     *
     * @return single-character status code
     */
    public String getWorkTreeStatus() {
        return workTreeStatus;
    }

    /**
     * Returns whether this change is staged for the next commit.
     *
     * @return {@code true} if staged
     */
    public boolean isStaged() {
        return staged;
    }

    /**
     * Returns the original path before a rename operation.
     *
     * @return original file path, or {@code null} if not renamed
     */
    public String getRenamedFrom() {
        return renamedFrom;
    }
}
