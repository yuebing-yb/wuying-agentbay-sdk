/**
 * Example demonstrating how to receive backend push notifications via Session WS.
 *
 * This example shows how to:
 * - Create a browser session
 * - Connect to the session WS endpoint
 * - Register a push callback for target: wuying_cdp_mcp_server
 * - Trigger a captcha flow on Tongcheng and wait for backend push
 */

import { AgentBay } from "wuying-agentbay-sdk";
import * as playwright from "playwright";

async function main(): Promise<void> {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable not set");
  }

  const imageId = process.env.AGENTBAY_WS_IMAGE_ID || "imgc-0ab5ta4kuo0x3pa70";
  const agentBay = new AgentBay({ apiKey });
  const created = await agentBay.create({ imageId });
  if (!created.success || !created.session) {
    throw new Error(`Failed to create session: ${created.errorMessage}`);
  }
  const session = created.session;

  try {
    const wsClient = await session.getWsClient();
    const pushPromise = new Promise<void>((resolve, reject) => {
      const t = setTimeout(() => reject(new Error("timeout waiting for WS push")), 180000);
      wsClient.registerCallback("wuying_cdp_mcp_server", (payload) => {
        clearTimeout(t);
        process.stdout.write(`WS PUSH: ${JSON.stringify(payload)}\n`);
        resolve();
      });
    });

    const ok = await session.browser.initializeAsync({ useStealth: true, solveCaptchas: true });
    if (!ok) {
      throw new Error("Failed to initialize browser");
    }
    const endpointUrl = await session.browser.getEndpointUrl();

    const browser = await playwright.chromium.connectOverCDP(endpointUrl);
    try {
      const context = browser.contexts()[0];
      const page = await context.newPage();
      await page.goto("https://passport.ly.com/Passport/GetPassword", { waitUntil: "domcontentloaded" });
      const input = await page.waitForSelector("#name_in", { timeout: 10000 });
      await input.click();
      await input.fill("");
      await input.type("13000000000");
      await page.waitForTimeout(1000);
      await page.click("#next_step1");

      process.stdout.write("Waiting for backend push...\n");
      await pushPromise;
      process.stdout.write("Received backend push.\n");
    } finally {
      await browser.close();
    }
  } finally {
    await agentBay.delete(session);
  }
}

if (require.main === module) {
  main().catch((e) => {
    process.stderr.write(String(e) + "\n");
    process.exitCode = 1;
  });
}

