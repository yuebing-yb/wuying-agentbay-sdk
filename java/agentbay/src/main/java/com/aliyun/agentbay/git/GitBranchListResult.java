package com.aliyun.agentbay.git;

import java.util.List;

public class GitBranchListResult {
    private final List<GitBranchInfo> branches;
    private final String current;

    public GitBranchListResult(List<GitBranchInfo> branches, String current) {
        this.branches = branches;
        this.current = current;
    }

    public List<GitBranchInfo> getBranches() {
        return branches;
    }

    public String getCurrent() {
        return current;
    }
}
