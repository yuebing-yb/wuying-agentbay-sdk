package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.Assume;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.*;

public class RunCodeWsStreamingBetaIntegrationTest {
    private static AgentBay agentBay;
    private static Session session;

    @BeforeClass
    public static void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue(apiKey != null && !apiKey.isEmpty());

        agentBay = new AgentBay(apiKey);

        String imageId = System.getenv("AGENTBAY_WS_IMAGE_ID");
        if (imageId == null || imageId.isEmpty()) {
            imageId = "imgc-0ab5taki2khozz0p8";
        }

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(imageId);
        SessionResult created = agentBay.create(params);
        assertTrue("Failed to create session: " + created.getErrorMessage(), created.isSuccess());
        session = created.getSession();
        assertNotNull(session);
        assertNotNull("wsUrl should not be null", session.getWsUrl());
        assertFalse("wsUrl should not be empty", session.getWsUrl().isEmpty());
    }

    @AfterClass
    public static void tearDown() {
        if (session != null && agentBay != null) {
            try {
                DeleteResult deleteResult = agentBay.delete(session, false);
                if (!deleteResult.isSuccess()) {
                    System.err.println("Failed to delete session: " + deleteResult.getErrorMessage());
                }
            } catch (Exception e) {
                System.err.println("Cleanup error: " + e.getMessage());
            }
        }
    }

    @Test
    public void testRunCodeWsStreamingBetaE2E() {
        List<String> stdoutChunks = new ArrayList<>();
        List<String> errors = new ArrayList<>();

        EnhancedCodeExecutionResult r = session.getCode().runCode(
            "import time\nprint('hello', flush=True)\ntime.sleep(1.0)\nprint(2, flush=True)\n",
            "python",
            60,
            true,
            stdoutChunks::add,
            null,
            err -> errors.add(String.valueOf(err))
        );

        assertTrue("errors should be empty: " + errors, errors.isEmpty());
        assertTrue("expected success: " + r.getErrorMessage(), r.isSuccess());
        assertTrue("expected >=2 stdout events, got " + stdoutChunks.size(), stdoutChunks.size() >= 2);

        String joined = String.join("", stdoutChunks);
        assertTrue("expected stdout contains hello", joined.contains("hello"));
        assertTrue("expected stdout contains 2", joined.contains("2"));
    }
}

