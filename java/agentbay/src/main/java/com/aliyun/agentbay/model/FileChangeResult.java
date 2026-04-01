package com.aliyun.agentbay.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Result of a file change detection operation.
 */
public class FileChangeResult extends ApiResponse {
    private final boolean success;
    private final List<FileChangeEvent> events;
    private final String rawData;
    private final String errorMessage;

    public FileChangeResult(String requestId, boolean success,
                            List<FileChangeEvent> events, String rawData,
                            String errorMessage) {
        super(requestId);
        this.success = success;
        this.events = events != null ? events : new ArrayList<>();
        this.rawData = rawData != null ? rawData : "";
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }

    public boolean isSuccess() {
        return success;
    }

    public List<FileChangeEvent> getEvents() {
        return events;
    }

    public String getRawData() {
        return rawData;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public boolean hasChanges() {
        return !events.isEmpty();
    }

    public List<String> getModifiedFiles() {
        List<String> result = new ArrayList<>();
        for (FileChangeEvent e : events) {
            if ("modify".equals(e.getEventType()) && "file".equals(e.getPathType())) {
                result.add(e.getPath());
            }
        }
        return result;
    }

    public List<String> getCreatedFiles() {
        List<String> result = new ArrayList<>();
        for (FileChangeEvent e : events) {
            if ("create".equals(e.getEventType()) && "file".equals(e.getPathType())) {
                result.add(e.getPath());
            }
        }
        return result;
    }

    public List<String> getDeletedFiles() {
        List<String> result = new ArrayList<>();
        for (FileChangeEvent e : events) {
            if ("delete".equals(e.getEventType()) && "file".equals(e.getPathType())) {
                result.add(e.getPath());
            }
        }
        return result;
    }
}
