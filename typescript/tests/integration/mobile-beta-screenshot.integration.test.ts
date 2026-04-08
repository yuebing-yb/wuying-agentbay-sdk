// ci-stable
/**
 * Integration tests for Mobile beta screenshot APIs.
 *
 * Note: This test creates a real session. Do not run concurrently.
 */

import { AgentBay } from "../../src/agent-bay";
import { log } from "../../src/utils/logger";

describe("Mobile beta screenshot integration tests", () => {
  const apiKey = process.env.AGENTBAY_API_KEY;
  let agentBay: AgentBay;

  beforeEach(() => {
    if (apiKey) {
      agentBay = new AgentBay({ apiKey });
    }
  });

  test("should capture screenshot as PNG bytes", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const sessionResult = await agentBay.create({
      imageId: "mobile-use-android-12-gw",
    });
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(
        `Failed to create session: ${sessionResult.errorMessage || ""}`
      );
    }
    const session = sessionResult.session!;

    try {
      await new Promise((resolve) => setTimeout(resolve, 15000));

      const cmds = ["wm size 720x1280", "wm density 160"];
      for (const c of cmds) {
        const r = await session.command.executeCommand(c, 10000);
        if (!r.success) {
          throw new Error(
            `command failed: ${c}, error=${r.errorMessage}, output=${r.output}`
          );
        }
      }

      const start = await session.mobile.startApp(
        "monkey -p com.android.settings 1"
      );
      expect(start.success).toBe(true);
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const s = await session.mobile.betaTakeScreenshot();
      if (!s.success) {
        throw new Error(
          `betaTakeScreenshot failed: requestId=${s.requestId || ""}, error=${
            s.errorMessage || ""
          }`
        );
      }
      expect(s.requestId).toBeDefined();
      expect(s.type).toBe("image");
      expect(s.mimeType).toBe("image/png");
      expect(s.data.length).toBeGreaterThan(8);
      expect(
        Buffer.from(s.data)
          .slice(0, 8)
          .equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
      ).toBe(true);
      expect(typeof s.width).toBe("number");
      expect(typeof s.height).toBe("number");
      expect((s.width as number) > 0).toBe(true);
      expect((s.height as number) > 0).toBe(true);
    } finally {
      await session.delete();
    }
  }, 60000);

  test("should capture screenshot as JPEG bytes", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const sessionResult = await agentBay.create({
      imageId: "mobile-use-android-12-gw",
    });
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(
        `Failed to create session: ${sessionResult.errorMessage || ""}`
      );
    }
    const session = sessionResult.session!;

    try {
      await new Promise((resolve) => setTimeout(resolve, 15000));

      const cmds = ["wm size 720x1280", "wm density 160"];
      for (const c of cmds) {
        const r = await session.command.executeCommand(c, 10000);
        if (!r.success) {
          throw new Error(
            `command failed: ${c}, error=${r.errorMessage}, output=${r.output}`
          );
        }
      }

      const start = await session.mobile.startApp(
        "monkey -p com.android.settings 1"
      );
      expect(start.success).toBe(true);
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const s = await (session.mobile as any).betaTakeScreenshot("jpeg");
      if (!s.success) {
        throw new Error(
          `betaTakeScreenshot failed: requestId=${s.requestId || ""}, error=${
            s.errorMessage || ""
          }`
        );
      }
      expect(s.requestId).toBeDefined();
      expect(s.type).toBe("image");
      expect(s.mimeType).toBe("image/jpeg");
      expect(s.data.length).toBeGreaterThan(3);
      expect(
        Buffer.from(s.data)
          .slice(0, 3)
          .equals(Buffer.from([0xff, 0xd8, 0xff]))
      ).toBe(true);
      expect(typeof s.width).toBe("number");
      expect(typeof s.height).toBe("number");
      expect((s.width as number) > 0).toBe(true);
      expect((s.height as number) > 0).toBe(true);
    } finally {
      await session.delete();
    }
  }, 60000);

  test("should capture long screenshot as PNG bytes", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const sessionResult = await agentBay.create({
      imageId: "mobile-use-android-12-gw",
    });
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(
        `Failed to create session: ${sessionResult.errorMessage || ""}`
      );
    }
    const session = sessionResult.session!;

    try {
      await new Promise((resolve) => setTimeout(resolve, 15000));

      const cmds = ["wm size 720x1280", "wm density 160"];
      for (const c of cmds) {
        const r = await session.command.executeCommand(c, 10000);
        if (!r.success) {
          throw new Error(
            `command failed: ${c}, error=${r.errorMessage}, output=${r.output}`
          );
        }
      }

      const start = await session.mobile.startApp(
        "monkey -p com.android.settings 1"
      );
      expect(start.success).toBe(true);
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const nav = await session.command.executeCommand(
        "am start -a android.settings.SETTINGS",
        10000
      );
      if (!nav.success) {
        throw new Error(
          `command failed: am start -a android.settings.SETTINGS, error=${nav.errorMessage}, output=${nav.output}`
        );
      }
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const ls = await session.mobile.betaTakeLongScreenshot(2, "png");
      if (!ls.success) {
        throw new Error(
          `betaTakeLongScreenshot failed: requestId=${
            ls.requestId || ""
          }, error=${ls.errorMessage || ""}`
        );
      }
      expect(ls.requestId).toBeDefined();
      expect(ls.type).toBe("image");
      expect(ls.mimeType).toBe("image/png");
      expect(ls.data.length).toBeGreaterThan(8);
      expect(
        Buffer.from(ls.data)
          .slice(0, 8)
          .equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]))
      ).toBe(true);
      expect(typeof ls.width).toBe("number");
      expect(typeof ls.height).toBe("number");
      expect((ls.width as number) > 0).toBe(true);
      expect((ls.height as number) > 0).toBe(true);
    } finally {
      await session.delete();
    }
  }, 60000);

  test("should capture long screenshot as JPEG bytes with quality", async () => {
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const sessionResult = await agentBay.create({
      imageId: "mobile-use-android-12-gw",
    });
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(
        `Failed to create session: ${sessionResult.errorMessage || ""}`
      );
    }
    const session = sessionResult.session!;

    try {
      await new Promise((resolve) => setTimeout(resolve, 15000));

      const cmds = ["wm size 720x1280", "wm density 160"];
      for (const c of cmds) {
        const r = await session.command.executeCommand(c, 10000);
        if (!r.success) {
          throw new Error(
            `command failed: ${c}, error=${r.errorMessage}, output=${r.output}`
          );
        }
      }

      const start = await session.mobile.startApp(
        "monkey -p com.android.settings 1"
      );
      expect(start.success).toBe(true);
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const nav = await session.command.executeCommand(
        "am start -a android.settings.SETTINGS",
        10000
      );
      if (!nav.success) {
        throw new Error(
          `command failed: am start -a android.settings.SETTINGS, error=${nav.errorMessage}, output=${nav.output}`
        );
      }
      await new Promise((resolve) => setTimeout(resolve, 2000));

      const invalid = await session.mobile.betaTakeLongScreenshot(2, "jpeg", 0);
      expect(invalid.success).toBe(false);
      expect(invalid.errorMessage).toContain("Invalid quality");

      const high = await session.mobile.betaTakeLongScreenshot(2, "jpeg", 95);
      const low = await session.mobile.betaTakeLongScreenshot(2, "jpeg", 10);

      if (!high.success) {
        throw new Error(
          `betaTakeLongScreenshot (jpeg, q=95) failed: requestId=${
            high.requestId || ""
          }, error=${high.errorMessage || ""}`
        );
      }
      if (!low.success) {
        throw new Error(
          `betaTakeLongScreenshot (jpeg, q=10) failed: requestId=${
            low.requestId || ""
          }, error=${low.errorMessage || ""}`
        );
      }

      expect(high.requestId).toBeDefined();
      expect(high.type).toBe("image");
      expect(high.mimeType).toBe("image/jpeg");
      expect(high.data.length).toBeGreaterThan(3);
      expect(
        Buffer.from(high.data)
          .slice(0, 3)
          .equals(Buffer.from([0xff, 0xd8, 0xff]))
      ).toBe(true);
      expect(typeof high.width).toBe("number");
      expect(typeof high.height).toBe("number");
      expect((high.width as number) > 0).toBe(true);
      expect((high.height as number) > 0).toBe(true);

      expect(low.requestId).toBeDefined();
      expect(low.type).toBe("image");
      expect(low.mimeType).toBe("image/jpeg");
      expect(low.data.length).toBeGreaterThan(3);
      expect(
        Buffer.from(low.data)
          .slice(0, 3)
          .equals(Buffer.from([0xff, 0xd8, 0xff]))
      ).toBe(true);
      expect(typeof low.width).toBe("number");
      expect(typeof low.height).toBe("number");
      expect((low.width as number) > 0).toBe(true);
      expect((low.height as number) > 0).toBe(true);

      expect(high.data.length).toBeGreaterThan(low.data.length);
    } finally {
      await session.delete();
    }
  }, 90000);
});
