import { AgentBay } from "./agent-bay";
import * as $_client from "./api";
import { APIError } from "./exceptions";
import { extractRequestId } from "./types/api-response";
import type { NetworkResult, NetworkStatusResult } from "./types/api-response";
import { logAPICall, logAPIResponseWithDetails, logDebug } from "./utils/logger";

/**
 * Beta network service (trial feature).
 */
export class BetaNetworkService {
  private agentBay: AgentBay;

  constructor(agentBay: AgentBay) {
    this.agentBay = agentBay;
  }

  async getNetworkBindToken(networkId?: string): Promise<NetworkResult> {
    try {
      const request = new $_client.CreateNetworkRequest({
        authorization: `Bearer ${this.agentBay.getAPIKey()}`,
        loginRegionId: this.agentBay.getRegionId(),
        networkId,
      });

      logAPICall("CreateNetwork(beta)");
      if (networkId) {
        logDebug(`Request: NetworkId=${networkId}`);
      }

      const response = await this.agentBay.getClient().createNetwork(request);
      const requestId = extractRequestId(response) || "";

      if (!response.body || typeof response.body !== "object") {
        logAPIResponseWithDetails("CreateNetwork(beta)", requestId, false, undefined, "Invalid response format");
        return {
          requestId,
          success: false,
          networkId: "",
          networkToken: "",
          errorMessage: "Invalid response from CreateNetwork API",
        };
      }

      if (response.body.success === false) {
        const code = response.body.code ? `[${response.body.code}] ` : "";
        const msg = response.body.message || "Unknown error";
        return {
          requestId,
          success: false,
          networkId: "",
          networkToken: "",
          errorMessage: `${code}${msg}`,
        };
      }

      const data = response.body.data;
      if (!data || typeof data !== "object") {
        return {
          requestId,
          success: false,
          networkId: "",
          networkToken: "",
          errorMessage: "Network data not found in response",
        };
      }

      return {
        requestId,
        success: true,
        networkId: data.networkId || "",
        networkToken: data.networkToken || "",
      };
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : `${error}`;
      throw new APIError(`CreateNetwork(beta) failed: ${msg}`);
    }
  }

  /**
   * Deprecated: use getNetworkBindToken().
   */
  async create(networkId?: string): Promise<NetworkResult> {
    return await this.getNetworkBindToken(networkId);
  }

  async describe(networkId: string): Promise<NetworkStatusResult> {
    if (!networkId) {
      return {
        requestId: "",
        success: false,
        online: false,
        errorMessage: "network_id is required",
      };
    }

    const maxAttempts = 3;
    let delayMs = 200;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        const request = new $_client.DescribeNetworkRequest({
          authorization: `Bearer ${this.agentBay.getAPIKey()}`,
          networkId,
        });

        logAPICall("DescribeNetwork(beta)");
        logDebug(`Request: NetworkId=${networkId}`);

        const response = await this.agentBay.getClient().describeNetwork(request);
        const requestId = extractRequestId(response) || "";

        if (!response.body || typeof response.body !== "object") {
          logAPIResponseWithDetails("DescribeNetwork(beta)", requestId, false, undefined, "Invalid response format");
          return {
            requestId,
            success: false,
            online: false,
            errorMessage: "Invalid response from DescribeNetwork API",
          };
        }

        if (response.body.success === false) {
          const code = response.body.code ? `[${response.body.code}] ` : "";
          const msg = response.body.message || "Unknown error";
          return {
            requestId,
            success: false,
            online: false,
            errorMessage: `${code}${msg}`,
          };
        }

        const online = Boolean(response.body.data?.online);
        return {
          requestId,
          success: true,
          online,
        };
      } catch (error: unknown) {
        const msg = error instanceof Error ? error.message : `${error}`;
        if (attempt < maxAttempts && (msg.includes("ServiceUnavailable") || msg.includes("503"))) {
          await new Promise((resolve) => setTimeout(resolve, delayMs));
          delayMs *= 2;
          continue;
        }
        throw new APIError(`DescribeNetwork(beta) failed: ${msg}`);
      }
    }
    throw new APIError("DescribeNetwork(beta) failed: exhausted retries");
  }
}


