import { Client } from "../../src/api/client";
import {
  GetCdpLinkRequest,
  GetCdpLinkResponse,
  GetAdbLinkRequest,
  GetAdbLinkResponse,
} from "../../src/api/models/model";
import * as $dara from "@darabonba/typescript";
import { $OpenApiUtil } from "@alicloud/openapi-core";

describe("GetCdpLink and GetAdbLink API", () => {
  let client: Client;
  let mockDoRPCRequest: jest.SpyInstance;

  beforeEach(() => {
    const config = new $OpenApiUtil.Config({
      endpoint: "https://test.endpoint.com",
      accessKeyId: "test-key",
      accessKeySecret: "test-secret",
      regionId: "cn-hangzhou",
    });
    client = new Client(config);
    mockDoRPCRequest = jest.spyOn(client as any, "doRPCRequest");
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe("getCdpLink", () => {
    it("should successfully get CDP link", async () => {
      const mockResponse = {
        headers: {},
        statusCode: 200,
        body: {
          Success: true,
          Data: {
            Url: "ws://test.cdp.link",
          },
          RequestId: "req123",
        },
      };

      mockDoRPCRequest.mockResolvedValue(mockResponse);

      const request = new GetCdpLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
      });

      const response = await client.getCdpLink(request);

      expect(response).toBeInstanceOf(GetCdpLinkResponse);
      expect(response.body?.success).toBe(true);
      expect(response.body?.data?.url).toBe("ws://test.cdp.link");
      expect(response.body?.requestId).toBe("req123");
      expect(mockDoRPCRequest).toHaveBeenCalledTimes(1);
    });

    it("should call getCdpLinkWithOptions with runtime", async () => {
      const mockResponse = {
        headers: {},
        statusCode: 200,
        body: {
          Success: true,
          Data: {
            Url: "ws://test.cdp.link",
          },
        },
      };

      mockDoRPCRequest.mockResolvedValue(mockResponse);

      const request = new GetCdpLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
      });
      const runtime = new $dara.RuntimeOptions({});

      const response = await client.getCdpLinkWithOptions(request, runtime);

      expect(response).toBeInstanceOf(GetCdpLinkResponse);
      expect(response.body?.success).toBe(true);
      expect(mockDoRPCRequest).toHaveBeenCalledTimes(1);
    });

    it("should handle getCdpLink failure", async () => {
      mockDoRPCRequest.mockRejectedValue(new Error("API call failed"));

      const request = new GetCdpLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
      });

      await expect(client.getCdpLink(request)).rejects.toThrow(
        "API call failed"
      );
    });
  });

  describe("getAdbLink", () => {
    it("should successfully get ADB link", async () => {
      const mockResponse = {
        headers: {},
        statusCode: 200,
        body: {
          Success: true,
          Data: {
            Url: "adb://test.adb.link:5555",
          },
          RequestId: "req456",
        },
      };

      mockDoRPCRequest.mockResolvedValue(mockResponse);

      const request = new GetAdbLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
        option: JSON.stringify({ adbkey_pub: "test-public-key" }),
      });

      const response = await client.getAdbLink(request);

      expect(response).toBeInstanceOf(GetAdbLinkResponse);
      expect(response.body?.success).toBe(true);
      expect(response.body?.data?.url).toBe("adb://test.adb.link:5555");
      expect(response.body?.requestId).toBe("req456");
      expect(mockDoRPCRequest).toHaveBeenCalledTimes(1);
    });

    it("should call getAdbLinkWithOptions with runtime", async () => {
      const mockResponse = {
        headers: {},
        statusCode: 200,
        body: {
          Success: true,
          Data: {
            Url: "adb://test.adb.link:5555",
          },
        },
      };

      mockDoRPCRequest.mockResolvedValue(mockResponse);

      const request = new GetAdbLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
        option: JSON.stringify({ adbkey_pub: "test-public-key" }),
      });
      const runtime = new $dara.RuntimeOptions({});

      const response = await client.getAdbLinkWithOptions(request, runtime);

      expect(response).toBeInstanceOf(GetAdbLinkResponse);
      expect(response.body?.success).toBe(true);
      expect(mockDoRPCRequest).toHaveBeenCalledTimes(1);
    });

    it("should handle getAdbLink failure", async () => {
      mockDoRPCRequest.mockRejectedValue(new Error("API call failed"));

      const request = new GetAdbLinkRequest({
        authorization: "Bearer test_token",
        sessionId: "test_session_id",
        option: JSON.stringify({ adbkey_pub: "test-key" }),
      });

      await expect(client.getAdbLink(request)).rejects.toThrow(
        "API call failed"
      );
    });
  });
});

