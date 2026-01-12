package com.aliyun.agentbay.model;

import java.util.Map;

public class DirectoryEntry {
    private final Map<String, Object> data;

    public DirectoryEntry(Map<String, Object> data) {
        this.data = data;
    }

    public String getName() {
        return (String) data.get("name");
    }

    public boolean isFile() {
        Object isFile = data.get("isFile");
        if (isFile != null) {
            return (Boolean) isFile;
        }
        isFile = data.get("is_file");
        return isFile != null && (Boolean) isFile;
    }

    public boolean isDirectory() {
        Object isDirectory = data.get("isDirectory");
        if (isDirectory != null) {
            return (Boolean) isDirectory;
        }
        isDirectory = data.get("is_directory");
        return isDirectory != null && (Boolean) isDirectory;
    }

    public Long getSize() {
        Object size = data.get("size");
        if (size instanceof Number) {
            return ((Number) size).longValue();
        }
        return 0L;
    }

    public Map<String, Object> getData() {
        return data;
    }
}
