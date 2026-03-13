package com.aliyun.agentbay.agent;

import java.util.function.Function;

/**
 * Options for mobile task execution, including streaming callbacks.
 * Extends StreamOptions with mobile-specific options like maxSteps and onCallForUser.
 */
public class MobileTaskOptions extends StreamOptions {
    private int maxSteps = 50;
    private Function<AgentEvent, String> onCallForUser;

    public MobileTaskOptions() {
        super();
    }

    public int getMaxSteps() {
        return maxSteps;
    }

    public void setMaxSteps(int maxSteps) {
        this.maxSteps = maxSteps;
    }

    public Function<AgentEvent, String> getOnCallForUser() {
        return onCallForUser;
    }

    public void setOnCallForUser(Function<AgentEvent, String> onCallForUser) {
        this.onCallForUser = onCallForUser;
    }

    @Override
    public boolean hasStreamingParams() {
        return super.hasStreamingParams() || onCallForUser != null;
    }

    public static MobileBuilder mobileBuilder() {
        return new MobileBuilder();
    }

    public static class MobileBuilder {
        private final MobileTaskOptions options;

        MobileBuilder() {
            this.options = new MobileTaskOptions();
        }

        public MobileBuilder maxSteps(int maxSteps) {
            options.setMaxSteps(maxSteps);
            return this;
        }

        public MobileBuilder onReasoning(java.util.function.Consumer<AgentEvent> cb) {
            options.setOnReasoning(cb);
            return this;
        }

        public MobileBuilder onContent(java.util.function.Consumer<AgentEvent> cb) {
            options.setOnContent(cb);
            return this;
        }

        public MobileBuilder onToolCall(java.util.function.Consumer<AgentEvent> cb) {
            options.setOnToolCall(cb);
            return this;
        }

        public MobileBuilder onToolResult(java.util.function.Consumer<AgentEvent> cb) {
            options.setOnToolResult(cb);
            return this;
        }

        public MobileBuilder onError(java.util.function.Consumer<AgentEvent> cb) {
            options.setOnError(cb);
            return this;
        }

        public MobileBuilder onCallForUser(Function<AgentEvent, String> cb) {
            options.setOnCallForUser(cb);
            return this;
        }

        public MobileTaskOptions build() {
            return options;
        }
    }
}
