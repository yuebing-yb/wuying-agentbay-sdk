package com.aliyun.agentbay.agent;

import java.util.function.Consumer;

/**
 * Options for WebSocket streaming execution of agent tasks.
 *
 * <p>When any callback is set, the SDK uses the WebSocket streaming channel
 * for real-time event delivery instead of HTTP polling.</p>
 */
public class StreamOptions {
    private Consumer<AgentEvent> onReasoning;
    private Consumer<AgentEvent> onContent;
    private Consumer<AgentEvent> onToolCall;
    private Consumer<AgentEvent> onToolResult;
    private Consumer<AgentEvent> onError;

    public StreamOptions() {
        this.onReasoning = null;
        this.onContent = null;
        this.onToolCall = null;
        this.onToolResult = null;
        this.onError = null;
    }

    /**
     * Returns the callback for reasoning events (LLM reasoning_content).
     */
    public Consumer<AgentEvent> getOnReasoning() {
        return onReasoning;
    }

    public void setOnReasoning(Consumer<AgentEvent> onReasoning) {
        this.onReasoning = onReasoning;
    }

    /**
     * Returns the callback for content events (LLM content output).
     */
    public Consumer<AgentEvent> getOnContent() {
        return onContent;
    }

    public void setOnContent(Consumer<AgentEvent> onContent) {
        this.onContent = onContent;
    }

    /**
     * Returns the callback for tool_call events.
     */
    public Consumer<AgentEvent> getOnToolCall() {
        return onToolCall;
    }

    public void setOnToolCall(Consumer<AgentEvent> onToolCall) {
        this.onToolCall = onToolCall;
    }

    /**
     * Returns the callback for tool_result events.
     */
    public Consumer<AgentEvent> getOnToolResult() {
        return onToolResult;
    }

    public void setOnToolResult(Consumer<AgentEvent> onToolResult) {
        this.onToolResult = onToolResult;
    }

    /**
     * Returns the callback for error events.
     */
    public Consumer<AgentEvent> getOnError() {
        return onError;
    }

    public void setOnError(Consumer<AgentEvent> onError) {
        this.onError = onError;
    }

    /**
     * Returns true if streaming should be used (any callback is set).
     */
    public boolean hasStreamingParams() {
        return onReasoning != null
                || onContent != null || onToolCall != null
                || onToolResult != null || onError != null;
    }

    /**
     * Builder for StreamOptions.
     */
    public static Builder builder() {
        return new Builder();
    }

    public static class Builder {
        private final StreamOptions options;

        Builder() {
            this.options = new StreamOptions();
        }

        public Builder onReasoning(Consumer<AgentEvent> onReasoning) {
            options.setOnReasoning(onReasoning);
            return this;
        }

        public Builder onContent(Consumer<AgentEvent> onContent) {
            options.setOnContent(onContent);
            return this;
        }

        public Builder onToolCall(Consumer<AgentEvent> onToolCall) {
            options.setOnToolCall(onToolCall);
            return this;
        }

        public Builder onToolResult(Consumer<AgentEvent> onToolResult) {
            options.setOnToolResult(onToolResult);
            return this;
        }

        public Builder onError(Consumer<AgentEvent> onError) {
            options.setOnError(onError);
            return this;
        }

        public StreamOptions build() {
            return options;
        }
    }
}
