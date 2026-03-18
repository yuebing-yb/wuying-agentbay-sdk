/**
 * Integration tests for BetaSkills.getMetadata() via GetSkillMetaData POP action.
 *
 * Note: This test calls the real backend. Do not run concurrently.
 */

import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Beta skills getMetadata integration tests", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  test("should return skillsRootPath and skills list", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const result = await agentBay.betaSkills.getMetadata();

    expect(result).toBeDefined();
    expect(typeof result.skillsRootPath).toBe("string");
    expect(result.skillsRootPath.length).toBeGreaterThan(0);
    expect(Array.isArray(result.skills)).toBe(true);
  }, 30000);

  test("should filter by group IDs", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const result = await agentBay.betaSkills.getMetadata({
      skillNames: ["5kvAvffm"],
    });

    expect(result).toBeDefined();
    expect(Array.isArray(result.skills)).toBe(true);
    expect(typeof result.skillsRootPath).toBe("string");
  }, 30000);

  test("should accept imageId parameter", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const result = await agentBay.betaSkills.getMetadata({
      imageId: "linux_latest",
    });

    expect(result).toBeDefined();
    expect(typeof result.skillsRootPath).toBe("string");
    expect(result.skillsRootPath.length).toBeGreaterThan(0);
  }, 30000);
});
