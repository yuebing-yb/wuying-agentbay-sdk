package com.aliyun.agentbay.git;

public class GitFileStatus {
    private final String path;
    private final String status;
    private final String indexStatus;
    private final String workTreeStatus;
    private final boolean staged;
    private final String renamedFrom;

    public GitFileStatus(String path, String status, String indexStatus, String workTreeStatus, boolean staged, String renamedFrom) {
        this.path = path;
        this.status = status;
        this.indexStatus = indexStatus;
        this.workTreeStatus = workTreeStatus;
        this.staged = staged;
        this.renamedFrom = renamedFrom;
    }

    public String getPath() {
        return path;
    }

    public String getStatus() {
        return status;
    }

    public String getIndexStatus() {
        return indexStatus;
    }

    public String getWorkTreeStatus() {
        return workTreeStatus;
    }

    public boolean isStaged() {
        return staged;
    }

    public String getRenamedFrom() {
        return renamedFrom;
    }
}
