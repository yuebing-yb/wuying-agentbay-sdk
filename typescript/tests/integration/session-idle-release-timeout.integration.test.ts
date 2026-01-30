import { AgentBay } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

describe("Session idle release timeout (integration)", () => {
  it("should release session between timeout and timeout+60s", async () => {
    const apiKey = getTestApiKey();
    const agentBay = new AgentBay({ apiKey });

    const idleReleaseTimeoutSeconds = 60;
    const maxOverSeconds = 60;
    const pollIntervalMs = 2000;
    const imageId = "computer-use-ubuntu-2204-regionGW";

    const createStart = Date.now();
    const createResult = await agentBay.create({
      imageId,
      idleReleaseTimeout: idleReleaseTimeoutSeconds,
      labels: {
        test: "idle-release-timeout",
        sdk: "typescript",
      },
    });

    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    const session = createResult.session!;

    try {
      const start = Date.now();
      const timeoutDeadline = start + idleReleaseTimeoutSeconds * 1000;

      while (Date.now() < timeoutDeadline) {
        const status = await session.getStatus();
        if (!status.success && status.code === "InvalidMcpSession.NotFound") {
          throw new Error(`Session released too early: NotFound before ${idleReleaseTimeoutSeconds}s`);
        }
        if (status.success && ["FINISH", "DELETING", "DELETED"].includes(status.status)) {
          throw new Error(`Session released too early: status=${status.status} before ${idleReleaseTimeoutSeconds}s`);
        }
        const remaining = timeoutDeadline - Date.now();
        await sleep(Math.min(pollIntervalMs, Math.max(0, remaining)));
      }

      const deadline = timeoutDeadline + maxOverSeconds * 1000;
      while (Date.now() < deadline) {
        const status = await session.getStatus();

        if (!status.success && status.code === "InvalidMcpSession.NotFound") {
          const elapsed = (Date.now() - start) / 1000;
          expect(elapsed).toBeGreaterThanOrEqual(idleReleaseTimeoutSeconds);
          expect(elapsed).toBeLessThanOrEqual(idleReleaseTimeoutSeconds + maxOverSeconds);
          log(`✅ Session released: NotFound, elapsed=${elapsed.toFixed(2)}s`);
          return;
        }

        if (status.success && ["FINISH", "DELETING", "DELETED"].includes(status.status)) {
          const elapsed = (Date.now() - start) / 1000;
          expect(elapsed).toBeGreaterThanOrEqual(idleReleaseTimeoutSeconds);
          expect(elapsed).toBeLessThanOrEqual(idleReleaseTimeoutSeconds + maxOverSeconds);
          log(`✅ Session released: status=${status.status}, elapsed=${elapsed.toFixed(2)}s`);
          return;
        }

        await sleep(pollIntervalMs);
      }

      throw new Error(
        `Session was not released within ${idleReleaseTimeoutSeconds}s~${idleReleaseTimeoutSeconds + maxOverSeconds}s`
      );
    } finally {
      // Best-effort cleanup (session may already be released)
      try {
        const status = await session.getStatus();
        if (status.success && !["FINISH", "DELETING", "DELETED"].includes(status.status)) {
          await session.delete();
        }
      } catch (e) {
        // ignore
      }
      log(`Create request started at: ${new Date(createStart).toISOString()}`);
    }
  }, 2 * 60 * 1000);
});

