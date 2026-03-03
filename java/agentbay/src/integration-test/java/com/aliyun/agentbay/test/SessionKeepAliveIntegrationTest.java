package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.model.SessionStatusResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Assume;
import org.junit.Test;

import java.util.HashMap;
import java.util.Map;

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
    public void testKeepAliveResetsIdleTimer() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY must be set for integration tests", apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);

        int idleReleaseTimeoutSeconds = 30;
        int maxOverSeconds = 60;
        int pollInterval = 15;
        String imageId = "linux_latest";
        System.out.println("Creating 2 sessions with image_id=" + imageId + ", idle_release_timeout=" + idleReleaseTimeoutSeconds + "s");

        Map<String, String> commonLabels = new HashMap<>();
        commonLabels.put("test", "session-keep-alive");
        commonLabels.put("sdk", "java");

        CreateSessionParams controlParams = new CreateSessionParams();
        controlParams.setImageId(imageId);
        controlParams.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);
        Map<String, String> controlLabels = new HashMap<>(commonLabels);
        controlLabels.put("role", "control");
        controlParams.setLabels(controlLabels);

        CreateSessionParams refreshedParams = new CreateSessionParams();
        refreshedParams.setImageId(imageId);
        refreshedParams.setIdleReleaseTimeout(idleReleaseTimeoutSeconds);
        Map<String, String> refreshedLabels = new HashMap<>(commonLabels);
        refreshedLabels.put("role", "refreshed");
        refreshedParams.setLabels(refreshedLabels);

        long start = System.currentTimeMillis();

        SessionResult controlCreate = agentBay.create(controlParams);
        assertTrue("Create control session failed: " + controlCreate.getErrorMessage(), controlCreate.isSuccess());
        assertNotNull(controlCreate.getSession());
        Session control = controlCreate.getSession();
        assertNotNull(control.getSessionId());

        SessionResult refreshedCreate = agentBay.create(refreshedParams);
        assertTrue("Create refreshed session failed: " + refreshedCreate.getErrorMessage(), refreshedCreate.isSuccess());
        assertNotNull(refreshedCreate.getSession());
        Session refreshed = refreshedCreate.getSession();
        assertNotNull(refreshed.getSessionId());

        System.out.println("✅ Control session: " + control.getSessionId());
        System.out.println("✅ Refreshed session: " + refreshed.getSessionId());

        try {
            // Wait until halfway through, then refresh the idle timer for refreshed session
            Thread.sleep(idleReleaseTimeoutSeconds * 1000L / 2);
            OperationResult keepAliveResult = refreshed.keepAlive();
            assertTrue("keep_alive failed", keepAliveResult.isSuccess());

            long deadline = start + (idleReleaseTimeoutSeconds + maxOverSeconds) * 1000L;
            Long controlReleasedAt = null;

            while (System.currentTimeMillis() < deadline) {
                // Check control session status
                boolean controlReleased = false;
                try {
                    String s = getSessionStatus(control);
                    System.out.println("Control session status: " + s);
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

                // Check refreshed session status
                boolean refreshedReleased = false;
                try {
                    String s = getSessionStatus(refreshed);
                    System.out.println("Refreshed session status: " + s);
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

                if (controlReleased) {
                    controlReleasedAt = System.currentTimeMillis();
                    assertFalse(
                        "Refreshed session was released no later than control session; " +
                        "keep_alive did not extend idle timer as expected",
                        refreshedReleased
                    );
                    double elapsed = (controlReleasedAt - start) / 1000.0;
                    System.out.println("✅ Control session released while refreshed session still alive, elapsed=" + String.format("%.2f", elapsed) + "s");
                    return;
                }

                // Check if refreshed session was released before control session (unexpected)
                if (refreshedReleased) {
                    throw new AssertionError(
                        "Refreshed session was released before control session; " +
                        "keep_alive may have failed"
                    );
                }

                Thread.sleep(pollInterval * 1000L);
            }

            throw new AssertionError("Control session was not released within expected time window");
        } finally {
            // Best-effort cleanup
            for (Session s : new Session[]{refreshed, control}) {
                if (s == null) {
                    continue;
                }
                try {
                    SessionStatusResult statusFinal = s.getStatus();
                    if (statusFinal != null && statusFinal.isSuccess()) {
                        String status = statusFinal.getStatus();
                        if (!isReleasedByStatusString(status)) {
                            
                            s.delete(false);
                        }
                    }
                } catch (Exception e) {
                    // Ignore cleanup errors
                }
            }
        }
    }
}

