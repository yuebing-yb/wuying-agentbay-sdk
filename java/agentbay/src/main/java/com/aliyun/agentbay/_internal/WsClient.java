package com.aliyun.agentbay._internal;

import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;

public class WsClient {
    private static final Logger logger = LoggerFactory.getLogger(WsClient.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final String wsUrl;
    private final String token;

    private final OkHttpClient client;
    private volatile WebSocket webSocket;
    private volatile CompletableFuture<Void> connecting;

    private final ConcurrentHashMap<String, PendingStream> pendingById = new ConcurrentHashMap<>();

    public interface OnEvent {
        void onEvent(String invocationId, Map<String, Object> data);
    }

    public interface OnEnd {
        void onEnd(String invocationId, Map<String, Object> data);
    }

    public interface OnError {
        void onError(String invocationId, Exception err);
    }

    private static class PendingStream {
        final OnEvent onEvent;
        final OnEnd onEnd;
        final OnError onError;
        final CompletableFuture<Map<String, Object>> endFuture;

        PendingStream(OnEvent onEvent, OnEnd onEnd, OnError onError) {
            this.onEvent = onEvent;
            this.onEnd = onEnd;
            this.onError = onError;
            this.endFuture = new CompletableFuture<>();
        }
    }

    public static class StreamHandle {
        public final String invocationId;
        private final CompletableFuture<Map<String, Object>> endFuture;

        StreamHandle(String invocationId, CompletableFuture<Map<String, Object>> endFuture) {
            this.invocationId = invocationId;
            this.endFuture = endFuture;
        }

        public CompletableFuture<Map<String, Object>> waitEnd() {
            return endFuture;
        }
    }

    public WsClient(String wsUrl, String token) {
        this.wsUrl = wsUrl;
        this.token = token;
        this.client = new OkHttpClient.Builder().build();
    }

    public synchronized CompletableFuture<Void> connect() {
        if (webSocket != null) {
            return CompletableFuture.completedFuture(null);
        }
        if (connecting != null) {
            return connecting;
        }

        connecting = new CompletableFuture<>();
        Request request = new Request.Builder()
            .url(wsUrl)
            .addHeader("X-Access-Token", token)
            .build();
        client.newWebSocket(request, new Listener());

        return connecting;
    }

    public synchronized void close() {
        WebSocket ws = webSocket;
        webSocket = null;
        connecting = null;
        if (ws != null) {
            try {
                ws.close(1000, "close");
            } catch (Exception e) {
            }
        }
        failAllPending(new RuntimeException("WS connection closed"));
    }

    public CompletableFuture<StreamHandle> callStream(
        String target,
        Map<String, Object> data,
        OnEvent onEvent,
        OnEnd onEnd,
        OnError onError
    ) {
        return connect().thenApply(_v -> {
            WebSocket ws = webSocket;
            if (ws == null) {
                throw new RuntimeException("WS is not connected");
            }

            String invocationId = newInvocationId();
            PendingStream pending = new PendingStream(onEvent, onEnd, onError);
            pendingById.put(invocationId, pending);

            Map<String, Object> payload = new HashMap<>();
            payload.put("invocationId", invocationId);
            payload.put("source", "SDK");
            payload.put("target", target);
            payload.put("data", data);
            logFrame(">>", payload);

            try {
                String raw = objectMapper.writeValueAsString(payload);
                ws.send(raw);
            } catch (Exception e) {
                pendingById.remove(invocationId);
                pending.endFuture.completeExceptionally(e);
                throw new RuntimeException(e);
            }

            return new StreamHandle(invocationId, pending.endFuture);
        });
    }

    private void handleIncoming(String raw) {
        Map<String, Object> msg;
        try {
            msg = objectMapper.readValue(raw, Map.class);
        } catch (Exception e) {
            failAllPending(e);
            return;
        }

        Object invocationIdObj = msg.get("invocationId");
        if (invocationIdObj == null) invocationIdObj = msg.get("requestId");
        if (!(invocationIdObj instanceof String)) return;
        String invocationId = (String) invocationIdObj;

        PendingStream pending = pendingById.get(invocationId);
        if (pending == null) return;

        Object sourceObj = msg.get("source");
        String source = sourceObj instanceof String ? (String) sourceObj : "";
        Object dataObj = msg.get("data");

        if ("WEBSOCKET_SERVER".equals(source)) {
            Map<String, Object> lf = new HashMap<>();
            lf.put("invocationId", invocationId);
            lf.put("source", source);
            lf.put("data", dataObj);
            logFrame("<<", lf);
            String errMsg = "";
            Object errObj = msg.get("error");
            if (errObj instanceof String && !((String) errObj).isEmpty()) {
                errMsg = (String) errObj;
            }
            if (errMsg.isEmpty() && dataObj instanceof Map) {
                Object e = ((Map<?, ?>) dataObj).get("error");
                if (e instanceof String && !((String) e).isEmpty()) {
                    errMsg = (String) e;
                }
            }
            if (!errMsg.isEmpty()) {
                Exception err = new RuntimeException(errMsg);
                if (pending.onError != null) pending.onError.onError(invocationId, err);
                pending.endFuture.completeExceptionally(err);
                pendingById.remove(invocationId);
                return;
            }
            Map<String, Object> d = dataObj instanceof Map ? (Map<String, Object>) dataObj : new HashMap<>();
            if (pending.onEnd != null) pending.onEnd.onEnd(invocationId, d);
            pending.endFuture.complete(d);
            pendingById.remove(invocationId);
            return;
        }

        if (!(dataObj instanceof Map)) return;
        Map<String, Object> data = (Map<String, Object>) dataObj;
        Map<String, Object> lf = new HashMap<>();
        lf.put("invocationId", invocationId);
        lf.put("source", source);
        lf.put("target", msg.get("target"));
        lf.put("data", data);
        logFrame("<<", lf);

        Object errObj = data.get("error");
        if (errObj instanceof String && !((String) errObj).isEmpty()) {
            Exception err = new RuntimeException((String) errObj);
            if (pending.onError != null) pending.onError.onError(invocationId, err);
            pending.endFuture.completeExceptionally(err);
            pendingById.remove(invocationId);
            return;
        }

        Object phaseObj = data.get("phase");
        String phase = phaseObj instanceof String ? (String) phaseObj : "";
        if ("event".equals(phase)) {
            if (pending.onEvent != null) pending.onEvent.onEvent(invocationId, data);
            return;
        }
        if ("end".equals(phase)) {
            if (pending.onEnd != null) pending.onEnd.onEnd(invocationId, data);
            pending.endFuture.complete(data);
            pendingById.remove(invocationId);
            return;
        }

        Exception err = new RuntimeException("Unsupported phase: " + phaseObj);
        if (pending.onError != null) pending.onError.onError(invocationId, err);
        pending.endFuture.completeExceptionally(err);
        pendingById.remove(invocationId);
    }

    private void failAllPending(Exception err) {
        for (Map.Entry<String, PendingStream> e : pendingById.entrySet()) {
            PendingStream p = e.getValue();
            if (p.onError != null) p.onError.onError(e.getKey(), err);
            p.endFuture.completeExceptionally(err);
        }
        pendingById.clear();
    }

    private void logFrame(String direction, Map<String, Object> payload) {
        try {
            String raw = objectMapper.writeValueAsString(payload);
            if (raw.length() > 1200) raw = raw.substring(0, 1200) + "...";
            logger.debug("WS {} {}", direction, raw);
        } catch (Exception e) {
            logger.debug("WS {} {}", direction, String.valueOf(payload));
        }
    }

    private static String newInvocationId() {
        return Long.toHexString(System.nanoTime());
    }

    private class Listener extends WebSocketListener {
        @Override
        public void onOpen(WebSocket webSocket, Response response) {
            WsClient.this.webSocket = webSocket;
            CompletableFuture<Void> c = WsClient.this.connecting;
            WsClient.this.connecting = null;
            if (c != null && !c.isDone()) {
                c.complete(null);
            }
        }

        @Override
        public void onMessage(WebSocket webSocket, String text) {
            handleIncoming(text);
        }

        @Override
        public void onClosing(WebSocket webSocket, int code, String reason) {
            failAllPending(new RuntimeException("WS closing: " + code + " " + reason));
        }

        @Override
        public void onClosed(WebSocket webSocket, int code, String reason) {
            failAllPending(new RuntimeException("WS closed: " + code + " " + reason));
        }

        @Override
        public void onFailure(WebSocket webSocket, Throwable t, Response response) {
            Exception e = t instanceof Exception ? (Exception) t : new RuntimeException(t);
            CompletableFuture<Void> c = WsClient.this.connecting;
            WsClient.this.connecting = null;
            if (c != null && !c.isDone()) {
                c.completeExceptionally(e);
            }
            failAllPending(e);
        }
    }
}

