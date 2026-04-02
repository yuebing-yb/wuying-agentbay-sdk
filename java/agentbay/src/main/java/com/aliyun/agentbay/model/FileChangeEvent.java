package com.aliyun.agentbay.model;

import java.util.Map;

/**
 * Represents a single file change event detected in a watched directory.
 */
public class FileChangeEvent {
    private final String eventType;
    private final String path;
    private final String pathType;

    public FileChangeEvent(String eventType, String path, String pathType) {
        this.eventType = eventType != null ? eventType : "";
        this.path = path != null ? path : "";
        this.pathType = pathType != null ? pathType : "";
    }

    public String getEventType() {
        return eventType;
    }

    public String getPath() {
        return path;
    }

    public String getPathType() {
        return pathType;
    }

    /**
     * Create a FileChangeEvent from a raw dictionary (Map).
     */
    public static FileChangeEvent fromDict(Map<String, Object> dict) {
        String eventType = dict.get("eventType") instanceof String ? (String) dict.get("eventType") : "";
        String path = dict.get("path") instanceof String ? (String) dict.get("path") : "";
        String pathType = dict.get("pathType") instanceof String ? (String) dict.get("pathType") : "";
        return new FileChangeEvent(eventType, path, pathType);
    }

    @Override
    public String toString() {
        return "FileChangeEvent(eventType='" + eventType +
            "', path='" + path +
            "', pathType='" + pathType + "')";
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof FileChangeEvent)) return false;
        FileChangeEvent that = (FileChangeEvent) o;
        return eventType.equals(that.eventType) &&
            path.equals(that.path) &&
            pathType.equals(that.pathType);
    }

    @Override
    public int hashCode() {
        int result = eventType.hashCode();
        result = 31 * result + path.hashCode();
        result = 31 * result + pathType.hashCode();
        return result;
    }
}
