import { AgentBay } from "../../src/agent-bay";
import { Session } from "../../src/session";

describe("AgentBay.get unit tests", () => {
  describe("Input validation", () => {
    let agentBay: AgentBay;

    beforeEach(() => {
      agentBay = new AgentBay({ apiKey: "test-api-key" });
    });

    test("should throw error for empty session ID", async () => {
      await expect(agentBay.get("")).rejects.toThrow("session_id is required");
    });

    test("should throw error for whitespace-only session ID", async () => {
      await expect(agentBay.get("   ")).rejects.toThrow(
        "session_id is required"
      );
    });

    test("should throw error for undefined session ID", async () => {
      await expect(agentBay.get(undefined as any)).rejects.toThrow(
        "session_id is required"
      );
    });

    test("should throw error for null session ID", async () => {
      await expect(agentBay.get(null as any)).rejects.toThrow(
        "session_id is required"
      );
    });
  });

  describe("Method existence", () => {
    test("should have get method", () => {
      const agentBay = new AgentBay({ apiKey: "test-api-key" });
      expect(agentBay.get).toBeDefined();
      expect(typeof agentBay.get).toBe("function");
    });
  });

  describe("Error messages", () => {
    let agentBay: AgentBay;

    beforeEach(() => {
      agentBay = new AgentBay({ apiKey: "test-api-key" });
    });

    test("should format validation error correctly", async () => {
      const testCases = [
        { input: "", expected: "session_id is required" },
        { input: "   ", expected: "session_id is required" },
        { input: null as any, expected: "session_id is required" },
        { input: undefined as any, expected: "session_id is required" },
      ];

      for (const testCase of testCases) {
        await expect(agentBay.get(testCase.input)).rejects.toThrow(
          testCase.expected
        );
      }
    });
  });

  describe("Interface compliance", () => {
    test("get method should return Promise<Session>", () => {
      const agentBay = new AgentBay({ apiKey: "test-api-key" });
      const result = agentBay.get("test-session-id");
      expect(result).toBeInstanceOf(Promise);
    });
  });
});

