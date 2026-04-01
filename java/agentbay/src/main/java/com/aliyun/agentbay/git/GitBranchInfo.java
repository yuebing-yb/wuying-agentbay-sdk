package com.aliyun.agentbay.git;

/**
 * Information about a single git branch.
 *
 * <p>Returned as part of {@link GitBranchListResult} when listing
 * repository branches.
 */
public class GitBranchInfo {

    /** The short name of the branch (e.g., {@code "main"}). */
    private final String name;

    /** Whether this branch is the currently checked-out branch. */
    private final boolean current;

    /**
     * Constructs a new {@code GitBranchInfo}.
     *
     * @param name    the branch name
     * @param current {@code true} if this is the currently checked-out branch
     */
    public GitBranchInfo(String name, boolean current) {
        this.name = name;
        this.current = current;
    }

    /**
     * Returns the branch name.
     *
     * @return branch name
     */
    public String getName() {
        return name;
    }

    /**
     * Returns whether this is the currently checked-out branch.
     *
     * @return {@code true} if this branch is checked out
     */
    public boolean isCurrent() {
        return current;
    }
}
