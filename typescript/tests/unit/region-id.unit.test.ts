import { AgentBay } from "../../src";

describe("Region ID Unit Tests", () => {
  const mockApiKey = "test-api-key-12345";

  describe("AgentBay initialization", () => {
    test("should create AgentBay client with region_id", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        regionId: "cn-hangzhou"
      });

      expect(client.getRegionId()).toBe("cn-hangzhou");
    });

    test("should create AgentBay client without region_id", () => {
      const client = new AgentBay({ 
        apiKey: mockApiKey 
      });

      expect(client.getRegionId()).toBeUndefined();
    });

    test("should handle empty region_id", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        regionId: ""
      });

      expect(client.getRegionId()).toBe("");
    });

    test("should handle multiple initialization options", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        regionId: "cn-beijing",
        config: {
          endpoint: "test.endpoint.com",
          timeout_ms: 30000
        }
      });

      expect(client.getRegionId()).toBe("cn-beijing");
    });
  });
});