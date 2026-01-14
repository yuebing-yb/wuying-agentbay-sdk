package com.aliyun.agentbay.service;

import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.session.Session;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponse;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponseBody;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.Assert;
import org.junit.Test;
import org.mockito.Mockito;

public class BaseServiceRequestIdLoggingTest {

    private static class TestableBaseService extends BaseService {
        TestableBaseService(Session session) {
            super(session);
        }

        OperationResult call(String toolName, Object args) {
            return callMcpTool(toolName, args);
        }
    }

    @Test
    public void callMcpToolApi_isError_shouldIncludeRequestIdInErrorMessage() throws Exception {
        Session session = Mockito.mock(Session.class);
        Mockito.when(session.getLinkUrl()).thenReturn("");
        Mockito.when(session.getToken()).thenReturn("");

        CallMcpToolResponse response = Mockito.mock(CallMcpToolResponse.class);
        CallMcpToolResponseBody body = Mockito.mock(CallMcpToolResponseBody.class);
        Mockito.when(response.getBody()).thenReturn(body);

        Map<String, Object> contentItem = new HashMap<>();
        contentItem.put("text", "Error: boom");
        List<Object> content = new ArrayList<>();
        content.add(contentItem);

        Map<String, Object> data = new HashMap<>();
        data.put("isError", Boolean.TRUE);
        data.put("content", content);
        Mockito.when(body.getData()).thenReturn(data);

        Map<String, Object> bodyMap = new HashMap<>();
        bodyMap.put("RequestId", "req-123");
        Map<String, Object> toMap = new HashMap<>();
        toMap.put("body", bodyMap);
        Mockito.when(response.toMap()).thenReturn(toMap);

        Mockito.when(session.callTool(Mockito.eq("shell"), Mockito.any())).thenReturn(response);

        TestableBaseService svc = new TestableBaseService(session);
        OperationResult result = svc.call("shell", new HashMap<>());

        Assert.assertFalse(result.isSuccess());
        Assert.assertEquals("req-123", result.getRequestId());
        Assert.assertTrue(result.getErrorMessage().contains("RequestId=req-123"));
        Assert.assertTrue(result.getErrorMessage().contains("Error: boom"));
    }

    @Test
    public void callMcpToolLinkUrl_withoutServerName_shouldFailFast() throws Exception {
        Session session = Mockito.mock(Session.class);
        Mockito.when(session.getLinkUrl()).thenReturn("http://127.0.0.1:1");
        Mockito.when(session.getToken()).thenReturn("token");

        TestableBaseService svc = new TestableBaseService(session);
        OperationResult result = svc.call("read_file", new HashMap<>());

        Assert.assertFalse(result.isSuccess());
        Assert.assertTrue(result.getErrorMessage().toLowerCase().contains("server"));
        Assert.assertTrue(result.getErrorMessage().toLowerCase().contains("required"));
    }
}

