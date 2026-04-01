package com.aliyun.agentbay.git;

import java.util.List;

/**
 * Result of a {@code git status} operation.
 *
 * <p>Contains the current branch name, upstream tracking information,
 * ahead/behind counts, detached HEAD state, and a list of individual
 * file statuses. Convenience methods are provided to query the
 * overall repository state.
 */
public class GitStatusResult {

    /** The name of the currently checked-out branch. */
    private final String currentBranch;

    /** The upstream tracking branch, or {@code null} if none. */
    private final String upstream;

    /** Number of commits ahead of the upstream branch. */
    private final int ahead;

    /** Number of commits behind the upstream branch. */
    private final int behind;

    /** Whether HEAD is in a detached state. */
    private final boolean detached;

    /** List of individual file status entries. */
    private final List<GitFileStatus> files;

    /**
     * Constructs a new {@code GitStatusResult}.
     *
     * @param currentBranch the current branch name
     * @param upstream      upstream tracking branch, or {@code null}
     * @param ahead         number of commits ahead of upstream
     * @param behind        number of commits behind upstream
     * @param detached      whether HEAD is detached
     * @param files         list of file status entries
     */
    public GitStatusResult(String currentBranch, String upstream, int ahead, int behind, boolean detached, List<GitFileStatus> files) {
        this.currentBranch = currentBranch;
        this.upstream = upstream;
        this.ahead = ahead;
        this.behind = behind;
        this.detached = detached;
        this.files = files;
    }

    /**
     * Returns the current branch name.
     *
     * @return branch name, or {@code null} if unknown
     */
    public String getCurrentBranch() {
        return currentBranch;
    }

    /**
     * Returns the upstream tracking branch.
     *
     * @return upstream branch name, or {@code null} if no upstream is set
     */
    public String getUpstream() {
        return upstream;
    }

    /**
     * Returns the number of commits the local branch is ahead of upstream.
     *
     * @return ahead count
     */
    public int getAhead() {
        return ahead;
    }

    /**
     * Returns the number of commits the local branch is behind upstream.
     *
     * @return behind count
     */
    public int getBehind() {
        return behind;
    }

    /**
     * Returns whether HEAD is in a detached state.
     *
     * @return {@code true} if HEAD is detached
     */
    public boolean isDetached() {
        return detached;
    }

    /**
     * Returns the list of individual file status entries.
     *
     * @return list of {@link GitFileStatus} objects
     */
    public List<GitFileStatus> getFiles() {
        return files;
    }

    /**
     * Returns whether the working tree is clean (no changes at all).
     *
     * @return {@code true} if there are no modified, staged, or untracked files
     */
    public boolean isClean() {
        return files.isEmpty();
    }

    /**
     * Returns whether the working tree has any changes.
     *
     * @return {@code true} if there are any modified, staged, or untracked files
     */
    public boolean hasChanges() {
        return !files.isEmpty();
    }

    /**
     * Returns whether there are any staged changes.
     *
     * @return {@code true} if at least one file is staged
     */
    public boolean hasStaged() {
        return files.stream().anyMatch(GitFileStatus::isStaged);
    }

    /**
     * Returns whether there are any untracked files.
     *
     * @return {@code true} if at least one file is untracked
     */
    public boolean hasUntracked() {
        return files.stream().anyMatch(f -> "untracked".equals(f.getStatus()));
    }

    /**
     * Returns whether there are any merge conflicts.
     *
     * @return {@code true} if at least one file has a conflict status
     */
    public boolean hasConflicts() {
        return files.stream().anyMatch(f -> "conflict".equals(f.getStatus()));
    }

    /**
     * Returns the total number of files with changes.
     *
     * @return total file count
     */
    public int getTotalCount() {
        return files.size();
    }

    /**
     * Returns the number of staged files.
     *
     * @return staged file count
     */
    public int getStagedCount() {
        return (int) files.stream().filter(GitFileStatus::isStaged).count();
    }

    /**
     * Returns the number of unstaged (modified but not staged) files.
     *
     * @return unstaged file count
     */
    public int getUnstagedCount() {
        return (int) files.stream().filter(f -> !f.isStaged() && !"untracked".equals(f.getStatus())).count();
    }

    /**
     * Returns the number of untracked files.
     *
     * @return untracked file count
     */
    public int getUntrackedCount() {
        return (int) files.stream().filter(f -> "untracked".equals(f.getStatus())).count();
    }

    /**
     * Returns the number of files with merge conflicts.
     *
     * @return conflict file count
     */
    public int getConflictCount() {
        return (int) files.stream().filter(f -> "conflict".equals(f.getStatus())).count();
    }
}
