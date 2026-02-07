const path = require("path");

const { chromium } = require("playwright");

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    process.stdout.write("AGENTBAY_API_KEY is not set; skipping.\n");
    return;
  }

  const sdkPath = path.join(__dirname, "..", "..", "dist", "index.cjs");
  // eslint-disable-next-line import/no-dynamic-require, global-require
  const { AgentBay } = require(sdkPath);

  const imageId = process.env.AGENTBAY_WS_IMAGE_ID || "imgc-0ab5ta4kuo0x3pa70";
  const agentBay = new AgentBay({ apiKey });
  const created = await agentBay.create({ imageId });
  if (!created.success || !created.session) {
    throw new Error(`Failed to create session: ${created.errorMessage}`);
  }
  const session = created.session;

  const wsClient = await session.getWsClient();
  let timeoutId = null;
  const pushPromise = new Promise((resolve, reject) => {
    timeoutId = setTimeout(() => reject(new Error("timeout waiting for WS push")), 180000);
    wsClient.registerCallback("wuying_cdp_mcp_server", (payload) => {
      if (timeoutId) clearTimeout(timeoutId);
      process.stdout.write(`WS PUSH: ${JSON.stringify(payload)}\n`);
      resolve(payload);
    });
  });

  try {
    const ok = await session.browser.initializeAsync({ useStealth: true, solveCaptchas: true });
    if (!ok) {
      throw new Error("Failed to initialize browser");
    }
    const endpointUrl = await session.browser.getEndpointUrl();

    const browser = await chromium.connectOverCDP(endpointUrl);
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

      const payload = await pushPromise;
      if (!payload || payload.target !== "wuying_cdp_mcp_server") {
        throw new Error(`unexpected payload: ${JSON.stringify(payload)}`);
      }
      if (!payload.data || ![201, 202].includes(payload.data.code)) {
        throw new Error(`unexpected payload.data: ${JSON.stringify(payload.data)}`);
      }
      process.stdout.write("E2E OK\n");
    } finally {
      await browser.close();
    }
  } finally {
    try {
      await wsClient.close();
    } catch (_e) {
      // ignore
    }
    try {
      await session.delete();
    } catch (_e) {
      // ignore
    }
  }
}

main().catch((e) => {
  process.stderr.write(String(e && e.stack ? e.stack : e) + "\n");
  process.exitCode = 1;
});

