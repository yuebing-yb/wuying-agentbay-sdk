package com.aliyun.agentbay;

import com.aliyun.agentbay.network.Network;
import com.aliyun.agentbay.network.NetworkResult;
import com.aliyun.agentbay.network.NetworkStatusResult;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.*;
import org.junit.Before;
import org.junit.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

public class NetworkTest {

    @Mock
    private AgentBay mockAgentBay;

    @Mock
    private Client mockClient;

    private Network network;

    @Before
    public void setUp() {
        MockitoAnnotations.openMocks(this);
        when(mockAgentBay.getApiKey()).thenReturn("test-api-key");
        when(mockAgentBay.getClient()).thenReturn(mockClient);
        network = new Network(mockAgentBay);
    }

    @Test
    public void testCreateNetworkSuccess() throws Exception {
        CreateNetworkResponseBody.CreateNetworkResponseBodyData responseData =
            new CreateNetworkResponseBody.CreateNetworkResponseBodyData();
        responseData.setNetworkId("network-123");
        responseData.setNetworkToken("token-abc");

        CreateNetworkResponseBody responseBody = new CreateNetworkResponseBody();
        responseBody.setSuccess(true);
        responseBody.setData(responseData);
        responseBody.setRequestId("req-123");

        CreateNetworkResponse response = new CreateNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.createNetwork(any(CreateNetworkRequest.class))).thenReturn(response);

        NetworkResult result = network.create();

        assertTrue(result.isSuccess());
        assertEquals("network-123", result.getNetworkId());
        assertEquals("token-abc", result.getNetworkToken());
        assertEquals("req-123", result.getRequestId());
        assertNull(result.getErrorMessage());
    }

    @Test
    public void testCreateNetworkWithCustomId() throws Exception {
        CreateNetworkResponseBody.CreateNetworkResponseBodyData responseData =
            new CreateNetworkResponseBody.CreateNetworkResponseBodyData();
        responseData.setNetworkId("custom-network");
        responseData.setNetworkToken("token-xyz");

        CreateNetworkResponseBody responseBody = new CreateNetworkResponseBody();
        responseBody.setSuccess(true);
        responseBody.setData(responseData);
        responseBody.setRequestId("req-456");

        CreateNetworkResponse response = new CreateNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.createNetwork(any(CreateNetworkRequest.class))).thenReturn(response);

        NetworkResult result = network.create("custom-network");

        assertTrue(result.isSuccess());
        assertEquals("custom-network", result.getNetworkId());
        assertEquals("token-xyz", result.getNetworkToken());
        assertEquals("req-456", result.getRequestId());
    }

    @Test
    public void testCreateNetworkFailure() throws Exception {
        CreateNetworkResponseBody responseBody = new CreateNetworkResponseBody();
        responseBody.setSuccess(false);
        responseBody.setMessage("Network creation failed");
        responseBody.setCode("InvalidParameter");
        responseBody.setRequestId("req-error");

        CreateNetworkResponse response = new CreateNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.createNetwork(any(CreateNetworkRequest.class))).thenReturn(response);

        NetworkResult result = network.create();

        assertFalse(result.isSuccess());
        assertNull(result.getNetworkId());
        assertNull(result.getNetworkToken());
        assertEquals("req-error", result.getRequestId());
        assertTrue(result.getErrorMessage().contains("InvalidParameter"));
        assertTrue(result.getErrorMessage().contains("Network creation failed"));
    }

    @Test
    public void testCreateNetworkNullResponse() throws Exception {
        when(mockClient.createNetwork(any(CreateNetworkRequest.class))).thenReturn(null);

        NetworkResult result = network.create();

        assertFalse(result.isSuccess());
        assertNull(result.getNetworkId());
        assertTrue(result.getErrorMessage().contains("Invalid response"));
    }

    @Test
    public void testDescribeNetworkSuccess() throws Exception {
        DescribeNetworkResponseBody.DescribeNetworkResponseBodyData responseData =
            new DescribeNetworkResponseBody.DescribeNetworkResponseBodyData();
        responseData.setOnline(true);

        DescribeNetworkResponseBody responseBody = new DescribeNetworkResponseBody();
        responseBody.setSuccess(true);
        responseBody.setData(responseData);
        responseBody.setRequestId("req-789");

        DescribeNetworkResponse response = new DescribeNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.describeNetwork(any(DescribeNetworkRequest.class))).thenReturn(response);

        NetworkStatusResult result = network.describe("network-123");

        assertTrue(result.isSuccess());
        assertTrue(result.isOnline());
        assertEquals("req-789", result.getRequestId());
        assertNull(result.getErrorMessage());
    }

    @Test
    public void testDescribeNetworkOffline() throws Exception {
        DescribeNetworkResponseBody.DescribeNetworkResponseBodyData responseData =
            new DescribeNetworkResponseBody.DescribeNetworkResponseBodyData();
        responseData.setOnline(false);

        DescribeNetworkResponseBody responseBody = new DescribeNetworkResponseBody();
        responseBody.setSuccess(true);
        responseBody.setData(responseData);
        responseBody.setRequestId("req-offline");

        DescribeNetworkResponse response = new DescribeNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.describeNetwork(any(DescribeNetworkRequest.class))).thenReturn(response);

        NetworkStatusResult result = network.describe("network-offline");

        assertTrue(result.isSuccess());
        assertFalse(result.isOnline());
        assertEquals("req-offline", result.getRequestId());
    }

    @Test
    public void testDescribeNetworkInvalidId() {
        NetworkStatusResult result = network.describe(null);

        assertFalse(result.isSuccess());
        assertFalse(result.isOnline());
        assertTrue(result.getErrorMessage().contains("network_id is required"));

        result = network.describe("");
        assertFalse(result.isSuccess());
        assertTrue(result.getErrorMessage().contains("network_id is required"));
    }

    @Test
    public void testDescribeNetworkNotFound() throws Exception {
        Map<String, Object> errorMap = new HashMap<>();
        errorMap.put("message", "Network NotFound");
        when(mockClient.describeNetwork(any(DescribeNetworkRequest.class)))
            .thenThrow(new com.aliyun.tea.TeaException(errorMap));

        NetworkStatusResult result = network.describe("non-existent");

        assertFalse(result.isSuccess());
        assertFalse(result.isOnline());
        assertTrue(result.getErrorMessage().contains("not found"));
    }

    @Test
    public void testDescribeNetworkFailure() throws Exception {
        DescribeNetworkResponseBody responseBody = new DescribeNetworkResponseBody();
        responseBody.setSuccess(false);
        responseBody.setMessage("Failed to describe network");
        responseBody.setCode("InternalError");
        responseBody.setRequestId("req-fail");

        DescribeNetworkResponse response = new DescribeNetworkResponse();
        response.setBody(responseBody);

        when(mockClient.describeNetwork(any(DescribeNetworkRequest.class))).thenReturn(response);

        NetworkStatusResult result = network.describe("network-123");

        assertFalse(result.isSuccess());
        assertFalse(result.isOnline());
        assertEquals("req-fail", result.getRequestId());
        assertTrue(result.getErrorMessage().contains("InternalError"));
    }

    @Test
    public void testNetworkResultToString() {
        NetworkResult result = new NetworkResult(
            "req-123",
            true,
            "network-id",
            "token",
            ""
        );

        String str = result.toString();
        assertTrue(str.contains("network-id"));
        assertTrue(str.contains("token"));
        assertTrue(str.contains("req-123"));
    }

    @Test
    public void testNetworkStatusResultToString() {
        NetworkStatusResult result = new NetworkStatusResult(
            "req-456",
            true,
            true,
            ""
        );

        String str = result.toString();
        assertTrue(str.contains("req-456"));
        assertTrue(str.contains("online=true"));
    }
}
