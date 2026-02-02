package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.Context;
import com.aliyun.agentbay.context.ContextInfoResult;
import com.aliyun.agentbay.context.ContextStatusData;
import com.aliyun.agentbay.context.ContextResult;
import com.aliyun.agentbay.context.ContextSync;
import com.aliyun.agentbay.context.SyncPolicy;
import com.aliyun.agentbay.model.FileUrlResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.Assume;
import org.junit.Test;

import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import static org.junit.Assert.assertNotNull;
import static org.junit.Assert.assertTrue;

public class SessionCreateContextBetaWaitFlagIntegrationTest {

    private static Path createTempFileWithZeros(int sizeMB) throws Exception {
        Path p = Files.createTempFile("agentbay-beta-wait-", ".bin");
        byte[] chunk = new byte[1024 * 1024];
        try (OutputStream out = Files.newOutputStream(p)) {
            for (int i = 0; i < sizeMB; i++) {
                out.write(chunk);
            }
        }
        return p;
    }

    private static void uploadFileWithRetries(String uploadUrl, Path localPath, int maxAttempts) throws Exception {
        Exception last = null;
        for (int attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                URL url = new URL(uploadUrl);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setConnectTimeout(30000);
                conn.setReadTimeout(300000);
                conn.setDoOutput(true);
                conn.setRequestMethod("PUT");
                conn.setRequestProperty("Content-Length", String.valueOf(Files.size(localPath)));

                byte[] buf = new byte[1024 * 1024];
                try (OutputStream out = conn.getOutputStream(); InputStream in = Files.newInputStream(localPath)) {
                    int n;
                    while ((n = in.read(buf)) >= 0) {
                        out.write(buf, 0, n);
                    }
                }

                int status = conn.getResponseCode();
                conn.disconnect();
                if (status == 200 || status == 204) {
                    return;
                }
                last = new RuntimeException("upload failed: status=" + status);
            } catch (Exception e) {
                last = e;
            }
            if (attempt < maxAttempts) {
                long sleepMs = Math.min((long) Math.pow(2, attempt) * 1000L, 10000L);
                Thread.sleep(sleepMs);
            }
        }
        throw last != null ? last : new RuntimeException("upload failed");
    }

    private static void assertDownloadTerminalSuccess(Session session, String contextId, String label) {
        ContextInfoResult info = session.getContext().info(contextId, null, "download");
        assertTrue(label + ": context info should be success", info.isSuccess());

        List<String> statuses = new ArrayList<>();
        for (ContextStatusData it : info.getContextStatusData()) {
            if (contextId.equals(it.getContextId())) {
                statuses.add(it.getStatus());
            }
        }
        assertTrue(label + ": expected at least one download status entry", !statuses.isEmpty());
        for (String st : statuses) {
            assertTrue(label + ": status should be terminal, got=" + st, "Success".equals(st) || "Failed".equals(st));
            assertTrue(label + ": download should not fail", !"Failed".equals(st));
        }
    }

    private static void waitDownloadTerminalSuccess(Session session, String contextId, long timeoutMs) throws Exception {
        long deadline = System.currentTimeMillis() + timeoutMs;
        List<String> lastStatuses = new ArrayList<>();
        while (System.currentTimeMillis() < deadline) {
            ContextInfoResult info = session.getContext().info(contextId, null, "download");
            assertTrue("Polling: context info should be success", info.isSuccess());

            List<String> statuses = new ArrayList<>();
            for (ContextStatusData it : info.getContextStatusData()) {
                if (contextId.equals(it.getContextId())) {
                    statuses.add(it.getStatus());
                }
            }
            if (!statuses.isEmpty()) {
                lastStatuses = statuses;
            }

            if (!statuses.isEmpty()) {
                boolean allTerminal = true;
                for (String st : statuses) {
                    if (!"Success".equals(st) && !"Failed".equals(st)) {
                        allTerminal = false;
                        break;
                    }
                }
                if (allTerminal) {
                    for (String st : statuses) {
                        assertTrue("Download should not fail, statuses=" + statuses, !"Failed".equals(st));
                    }
                    return;
                }
            }
            Thread.sleep(2000L);
        }
        throw new AssertionError("Download did not complete within timeout. lastStatuses=" + lastStatuses);
    }

    @Test
    public void testCreateSessionBetaWaitForCompletionFlag() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        Assume.assumeTrue("AGENTBAY_API_KEY must be set for integration tests", apiKey != null && !apiKey.trim().isEmpty());

        AgentBay agentBay = new AgentBay(apiKey);

        long unique = System.currentTimeMillis();
        String ctxName1 = "test-beta-wait-flag-1-" + unique;
        String ctxName2 = "test-beta-wait-flag-2-" + unique;

        ContextResult ctxRes1 = agentBay.getContext().create(ctxName1);
        ContextResult ctxRes2 = agentBay.getContext().create(ctxName2);
        assertTrue(ctxRes1.isSuccess());
        assertTrue(ctxRes2.isSuccess());
        assertNotNull(ctxRes1.getContext());
        assertNotNull(ctxRes2.getContext());

        Context ctx1 = ctxRes1.getContext();
        Context ctx2 = ctxRes2.getContext();

        String mount1 = "/tmp/beta-wait-flag-1";
        String mount2 = "/tmp/beta-wait-flag-2";
        int sizeMB = 200;

        Path tmpFile = createTempFileWithZeros(sizeMB);
        Session sWaitBoth = null;
        Session sWaitOne = null;
        Session sWaitNone = null;

        try {
            FileUrlResult up1 = agentBay.getContext().getFileUploadUrl(ctx1.getContextId(), mount1 + "/large.bin");
            assertTrue(up1.isSuccess());
            uploadFileWithRetries(up1.getUrl(), tmpFile, 5);

            FileUrlResult up2 = agentBay.getContext().getFileUploadUrl(ctx2.getContextId(), mount2 + "/large.bin");
            assertTrue(up2.isSuccess());
            uploadFileWithRetries(up2.getUrl(), tmpFile, 5);

            String imageId = "linux_latest";

            CreateSessionParams waitBothParams = new CreateSessionParams();
            waitBothParams.setImageId(imageId);
            List<ContextSync> waitBothSyncs = new ArrayList<>();
            waitBothSyncs.add(new ContextSync(ctx1.getContextId(), mount1, SyncPolicy.defaultPolicy()));
            waitBothSyncs.add(new ContextSync(ctx2.getContextId(), mount2, SyncPolicy.defaultPolicy()));
            waitBothParams.setContextSyncs(waitBothSyncs);

            long t0 = System.currentTimeMillis();
            SessionResult waitBothRes = agentBay.create(waitBothParams);
            long tWaitBoth = System.currentTimeMillis() - t0;
            assertTrue(waitBothRes.isSuccess());
            assertNotNull(waitBothRes.getSession());
            sWaitBoth = waitBothRes.getSession();
            assertDownloadTerminalSuccess(sWaitBoth, ctx1.getContextId(), "wait-both ctx1");
            assertDownloadTerminalSuccess(sWaitBoth, ctx2.getContextId(), "wait-both ctx2");

            CreateSessionParams waitOneParams = new CreateSessionParams();
            waitOneParams.setImageId(imageId);
            List<ContextSync> waitOneSyncs = new ArrayList<>();
            waitOneSyncs.add(new ContextSync(ctx1.getContextId(), mount1, SyncPolicy.defaultPolicy()));
            waitOneSyncs.add(new ContextSync(ctx2.getContextId(), mount2, SyncPolicy.defaultPolicy()).withBetaWaitForCompletion(false));
            waitOneParams.setContextSyncs(waitOneSyncs);

            long t1 = System.currentTimeMillis();
            SessionResult waitOneRes = agentBay.create(waitOneParams);
            long tWaitOne = System.currentTimeMillis() - t1;
            assertTrue(waitOneRes.isSuccess());
            assertNotNull(waitOneRes.getSession());
            sWaitOne = waitOneRes.getSession();
            assertDownloadTerminalSuccess(sWaitOne, ctx1.getContextId(), "wait-one ctx1");
            waitDownloadTerminalSuccess(sWaitOne, ctx2.getContextId(), 4 * 60 * 1000L);

            CreateSessionParams waitNoneParams = new CreateSessionParams();
            waitNoneParams.setImageId(imageId);
            List<ContextSync> waitNoneSyncs = new ArrayList<>();
            waitNoneSyncs.add(new ContextSync(ctx1.getContextId(), mount1, SyncPolicy.defaultPolicy()).withBetaWaitForCompletion(false));
            waitNoneSyncs.add(new ContextSync(ctx2.getContextId(), mount2, SyncPolicy.defaultPolicy()).withBetaWaitForCompletion(false));
            waitNoneParams.setContextSyncs(waitNoneSyncs);

            long t2 = System.currentTimeMillis();
            SessionResult waitNoneRes = agentBay.create(waitNoneParams);
            long tWaitNone = System.currentTimeMillis() - t2;
            assertTrue(waitNoneRes.isSuccess());
            assertNotNull(waitNoneRes.getSession());
            sWaitNone = waitNoneRes.getSession();
            waitDownloadTerminalSuccess(sWaitNone, ctx1.getContextId(), 4 * 60 * 1000L);
            waitDownloadTerminalSuccess(sWaitNone, ctx2.getContextId(), 4 * 60 * 1000L);

            System.out.println("Create durations (ms): wait-both=" + tWaitBoth + " wait-one=" + tWaitOne + " wait-none=" + tWaitNone);
        } finally {
            try {
                Files.deleteIfExists(tmpFile);
            } catch (Exception e) {
                // ignore
            }
            for (Session s : new Session[]{sWaitNone, sWaitOne, sWaitBoth}) {
                if (s == null) {
                    continue;
                }
                try {
                    s.delete(false);
                } catch (Exception e) {
                    // ignore
                }
            }
            try {
                agentBay.getContext().delete(ctx1);
            } catch (Exception e) {
                // ignore
            }
            try {
                agentBay.getContext().delete(ctx2);
            } catch (Exception e) {
                // ignore
            }
        }
    }
}

