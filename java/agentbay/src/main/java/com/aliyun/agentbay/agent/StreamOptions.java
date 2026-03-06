package com.aliyun.agentbay.agent;

import java.util.function.Consumer;

/**
 * Options for WebSocket streaming execution of agent tasks.
 *
 * <p>When {@link #isStreamBeta()} is true or any callback is set, the SDK uses
 * the WebSocket streaming channel for real-time event delivery instead of HTTP polling.</p>
 */
public class StreamOptions {
    private boolean streamBeta;
    private Consumer<AgentEvent> onEvent;
    private Consumer<AgentEvent> onReasoning;
    private Consumer<AgentEvent> onContent;
    private Consumer<AgentEvent> onToolCall;
    private Consumer<AgentEvent> onToolResult;

    public StreamOptions() {
        this.streamBeta = false;
        this.onEvent = null;
        this.onReasoning = null;
        this.onContent = null;
        this.onToolCall = null;
        this.onToolResult = null;
    }

    /**
     * Returns whether token-level streaming via WebSocket is enabled.
     */
    public boolean isStreamBeta() {
        return streamBeta;
    }

    public void setStreamBeta(boolean streamBeta) {
        this.streamBeta = streamBeta;
    }

    /**
     * Returns the callback for all event types.
     */
    public Consumer<AgentEvent> getOnEvent() {
        return onEvent;
    }

    public void setOnEvent(Consumer<AgentEvent> onEvent) {
        this.onEvent = onEvent;
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
     * Returns true if streaming should be used (streamBeta or any callback is set).
     */
    public boolean hasStreamingParams() {
        return streamBeta || onEvent != null || onReasoning != null
                || onContent != null || onToolCall != null || onToolResult != null;
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

        public Builder streamBeta(boolean streamBeta) {
            options.setStreamBeta(streamBeta);
            return this;
        }

        public Builder onEvent(Consumer<AgentEvent> onEvent) {
            options.setOnEvent(onEvent);
            return this;
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

        public StreamOptions build() {
            return options;
        }
    }
}
