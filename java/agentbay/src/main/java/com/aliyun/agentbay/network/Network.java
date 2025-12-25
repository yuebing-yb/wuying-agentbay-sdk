package com.aliyun.agentbay.network;

import com.aliyun.agentbay.AgentBay;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Network {
    private static final Logger logger = LoggerFactory.getLogger(Network.class);

    private AgentBay agentBay;

    public Network(AgentBay agentBay) {
        this.agentBay = agentBay;
    }

    public NetworkResult create() {
        return create(null);
    }

    public NetworkResult create(String networkId) {
        try {
            logger.debug("Creating network with networkId: {}", networkId);

            com.aliyun.wuyingai20250506.models.CreateNetworkRequest request =
                new com.aliyun.wuyingai20250506.models.CreateNetworkRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());

            if (networkId != null && !networkId.isEmpty()) {
                request.setNetworkId(networkId);
            }

            com.aliyun.wuyingai20250506.models.CreateNetworkResponse response =
                agentBay.getClient().createNetwork(request);

            if (response == null || response.getBody() == null) {
                return new NetworkResult(
                    "",
                    false,
                    null,
                    null,
                    "Invalid response from CreateNetwork API"
                );
            }

            com.aliyun.wuyingai20250506.models.CreateNetworkResponseBody body = response.getBody();
            String requestId = body.getRequestId() != null ? body.getRequestId() : "";

            if (body.getSuccess() == null || !body.getSuccess()) {
                String errorMsg = body.getMessage() != null ? body.getMessage() : "Unknown error";
                if (body.getCode() != null) {
                    errorMsg = "[" + body.getCode() + "] " + errorMsg;
                }
                return new NetworkResult(
                    requestId,
                    false,
                    null,
                    null,
                    errorMsg
                );
            }

            if (body.getData() == null) {
                return new NetworkResult(
                    requestId,
                    false,
                    null,
                    null,
                    "Network data not found in response"
                );
            }

            String createdNetworkId = body.getData().getNetworkId();
            String networkToken = body.getData().getNetworkToken();

            logger.info("Network created successfully: {}", createdNetworkId);

            return new NetworkResult(
                requestId,
                true,
                createdNetworkId,
                networkToken,
                ""
            );

        } catch (com.aliyun.tea.TeaException e) {
            String errorStr = e.getMessage();
            String requestId = "";
            if (e.getData() != null && e.getData().get("RequestId") != null) {
                requestId = e.getData().get("RequestId").toString();
            }

            logger.error("Error creating network: {}", errorStr, e);
            return new NetworkResult(
                requestId,
                false,
                null,
                null,
                "Failed to create network: " + errorStr
            );
        } catch (Exception e) {
            logger.error("Unexpected error creating network", e);
            return new NetworkResult(
                "",
                false,
                null,
                null,
                "Failed to create network: " + e.getMessage()
            );
        }
    }

    public NetworkStatusResult describe(String networkId) {
        if (networkId == null || networkId.isEmpty()) {
            return new NetworkStatusResult(
                "",
                false,
                false,
                "network_id is required"
            );
        }

        try {
            logger.debug("Describing network: {}", networkId);

            com.aliyun.wuyingai20250506.models.DescribeNetworkRequest request =
                new com.aliyun.wuyingai20250506.models.DescribeNetworkRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setNetworkId(networkId);

            com.aliyun.wuyingai20250506.models.DescribeNetworkResponse response =
                agentBay.getClient().describeNetwork(request);

            if (response == null || response.getBody() == null) {
                return new NetworkStatusResult(
                    "",
                    false,
                    false,
                    "Invalid response from DescribeNetwork API"
                );
            }

            com.aliyun.wuyingai20250506.models.DescribeNetworkResponseBody body = response.getBody();
            String requestId = body.getRequestId() != null ? body.getRequestId() : "";

            if (body.getSuccess() == null || !body.getSuccess()) {
                String errorMsg = body.getMessage() != null ? body.getMessage() : "Unknown error";
                if (body.getCode() != null) {
                    errorMsg = "[" + body.getCode() + "] " + errorMsg;
                }
                return new NetworkStatusResult(
                    requestId,
                    false,
                    false,
                    errorMsg
                );
            }

            boolean online = false;
            if (body.getData() != null && body.getData().getOnline() != null) {
                online = body.getData().getOnline();
            }

            logger.debug("Network {} status: online={}", networkId, online);

            return new NetworkStatusResult(
                requestId,
                true,
                online,
                ""
            );

        } catch (com.aliyun.tea.TeaException e) {
            String errorStr = e.getMessage();
            String requestId = "";
            if (e.getData() != null && e.getData().get("RequestId") != null) {
                requestId = e.getData().get("RequestId").toString();
            }

            if (errorStr != null && errorStr.contains("NotFound")) {
                logger.info("Network not found: {}", networkId);
                return new NetworkStatusResult(
                    requestId,
                    false,
                    false,
                    "Network " + networkId + " not found"
                );
            }

            logger.error("Error describing network: {}", errorStr, e);
            return new NetworkStatusResult(
                requestId,
                false,
                false,
                "Failed to describe network: " + errorStr
            );
        } catch (Exception e) {
            logger.error("Unexpected error describing network", e);
            return new NetworkStatusResult(
                "",
                false,
                false,
                "Failed to describe network: " + e.getMessage()
            );
        }
    }
}
