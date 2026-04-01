package com.aliyun.agentbay.git;

public class GitCloneResult {
    private final String path;

    public GitCloneResult(String path) {
        this.path = path;
    }

    public String getPath() {
        return path;
    }
}
