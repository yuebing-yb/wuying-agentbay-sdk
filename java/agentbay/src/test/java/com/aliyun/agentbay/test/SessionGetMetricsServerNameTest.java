package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.client.ApiClient;
import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.model.SessionMetricsResult;
import com.aliyun.agentbay.model.SessionParams;
import com.aliyun.agentbay.session.Session;
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

        Session session = new Session("test-session-id", agentBay, new SessionParams());
        McpTool tool = new McpTool();
        tool.setName("get_metrics");
        tool.setServer("wuying_system");
        session.setMcpTools(Collections.singletonList(tool));

        when(apiClient.callMcpTool(
            eq("test-session-id"),
            eq("get_metrics"),
            any(),
            eq("wuying_system")
        )).thenReturn(null);

        SessionMetricsResult result = session.getMetrics();
        assertNotNull(result);

        verify(apiClient, times(1)).callMcpTool(
            eq("test-session-id"),
            eq("get_metrics"),
            any(),
            eq("wuying_system")
        );
    }
}

