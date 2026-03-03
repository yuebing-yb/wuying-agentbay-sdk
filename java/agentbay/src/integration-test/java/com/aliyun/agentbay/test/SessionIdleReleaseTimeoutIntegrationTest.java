package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.model.SessionStatusResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Assume;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public class SessionIdleReleaseTimeoutIntegrationTest {

    private static String maskSecret(String secret, int visible) {
        if (secret == null || secret.isEmpty()) {
            return "";
        }
        if (secret.length() <= visible) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < secret.length(); i++) {
                sb.append("*");
            }
            return sb.toString();
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < secret.length() - visible; i++) {
            sb.append("*");
        }
        sb.append(secret.substring(secret.length() - visible));
        return sb.toString();
    }

    private static boolean isNotFound(Throwable e) {
        if (!(e instanceof com.aliyun.tea.TeaException)) {
            return false;
        }
        com.aliyun.tea.TeaException te = (com.aliyun.tea.TeaException) e;
        String msg = te.getMessage() != null ? te.getMessage() : "";
        String lower = msg.toLowerCase();
        return lower.contains("invalidmcpsession.notfound") || lower.contains("notfound") || lower.contains("not found");
    }

    private static String getSessionStatus(Session session) {
        SessionStatusResult result = session.getStatus();
        if (result == null || !result.isSuccess()) {
            return "";
        }
        return result.getStatus() != null ? result.getStatus() : "";
    }

    private static boolean isReleasedByStatusString(String status) {
        return "FINISH".equals(status) || "DELETING".equals(status) || "DELETED".equals(status);
    }

    @Test
    public void testSessionIdleReleaseTimeout() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY must be set for integration tests", apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);

        int idleReleaseTimeoutSeconds = 60;
        int maxOverSeconds = 60;
        int pollInterval = 2;
        String imageId = "computer-use-ubuntu-2204-regionGW";

        System.out.println("api_key = " + maskSecret(apiKey, 4));
        System.out.println("Creating session with image_id=" + imageId + ", idle_release_timeout=" + idleReleaseTimeoutSeconds + "s");

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(imageId);
        params.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "idle-release-timeout");
        labels.put("sdk", "java");
        params.setLabels(labels);

        long start = System.currentTimeMillis();
        SessionResult createResult = agentBay.create(params);
        assertTrue(createResult.isSuccess());
        assertNotNull(createResult.getSession());
        Session session = createResult.getSession();
        String sessionId = session.getSessionId();
        assertNotNull(sessionId);
        System.out.println("✅ Session created: " + sessionId);

        try {
            long timeoutDeadline = start + idleReleaseTimeoutSeconds * 1000L;
            while (System.currentTimeMillis() < timeoutDeadline) {
                boolean released = false;
                try {
                    String status = getSessionStatus(session);
                    if (isReleasedByStatusString(status)) {
                        released = true;
                    }
                } catch (Throwable e) {
                    if (isNotFound(e)) {
                        released = true;
                    } else {
                        throw new RuntimeException(e);
                    }
                }
                
                if (released) {
                    throw new AssertionError("Session was released too early before " + idleReleaseTimeoutSeconds + "s");
                }
                
                long remaining = timeoutDeadline - System.currentTimeMillis();
                Thread.sleep(Math.min(pollInterval * 1000L, Math.max(0L, remaining)));
            }

            long deadline = timeoutDeadline + maxOverSeconds * 1000L;
            String lastStatus = null;
            while (System.currentTimeMillis() < deadline) {
                boolean released = false;
                try {
                    String status = getSessionStatus(session);
                    lastStatus = status;
                    if (isReleasedByStatusString(status)) {
                        released = true;
                    }
                } catch (Throwable e) {
                    if (isNotFound(e)) {
                        released = true;
                        lastStatus = "NotFound";
                    } else {
                        throw new RuntimeException(e);
                    }
                }

                if (released) {
                    double elapsed = (System.currentTimeMillis() - start) / 1000.0;
                    assertTrue("Session was released too early, elapsed=" + elapsed, elapsed >= idleReleaseTimeoutSeconds);
                    assertTrue("Session was released too late, elapsed=" + elapsed, elapsed <= idleReleaseTimeoutSeconds + maxOverSeconds);
                    System.out.println("✅ Session released: status=" + lastStatus + ", elapsed=" + String.format("%.2f", elapsed) + "s");
                    return;
                }

                Thread.sleep(pollInterval * 1000L);
            }

            String details = "last_status=" + lastStatus;
            throw new AssertionError("Session was not released within expected time window: " + 
                idleReleaseTimeoutSeconds + "s~" + (idleReleaseTimeoutSeconds + maxOverSeconds) + "s. " + details);
        } finally {
            if (session != null) {
                try {
                    boolean needsCleanup = false;
                    try {
                        String status = getSessionStatus(session);
                        if (!isReleasedByStatusString(status)) {
                            needsCleanup = true;
                        }
                    } catch (Throwable e) {
                        if (!isNotFound(e)) {
                            needsCleanup = true;
                        }
                    }
                    
                    if (needsCleanup) {
                        System.out.println("🧹 Cleaning up: deleting session explicitly...");
                        session.delete(false);
                    }
                } catch (Exception e) {
                    // ignore
                }
            }
        }
    }
}
