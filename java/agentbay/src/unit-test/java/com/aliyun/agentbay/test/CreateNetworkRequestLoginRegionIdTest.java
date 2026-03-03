package com.aliyun.agentbay.test;

import com.aliyun.teaopenapi.models.Config;
import com.aliyun.teautil.models.RuntimeOptions;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.CreateNetworkRequest;
import org.junit.Test;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertNotNull;

public class CreateNetworkRequestLoginRegionIdTest {

    static class CapturingClient extends Client {
        Map<String, Object> lastRequestBody;

        CapturingClient(Config config) throws Exception {
            super(config);
        }

        @Override
        public Map<String, Object> doRPCRequest(
            String action,
            String version,
            String protocol,
            String method,
            String authType,
            String bodyType,
            com.aliyun.teaopenapi.models.OpenApiRequest request,
            RuntimeOptions runtime
        ) throws Exception {
            lastRequestBody = extractBodyMap(request);
            Map<String, Object> response = new HashMap<>();
            Map<String, Object> body = new HashMap<>();
            body.put("RequestId", "test-request-id");
            body.put("Success", false);
            body.put("Code", "UnitTest");
            body.put("Message", "UnitTest");
            response.put("body", body);
            return response;
        }

        @SuppressWarnings("unchecked")
        private static Map<String, Object> extractBodyMap(com.aliyun.teaopenapi.models.OpenApiRequest request) throws Exception {
            try {
                Method getBody = request.getClass().getMethod("getBody");
                Object body = getBody.invoke(request);
                if (body instanceof Map) {
                    return (Map<String, Object>) body;
                }
            } catch (NoSuchMethodException ignored) {
                // fall through
            }
            try {
                Field bodyField = request.getClass().getDeclaredField("body");
                bodyField.setAccessible(true);
                Object body = bodyField.get(request);
                if (body instanceof Map) {
                    return (Map<String, Object>) body;
                }
            } catch (NoSuchFieldException ignored) {
                // fall through
            }
            return null;
        }
    }

    @Test
    public void testCreateNetworkIncludesLoginRegionIdInRequestBody() throws Exception {
        Config config = new Config();
        config.setEndpoint("example.com");
        config.setAccessKeyId("Bearer");
        config.setAccessKeySecret("test");

        CapturingClient client = new CapturingClient(config);
        CreateNetworkRequest request = new CreateNetworkRequest()
            .setAuthorization("Bearer test")
            .setNetworkId("net-123")
            .setLoginRegionId("cn-hangzhou");

        client.createNetworkWithOptions(request, new RuntimeOptions());

        assertNotNull(client.lastRequestBody);
        assertEquals("Bearer test", client.lastRequestBody.get("Authorization"));
        assertEquals("net-123", client.lastRequestBody.get("NetworkId"));
        assertEquals("cn-hangzhou", client.lastRequestBody.get("LoginRegionId"));
    }
}

