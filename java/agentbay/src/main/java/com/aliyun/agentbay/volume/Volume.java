package com.aliyun.agentbay.volume;

/**
 * Block storage volume (data disk).
 *
 * Note: This is a beta feature and may change in future releases.
 */
public class Volume {
    private String id;
    private String name;
    private String status;

    public Volume() {}

    public Volume(String id, String name) {
        this.id = id;
        this.name = name;
    }

    public Volume(String id, String name, String status) {
        this.id = id;
        this.name = name;
        this.status = status;
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

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}


