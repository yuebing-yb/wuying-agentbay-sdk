package com.aliyun.agentbay.context;

/**
 * Represents a single context binding entry returned by DescribeSessionContexts.
 */
public class ContextBinding {
    private String contextId;
    private String contextName;
    private String path;
    private String policy;
    private String bindTime;

    public ContextBinding(String contextId, String contextName, String path, String policy, String bindTime) {
        this.contextId = contextId;
        this.contextName = contextName;
        this.path = path;
        this.policy = policy;
        this.bindTime = bindTime;
    }

    public String getContextId() {
        return contextId;
    }

    public String getContextName() {
        return contextName;
    }

    public String getPath() {
        return path;
    }

    public String getPolicy() {
        return policy;
    }

    public String getBindTime() {
        return bindTime;
    }
}
