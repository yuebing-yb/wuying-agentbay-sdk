package com.aliyun.agentbay.test;

import com.aliyun.agentbay.agent.AgentEvent;
import com.aliyun.agentbay.agent.StreamOptions;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for Agent streaming functionality.
 */
class AgentStreamingTest {

    @Test
    void testAgentEventFields() {
        AgentEvent event = new AgentEvent("reasoning", 1, 1);
        event.setContent("thinking...");

        assertEquals("reasoning", event.getType());
        assertEquals(1, event.getSeq());
        assertEquals(1, event.getRound());
        assertEquals("thinking...", event.getContent());
    }

    @Test
    void testAgentEventToolCall() {
        AgentEvent event = new AgentEvent("tool_call", 2, 1);
        event.setToolCallId("call_001");
        event.setToolName("click");
        Map<String, Object> args = new HashMap<>();
        args.put("x", 100);
        event.setArgs(args);

        assertEquals("tool_call", event.getType());
        assertEquals("click", event.getToolName());
        assertEquals(100, event.getArgs().get("x"));
    }

    @Test
    void testAgentEventError() {
        AgentEvent event = new AgentEvent("error", 3, 1);
        Map<String, Object> error = new HashMap<>();
        error.put("message", "something went wrong");
        event.setError(error);

        assertEquals("error", event.getType());
        assertEquals("something went wrong", event.getError().get("message"));
    }

    @Test
    void testStreamOptionsNoStreamBeta() {
        StreamOptions opts = new StreamOptions();
        assertFalse(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnEvent() {
        StreamOptions opts = StreamOptions.builder()
                .onEvent(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnReasoning() {
        StreamOptions opts = StreamOptions.builder()
                .onReasoning(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnContent() {
        StreamOptions opts = StreamOptions.builder()
                .onContent(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnToolCall() {
        StreamOptions opts = StreamOptions.builder()
                .onToolCall(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnToolResult() {
        StreamOptions opts = StreamOptions.builder()
                .onToolResult(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsWithOnError() {
        StreamOptions opts = StreamOptions.builder()
                .onError(e -> {})
                .build();
        assertTrue(opts.hasStreamingParams());
    }

    @Test
    void testStreamOptionsBuilderAllCallbacks() {
        StreamOptions opts = StreamOptions.builder()
                .onEvent(e -> {})
                .onReasoning(e -> {})
                .onContent(e -> {})
                .onToolCall(e -> {})
                .onToolResult(e -> {})
                .onError(e -> {})
                .build();

        assertNotNull(opts.getOnEvent());
        assertNotNull(opts.getOnReasoning());
        assertNotNull(opts.getOnContent());
        assertNotNull(opts.getOnToolCall());
        assertNotNull(opts.getOnToolResult());
        assertNotNull(opts.getOnError());
        assertTrue(opts.hasStreamingParams());
    }
}
