/**
 * Integration tests for Computer beta screenshot APIs.
 *
 * Note: This test creates a real session. Do not run concurrently.
 */

import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Computer beta screenshot integration tests", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  test("should capture screenshot as JPEG bytes", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const sessionResult = await agentBay.create({ imageId: "linux_latest" });
    expect(sessionResult.session).toBeDefined();
    const session = sessionResult.session!;

    try {
      await new Promise((resolve) => setTimeout(resolve, 10000));
      const s = await session.computer.betaTakeScreenshot("jpg");
      expect(s.success).toBe(true);
      expect(s.format).toBe("jpeg");
      expect(s.data.length).toBeGreaterThan(3);
      expect(Buffer.from(s.data).slice(0, 3).equals(Buffer.from([0xff, 0xd8, 0xff]))).toBe(true);
      expect(typeof s.width).toBe("number");
      expect(typeof s.height).toBe("number");
      expect((s.width as number) > 0).toBe(true);
      expect((s.height as number) > 0).toBe(true);
    } finally {
      await session.delete();
    }
  }, 60000);
});

