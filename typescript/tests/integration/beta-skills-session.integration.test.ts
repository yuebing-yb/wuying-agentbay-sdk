// ci-stable
/**
 * Integration tests for session creation with skills loading.
 *
 * Note: This test calls the real backend. Do not run concurrently.
 */

import { AgentBay } from "../../src/agent-bay";
import { CreateSessionParams } from "../../src/session-params";
import { log } from "../../src/utils/logger";

describe("Beta skills session integration tests", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  test("should create session with loadSkills succeeds", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const params = new CreateSessionParams({
      loadSkills: true,
    });
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();

    const session = result.session!;
    try {
      expect(session.sessionId).toBeDefined();
    } finally {
      await agentBay.delete(session);
    }
  }, 120000);

  test("should create session without skills", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const params = new CreateSessionParams({});
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();

    const session = result.session!;
    try {
      expect(session.sessionId).toBeDefined();
    } finally {
      await agentBay.delete(session);
    }
  }, 120000);
});
