package com.aliyun.agentbay.git;

import java.util.List;

public class GitStatusResult {
    private final String currentBranch;
    private final String upstream;
    private final int ahead;
    private final int behind;
    private final boolean detached;
    private final List<GitFileStatus> files;

    public GitStatusResult(String currentBranch, String upstream, int ahead, int behind, boolean detached, List<GitFileStatus> files) {
        this.currentBranch = currentBranch;
        this.upstream = upstream;
        this.ahead = ahead;
        this.behind = behind;
        this.detached = detached;
        this.files = files;
    }

    public String getCurrentBranch() {
        return currentBranch;
    }

    public String getUpstream() {
        return upstream;
    }

    public int getAhead() {
        return ahead;
    }

    public int getBehind() {
        return behind;
    }

    public boolean isDetached() {
        return detached;
    }

    public List<GitFileStatus> getFiles() {
        return files;
    }

    public boolean isClean() {
        return files.isEmpty();
    }

    public boolean hasChanges() {
        return !files.isEmpty();
    }

    public boolean hasStaged() {
        return files.stream().anyMatch(GitFileStatus::isStaged);
    }

    public boolean hasUntracked() {
        return files.stream().anyMatch(f -> "untracked".equals(f.getStatus()));
    }

    public boolean hasConflicts() {
        return files.stream().anyMatch(f -> "conflict".equals(f.getStatus()));
    }

    public int getTotalCount() {
        return files.size();
    }

    public int getStagedCount() {
        return (int) files.stream().filter(GitFileStatus::isStaged).count();
    }

    public int getUnstagedCount() {
        return (int) files.stream().filter(f -> !f.isStaged() && !"untracked".equals(f.getStatus())).count();
    }

    public int getUntrackedCount() {
        return (int) files.stream().filter(f -> "untracked".equals(f.getStatus())).count();
    }

    public int getConflictCount() {
        return (int) files.stream().filter(f -> "conflict".equals(f.getStatus())).count();
    }
}
