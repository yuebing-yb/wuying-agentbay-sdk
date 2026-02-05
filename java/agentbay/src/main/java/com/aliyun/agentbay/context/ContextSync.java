package com.aliyun.agentbay.context;

/**
 * Defines the context synchronization configuration
 */
public class ContextSync {
    private String contextId;
    private String path;
    private SyncPolicy policy;
    /**
     * Beta feature flag to control whether session creation should wait for this context's
     * initial download to finish. If set to false, the SDK will not block create() on this context.
     * Defaults to null (treated as true for backward compatibility).
     */
    private Boolean betaWaitForCompletion;

    public ContextSync() {
    }

    public ContextSync(String contextId, String path, SyncPolicy policy) {
        this.contextId = contextId;
        this.path = path;
        this.policy = policy;
    }

    public static ContextSync create(String contextId, String path, SyncPolicy policy) {
        return new ContextSync(contextId, path, policy);
    }

    public ContextSync withPolicy(SyncPolicy policy) {
        this.policy = policy;
        return this;
    }

    public ContextSync withBetaWaitForCompletion(Boolean wait) {
        this.betaWaitForCompletion = wait;
        return this;
    }

    public String getContextId() {
        return contextId;
    }

    public void setContextId(String contextId) {
        this.contextId = contextId;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public SyncPolicy getPolicy() {
        return policy;
    }

    public void setPolicy(SyncPolicy policy) {
        this.policy = policy;
    }

    public Boolean getBetaWaitForCompletion() {
        return betaWaitForCompletion;
    }

    public void setBetaWaitForCompletion(Boolean betaWaitForCompletion) {
        this.betaWaitForCompletion = betaWaitForCompletion;
    }
}