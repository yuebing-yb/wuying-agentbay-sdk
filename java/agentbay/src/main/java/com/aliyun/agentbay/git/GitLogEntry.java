package com.aliyun.agentbay.git;

/**
 * A single commit entry from the git log.
 *
 * <p>Each entry contains the commit hash, author information, date,
 * and commit message.
 */
public class GitLogEntry {

    /** Full SHA-1 hash of the commit. */
    private final String hash;

    /** Abbreviated commit hash. */
    private final String shortHash;

    /** Name of the commit author. */
    private final String authorName;

    /** Email address of the commit author. */
    private final String authorEmail;

    /** ISO 8601 formatted author date string. */
    private final String date;

    /** The commit subject line (first line of the commit message). */
    private final String message;

    /**
     * Constructs a new {@code GitLogEntry}.
     *
     * @param hash        full SHA-1 hash
     * @param shortHash   abbreviated hash
     * @param authorName  author name
     * @param authorEmail author email address
     * @param date        ISO 8601 formatted date
     * @param message     commit subject line
     */
    public GitLogEntry(String hash, String shortHash, String authorName, String authorEmail, String date, String message) {
        this.hash = hash;
        this.shortHash = shortHash;
        this.authorName = authorName;
        this.authorEmail = authorEmail;
        this.date = date;
        this.message = message;
    }

    /**
     * Returns the full SHA-1 commit hash.
     *
     * @return 40-character hex string
     */
    public String getHash() {
        return hash;
    }

    /**
     * Returns the abbreviated commit hash.
     *
     * @return short hash string
     */
    public String getShortHash() {
        return shortHash;
    }

    /**
     * Returns the author name.
     *
     * @return author name
     */
    public String getAuthorName() {
        return authorName;
    }

    /**
     * Returns the author email address.
     *
     * @return email address
     */
    public String getAuthorEmail() {
        return authorEmail;
    }

    /**
     * Returns the author date in ISO 8601 format.
     *
     * @return date string
     */
    public String getDate() {
        return date;
    }

    /**
     * Returns the commit subject line.
     *
     * @return commit message
     */
    public String getMessage() {
        return message;
    }
}
