package com.aliyun.agentbay.session;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.client.ApiClient;
import com.aliyun.agentbay.context.ContextManager;
import com.aliyun.agentbay.context.ContextSyncResult;
import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionStatusResult;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.*;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.lang.reflect.Field;
import java.util.Collections;
import java.util.HashMap;

import static org.junit.Assert.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

/**
 * Unit tests for Session class.
 * Uses mock data to test interfaces and logic following ComputerTest pattern.
 */
public class SessionTest {

    @Mock
    private AgentBay mockAgentBay;

    @Mock
    private Client mockClient;

    @Mock
    private ApiClient mockApiClient;

    private Session session;

    @Before
    public void setUp() throws Exception {
        MockitoAnnotations.openMocks(this);
        when(mockAgentBay.getClient()).thenReturn(mockClient);
        when(mockAgentBay.getApiClient()).thenReturn(mockApiClient);
        when(mockAgentBay.getApiKey()).thenReturn("test-api-key");
        session = new Session("test-session-id", mockAgentBay);
    }

    // ==================== getStatus() tests ====================

    @Test
    public void testGetStatusSuccess() throws Exception {
        GetSessionDetailResponse response = mock(GetSessionDetailResponse.class);
        GetSessionDetailResponseBody body = mock(GetSessionDetailResponseBody.class);
        GetSessionDetailResponseBody.GetSessionDetailResponseBodyData data =
            mock(GetSessionDetailResponseBody.GetSessionDetailResponseBodyData.class);

        when(mockClient.getSessionDetail(any())).thenReturn(response);
        when(response.getBody()).thenReturn(body);
        when(body.getSuccess()).thenReturn(true);
        when(body.getHttpStatusCode()).thenReturn(200);
        when(body.getCode()).thenReturn("");
        when(body.getMessage()).thenReturn("");
        when(body.getRequestId()).thenReturn("req-status-1");
        when(body.getData()).thenReturn(data);
        when(data.getStatus()).thenReturn("RUNNING");

        SessionStatusResult result = session.getStatus();

        assertTrue(result.isSuccess());
        assertEquals("RUNNING", result.getStatus());
        assertEquals(200, result.getHttpStatusCode());
    }

    @Test
    public void testGetStatusNotFoundViaException() throws Exception {
        when(mockClient.getSessionDetail(any()))
            .thenThrow(new RuntimeException("code: InvalidMcpSession.NotFound"));

        SessionStatusResult result = session.getStatus();

        assertFalse(result.isSuccess());
        assertEquals("InvalidMcpSession.NotFound", result.getCode());
        assertEquals(400, result.getHttpStatusCode());
        assertTrue(result.getErrorMessage().contains("not found"));
    }

    @Test
    public void testGetStatusApiError() throws Exception {
        GetSessionDetailResponse response = mock(GetSessionDetailResponse.class);
        GetSessionDetailResponseBody body = mock(GetSessionDetailResponseBody.class);

        when(mockClient.getSessionDetail(any())).thenReturn(response);
        when(response.getBody()).thenReturn(body);
        when(body.getSuccess()).thenReturn(false);
        when(body.getHttpStatusCode()).thenReturn(500);
        when(body.getCode()).thenReturn("InternalError");
        when(body.getMessage()).thenReturn("Server error");
        when(body.getRequestId()).thenReturn("req-err");

        SessionStatusResult result = session.getStatus();

        assertFalse(result.isSuccess());
        assertEquals("InternalError", result.getCode());
        assertTrue(result.getErrorMessage().contains("Server error"));
    }

    @Test
    public void testGetStatusNullBody() throws Exception {
        GetSessionDetailResponse response = mock(GetSessionDetailResponse.class);
        when(mockClient.getSessionDetail(any())).thenReturn(response);
        when(response.getBody()).thenReturn(null);

        SessionStatusResult result = session.getStatus();

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Invalid response"));
    }

    // ==================== keepAlive() tests ====================

    @Test
    public void testKeepAliveSuccess() throws Exception {
        RefreshSessionIdleTimeResponse response = mock(RefreshSessionIdleTimeResponse.class);
        RefreshSessionIdleTimeResponseBody body = mock(RefreshSessionIdleTimeResponseBody.class);

        when(mockClient.refreshSessionIdleTime(any())).thenReturn(response);
        when(response.getBody()).thenReturn(body);
        when(body.getSuccess()).thenReturn(true);

        OperationResult result = session.keepAlive();

        assertTrue(result.isSuccess());
    }

    @Test
    public void testKeepAliveFailure() throws Exception {
        RefreshSessionIdleTimeResponse response = mock(RefreshSessionIdleTimeResponse.class);
        RefreshSessionIdleTimeResponseBody body = mock(RefreshSessionIdleTimeResponseBody.class);

        when(mockClient.refreshSessionIdleTime(any())).thenReturn(response);
        when(response.getBody()).thenReturn(body);
        when(body.getSuccess()).thenReturn(false);
        when(body.getCode()).thenReturn("SessionExpired");
        when(body.getMessage()).thenReturn("Session has expired");

        OperationResult result = session.keepAlive();

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Session has expired"));
    }

    @Test
    public void testKeepAliveException() throws Exception {
        when(mockClient.refreshSessionIdleTime(any()))
            .thenThrow(new RuntimeException("Network error"));

        OperationResult result = session.keepAlive();

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Network error"));
    }

    // ==================== delete() tests ====================

    @Test
    public void testDeleteSuccessNotFound() throws Exception {
        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(true);

        // Polling: getSessionDetail throws NotFound
        when(mockClient.getSessionDetail(any()))
            .thenThrow(new RuntimeException("InvalidMcpSession.NotFound"));

        DeleteResult result = session.delete(false);

        assertTrue(result.isSuccess());
        assertEquals("", result.getErrorMessage());
    }

    @Test
    public void testDeleteSuccessFinishStatus() throws Exception {
        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(true);

        // Polling: getSessionDetail returns FINISH status
        GetSessionDetailResponse statusResponse = mock(GetSessionDetailResponse.class);
        GetSessionDetailResponseBody statusBody = mock(GetSessionDetailResponseBody.class);
        GetSessionDetailResponseBody.GetSessionDetailResponseBodyData statusData =
            mock(GetSessionDetailResponseBody.GetSessionDetailResponseBodyData.class);
        when(mockClient.getSessionDetail(any())).thenReturn(statusResponse);
        when(statusResponse.getBody()).thenReturn(statusBody);
        when(statusBody.getSuccess()).thenReturn(true);
        when(statusBody.getHttpStatusCode()).thenReturn(200);
        when(statusBody.getCode()).thenReturn("");
        when(statusBody.getMessage()).thenReturn("");
        when(statusBody.getRequestId()).thenReturn("req-poll");
        when(statusBody.getData()).thenReturn(statusData);
        when(statusData.getStatus()).thenReturn("FINISH");

        DeleteResult result = session.delete(false);

        assertTrue(result.isSuccess());
    }

    @Test
    public void testDeleteApiFailure() throws Exception {
        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(false);
        when(deleteBody.getCode()).thenReturn("DeleteFailed");
        when(deleteBody.getMessage()).thenReturn("Cannot delete session");

        DeleteResult result = session.delete(false);

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Cannot delete session"));
    }

    @Test
    public void testDeleteWithSyncContextSuccess() throws Exception {
        // Inject mock ContextManager via reflection
        ContextManager mockContextManager = mock(ContextManager.class);
        Field cmField = Session.class.getDeclaredField("contextManager");
        cmField.setAccessible(true);
        cmField.set(session, mockContextManager);

        when(mockContextManager.sync()).thenReturn(new ContextSyncResult("sync-req", true));

        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(true);

        when(mockClient.getSessionDetail(any()))
            .thenThrow(new RuntimeException("InvalidMcpSession.NotFound"));

        DeleteResult result = session.delete(true);

        assertTrue(result.isSuccess());
        verify(mockContextManager).sync();
    }

    @Test
    public void testDeleteSyncFailureContinuesDelete() throws Exception {
        // Inject mock ContextManager that throws
        ContextManager mockContextManager = mock(ContextManager.class);
        Field cmField = Session.class.getDeclaredField("contextManager");
        cmField.setAccessible(true);
        cmField.set(session, mockContextManager);

        when(mockContextManager.sync()).thenThrow(new RuntimeException("Sync failed"));

        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(true);

        when(mockClient.getSessionDetail(any()))
            .thenThrow(new RuntimeException("InvalidMcpSession.NotFound"));

        DeleteResult result = session.delete(true);

        // Should still succeed despite sync failure
        assertTrue(result.isSuccess());
        verify(mockContextManager).sync();
    }

    @Test
    public void testDeleteException() throws Exception {
        when(mockClient.deleteSessionAsync(any()))
            .thenThrow(new RuntimeException("Connection refused"));

        DeleteResult result = session.delete(false);

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Connection refused"));
    }

    @Test
    public void testDeleteDefaultNoSync() throws Exception {
        Session spySession = spy(session);

        DeleteSessionAsyncResponse deleteResponse = mock(DeleteSessionAsyncResponse.class);
        DeleteSessionAsyncResponseBody deleteBody = mock(DeleteSessionAsyncResponseBody.class);
        when(mockClient.deleteSessionAsync(any())).thenReturn(deleteResponse);
        when(deleteResponse.getBody()).thenReturn(deleteBody);
        when(deleteBody.getSuccess()).thenReturn(true);

        when(mockClient.getSessionDetail(any()))
            .thenThrow(new RuntimeException("InvalidMcpSession.NotFound"));

        spySession.delete();

        verify(spySession).delete(false);
    }

    // ==================== callMcpTool() tests ====================

    @Test
    public void testCallMcpToolApiRouteSuccess() throws Exception {
        CallMcpToolResponse toolResponse = mock(CallMcpToolResponse.class);
        CallMcpToolResponseBody toolBody = mock(CallMcpToolResponseBody.class);
        when(mockApiClient.callMcpTool(eq("test-session-id"), eq("shell"), any(), isNull()))
            .thenReturn(toolResponse);
        when(toolResponse.getBody()).thenReturn(toolBody);
        when(toolBody.getSuccess()).thenReturn(true);
        when(toolBody.getData()).thenReturn(
            "{\"content\":[{\"text\":\"hello world\",\"type\":\"text\"}],\"isError\":false}");

        OperationResult result = session.callMcpTool("shell", new HashMap<>());

        assertTrue(result.isSuccess());
        assertEquals("hello world", result.getData());
    }

    @Test
    public void testCallMcpToolApiRouteIsError() throws Exception {
        CallMcpToolResponse toolResponse = mock(CallMcpToolResponse.class);
        CallMcpToolResponseBody toolBody = mock(CallMcpToolResponseBody.class);
        when(mockApiClient.callMcpTool(eq("test-session-id"), eq("shell"), any(), isNull()))
            .thenReturn(toolResponse);
        when(toolResponse.getBody()).thenReturn(toolBody);
        when(toolBody.getSuccess()).thenReturn(true);
        when(toolBody.getData()).thenReturn(
            "{\"content\":[{\"text\":\"command not found\",\"type\":\"text\"}],\"isError\":true}");

        OperationResult result = session.callMcpTool("shell", new HashMap<>());

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("command not found"));
    }

    @Test
    public void testCallMcpToolWithServerName() throws Exception {
        McpTool tool = new McpTool();
        tool.setName("shell");
        tool.setServer("wuying_system");
        session.setMcpTools(Collections.singletonList(tool));

        CallMcpToolResponse toolResponse = mock(CallMcpToolResponse.class);
        CallMcpToolResponseBody toolBody = mock(CallMcpToolResponseBody.class);
        when(mockApiClient.callMcpTool(eq("test-session-id"), eq("shell"), any(), eq("wuying_system")))
            .thenReturn(toolResponse);
        when(toolResponse.getBody()).thenReturn(toolBody);
        when(toolBody.getSuccess()).thenReturn(true);
        when(toolBody.getData()).thenReturn(
            "{\"content\":[{\"text\":\"ok\",\"type\":\"text\"}],\"isError\":false}");

        OperationResult result = session.callMcpTool("shell", new HashMap<>());

        assertTrue(result.isSuccess());
        verify(mockApiClient).callMcpTool(eq("test-session-id"), eq("shell"), any(), eq("wuying_system"));
    }

    @Test
    public void testCallMcpToolNullResponse() throws Exception {
        when(mockApiClient.callMcpTool(anyString(), anyString(), any(), any()))
            .thenReturn(null);

        OperationResult result = session.callMcpTool("shell", new HashMap<>());

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("No response"));
    }

    @Test
    public void testCallMcpToolException() throws Exception {
        when(mockApiClient.callMcpTool(anyString(), anyString(), any(), any()))
            .thenThrow(new RuntimeException("Timeout"));

        OperationResult result = session.callMcpTool("shell", new HashMap<>());

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("Timeout"));
    }

    // ==================== getLink() tests ====================

    @Test
    public void testGetLinkSuccess() throws Exception {
        GetLinkResponse linkResponse = mock(GetLinkResponse.class);
        GetLinkResponseBody linkBody = mock(GetLinkResponseBody.class);
        GetLinkResponseBody.GetLinkResponseBodyData linkData =
            mock(GetLinkResponseBody.GetLinkResponseBodyData.class);

        when(mockClient.getLink(any())).thenReturn(linkResponse);
        when(linkResponse.getBody()).thenReturn(linkBody);
        when(linkBody.getData()).thenReturn(linkData);
        when(linkData.getUrl()).thenReturn("https://example.com/link");

        OperationResult result = session.getLink("https", 30100);

        assertTrue(result.isSuccess());
        assertEquals("https://example.com/link", result.getData());
    }

    @Test
    public void testGetLinkNoUrl() throws Exception {
        GetLinkResponse linkResponse = mock(GetLinkResponse.class);
        GetLinkResponseBody linkBody = mock(GetLinkResponseBody.class);

        when(mockClient.getLink(any())).thenReturn(linkResponse);
        when(linkResponse.getBody()).thenReturn(linkBody);
        when(linkBody.getData()).thenReturn(null);

        OperationResult result = session.getLink("https", 30100);

        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("No URL"));
    }

    // ==================== Property and utility tests ====================

    @Test
    public void testSessionProperties() {
        assertEquals("test-session-id", session.getSessionId());
        assertEquals("test-api-key", session.getApiKey());
        assertEquals("", session.getLinkUrl());
        assertNull(session.getToken());
        assertNotNull(session.getComputer());
        assertNotNull(session.getBrowser());
        assertNotNull(session.getMobile());
        assertNotNull(session.getFileSystem());
        assertNotNull(session.getAgent());
        assertNotNull(session.getContext());
        assertNotNull(session.getOss());
        assertNotNull(session.getCode());
        assertNotNull(session.getCommand());
    }

    @Test
    public void testSettersAndGetters() {
        session.setToken("test-token");
        assertEquals("test-token", session.getToken());

        session.setLinkUrl("https://link.example.com");
        assertEquals("https://link.example.com", session.getLinkUrl());

        session.setResourceUrl("https://resource.example.com");
        assertEquals("https://resource.example.com", session.getResourceUrl());

        session.setImageId("custom-image");
        assertEquals("custom-image", session.getImageId());

        session.setEnableBrowserReplay(true);
        assertTrue(session.getEnableBrowserReplay());

        session.setFileTransferContextId("ctx-123");
        assertEquals("ctx-123", session.getFileTransferContextId());

        session.setWsUrl("wss://ws.example.com");
        assertEquals("wss://ws.example.com", session.getWsUrl());
    }

    @Test
    public void testGetMcpServerForToolFound() {
        McpTool tool = new McpTool();
        tool.setName("shell");
        tool.setServer("wuying_system");
        session.setMcpTools(Collections.singletonList(tool));

        assertEquals("wuying_system", session.getMcpServerForTool("shell"));
    }

    @Test
    public void testGetMcpServerForToolNotFound() {
        assertEquals("", session.getMcpServerForTool("nonexistent"));
        assertEquals("", session.getMcpServerForTool(null));
        assertEquals("", session.getMcpServerForTool(""));
    }

    @Test
    public void testAlternativeConstructor() {
        Session altSession = new Session(mockAgentBay, "alt-session-id");
        assertEquals("alt-session-id", altSession.getSessionId());
    }
}
