package com.aliyun.agentbay.git;

import java.util.List;

/**
 * Result of a {@code git branch --list} operation.
 *
 * <p>Contains the list of all branches and the name of the currently
 * checked-out branch.
 */
public class GitBranchListResult {

    /** All branches in the repository. */
    private final List<GitBranchInfo> branches;

    /** The name of the currently checked-out branch, or {@code null} in detached HEAD state. */
    private final String current;

    /**
     * Constructs a new {@code GitBranchListResult}.
     *
     * @param branches list of branch information entries
     * @param current  name of the currently checked-out branch, or {@code null}
     */
    public GitBranchListResult(List<GitBranchInfo> branches, String current) {
        this.branches = branches;
        this.current = current;
    }

    /**
     * Returns the list of all branches.
     *
     * @return unmodifiable list of {@link GitBranchInfo} entries
     */
    public List<GitBranchInfo> getBranches() {
        return branches;
    }

    /**
     * Returns the name of the currently checked-out branch.
     *
     * @return current branch name, or {@code null} if in detached HEAD state
     */
    public String getCurrent() {
        return current;
    }
}
