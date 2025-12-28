package com.aliyun.agentbay.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Result object for session list operations
 */
public class SessionListResult {
    private String requestId;
    private boolean success;
    private String errorMessage;
    private List<SessionInfo> sessionInfos;
    private String nextToken;
    private int maxResults;
    private int totalCount;

    public SessionListResult() {
        this.sessionInfos = new ArrayList<>();
    }

    public SessionListResult(String requestId, boolean success, String errorMessage,
                            List<SessionInfo> sessionInfos, String nextToken,
                            int maxResults, int totalCount) {
        this.requestId = requestId;
        this.success = success;
        this.errorMessage = errorMessage;
        this.sessionInfos = sessionInfos != null ? sessionInfos : new ArrayList<>();
        this.nextToken = nextToken;
        this.maxResults = maxResults;
        this.totalCount = totalCount;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public List<SessionInfo> getSessionInfos() {
        return sessionInfos;
    }

    public void setSessionInfos(List<SessionInfo> sessionInfos) {
        this.sessionInfos = sessionInfos;
    }

    public String getNextToken() {
        return nextToken;
    }

    public void setNextToken(String nextToken) {
        this.nextToken = nextToken;
    }

    public int getMaxResults() {
        return maxResults;
    }

    public void setMaxResults(int maxResults) {
        this.maxResults = maxResults;
    }

    public int getTotalCount() {
        return totalCount;
    }

    public void setTotalCount(int totalCount) {
        this.totalCount = totalCount;
    }

    /**
     * Inner class representing session information in the list
     */
    public static class SessionInfo {
        private String sessionId;
        private String sessionStatus;

        public SessionInfo() {
        }

        public SessionInfo(String sessionId, String sessionStatus) {
            this.sessionId = sessionId;
            this.sessionStatus = sessionStatus;
        }

        public String getSessionId() {
            return sessionId;
        }

        public void setSessionId(String sessionId) {
            this.sessionId = sessionId;
        }

        public String getSessionStatus() {
            return sessionStatus;
        }

        public void setSessionStatus(String sessionStatus) {
            this.sessionStatus = sessionStatus;
        }
    }
}
