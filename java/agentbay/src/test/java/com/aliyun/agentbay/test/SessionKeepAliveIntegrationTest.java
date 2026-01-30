package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.wuyingai20250506.models.GetSessionRequest;
import com.aliyun.wuyingai20250506.models.GetSessionResponse;
import org.junit.Assume;
import org.junit.Test;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public class SessionKeepAliveIntegrationTest {

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

    private static boolean isReleasedByStatusString(String status) {
        return "FINISH".equals(status) || "DELETING".equals(status) || "DELETED".equals(status);
    }

    @Test
    public void testKeepAliveResetsIdleTimer() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY must be set for integration tests", apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);

        int idleReleaseTimeoutSeconds = 30;
        int maxOverSeconds = 60;
        String imageId = "linux_latest";

        CreateSessionParams controlParams = new CreateSessionParams();
        controlParams.setImageId(imageId);
        controlParams.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);

        CreateSessionParams refreshedParams = new CreateSessionParams();
        refreshedParams.setImageId(imageId);
        refreshedParams.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);

        long start = System.currentTimeMillis();

        SessionResult controlCreate = agentBay.create(controlParams);
        assertTrue(controlCreate.isSuccess());
        assertNotNull(controlCreate.getSession());
        Session control = controlCreate.getSession();
        String controlId = control.getSessionId();
        assertNotNull(controlId);

        SessionResult refreshedCreate = agentBay.create(refreshedParams);
        assertTrue(refreshedCreate.isSuccess());
        assertNotNull(refreshedCreate.getSession());
        Session refreshed = refreshedCreate.getSession();
        String refreshedId = refreshed.getSessionId();
        assertNotNull(refreshedId);

        try {
            Thread.sleep(idleReleaseTimeoutSeconds * 1000L / 2);
            assertTrue("keepAlive should succeed", refreshed.keepAlive().isSuccess());

            long deadline = start + (idleReleaseTimeoutSeconds + maxOverSeconds) * 1000L;
            while (System.currentTimeMillis() < deadline) {
                boolean controlReleased = false;
                try {
                    String s = getSessionStatus(agentBay, apiKey, controlId);
                    if (isReleasedByStatusString(s)) {
                        controlReleased = true;
                    }
                } catch (Throwable e) {
                    if (isNotFound(e)) {
                        controlReleased = true;
                    } else {
                        throw new RuntimeException(e);
                    }
                }

                if (controlReleased) {
                    boolean refreshedReleased = false;
                    try {
                        String s = getSessionStatus(agentBay, apiKey, refreshedId);
                        if (isReleasedByStatusString(s)) {
                            refreshedReleased = true;
                        }
                    } catch (Throwable e) {
                        if (isNotFound(e)) {
                            refreshedReleased = true;
                        } else {
                            throw new RuntimeException(e);
                        }
                    }
                    assertFalse("refreshed session should still be alive when control is released", refreshedReleased);
                    return;
                }

                Thread.sleep(2000L);
            }

            throw new AssertionError("Control session was not released within expected time window");
        } finally {
            try {
                refreshed.delete(false);
            } catch (Exception e) {
                // ignore
            }
            try {
                control.delete(false);
            } catch (Exception e) {
                // ignore
            }
        }
    }
}

