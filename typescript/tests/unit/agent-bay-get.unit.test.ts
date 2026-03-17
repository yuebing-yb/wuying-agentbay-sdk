import { AgentBay } from "../../src/agent-bay";
import * as sinon from "sinon";

describe("AgentBay.get unit tests", () => {
  let mockClient: any;

  beforeEach(() => {
    mockClient = {
      getSession: sinon.stub(),
      getSessionDetail: sinon.stub(),
      createMcpSession: sinon.stub(),
      listSession: sinon.stub(),
      deleteSessionAsync: sinon.stub(),
      getContextInfo: sinon.stub(),
    };

    sinon
      .stub(require("../../src/api/client"), "Client")
      .callsFake(() => mockClient);
    sinon
      .stub(require("../../src/context"), "ContextService")
      .callsFake(() => ({
        get: sinon
          .stub()
          .resolves({ success: false, errorMessage: "Context not found" }),
      }));
  });

  afterEach(() => {
    sinon.restore();
  });

  describe("Input validation", () => {
    let agentBay: AgentBay;

    beforeEach(() => {
      agentBay = new AgentBay({ apiKey: "test-api-key" });
    });

    test("should return error for empty session ID", async () => {
      const result = await agentBay.get("");
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain("session_id is required");
    });

    test("should return error for whitespace-only session ID", async () => {
      const result = await agentBay.get("   ");
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain("session_id is required");
    });

    test("should return error for undefined session ID", async () => {
      const result = await agentBay.get(undefined as any);
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain("session_id is required");
    });

    test("should return error for null session ID", async () => {
      const result = await agentBay.get(null as any);
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain("session_id is required");
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
        const result = await agentBay.get(testCase.input);
        expect(result.success).toBe(false);
        expect(result.errorMessage).toContain(testCase.expected);
      }
    });
  });

  describe("Interface compliance", () => {
    test("get method should return Promise<SessionResult>", () => {
      const agentBay = new AgentBay({ apiKey: "test-api-key" });
      const result = agentBay.get("test-session-id");
      expect(result).toBeInstanceOf(Promise);
    });
  });
});
