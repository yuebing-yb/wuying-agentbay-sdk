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
            imageId = "imgc-0ab5ta4n2htfrppyw";
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
        List<Long> stdoutTimesMs = new ArrayList<>();
        List<Object> errors = new ArrayList<>();

        long startMs = System.currentTimeMillis();
        EnhancedCodeExecutionResult r = session.getCode().runCode(
            "import time\n" +
                "print('hello', flush=True)\n" +
                "time.sleep(1.0)\n" +
                "print(2, flush=True)\n",
            "python",
            60,
            true,
            chunk -> {
                stdoutChunks.add(chunk);
                stdoutTimesMs.add(System.currentTimeMillis());
            },
            null,
            errors::add
        );
        long endMs = System.currentTimeMillis();

        assertTrue("errors should be empty, got=" + errors, errors.isEmpty());
        assertTrue("expected success, error_message=" + r.getErrorMessage(), r.isSuccess());
        assertTrue("expected >=2 stdout chunks, got=" + stdoutChunks.size(), stdoutChunks.size() >= 2);
        assertTrue("expected duration >=1.0s, got=" + (endMs - startMs) + "ms", (endMs - startMs) >= 1000);

        String joined = String.join("", stdoutChunks);
        assertTrue("expected stdout contains hello, got=" + joined, joined.contains("hello"));
        assertTrue("expected stdout contains 2, got=" + joined, joined.contains("2"));

        Long helloT = null;
        Long twoT = null;
        for (int i = 0; i < stdoutChunks.size(); i += 1) {
            String chunk = stdoutChunks.get(i);
            long t = stdoutTimesMs.get(i);
            if (helloT == null && chunk.contains("hello")) {
                helloT = t;
            }
            if (twoT == null && chunk.contains("2")) {
                twoT = t;
            }
        }
        assertNotNull("hello not observed in stdout chunks: " + stdoutChunks, helloT);
        assertNotNull("2 not observed in stdout chunks: " + stdoutChunks, twoT);
        assertTrue("stdout did not behave like streaming; delta=" + (twoT - helloT) + "ms", (twoT - helloT) >= 800);
    }
}

