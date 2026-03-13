import { AgentBay } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function isReleased(status: any): boolean {
  if (!status) {
    return false;
  }
  if (
    status.success === false &&
    status.code === "InvalidMcpSession.NotFound"
  ) {
    return true;
  }
  if (
    status.success === true &&
    ["FINISH", "DELETING", "DELETED"].includes(status.status)
  ) {
    log(`✅ Session released: ${status.status}`);
    return true;
  }
  return false;
}

describe("Session keepAlive (integration)", () => {
  it(
    "should keep refreshed session alive longer than control session",
    async () => {
      const apiKey = getTestApiKey();
      const agentBay = new AgentBay({ apiKey });

      const idleReleaseTimeoutSeconds = 30;
      const maxOverSeconds = 60;
      const pollIntervalMs = 2000;
      const imageId = "linux_latest";

      const start = Date.now();

      const commonLabels = {
        test: "session-keep-alive",
        sdk: "typescript",
      };

      const controlCreate = await agentBay.create({
        imageId,
        idleReleaseTimeout: idleReleaseTimeoutSeconds,
        labels: { ...commonLabels, role: "control" },
      });
      expect(controlCreate.success).toBe(true);
      expect(controlCreate.session).toBeDefined();
      const control = controlCreate.session!;

      const refreshedCreate = await agentBay.create({
        imageId,
        idleReleaseTimeout: idleReleaseTimeoutSeconds,
        labels: { ...commonLabels, role: "refreshed" },
      });
      expect(refreshedCreate.success).toBe(true);
      expect(refreshedCreate.session).toBeDefined();
      const refreshed = refreshedCreate.session!;

      try {
        await sleep((idleReleaseTimeoutSeconds * 1000) / 2);
        const keepAliveResult = await refreshed.keepAlive();
        expect(keepAliveResult.success).toBe(true);

        const deadline =
          start + (idleReleaseTimeoutSeconds + maxOverSeconds) * 1000;
        while (Date.now() < deadline) {
          const controlStatus = await control.getStatus();
          const refreshedStatus = await refreshed.getStatus();

          if (isReleased(controlStatus)) {
            expect(isReleased(refreshedStatus)).toBe(false);
            const elapsed = (Date.now() - start) / 1000;
            log(
              `✅ Control released while refreshed alive, elapsed=${elapsed.toFixed(
                2
              )}s`
            );
            return;
          }

          // Check if refreshed session was released before control session (unexpected)
          if (isReleased(refreshedStatus)) {
            throw new Error(
              "Refreshed session was released before control session; keep-alive may have failed"
            );
          }

          await sleep(pollIntervalMs);
        }
      } finally {
        // Best-effort cleanup: delete both if still alive
        for (const s of [refreshed, control]) {
          try {
            const status = await s.getStatus();
            if (!isReleased(status)) {
              await s.delete();
            }
          } catch (e) {
            // ignore
          }
        }
      }
    },
    2 * 60 * 1000
  );
});
