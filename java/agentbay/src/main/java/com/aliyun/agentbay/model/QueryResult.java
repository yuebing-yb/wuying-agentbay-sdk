package com.aliyun.agentbay.model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class QueryResult extends ApiResponse {
    private boolean success;
    private String errorMessage;
    private String taskId;
    private String taskStatus;
    private String taskAction;
    private String taskProduct;
    private List<Map<String, Object>> stream;
    private String error;

    public QueryResult() {
        super();
        this.success = false;
        this.errorMessage = "";
        this.taskId = "";
        this.taskStatus = "";
        this.taskAction = "";
        this.taskProduct = "";
        this.stream = new ArrayList<>();
        this.error = "";
    }

    public QueryResult(String requestId, boolean success, String errorMessage,
                      String taskId, String taskStatus) {
        super(requestId);
        this.success = success;
        this.errorMessage = errorMessage;
        this.taskId = taskId;
        this.taskStatus = taskStatus;
        this.taskAction = "";
        this.taskProduct = "";
        this.stream = new ArrayList<>();
        this.error = "";
    }

    public QueryResult(String requestId, boolean success, String errorMessage,
                      String taskId, String taskStatus, String taskAction, String taskProduct) {
        super(requestId);
        this.success = success;
        this.errorMessage = errorMessage;
        this.taskId = taskId;
        this.taskStatus = taskStatus;
        this.taskAction = taskAction;
        this.taskProduct = taskProduct;
        this.stream = new ArrayList<>();
        this.error = "";
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

    public String getTaskId() {
        return taskId;
    }

    public void setTaskId(String taskId) {
        this.taskId = taskId;
    }

    public String getTaskStatus() {
        return taskStatus;
    }

    public void setTaskStatus(String taskStatus) {
        this.taskStatus = taskStatus;
    }

    public String getTaskAction() {
        return taskAction;
    }

    public void setTaskAction(String taskAction) {
        this.taskAction = taskAction;
    }

    public String getTaskProduct() {
        return taskProduct;
    }

    public void setTaskProduct(String taskProduct) {
        this.taskProduct = taskProduct;
    }

    public List<Map<String, Object>> getStream() {
        return stream;
    }

    public void setStream(List<Map<String, Object>> stream) {
        this.stream = stream != null ? stream : new ArrayList<>();
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error != null ? error : "";
    }
}
