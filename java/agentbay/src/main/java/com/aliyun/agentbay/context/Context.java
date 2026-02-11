package com.aliyun.agentbay.context;

import java.util.Map;

/**
 * Represents a persistent storage context in the AgentBay cloud environment.
 * 
 * <p>A Context provides persistent storage that can be shared across multiple sessions.
 * It allows data to be preserved between session lifecycles and enables collaboration
 * between different sessions.</p>
 */
public class Context {
    /**
     * The unique identifier of the context.
     */
    private String contextId;
    
    /**
     * The name of the context.
     */
    private String name;
    
    /**
     * Description of the context.
     */
    private String description;
    
    /**
     * Additional metadata associated with the context.
     */
    private Map<String, Object> metadata;
    
    /**
     * Date and time when the Context was created.
     */
    private String createdAt;
    
    /**
     * Date and time when the Context was last updated.
     */
    private String updatedAt;
    
    /**
     * Current state of the context (e.g., "available", "clearing").
     */
    private String state;
    
    /**
     * Operating system type of the context.
     */
    private String osType;

    public Context() {
    }

    public Context(String contextId, String name) {
        this.contextId = contextId;
        this.name = name;
    }

    public String getContextId() {
        return contextId;
    }

    public void setContextId(String contextId) {
        this.contextId = contextId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(String updatedAt) {
        this.updatedAt = updatedAt;
    }

    public String getId() {
        return contextId;
    }

    public String getState() {
        return state;
    }

    public void setState(String state) {
        this.state = state;
    }

    public String getOsType() {
        return osType;
    }

    public void setOsType(String osType) {
        this.osType = osType;
    }

}