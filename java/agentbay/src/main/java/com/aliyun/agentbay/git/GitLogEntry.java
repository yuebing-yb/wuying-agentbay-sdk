package com.aliyun.agentbay.git;

public class GitLogEntry {
    private final String hash;
    private final String shortHash;
    private final String authorName;
    private final String authorEmail;
    private final String date;
    private final String message;

    public GitLogEntry(String hash, String shortHash, String authorName, String authorEmail, String date, String message) {
        this.hash = hash;
        this.shortHash = shortHash;
        this.authorName = authorName;
        this.authorEmail = authorEmail;
        this.date = date;
        this.message = message;
    }

    public String getHash() {
        return hash;
    }

    public String getShortHash() {
        return shortHash;
    }

    public String getAuthorName() {
        return authorName;
    }

    public String getAuthorEmail() {
        return authorEmail;
    }

    public String getDate() {
        return date;
    }

    public String getMessage() {
        return message;
    }
}
