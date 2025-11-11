/**
 * Example demonstrating Browser Fingerprint construct feature with AgentBay SDK.
 *
 * This example shows how to construct browser fingerprint from file and sync it to remote browser.
 * FingerprintFormat can be loaded from file and then used to sync to remote browser fingerprint
 * by using BrowserOption.fingerprintFormat.
 *
 * This example will:
 * 1. Load fingerprint format from file
 * 2. Sync fingerprint format to remote browser fingerprint
 * 3. Verify remote browser fingerprint
 * 4. Clean up session
 */

// @ts-nocheck
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, FingerprintFormat } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

async function generateFingerprintByFile(): Promise<FingerprintFormat> {
  /**
   * Generate fingerprint by file.
   */
  const fingerprintPath = path.join(__dirname, "../../../../../resource/fingerprint.example.json");
  const fingerprintData = fs.readFileSync(fingerprintPath, 'utf8');
  return FingerprintFormat.load(fingerprintData);
}

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

    // You can generate fingerprint by file or construct FingerprintFormat by yourself totally.
    const fingerprintFormat = await generateFingerprintByFile();

    // Create browser option with fingerprint format.
    // Fingerprint format is loaded from file by generateFingerprintByFile()
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
    
    // Verify that the user agent matches the fingerprint format
    if (fingerprintFormat.fingerprint?.navigator?.userAgent) {
      if (userAgent === fingerprintFormat.fingerprint.navigator.userAgent) {
        console.log("User Agent constructed correctly");
      } else {
        console.log("User Agent mismatch");
      }
    }

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
