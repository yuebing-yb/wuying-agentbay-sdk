package com.aliyun.agentbay.computer;

import com.aliyun.agentbay.model.ScreenshotBytesResult;
import com.aliyun.agentbay.session.Session;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponse;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponseBody;
import org.junit.Before;
import org.junit.Test;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

/**
 * Unit tests for Computer module.
 * Following TDD principles - tests first, then implementation.
 */
public class ComputerTest {

    @Mock
    private Session mockSession;

    private Computer computer;

    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.openMocks(this);
        computer = new Computer(mockSession);
        when(mockSession.isVpcEnabled()).thenReturn(false);
    }

    private CallMcpToolResponse createMockResponse(boolean success, String data, String requestId) {
        CallMcpToolResponse response = mock(CallMcpToolResponse.class);
        CallMcpToolResponseBody body = mock(CallMcpToolResponseBody.class);

        when(response.getBody()).thenReturn(body);
        when(body.getRequestId()).thenReturn(requestId);

        Map<String, Object> bodyMap = new HashMap<>();
        bodyMap.put("RequestId", requestId);
        Map<String, Object> map = new HashMap<>();
        map.put("body", bodyMap);
        try {
            when(response.toMap()).thenReturn(map);
        } catch (Exception e) {
        }

        Map<String, Object> contentItem = new HashMap<>();
        contentItem.put("text", data);
        Map<String, Object> dataMap = new HashMap<>();
        dataMap.put("content", java.util.Arrays.asList(contentItem));
        dataMap.put("isError", !success);
        when(body.getData()).thenReturn(dataMap);
        return response;
    }

    @Test
    public void testBetaTakeScreenshotSuccessJpeg() throws Exception {
        byte[] jpegHeader = new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff};
        byte[] payload = new byte[jpegHeader.length + 4];
        System.arraycopy(jpegHeader, 0, payload, 0, jpegHeader.length);
        System.arraycopy("test".getBytes(), 0, payload, jpegHeader.length, 4);
        String b64 = Base64.getEncoder().encodeToString(payload);
        String jsonPayload = "{\"type\":\"image\",\"mime_type\":\"image/jpeg\",\"width\":1280,\"height\":720,\"data\":\"" + b64 + "\"}";

        CallMcpToolResponse mockResponse = createMockResponse(true, jsonPayload, "beta-req-1");
        when(mockSession.callTool(anyString(), any())).thenReturn(mockResponse);

        ScreenshotBytesResult result = computer.betaTakeScreenshot("jpg");

        assertTrue(result.isSuccess());
        assertEquals("beta-req-1", result.getRequestId());
        assertEquals("jpeg", result.getFormat());
        assertNotNull(result.getData());
        assertTrue(result.getData().length >= 3);

        ArgumentCaptor<Object> argsCaptor = ArgumentCaptor.forClass(Object.class);
        verify(mockSession).callTool(eq("screenshot"), argsCaptor.capture());
        @SuppressWarnings("unchecked")
        Map<String, Object> args = (Map<String, Object>) argsCaptor.getValue();
        assertEquals("jpeg", args.get("format"));
    }

    @Test
    public void testBetaTakeScreenshotRejectsNonJsonPayload() throws Exception {
        byte[] jpegHeader = new byte[] {(byte) 0xff, (byte) 0xd8, (byte) 0xff};
        byte[] payload = new byte[jpegHeader.length + 4];
        System.arraycopy(jpegHeader, 0, payload, 0, jpegHeader.length);
        System.arraycopy("test".getBytes(), 0, payload, jpegHeader.length, 4);
        String b64 = Base64.getEncoder().encodeToString(payload);

        CallMcpToolResponse mockResponse = createMockResponse(true, b64, "beta-req-2");
        when(mockSession.callTool(anyString(), any())).thenReturn(mockResponse);

        ScreenshotBytesResult result = computer.betaTakeScreenshot("jpeg");
        assertFalse(result.isSuccess());
        assertEquals("beta-req-2", result.getRequestId());
        assertEquals("jpeg", result.getFormat());
        assertNotNull(result.getErrorMessage());
        assertTrue(result.getErrorMessage().toLowerCase().contains("non-json"));
    }
}

