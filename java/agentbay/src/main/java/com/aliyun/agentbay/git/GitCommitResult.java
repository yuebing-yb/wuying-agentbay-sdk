package com.aliyun.agentbay.git;

public class GitCommitResult {
    private final String commitHash;

    public GitCommitResult(String commitHash) {
        this.commitHash = commitHash;
    }

    public String getCommitHash() {
        return commitHash;
    }
}
