package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.agent.AgentEvent;
import com.aliyun.agentbay.model.ExecutionResult;
import com.aliyun.agentbay.agent.MobileTaskOptions;
import org.junit.jupiter.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Integration tests for Mobile Agent streaming output feature.
 *
 * Tests the WS-based streaming execution path with real backend services.
 * Uses debug image imgc-0ab5takhnmlvhx9gp for Mobile Agent.
 */
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class MobileAgentStreamingIntegrationTest {

    private static final Logger logger = LoggerFactory.getLogger(MobileAgentStreamingIntegrationTest.class);
    private static AgentBay agentBay;
    private static Session session;

    @BeforeAll
    static void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            logger.warn("AGENTBAY_API_KEY not set, skipping tests");
            return;
        }

        agentBay = new AgentBay(apiKey);
        Thread.sleep(3000);

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("imgc-0ab5takhnmlvhx9gp");
        SessionResult result = agentBay.create(params);
        if (!result.isSuccess() || result.getSession() == null) {
            logger.error("Failed to create session: {}", result.getErrorMessage());
            return;
        }

        session = result.getSession();
        logger.info("Session created: {}", session.getSessionId());
    }

    @AfterAll
    static void tearDown() {
        if (session != null) {
            try {
                logger.info("Cleaning up session: {}", session.getSessionId());
                session.delete();
                logger.info("Session deleted");
            } catch (Exception e) {
                logger.warn("Error deleting session: {}", e.getMessage());
            }
        }
    }

    @Test
    @Order(1)
    void testMobileStreamingWithTypedCallbacks() {
        Assumptions.assumeTrue(session != null, "Session not created");

        List<AgentEvent> reasoningEvents = new ArrayList<>();
        List<AgentEvent> contentEvents = new ArrayList<>();
        List<AgentEvent> toolCalls = new ArrayList<>();
        List<AgentEvent> toolResults = new ArrayList<>();

        MobileTaskOptions options = MobileTaskOptions.mobileBuilder()
                .maxSteps(10)
                .onReasoning(event -> {
                    reasoningEvents.add(event);
                    logger.info("[Reasoning] round={}: {}", event.getRound(),
                            event.getContent() != null && event.getContent().length() > 100
                                    ? event.getContent().substring(0, 100) + "..."
                                    : event.getContent());
                })
                .onContent(event -> {
                    contentEvents.add(event);
                    logger.info("[Content] round={}: {}", event.getRound(),
                            event.getContent() != null && event.getContent().length() > 100
                                    ? event.getContent().substring(0, 100) + "..."
                                    : event.getContent());
                })
                .onToolCall(event -> {
                    toolCalls.add(event);
                    logger.info("[ToolCall] round={}: {}({})", event.getRound(), event.getToolName(), event.getArgs());
                })
                .onToolResult(event -> {
                    toolResults.add(event);
                    logger.info("[ToolResult] round={}: {}", event.getRound(), event.getToolName());
                })
                .build();

        logger.info("Testing mobile agent streaming with typed callbacks");

        ExecutionResult result = session.getAgent().getMobile()
                .executeTaskAndWait("Open Settings app", 180, options);

        logger.info("Result: success={}, status={}", result.isSuccess(), result.getTaskStatus());
        logger.info("Reasoning: {}, Content: {}, ToolCalls: {}, ToolResults: {}",
                reasoningEvents.size(), contentEvents.size(), toolCalls.size(), toolResults.size());

        assertNotNull(result.getTaskStatus());
    }
}
