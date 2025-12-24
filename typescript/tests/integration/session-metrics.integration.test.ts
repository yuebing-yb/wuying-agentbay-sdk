/**
 * Integration test for Session.getMetrics()
 */

import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Session.getMetrics Integration Test", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeAll(() => {
    if (!apiKey) {
      throw new Error("AGENTBAY_API_KEY environment variable is not set");
    }
    agentBay = new AgentBay({ apiKey });
  });

  it("should retrieve structured metrics via MCP get_metrics", async () => {
    const createResult = await agentBay.create({ imageId: "linux_latest" });
    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    const session = createResult.session!;

    try {
      const result = await session.getMetrics();
      expect(result.requestId).toBeTruthy();
      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();

      const m = result.data!;
      expect(m.cpuCount).toBeGreaterThanOrEqual(1);
      expect(m.memTotal).toBeGreaterThan(0);
      expect(m.diskTotal).toBeGreaterThan(0);
      expect(m.cpuUsedPct).toBeGreaterThanOrEqual(0);
      expect(m.cpuUsedPct).toBeLessThanOrEqual(100);
      expect(m.timestamp).toBeTruthy();
      log(`metrics: ${JSON.stringify(m)}`);
    } finally {
      await session.delete();
    }
  });
});


