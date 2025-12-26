package com.aliyun.agentbay.context;

import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;

public class ContextManager {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Session session;

    public ContextManager(Session session) {
        this.session = session;
    }

    /**
     * Get context info for the session
     */
    public ContextInfoResult info() {
        return info(null, null, null);
    }

    /**
     * Get context info with optional filters
     *
     * @param contextId Context ID filter (optional)
     * @param path Path filter (optional)
     * @param taskType Task type filter (optional)
     * @return ContextInfoResult containing status data
     */
    public ContextInfoResult info(String contextId, String path, String taskType) {
        try {
            GetContextInfoRequest request = new GetContextInfoRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());

            if (contextId != null) {
                request.setContextId(contextId);
            }
            if (path != null) {
                request.setPath(path);
            }
            if (taskType != null) {
                request.setTaskType(taskType);
            }
            GetContextInfoResponse response = session.getAgentBay().getClient().getContextInfo(request);

            String requestId = ResponseUtil.extractRequestId(response);
            List<ContextStatusData> contextStatusData = new ArrayList<>();

            if (response != null && response.getBody() != null) {
                GetContextInfoResponseBody body = response.getBody();
                
                // Check for API-level errors
                Boolean bodySuccess = body.getSuccess();
                if (bodySuccess != null && !bodySuccess && body.getCode() != null) {
                    String code = body.getCode();
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    String errorMessage = String.format("[%s] %s", code, message);
                    return new ContextInfoResult(requestId, false, contextStatusData, errorMessage);
                }
                
                if (body.getData() != null) {
                    String contextStatus = body.getData().getContextStatus();
                    if (contextStatus != null && !contextStatus.isEmpty()) {
                        try {
                            // Parse the context status JSON
                            JsonNode statusItems = objectMapper.readTree(contextStatus);
                            for (JsonNode item : statusItems) {
                                if ("data".equals(item.get("type").asText())) {
                                    String dataString = item.get("data").asText();
                                    JsonNode dataItems = objectMapper.readTree(dataString);
                                    for (JsonNode dataItem : dataItems) {
                                        Map<String, Object> itemMap = objectMapper.convertValue(dataItem, Map.class);
                                        contextStatusData.add(ContextStatusData.fromMap(itemMap));
                                    }
                                }
                            }
                        } catch (Exception e) {
                        }
                    }
                }
            }

            return new ContextInfoResult(requestId, true, contextStatusData, "");

        } catch (Exception e) {
            return new ContextInfoResult("", false, new ArrayList<>(), "Failed to get context info: " + e.getMessage());
        }
    }

    /**
     * Sync context data (trigger upload)
     */
    public ContextSyncResult sync() {
        return sync(null, null, null);
    }

    /**
     * Sync context data with optional parameters
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @return ContextSyncResult indicating success/failure
     */
    public ContextSyncResult sync(String contextId, String path, String mode) {
        try {
            SyncContextRequest request = new SyncContextRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());

            if (contextId != null) {
                request.setContextId(contextId);
            }
            if (path != null) {
                request.setPath(path);
            }
            if (mode != null) {
                request.setMode(mode);
            }
            SyncContextResponse response = session.getAgentBay().getClient().syncContext(request);

            String requestId = ResponseUtil.extractRequestId(response);
            boolean success = false;
            String errorMessage = "";

            if (response != null && response.getBody() != null) {
                SyncContextResponseBody body = response.getBody();
                success = body.getSuccess() != null ? body.getSuccess() : false;
                
                // Check for API-level errors
                if (!success && body.getCode() != null) {
                    String code = body.getCode();
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    errorMessage = String.format("[%s] %s", code, message);
                }
            }

            return new ContextSyncResult(requestId, success, errorMessage);

        } catch (Exception e) {
            return new ContextSyncResult("", false, "Failed to sync context: " + e.getMessage());
        }
    }

    /**
     * Sync context data with callback mode (non-blocking)
     * Returns immediately and calls the callback when sync completes
     *
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(Consumer<Boolean> callback) {
        return sync(null, null, null, callback);
    }

    /**
     * Sync context data with optional parameters and callback mode (non-blocking)
     * Returns immediately and calls the callback when sync completes
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback) {
        return sync(contextId, path, mode, callback, 150, 1500);
    }

    /**
     * Sync context data with optional parameters and callback mode (non-blocking)
     * Returns immediately and calls the callback when sync completes
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @param maxRetries Maximum number of retries for polling completion status (default: 150)
     * @param retryInterval Milliseconds to wait between retries (default: 2000)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback,
                                  int maxRetries, int retryInterval) {
        // First trigger the sync
        ContextSyncResult syncResult = sync(contextId, path, mode);

        if (!syncResult.isSuccess()) {
            // If sync trigger failed, call callback with false
            if (callback != null) {
                callback.accept(false);
            }
            return syncResult;
        }

        // Start polling in background thread
        if (callback != null) {
            Thread pollThread = new Thread(() -> {
                pollForCompletion(callback, contextId, path, maxRetries, retryInterval);
            });
            pollThread.setDaemon(true);
            pollThread.start();
        }

        return syncResult;
    }

    /**
     * Polls the info interface to check if sync is completed and calls callback
     *
     * @param callback Callback function that receives success status
     * @param contextId ID of the context to check
     * @param path Path to check
     * @param maxRetries Maximum number of retries
     * @param retryInterval Milliseconds to wait between retries
     */
    private void pollForCompletion(Consumer<Boolean> callback, String contextId, String path,
                                   int maxRetries, int retryInterval) {
        for (int retry = 0; retry < maxRetries; retry++) {
            try {
                // Get context status data
                ContextInfoResult infoResult = info(contextId, path, null);

                // Check if all sync tasks are completed
                boolean allCompleted = true;
                boolean hasFailure = false;
                boolean hasSyncTasks = false;

                for (ContextStatusData item : infoResult.getContextStatusData()) {
                    // We only care about sync tasks (upload/download)
                    String taskType = item.getTaskType();
                    if (taskType == null || (!"upload".equals(taskType) && !"download".equals(taskType))) {
                        continue;
                    }

                    hasSyncTasks = true;
                    if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                        allCompleted = false;
                        break;
                    }

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                if (allCompleted || !hasSyncTasks) {
                    // All tasks completed or no sync tasks found
                    if (hasFailure) {
                        callback.accept(false);
                    } else if (hasSyncTasks) {
                        callback.accept(true);
                    } else {
                        callback.accept(true);
                    }
                    return;
                }
                Thread.sleep(retryInterval);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                callback.accept(false);
                return;
            } catch (Exception e) {
                try {
                    Thread.sleep(retryInterval);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    callback.accept(false);
                    return;
                }
            }
        }

        // Timeout
        callback.accept(false);
    }

    /**
     * Sync context data and wait for completion
     *
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait() {
        return syncAndWait(null, null, null);
    }

    /**
     * Sync context data with optional parameters and wait for completion
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait(String contextId, String path, String mode) {
        return syncAndWait(contextId, path, mode, 150, 1500);
    }

    /**
     * Sync context data with optional parameters and wait for completion
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @param maxRetries Maximum number of retries for polling completion status (default: 150)
     * @param retryInterval Milliseconds to wait between retries (default: 2000)
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait(String contextId, String path, String mode, 
                                         int maxRetries, int retryInterval) {
        // First trigger the sync
        ContextSyncResult syncResult = sync(contextId, path, mode);
        
        if (!syncResult.isSuccess()) {
            return syncResult;
        }

        // Wait for sync to complete
        for (int retry = 0; retry < maxRetries; retry++) {
            try {
                // Get context status data
                ContextInfoResult infoResult = info(contextId, path, null);

                // Check if all sync tasks are completed
                boolean allCompleted = true;
                boolean hasFailure = false;
                boolean hasSyncTasks = false;

                for (ContextStatusData item : infoResult.getContextStatusData()) {
                    // We only care about sync tasks (upload/download)
                    String taskType = item.getTaskType();
                    if (taskType == null || (!"upload".equals(taskType) && !"download".equals(taskType))) {
                        continue;
                    }

                    hasSyncTasks = true;
                    if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                        allCompleted = false;
                        break;
                    }

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                if (allCompleted || !hasSyncTasks) {
                    // All tasks completed or no sync tasks found
                    if (hasFailure) {
                        return new ContextSyncResult(syncResult.getRequestId(), false);
                    } else if (hasSyncTasks) {
                        return new ContextSyncResult(syncResult.getRequestId(), true);
                    } else {
                        return new ContextSyncResult(syncResult.getRequestId(), true);
                    }
                }
                Thread.sleep(retryInterval);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new ContextSyncResult(syncResult.getRequestId(), false);
            } catch (Exception e) {
                try {
                    Thread.sleep(retryInterval);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return new ContextSyncResult(syncResult.getRequestId(), false);
                }
            }
        }

        // Timeout
        return new ContextSyncResult(syncResult.getRequestId(), false);
    }

}
