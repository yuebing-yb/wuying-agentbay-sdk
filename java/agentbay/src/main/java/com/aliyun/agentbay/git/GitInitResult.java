package com.aliyun.agentbay.git;

public class GitInitResult {
    private final String path;

    public GitInitResult(String path) {
        this.path = path;
    }

    public String getPath() {
        return path;
    }
}
