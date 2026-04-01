package com.aliyun.agentbay.git;

public class GitBranchInfo {
    private final String name;
    private final boolean current;

    public GitBranchInfo(String name, boolean current) {
        this.name = name;
        this.current = current;
    }

    public String getName() {
        return name;
    }

    public boolean isCurrent() {
        return current;
    }
}
