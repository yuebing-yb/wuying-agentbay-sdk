package com.aliyun.agentbay.git;

import java.util.List;

/**
 * Result of a {@code git log} operation.
 *
 * <p>Contains a list of {@link GitLogEntry} objects, each representing
 * one commit in the log output.
 */
public class GitLogResult {

    /** The list of commit log entries, ordered newest-first. */
    private final List<GitLogEntry> entries;

    /**
     * Constructs a new {@code GitLogResult}.
     *
     * @param entries list of commit log entries
     */
    public GitLogResult(List<GitLogEntry> entries) {
        this.entries = entries;
    }

    /**
     * Returns the commit log entries.
     *
     * @return list of {@link GitLogEntry} objects
     */
    public List<GitLogEntry> getEntries() {
        return entries;
    }
}
