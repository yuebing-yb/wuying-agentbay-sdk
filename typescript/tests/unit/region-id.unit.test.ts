import { AgentBay } from "../../src";

describe("Region ID Unit Tests", () => {
  const mockApiKey = "test-api-key-12345";

  describe("AgentBay initialization", () => {
    test("should create AgentBay client with region_id", () => {
  const config = {
    endpoint: "wuyingai.cn-shanghai.aliyuncs.com",
    timeout_ms: 60000,
    region_id: "cn-hangzhou"
  };
  const client = new AgentBay({
    apiKey: "test-api-key",
    config: config
  });
  expect(client.getRegionId()).toBe("cn-hangzhou");
});

    test("should fill defaults when config only provides region_id", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        config: {
          region_id: "cn-hangzhou",
        } as any,
      });

      expect(client.getRegionId()).toBe("cn-hangzhou");
      expect((client as any).endpoint).toBe("wuyingai.cn-shanghai.aliyuncs.com");
      expect((client as any).config.timeout_ms).toBe(60000);
    });

    test("should create AgentBay client without region_id", () => {
      const client = new AgentBay({ 
        apiKey: mockApiKey 
      });

      expect(client.getRegionId()).toBeUndefined();
    });

    test("should handle empty region_id", () => {
  const config = {
    endpoint: "wuyingai.cn-shanghai.aliyuncs.com",
    timeout_ms: 60000,
    region_id: ""
  };
  const client = new AgentBay({
    apiKey: "test-api-key",
    config: config
  });
  expect(client.getRegionId()).toBe("");
});

    test("should handle multiple initialization options", () => {
      const config = {
    endpoint: "wuyingai.cn-shanghai.aliyuncs.com",
    timeout_ms: 60000,
    region_id: "cn-hangzhou"
  };
  const client = new AgentBay({
    apiKey: "test-api-key",
    config: config
  });

      expect(client.getRegionId()).toBe("cn-hangzhou");
    });
  });
});