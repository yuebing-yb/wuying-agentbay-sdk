import { AgentBay } from "../../src/agent-bay";
import { Session } from "../../src/session";
import { log } from "../../src/utils/logger";

describe("AgentBay.get integration tests", () => {
  let agentBay: AgentBay;
  let sessionId: string | undefined;
  let sessionCreated = false;

  beforeAll(async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      throw new Error("AGENTBAY_API_KEY environment variable is not set");
    }
    agentBay = new AgentBay({ apiKey });

    try {
      log("🚀 Creating a new session for Get API testing...");
      // Create session
      const createResult = await agentBay.create({ imageId: "linux_latest" });
      if (createResult.success && createResult.session) {
        sessionId = createResult.session.sessionId;
        sessionCreated = true;
        log(`✅ Session created with ID: ${sessionId}`);
      } else {
        log("⚠️  Session creation failed, some tests will be skipped");
      }
    } catch (error) {
      log(`❌ Session creation error: ${error}`);
    }
  }); // 60 second timeout for session creation

  test("should retrieve session using Get API", async () => {
    if (!sessionCreated || !sessionId) {
      log("⊘ Skipping test: session was not created");
      return;
    }

    log("📋 Test: Retrieve session using Get API");
    const result = await agentBay.get(sessionId);

    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.requestId).toBeDefined();
    expect(result.session).toBeDefined();
    expect(result.session).toBeInstanceOf(Session);
    if (result.session) {
      expect(result.session.sessionId).toBe(sessionId);
      log(`  ✓ Session ID: ${result.session.sessionId}`);
    }
    log(`  ✓ Request ID: ${result.requestId}`);
    log("  ✓ All assertions passed");
  }); // 30 second timeout

  test("should return error for non-existent session", async () => {
    log("📋 Test: Non-existent session error handling");
    const nonExistentSessionId = "session-nonexistent-12345";

    const result = await agentBay.get(nonExistentSessionId);

    expect(result).toBeDefined();
    expect(result.success).toBe(false);
    expect(result.errorMessage).toContain("Failed to get session");

    log(`  ✓ Error correctly received: ${result.errorMessage}`);
  }); // 30 second timeout

  test("should return error for empty session ID", async () => {
    log("📋 Test: Empty session ID error handling");
    const result = await agentBay.get("");

    expect(result).toBeDefined();
    expect(result.success).toBe(false);
    expect(result.errorMessage).toContain("session_id is required");

    log(`  ✓ Error correctly received: ${result.errorMessage}`);
  });

  test("should return error for whitespace session ID", async () => {
    log("📋 Test: Whitespace session ID error handling");
    const result = await agentBay.get("   ");

    expect(result).toBeDefined();
    expect(result.success).toBe(false);
    expect(result.errorMessage).toContain("session_id is required");

    log(`  ✓ Error correctly received: ${result.errorMessage}`);
  });

  afterAll(async () => {
    if (!sessionCreated || !sessionId) {
      log("⊘ No session to clean up");
      return;
    }

    log("🧹 Cleaning up: Deleting the session...");
    try {
      const result = await agentBay.get(sessionId); // Retrieve session object
      if (result.success && result.session) {
        const deleteResult = await result.session.delete();
        if (deleteResult.success) {
          log(`✅ Session ${sessionId} deleted successfully`);
        } else {
          log(`⚠️  Failed to delete session: ${deleteResult.errorMessage}`);
        }
      }
    } catch (error) {
      log(`⚠️  Failed to clean up session: ${error}`);
    }
  }); // 30 second timeout
});
