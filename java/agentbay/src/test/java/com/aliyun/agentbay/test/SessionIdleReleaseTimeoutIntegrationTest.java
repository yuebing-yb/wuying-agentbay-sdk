package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.wuyingai20250506.models.GetSessionRequest;
import com.aliyun.wuyingai20250506.models.GetSessionResponse;
import org.junit.Assume;
import org.junit.Test;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public class SessionIdleReleaseTimeoutIntegrationTest {

    private static boolean isNotFound(Throwable e) {
        if (!(e instanceof com.aliyun.tea.TeaException)) {
            return false;
        }
        com.aliyun.tea.TeaException te = (com.aliyun.tea.TeaException) e;
        String msg = te.getMessage() != null ? te.getMessage() : "";
        String lower = msg.toLowerCase();
        return lower.contains("invalidmcpsession.notfound") || lower.contains("notfound") || lower.contains("not found");
    }

    private static String getSessionStatus(AgentBay agentBay, String apiKey, String sessionId) throws Exception {
        GetSessionRequest req = new GetSessionRequest();
        req.setAuthorization("Bearer " + apiKey);
        req.setSessionId(sessionId);
        GetSessionResponse resp = agentBay.client.getSession(req);
        if (resp == null || resp.getBody() == null || resp.getBody().getData() == null) {
            return "";
        }
        return resp.getBody().getData().getStatus() != null ? resp.getBody().getData().getStatus() : "";
    }

    @Test
    public void testSessionIdleReleaseTimeout() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY must be set for integration tests", apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);

        int idleReleaseTimeoutSeconds = 60;
        int maxOverSeconds = 60;
        String imageId = "computer-use-ubuntu-2204-regionGW";

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(imageId);
        params.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);

        long start = System.currentTimeMillis();
        SessionResult createResult = agentBay.create(params);
        assertTrue(createResult.isSuccess());
        assertNotNull(createResult.getSession());
        Session session = createResult.getSession();
        String sessionId = session.getSessionId();
        assertNotNull(sessionId);

        try {
            long timeoutDeadline = start + idleReleaseTimeoutSeconds * 1000L;
            while (System.currentTimeMillis() < timeoutDeadline) {
                try {
                    String status = getSessionStatus(agentBay, apiKey, sessionId);
                    if ("FINISH".equals(status) || "DELETING".equals(status) || "DELETED".equals(status)) {
                        throw new AssertionError("Session released too early: status=" + status);
                    }
                } catch (Throwable e) {
                    if (isNotFound(e)) {
                        throw new AssertionError("Session released too early: NotFound before " + idleReleaseTimeoutSeconds + "s");
                    }
                    throw new RuntimeException(e);
                }
                long remaining = timeoutDeadline - System.currentTimeMillis();
                Thread.sleep(Math.min(2000L, Math.max(0L, remaining)));
            }

            long deadline = timeoutDeadline + maxOverSeconds * 1000L;
            while (System.currentTimeMillis() < deadline) {
                try {
                    String status = getSessionStatus(agentBay, apiKey, sessionId);
                    if ("FINISH".equals(status) || "DELETING".equals(status) || "DELETED".equals(status)) {
                        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
                        assertTrue("Session released too early, elapsed=" + elapsed, elapsed >= idleReleaseTimeoutSeconds);
                        assertTrue("Session released too late, elapsed=" + elapsed, elapsed <= idleReleaseTimeoutSeconds + maxOverSeconds);
                        return;
                    }
                } catch (Throwable e) {
                    if (isNotFound(e)) {
                        double elapsed = (System.currentTimeMillis() - start) / 1000.0;
                        assertTrue("Session released too early, elapsed=" + elapsed, elapsed >= idleReleaseTimeoutSeconds);
                        assertTrue("Session released too late, elapsed=" + elapsed, elapsed <= idleReleaseTimeoutSeconds + maxOverSeconds);
                        return;
                    }
                    throw new RuntimeException(e);
                }
                Thread.sleep(2000L);
            }

            throw new AssertionError("Session was not released within " + idleReleaseTimeoutSeconds + "s~" + (idleReleaseTimeoutSeconds + maxOverSeconds) + "s");
        } finally {
            try {
                session.delete(false);
            } catch (Exception e) {
                // ignore
            }
        }
    }
}

