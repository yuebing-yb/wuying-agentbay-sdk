package com.aliyun.agentbay.context;

import com.aliyun.agentbay.model.ApiResponse;
import java.util.List;

/**
 * Result of a listBindings() operation.
 */
public class ContextBindingsResult extends ApiResponse {
    private boolean success;
    private List<ContextBinding> bindings;
    private String errorMessage;

    public ContextBindingsResult(String requestId, boolean success, List<ContextBinding> bindings) {
        this(requestId, success, bindings, null);
    }

    public ContextBindingsResult(String requestId, boolean success, List<ContextBinding> bindings, String errorMessage) {
        super(requestId);
        this.success = success;
        this.bindings = bindings;
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public List<ContextBinding> getBindings() {
        return bindings;
    }

    public String getErrorMessage() {
        return errorMessage;
    }
}
