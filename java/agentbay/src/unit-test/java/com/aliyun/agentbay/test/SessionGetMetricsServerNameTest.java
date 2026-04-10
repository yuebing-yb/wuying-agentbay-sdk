package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.client.ApiClient;
import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.model.SessionMetricsResult;
import com.aliyun.agentbay.model.SessionParams;
import com.aliyun.agentbay.session.Session;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponse;
import com.aliyun.wuyingai20250506.models.CallMcpToolResponseBody;
import java.util.Collections;
import org.junit.Test;

import static org.junit.Assert.*;
import static org.mockito.Mockito.*;

public class SessionGetMetricsServerNameTest {

    @Test
    public void testGetMetricsUsesResolvedServerName() throws Exception {
        AgentBay agentBay = mock(AgentBay.class);
        ApiClient apiClient = mock(ApiClient.class);
        when(agentBay.getApiClient()).thenReturn(apiClient);

        Session session = new Session("test-session-id", agentBay);
        McpTool tool = new McpTool();
        tool.setName("get_metrics");
        tool.setServer("wuying_system");
        session.setMcpTools(Collections.singletonList(tool));

        // Build a valid success response so the full call path executes
        CallMcpToolResponseBody mockBody = new CallMcpToolResponseBody();
        mockBody.setSuccess(true);
        mockBody.setRequestId("test-request-id");
        mockBody.setData("{\"cpu_count\":4,\"cpu_used_pct\":10.5,"
                + "\"mem_total\":8192,\"mem_used\":4096,"
                + "\"disk_total\":102400,\"disk_used\":51200,"
                + "\"rx_rate_kbyte_per_s\":100.0,\"tx_rate_kbyte_per_s\":50.0,"
                + "\"rx_used_kbyte\":1024.0,\"tx_used_kbyte\":512.0,"
                + "\"timestamp\":\"2025-01-01T00:00:00Z\"}");

        CallMcpToolResponse mockResponse = new CallMcpToolResponse();
        mockResponse.setBody(mockBody);

        when(apiClient.callMcpTool(
            eq("test-session-id"),
            eq("get_metrics"),
            any(),
            eq("wuying_system")
        )).thenReturn(mockResponse);

        SessionMetricsResult result = session.getMetrics();

        assertNotNull(result);
        assertTrue("getMetrics() should succeed", result.isSuccess());

        verify(apiClient, times(1)).callMcpTool(
            eq("test-session-id"),
            eq("get_metrics"),
            any(),
            eq("wuying_system")
        );
    }
}
