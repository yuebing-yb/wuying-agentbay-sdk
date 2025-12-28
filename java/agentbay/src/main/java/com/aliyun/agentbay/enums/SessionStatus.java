package com.aliyun.agentbay.enums;

/**
 * Enum representing session status values
 */
public enum SessionStatus {
    RUNNING("RUNNING"),
    PAUSING("PAUSING"),
    PAUSED("PAUSED"),
    RESUMING("RESUMING"),
    DELETING("DELETING"),
    DELETED("DELETED");

    private final String value;

    SessionStatus(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }

    /**
     * Check if a given status string is valid
     *
     * @param status The status string to validate
     * @return true if the status is valid, false otherwise
     */
    public static boolean isValid(String status) {
        if (status == null) {
            return false;
        }
        for (SessionStatus s : SessionStatus.values()) {
            if (s.value.equals(status)) {
                return true;
            }
        }
        return false;
    }
}
