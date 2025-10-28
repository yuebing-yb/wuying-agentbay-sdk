import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session Cleanup Integration Test", () => {
  let agentBay: AgentBay;

  beforeAll(() => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
  });

  it("should list all sessions, recover them via get, and delete them", async () => {
    try {
      log("=== Starting Session Cleanup Test ===");

      // Step 1: List all sessions
      log("Step 1: Listing all sessions...");
      const listResult = await agentBay.list();

      if (!listResult.success) {
        log(`Failed to list sessions: ${listResult.errorMessage}`);
        expect(listResult.success).toBe(true);
        return;
      }

      const sessionIds = listResult.sessionIds || [];
      log(`Found ${sessionIds.length} sessions to clean up`);
      log(`Session IDs: ${JSON.stringify(sessionIds)}`);
      log(`Total Count: ${listResult.totalCount || "N/A"}`);
      log(`Request ID: ${listResult.requestId}`);

      if (sessionIds.length === 0) {
        log("No sessions to clean up, test passed");
        expect(sessionIds.length).toBe(0);
        return;
      }

      // Step 2: For each session ID, recover it via get() and delete it
      const deleteResults = [];
      const deletedSessionIds = [];

      for (let i = 0; i < sessionIds.length; i++) {
        const sessionId = sessionIds[i];
        log(`\n--- Processing session ${i + 1}/${sessionIds.length}: ${sessionId} ---`);

        // Step 2a: Recover session via get()
        log(`Recovering session ${sessionId} via get()...`);
        const getResult = await agentBay.get(sessionId);

        if (!getResult.success) {
          log(`Failed to recover session ${sessionId}: ${getResult.errorMessage}`);
          deleteResults.push({
            sessionId,
            recovered: false,
            deleted: false,
            error: getResult.errorMessage,
          });
          continue;
        }

        const recoveredSession: Session = getResult.session!;
        log(`Successfully recovered session ${sessionId}`);
        log(`Session details - sessionId: ${recoveredSession.sessionId}`);

        // Step 2b: Delete the recovered session
        log(`Deleting recovered session ${sessionId}...`);
        const deleteResult = await agentBay.delete(recoveredSession);

        if (!deleteResult.success) {
          log(`Failed to delete session ${sessionId}: ${deleteResult.errorMessage}`);
          deleteResults.push({
            sessionId,
            recovered: true,
            deleted: false,
            error: deleteResult.errorMessage,
          });
        } else {
          log(`Successfully deleted session ${sessionId}`);
          deletedSessionIds.push(sessionId);
          deleteResults.push({
            sessionId,
            recovered: true,
            deleted: true,
            requestId: deleteResult.requestId,
          });
        }
      }

      // Step 3: Verify results
      log("\n=== Cleanup Results ===");
      log(`Total sessions processed: ${deleteResults.length}`);

      const successfulDeletes = deleteResults.filter(r => r.deleted).length;
      const failedDeletes = deleteResults.filter(r => !r.deleted).length;

      log(`Successfully deleted: ${successfulDeletes}`);
      log(`Failed to delete: ${failedDeletes}`);

      if (failedDeletes > 0) {
        log("\nFailed deletions:");
        deleteResults.filter(r => !r.deleted).forEach(r => {
          log(`  - Session ${r.sessionId}: ${r.error}`);
        });
      }

      // Verify all sessions were deleted
      expect(failedDeletes).toBe(0);

      // List sessions again to confirm they're all gone
      log("\n--- Final Verification: Listing sessions again ---");
      const finalListResult = await agentBay.list();

      if (finalListResult.success) {
        const remainingSessionIds = finalListResult.sessionIds || [];
        log(`Remaining sessions: ${remainingSessionIds.length}`);
        if (remainingSessionIds.length > 0) {
          log(`Remaining session IDs: ${JSON.stringify(remainingSessionIds)}`);
        }

        // Verify deleted sessions are no longer in the list
        log(`\n--- Verifying ${deletedSessionIds.length} deleted sessions are gone ---`);
        let allDeletedSessionsGone = true;
        for (const deletedSessionId of deletedSessionIds) {
          const stillExists = remainingSessionIds.includes(deletedSessionId);
          if (stillExists) {
            log(`❌ Deleted session ${deletedSessionId} still exists in list!`);
            allDeletedSessionsGone = false;
          } else {
            log(`✅ Deleted session ${deletedSessionId} confirmed removed from list`);
          }
        }

        // If all deleted sessions are gone, the test passes
        expect(allDeletedSessionsGone).toBe(true);
      } else {
        log(`Failed to verify final list: ${finalListResult.errorMessage}`);
      }

      log("=== Session Cleanup Test Completed Successfully ===\n");
    } catch (error) {
      log(`Test error: ${error}`);
      throw error;
    }
  });
});
