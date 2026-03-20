package com.aliyun.agentbay.agent;

import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import com.aliyun.agentbay.model.ExecutionResult;

/**
 * Represents a running task that can be waited on for its final result.
 * Returned by Mobile.executeTask() when the task is started.
 */
public class TaskExecution {
    private final String taskId;
    private final CompletableFuture<ExecutionResult> resultFuture;
    private final Runnable cancelFn;

    public TaskExecution(String taskId, CompletableFuture<ExecutionResult> resultFuture) {
        this(taskId, resultFuture, null);
    }

    public TaskExecution(String taskId, CompletableFuture<ExecutionResult> resultFuture, Runnable cancelFn) {
        this.taskId = taskId;
        this.resultFuture = resultFuture;
        this.cancelFn = cancelFn;
    }

    public String getTaskId() {
        return taskId;
    }

    /**
     * Block until the task finishes or the timeout (in seconds) is reached.
     */
    public ExecutionResult wait(int timeout) {
        try {
            if (timeout > 0) {
                return resultFuture.get(timeout, TimeUnit.SECONDS);
            }
            return resultFuture.get();
        } catch (TimeoutException e) {
            if (cancelFn != null) {
                try {
                    cancelFn.run();
                } catch (Exception ignored) {
                }
            }
            return new ExecutionResult("", false,
                    "Task execution timed out after " + timeout + " seconds.",
                    taskId, "failed", "Task execution timed out.");
        } catch (Exception e) {
            return new ExecutionResult("", false,
                    "Failed to wait for result: " + e.getMessage(),
                    taskId, "failed", "Task Failed");
        }
    }
}
