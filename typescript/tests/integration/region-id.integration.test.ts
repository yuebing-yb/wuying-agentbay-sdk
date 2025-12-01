import { AgentBay } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";

describe("Region ID Integration Tests", () => {
  let apiKey: string;

  beforeAll(() => {
    apiKey = getTestApiKey();
  });

  describe("AgentBay initialization", () => {
    test("should create AgentBay client with region_id", () => {
      const client = new AgentBay({
        apiKey,
        regionId: "cn-hangzhou"
      });

      expect(client.getRegionId()).toBe("cn-hangzhou");
    });

    test("should create AgentBay client without region_id", () => {
      const client = new AgentBay({ apiKey });

      expect(client.getRegionId()).toBeUndefined();
    });

    test("should handle empty region_id", () => {
      const client = new AgentBay({
        apiKey,
        regionId: ""
      });

      expect(client.getRegionId()).toBe("");
    });
  });

  describe("Session creation with region_id", () => {
    test("should create session successfully with region_id", async () => {
      const client = new AgentBay({
        apiKey,
        regionId: "cn-beijing"
      });

      const sessionResult = await client.create({});

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.session!.sessionId).toBeDefined();

      // Clean up
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 60000);

    test("should create session successfully without region_id", async () => {
      const client = new AgentBay({ apiKey });

      const sessionResult = await client.create({});

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.session!.sessionId).toBeDefined();

      // Clean up
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 60000);
  });

  describe("Context operations with region_id", () => {
    test("should create context successfully with region_id", async () => {
      const client = new AgentBay({
        apiKey,
        regionId: "cn-shenzhen"
      });

      const contextName = `test-context-typescript-region-id-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.context).toBeDefined();
      expect(contextResult.context!.id).toBeDefined();
      expect(contextResult.context!.name).toBe(contextName);

      // Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
    }, 30000);

    test("should get existing context without create (no LoginRegionId)", async () => {
      const client = new AgentBay({
        apiKey,
        regionId: "cn-shenzhen"
      });

      // Try to get non-existent context without create
      const contextName = `non-existent-context-${Date.now()}`;
      const contextResult = await client.context.get(contextName, false);

      // Should fail for non-existent context
      expect(contextResult.success).toBe(false);
      expect(contextResult.context).toBeUndefined();
    }, 30000);

    test("should create context successfully without region_id", async () => {
      const client = new AgentBay({ apiKey });

      const contextName = `test-context-no-region-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.context).toBeDefined();
      expect(contextResult.context!.id).toBeDefined();

      // Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
    }, 30000);
  });

  describe("End-to-end workflow with region_id", () => {
    test("should complete full workflow with region_id", async () => {
      const client = new AgentBay({
        apiKey,
        regionId: "cn-hangzhou"
      });

      // 1. Create context
      const contextName = `e2e-test-context-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // 2. Create session
      const sessionResult = await client.create({});
      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();

      // 3. Get session info
      const sessionInfo = await sessionResult.session!.info();
      expect(sessionInfo.success).toBe(true);
      expect(sessionInfo.sessionId).toBe(sessionResult.session!.sessionId);

      // 4. Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 90000);
  });
});