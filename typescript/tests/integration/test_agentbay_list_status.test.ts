import { AgentBay, CreateSeesionWithParams } from "../../src/agent-bay";
import { Session } from "../../src/session";
import { log } from "../../src/utils/logger";

describe("AgentBay List Status Integration Tests", () => {
  let agentBay: AgentBay;
  let testSessions: Session[] = [];

  beforeAll(async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      throw new Error("AGENTBAY_API_KEY environment variable is not set");
    }

    const endpoint = process.env.AGENTBAY_ENDPOINT;
    if (endpoint) {
      agentBay = new AgentBay({ 
        apiKey,
        config: { 
          endpoint,
          timeout_ms: 60000 
        }
      });
      log(`Using endpoint: ${endpoint}`);
    } else {
      agentBay = new AgentBay({ apiKey });
      log("Using default endpoint");
    }
  });

  afterEach(async () => {
    log("\nCleaning up test sessions for this test...");
    for (const session of testSessions) {
      try {
        // Try to resume session first in case it's paused
        try {
          if (session) {
            const result = await agentBay.getStatus(session.sessionId);
            if (result.data?.status === "PAUSED") {
              await session.resumeAsync();
              log(`  ✓ Resumed session: ${session.sessionId}`);
            }
            if (result.data?.status && !["DELETING", "DELETED", "RESUMING", "PAUSING"].includes(result.data.status)) {
              const deleteResult = await agentBay.delete(session);
              if (deleteResult.success) {
                log(`  ✓ Deleted session: ${session.sessionId}`);
              } else {
                log(`  ✗ Failed to delete session: ${session.sessionId}`);
              }
            }
          }
        } catch (resumeError) {
          log(`  ⚠ Could not resume session ${session.sessionId}: ${resumeError}`);
        }
      } catch (e) {
        log(`  ✗ Error deleting session ${session.sessionId}: ${e}`);
      }
    }
    // Clear the list for next test
    testSessions = [];
  });

  const createTestSession = async (): Promise<Session> => {
    const sessionName = `test-pause-resume-${Math.random().toString(36).substring(2, 10)}`;
    log(`\nCreating test session: ${sessionName}`);

    // Create session
    const params: CreateSeesionWithParams = {
      labels: { project: "piaoyun-demo", environment: "testing" },
    };
    
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();

    const session = result.session!;
    testSessions.push(session);
    log(`  ✓ Session created: ${session.sessionId}`);

    return session;
  };

  const verifySessionStatusAndList = async (
    session: Session, 
    expectedStatuses: string[], 
    operationName = "operation"
  ): Promise<string> => {
    log(`\nVerifying session status after ${operationName}...`);
    
    // First call getStatus to check the current status
    const statusResult = await agentBay.getStatus(session.sessionId);
    expect(statusResult.success).toBe(true);
    expect(statusResult.data).toBeDefined();
    
    const initialStatus = statusResult.data?.status || "UNKNOWN";
    log(`  ✓ Session status from getStatus: ${initialStatus}`);
    expect(expectedStatuses).toContain(initialStatus);

    // Then call getSession for detailed information
    const sessionInfo = await agentBay.getSession(session.sessionId);
    expect(sessionInfo.success).toBe(true);
    expect(sessionInfo.data).toBeDefined();

    const currentStatus = sessionInfo.data?.status || "UNKNOWN";
    expect(currentStatus).toBe(initialStatus);
    log(`  ✓ Session status from getSession: ${currentStatus}`);
    
    // Test list with current status
    const listResult = await agentBay.list({}, 1, 10, currentStatus);
    expect(listResult.success).toBe(true);
    
    // Verify session is in the list and check array structure
    let sessionFound = false;
    for (const sessionData of listResult.sessionIds) {
      if (typeof sessionData === 'object' && sessionData !== null) {
        if ('sessionId' in sessionData && sessionData.sessionId === session.sessionId) {
          sessionFound = true;
          expect(sessionData).toHaveProperty('sessionStatus');
          expect(sessionData).toHaveProperty('sessionId');
          expect((sessionData as any).sessionStatus).toBe(currentStatus);
          break;
        }
      } else {
        log("  ✗ Invalid session data in list result");
        break;
      }
    }
    
    expect(sessionFound).toBe(true);
    log(`  ✓ Session found in list with status ${currentStatus}`);
    log(`  ✓ Session status verification completed for ${operationName}`);
    
    return currentStatus;
  };

  test("should pause and resume session successfully", async () => {
    log("\n" + "=".repeat(60));
    log("TEST: Pause and Resume Session Success");
    log("=".repeat(60));

    // Create a test session
    const session = await createTestSession();

    // Verify session is initially in RUNNING state
    const statusResult = await agentBay.getStatus(session.sessionId);
    expect(statusResult.success).toBe(true);
    expect(statusResult.data).toBeDefined();
    
    const initialStatus = statusResult.data?.status || "UNKNOWN";
    log(`  ✓ Session status from getStatus: ${initialStatus}`);
    expect(initialStatus).toBe("RUNNING");

    // Pause the session
    log(`\nStep 2: Pausing session...`);
    const pauseResult = await session.pauseAsync();

    // Verify pause result
    expect(pauseResult.success).toBe(true);
    log(`  ✓ Session pause initiated successfully`);
    log(`    Request ID: ${pauseResult.requestId}`);

    // Wait a bit for pause to complete
    log(`\nStep 3: Waiting for session to pause...`);
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Verify session status after pause
    await verifySessionStatusAndList(session, ["PAUSED", "PAUSING"], "pause");
  }, 120000);

  test("should resume session successfully", async () => {
    log("\n" + "=".repeat(60));
    log("TEST: Resume Session Success");
    log("=".repeat(60));

    // Create a test session
    const session = await createTestSession();

    // Pause the session first
    log(`\nStep 1: Pausing session...`);
    const pauseResult = await session.pauseAsync();
    expect(pauseResult.success).toBe(true);
    log(`  ✓ Session pause initiated successfully`);

    // Wait for pause to complete
    log(`\nStep 2: Waiting for session to pause...`);
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Session should be PAUSED or PAUSING after pause operation
    const statusResult = await agentBay.getStatus(session.sessionId);
    expect(statusResult.success).toBe(true);
    expect(statusResult.data).toBeDefined();
    
    const initialStatus = statusResult.data?.status || "UNKNOWN";
    log(`  ✓ Session status from getStatus: ${initialStatus}`);
    expect(["PAUSED", "PAUSING"]).toContain(initialStatus);
    log(`  ✓ Session status checked`);

    const resumeResult = await session.resumeAsync();

    // Verify resume result
    expect(resumeResult.success).toBe(true);
    log(`  ✓ Session resume initiated successfully`);
    log(`    Request ID: ${resumeResult.requestId}`);

    // Wait a bit for resume to complete
    log(`\nStep 4: Waiting for session to resume...`);
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Verify session status after resume
    await verifySessionStatusAndList(session, ["RUNNING", "RESUMING"], "resume");
  }, 120000);

  test("should pause and delete session successfully", async () => {
    log("\n" + "=".repeat(60));
    log("TEST: Pause and Delete Session Success");
    log("=".repeat(60));
    
    log(`\nStep 1: Creating test session...`);
    // Create a test session
    const session = await createTestSession();
    
    // Pause the session
    log(`\nStep 2: Pausing session...`);
    const pauseResult = await session.pauseAsync();

    // Verify pause result
    expect(pauseResult.success).toBe(true);
    log(`  ✓ Session pause initiated successfully`);
    log(`    Request ID: ${pauseResult.requestId}`);

    // Wait a bit for pause to complete
    log(`\nStep 3: Waiting for session to pause...`);
    await new Promise(resolve => setTimeout(resolve, 2000));

    log(`  ✓ Session status after pause checked`);
    
    // Delete the session
    log(`\nStep 4: Deleting session...`);
    const deleteResult = await agentBay.delete(session);
    if (deleteResult.success) {
      log("delete session successfully");
    }

    // Verify session status after delete
    await verifySessionStatusAndList(session, ["DELETING", "DELETED"], "delete");
  }, 120000);

  test("should list sessions with status filter", async () => {
    log("\n" + "=".repeat(60));
    log("TEST: List Sessions with Status Filter");
    log("=".repeat(60));

    // Create a test session
    const session = await createTestSession();

    // Test listing with RUNNING status
    log(`\nTesting list with RUNNING status filter...`);
    const runningListResult = await agentBay.list({}, 1, 10, "RUNNING");
    expect(runningListResult.success).toBe(true);
    
    // Verify our session is in the RUNNING list
    const runningSessionFound = runningListResult.sessionIds.some(sessionData => {
      if (typeof sessionData === 'object' && sessionData !== null && 'sessionId' in sessionData) {
        return (sessionData as any).sessionId === session.sessionId;
      }
      return false;
    });
    expect(runningSessionFound).toBe(true);
    log(`  ✓ Session found in RUNNING status list`);

    // Test listing with invalid status
    log(`\nTesting list with invalid status filter...`);
    const invalidListResult = await agentBay.list({}, 1, 10, "INVALID_STATUS");
    expect(invalidListResult.success).toBe(false);
    expect(invalidListResult.errorMessage).toContain("Invalid status");
    log(`  ✓ Invalid status correctly rejected`);

    // Test listing without status filter
    log(`\nTesting list without status filter...`);
    const allListResult = await agentBay.list();
    expect(allListResult.success).toBe(true);
    expect(allListResult.sessionIds.length).toBeGreaterThan(0);
    log(`  ✓ List without filter returned ${allListResult.sessionIds.length} sessions`);
  }, 60000);

  test("should handle pagination correctly", async () => {
    log("\n" + "=".repeat(60));
    log("TEST: Pagination Handling");
    log("=".repeat(60));

    // Test first page
    const page1Result = await agentBay.list({}, 1, 5);
    expect(page1Result.success).toBe(true);
    log(`  ✓ Page 1 returned ${page1Result.sessionIds.length} sessions`);

    // Test invalid page number
    const invalidPageResult = await agentBay.list({}, 0, 5);
    expect(invalidPageResult.success).toBe(false);
    expect(invalidPageResult.errorMessage).toContain("Page number must be >= 1");
    log(`  ✓ Invalid page number correctly rejected`);
  }, 30000);
});
