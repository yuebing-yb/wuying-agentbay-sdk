package com.aliyun.agentbay.service;

import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.Session;
import java.io.IOException;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.CountDownLatch;
import java.util.HashMap;
import java.util.Map;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;

public class BaseServiceLinkUrlFailureLoggingTest {

    private static class MiniHttpServer implements AutoCloseable {
        private final ServerSocket serverSocket;
        private final Thread thread;
        private final CountDownLatch ready = new CountDownLatch(1);
        private volatile boolean running = true;

        MiniHttpServer(final byte[] responseBytes) throws IOException {
            this.serverSocket = new ServerSocket(0);
            this.thread = new Thread(() -> {
                ready.countDown();
                while (running) {
                    try (Socket socket = serverSocket.accept()) {
                        socket.setSoTimeout(3000);
                        byte[] buf = new byte[4096];
                        int read = socket.getInputStream().read(buf);
                        if (read <= 0) {
                            continue;
                        }
                        OutputStream out = socket.getOutputStream();
                        out.write(responseBytes);
                        out.flush();
                        return;
                    } catch (IOException ignored) {
                        return;
                    }
                }
            });
            this.thread.setDaemon(true);
            this.thread.start();
            try {
                ready.await();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        int getPort() {
            return serverSocket.getLocalPort();
        }

        @Override
        public void close() throws Exception {
            running = false;
            try {
                serverSocket.close();
            } catch (IOException ignored) {
            }
        }
    }

    private static class TestableBaseService extends BaseService {
        String capturedApiName = "";
        String capturedRequestId = "";
        boolean capturedSuccess = true;
        Map<String, Object> capturedKeyFields = new HashMap<>();
        String capturedFullResponse = "";

        TestableBaseService(Session session) {
            super(session);
        }

        OperationResult callWithServer(String toolName, Object args, String serverName) {
            return callMcpTool(toolName, args, serverName);
        }

        @Override
        protected void logApiResponseWithDetails(
            String apiName,
            String requestId,
            boolean success,
            Map<String, Object> keyFields,
            String fullResponse
        ) {
            this.capturedApiName = apiName;
            this.capturedRequestId = requestId;
            this.capturedSuccess = success;
            this.capturedKeyFields = keyFields != null ? keyFields : new HashMap<>();
            this.capturedFullResponse = fullResponse != null ? fullResponse : "";
        }
    }

    @Test
    public void callMcpToolLinkUrl_non2xx_shouldLogMaskedBody() throws Exception {
        byte[] body = "{\"code\":\"BadGateway\",\"message\":\"upstream\",\"token\":\"tok_123456\"}".getBytes(StandardCharsets.UTF_8);
        String resp =
            "HTTP/1.1 502 Bad Gateway\r\n"
                + "Content-Type: application/json\r\n"
                + "Content-Length: " + body.length + "\r\n"
                + "Connection: close\r\n"
                + "\r\n";
        byte[] header = resp.getBytes(StandardCharsets.UTF_8);
        byte[] responseBytes = new byte[header.length + body.length];
        System.arraycopy(header, 0, responseBytes, 0, header.length);
        System.arraycopy(body, 0, responseBytes, header.length, body.length);

        try (MiniHttpServer server = new MiniHttpServer(responseBytes)) {
            int port = server.getPort();
            Session session = Mockito.mock(Session.class);
            Mockito.when(session.getLinkUrl()).thenReturn("http://127.0.0.1:" + port);
            Mockito.when(session.getToken()).thenReturn("tok_abcdef");

            TestableBaseService svc = new TestableBaseService(session);
            OperationResult result = svc.callWithServer("long_screenshot", new HashMap<>(), "android");

            Assert.assertFalse(result.isSuccess());
            Assert.assertEquals("CallMcpTool(LinkUrl) Response", svc.capturedApiName);
            Assert.assertFalse(svc.capturedSuccess);
            Assert.assertEquals(502, svc.capturedKeyFields.get("http_status"));
            Assert.assertEquals("long_screenshot", svc.capturedKeyFields.get("tool_name"));
            Assert.assertTrue(svc.capturedRequestId.startsWith("link-"));
            Assert.assertTrue(svc.capturedFullResponse.contains("BadGateway"));
            Assert.assertFalse(svc.capturedFullResponse.contains("tok_123456"));
            Assert.assertTrue(svc.capturedFullResponse.contains("to****56"));
        }
    }
}

