package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.Assume;
import org.junit.BeforeClass;
import org.junit.Ignore;
import org.junit.Test;

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
    @Ignore("Streaming API temporarily disabled; will be re-enabled in a future release")
    public void testRunCodeWsStreamingBetaE2E() {
        // Streaming runCode overload was removed in this release.
        // Test body will be restored when the streaming API is re-enabled.
    }
}

