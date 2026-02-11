/**
 * Integration tests for BetaSkills.listMetadata().
 *
 * Note: This test calls the real backend. Do not run concurrently.
 */

import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Beta skills metadata integration tests", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  test("should list official skills metadata", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const items = await agentBay.betaSkills.listMetadata();
    expect(Array.isArray(items)).toBe(true);
    expect(items.length).toBeGreaterThan(0);

    const first = items[0];
    expect(typeof first.name).toBe("string");
    expect(first.name.trim().length).toBeGreaterThan(0);
    expect(typeof first.description).toBe("string");

    expect((first as any).dir).toBeUndefined();
  }, 30000);
});

