/**
 * Example demonstrating Browser Fingerprint local sync feature with AgentBay SDK.
 *
 * This example shows how to sync local browser fingerprint to remote browser fingerprint.
 * BrowserFingerprintGenerator has ability to dump local installed chrome browser fingerprint,
 * and then you can sync it to remote browser fingerprint by using BrowserOption.fingerprintFormat.
 *
 * This example will:
 * 1. Generate local chrome browser fingerprint by BrowserFingerprintGenerator
 * 2. Sync local browser fingerprint to remote browser fingerprint
 * 3. Verify remote browser fingerprint
 * 4. Clean up session
 */

// @ts-nocheck
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserFingerprintGenerator } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

async function main(): Promise<void> {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.log("Error: AGENTBAY_API_KEY environment variable not set");
    return;
  }

  try {
    // Initialize AgentBay client
    console.log("Initializing AgentBay client...");
    const agentBay = new AgentBay({ apiKey });

    // Create a session
    console.log("Creating a new session...");
    const params: CreateSessionParams = {
      imageId: "browser_latest",
    };
    const sessionResult = await agentBay.create(params);

    if (!sessionResult.success) {
      console.log("Failed to create session");
      return;
    }

    const session = sessionResult.session;
    console.log(`Session created with ID: ${session.sessionId}`);

    // Generate fingerprint from local chrome browser
    const fingerprintGenerator = new BrowserFingerprintGenerator();
    const fingerprintFormat = await fingerprintGenerator.generateFingerprint();
    console.log(`Fingerprint format: ${JSON.stringify(fingerprintFormat)}`);

    // Create browser option with fingerprint format.
    // Fingerprint format is dumped from local chrome browser by BrowserFingerprintGenerator
    // automatically, you can use it to sync to remote browser fingerprint.
    const browserOption: BrowserOption = {
      useStealth: true,
      fingerprintFormat: fingerprintFormat
    };

    const initialized = await session.browser.initializeAsync(browserOption);
    if (!initialized) {
      console.log("Failed to initialize browser");
      return;
    }

    const endpointUrl = await session.browser.getEndpointUrl();
    console.log("endpoint_url =", endpointUrl);

    // Connect to browser using Playwright
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts()[0];
    const page = await context.newPage();

    // Check user agent
    console.log("\n--- Check User Agent ---");
    await page.goto("https://httpbin.org/user-agent");

    const response = await page.evaluate(() => JSON.parse(document.body.textContent));
    const userAgent = response["user-agent"] || "";
    console.log(`User Agent: ${userAgent}`);

    console.log("Please check if User Agent is synced correctly by visiting https://httpbin.org/user-agent in local chrome browser.");

    await page.waitForTimeout(3000);
    await browser.close();

    // Clean up session
    await agentBay.delete(session);
    console.log("Session cleaned up successfully");

  } catch (error) {
    console.error("Error in main function:", error);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
