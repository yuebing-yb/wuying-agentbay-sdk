package com.aliyun.agentbay.volume;

/**
 * Block storage volume (data disk).
 *
 * Note: This is a beta feature and may change in future releases.
 */
public class Volume {
    private String id;
    private String name;
    private String belongingImageId;
    private String status;
    private String createdAt;

    public Volume() {}

    public Volume(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getBelongingImageId() {
        return belongingImageId;
    }

    public void setBelongingImageId(String belongingImageId) {
        this.belongingImageId = belongingImageId;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }
}


