package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.exception.WsCancelledException;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.AfterClass;
import org.junit.Assume;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import static org.junit.Assert.*;

public class WsStreamCancelIntegrationTest {
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
        assertNotNull("Backend did not return wsUrl/WsUrl in CreateSession response", session.getWsUrl());
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
    public void testWsStreamCancelE2E() throws Exception {
        WsClient wsClient = session.getWsClient();
        assertNotNull("wsClient should not be null", wsClient);
        wsClient.connect().join();
        String target = "wuying_codespace";
        String server = session.getMcpServerForTool("run_code");
        if (server != null && !server.isEmpty()) {
            target = server;
        }

        List<Map<String, Object>> events = new ArrayList<>();
        List<Map<String, Object>> ends = new ArrayList<>();
        List<Exception> errors = new ArrayList<>();

        Map<String, Object> params = new HashMap<>();
        params.put("language", "python");
        params.put("timeoutS", 60);
        params.put("code",
            "import time\n" +
                "print(0, flush=True)\n" +
                "time.sleep(10)\n" +
                "print(1, flush=True)\n"
        );
        Map<String, Object> data = new HashMap<>();
        data.put("method", "run_code");
        data.put("mode", "stream");
        data.put("params", params);

        WsClient.StreamHandle handle = wsClient.callStream(
            target,
            data,
            (_invocationId, d) -> events.add(d),
            (_invocationId, d) -> ends.add(d),
            (_invocationId, e) -> errors.add(e)
        ).get(60, TimeUnit.SECONDS);

        Thread.sleep(500);
        handle.cancel();

        long t0 = System.currentTimeMillis();
        try {
            handle.waitEnd().get(2, TimeUnit.SECONDS);
            fail("Expected WsCancelledException");
        } catch (ExecutionException e) {
            Throwable cause = e.getCause();
            assertNotNull(cause);
            assertTrue("Expected WsCancelledException, got " + cause, cause instanceof WsCancelledException);
        } catch (TimeoutException e) {
            fail("Timeout waiting for waitEnd after cancel");
        }
        assertTrue("cancel should return promptly", System.currentTimeMillis() - t0 < 2000);

        assertTrue("unexpected onEnd after cancel: " + ends, ends.isEmpty());
        assertEquals("expected exactly 1 onError", 1, errors.size());
        assertTrue("expected onError WsCancelledException, got " + errors.get(0), errors.get(0) instanceof WsCancelledException);
    }
}

