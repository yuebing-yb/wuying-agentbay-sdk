package com.aliyun.agentbay.git;

import java.util.List;

public class GitLogResult {
    private final List<GitLogEntry> entries;

    public GitLogResult(List<GitLogEntry> entries) {
        this.entries = entries;
    }

    public List<GitLogEntry> getEntries() {
        return entries;
    }
}
