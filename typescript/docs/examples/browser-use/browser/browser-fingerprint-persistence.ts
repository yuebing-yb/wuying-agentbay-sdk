/**
 * Integration test for browser fingerprint persistence functionality.
 * This test verifies that browser fingerprint can be persisted
 * across sessions using the same ContextId and FingerprintContextId.
 */

// @ts-nocheck
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserFingerprint, BrowserContext, BrowserFingerprintContext } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

// Global variables for persistent context and fingerprint context
let persistentContext: any = null;
let persistentFingerprintContext: any = null;

function getTestApiKey(): string {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable not set");
  }
  return apiKey;
}

function isWindowsUserAgent(userAgent: string): boolean {
  if (!userAgent) {
    return false;
  }
  const userAgentLower = userAgent.toLowerCase();
  const windowsIndicators = [
    'windows nt',
    'win32',
    'win64',
    'windows',
    'wow64'
  ];
  return windowsIndicators.some(indicator => userAgentLower.includes(indicator));
}

async function runAsFirstTime(): Promise<void> {
  console.log("====================");
  console.log("Run as first time");
  console.log("====================");

  const apiKey = getTestApiKey();
  const agentBay = new AgentBay({ apiKey });

  // Create a browser context for first time
  const sessionContextName = `test-browser-context-${Date.now()}`;
  const contextResult = await agentBay.context.get(sessionContextName, true);
  if (!contextResult.success || !contextResult.context) {
    console.log("Failed to create browser context");
    return;
  }

  persistentContext = contextResult.context;
  console.log(`Created browser context: ${persistentContext.name} (ID: ${persistentContext.id})`);

  // Create a browser fingerprint context for first time
  const fingerprintContextName = `test-browser-fingerprint-${Date.now()}`;
  const fingerprintContextResult = await agentBay.context.get(fingerprintContextName, true);
  if (!fingerprintContextResult.success || !fingerprintContextResult.context) {
    console.log("Failed to create fingerprint context");
    return;
  }

  persistentFingerprintContext = fingerprintContextResult.context;
  console.log(`Created fingerprint context: ${persistentFingerprintContext.name} (ID: ${persistentFingerprintContext.id})`);

  // Create session with BrowserContext and FingerprintContext
  console.log(`Creating session with browser context ID: ${persistentContext.id} ` +
              `and fingerprint context ID: ${persistentFingerprintContext.id}`);
  
  const fingerprintContext = new BrowserFingerprintContext(persistentFingerprintContext.id);
  const browserContext = new BrowserContext(persistentContext.id, true, undefined, fingerprintContext);

  const params = new CreateSessionParams()
    .withImageId("browser_latest")
    .withBrowserContext(browserContext);

  const sessionResult = await agentBay.create(params);
  if (!sessionResult.success || !sessionResult.session) {
    console.log(`Failed to create first session: ${sessionResult.errorMessage}`);
    return;
  }

  const session = sessionResult.session;
  console.log(`First session created with ID: ${session.sessionId}`);

  // Get browser object and generate fingerprint for persistence
  async function firstSessionOperations(): Promise<void> {
    // Initialize browser with fingerprint persistent enabled and set fingerprint generation options
    const browserOption: BrowserOption = {
      useStealth: true,
      fingerprintPersistent: true,
      fingerprint: {
        devices: ["desktop"],
        operatingSystems: ["windows"],
        locales: ["zh-CN"]
      } as BrowserFingerprint
    };

    const initSuccess = await session.browser.initializeAsync(browserOption);
    if (!initSuccess) {
      console.log("Failed to initialize browser");
      return;
    }
    console.log("First session browser initialized successfully");

    // Get endpoint URL
    const endpointUrl = await session.browser.getEndpointUrl();
    if (!endpointUrl) {
      console.log("Failed to get browser endpoint URL");
      return;
    }
    console.log(`First session browser endpoint URL: ${endpointUrl}`);

    // Connect with playwright, test first session fingerprint
    console.log("Opening https://httpbin.org/user-agent and test user agent...");
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts().length > 0 ? browser.contexts()[0] : await browser.newContext();

    const page = await context.newPage();
    await page.goto("https://httpbin.org/user-agent", { timeout: 60000 });
    const response = await page.evaluate(() => JSON.parse(document.body.textContent));
    const userAgent = response["user-agent"];
    console.log("user_agent =", userAgent);
    
    const isWindows = isWindowsUserAgent(userAgent);
    if (!isWindows) {
      console.log("Failed to get windows user agent");
      return;
    }

    await context.close();
    console.log("First session browser fingerprint check completed");
  }

  // Run first session operations
  await firstSessionOperations();

  // Delete first session with syncContext=true
  console.log("Deleting first session with syncContext=true...");
  const deleteResult = await agentBay.delete(session, { syncContext: true });
  console.log(`First session deleted successfully (RequestID: ${deleteResult.requestId})`);
}

async function runAsSecondTime(): Promise<void> {
  console.log("====================");
  console.log("Run as second time");
  console.log("====================");

  const apiKey = getTestApiKey();
  const agentBay = new AgentBay({ apiKey });

  // Create second session with same browser context and fingerprint context
  console.log(`Creating second session with same browser context ID: ${persistentContext.id} ` +
              `and fingerprint context ID: ${persistentFingerprintContext.id}`);
  
  const fingerprintContext = new BrowserFingerprintContext(persistentFingerprintContext.id);
  const browserContext = new BrowserContext(persistentContext.id, true, undefined, fingerprintContext);

  const params = new CreateSessionParams()
    .withImageId("browser_latest")
    .withBrowserContext(browserContext);

  const sessionResult = await agentBay.create(params);
  if (!sessionResult.success || !sessionResult.session) {
    console.log(`Failed to create second session: ${sessionResult.errorMessage}`);
    return;
  }

  const session = sessionResult.session;
  console.log(`Second session created with ID: ${session.sessionId}`);

  // Get browser object and check if second session fingerprint is the same as first session
  async function secondSessionOperations(): Promise<void> {
    // Initialize browser with fingerprint persistent enabled but not specific fingerprint generation options
    const browserOption: BrowserOption = {
      useStealth: true,
      fingerprintPersistent: true
    };

    const initSuccess = await session.browser.initializeAsync(browserOption);
    if (!initSuccess) {
      console.log("Failed to initialize browser in second session");
      return;
    }
    console.log("Second session browser initialized successfully");

    // Get endpoint URL
    const endpointUrl = await session.browser.getEndpointUrl();
    if (!endpointUrl) {
      console.log("Failed to get browser endpoint URL in second session");
      return;
    }
    console.log(`Second session browser endpoint URL: ${endpointUrl}`);

    // Connect with playwright and test second session fingerprint
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts().length > 0 ? browser.contexts()[0] : await browser.newContext();
    const page = await context.newPage();
    await page.goto("https://httpbin.org/user-agent", { timeout: 60000 });
    const response = await page.evaluate(() => JSON.parse(document.body.textContent));
    const userAgent = response["user-agent"];
    console.log("user_agent =", userAgent);
    
    const isWindows = isWindowsUserAgent(userAgent);
    if (!isWindows) {
      console.log("Failed to get windows user agent in second session");
      return;
    }
    console.log("SUCCESS: fingerprint persisted correctly!");

    await context.close();
    console.log("Second session browser fingerprint check completed");
  }

  // Run second session operations
  await secondSessionOperations();

  // Delete second session with syncContext=true
  console.log("Deleting second session with syncContext=true...");
  const deleteResult = await agentBay.delete(session, { syncContext: true });
  console.log(`Second session deleted successfully (RequestID: ${deleteResult.requestId})`);
}

async function main(): Promise<void> {
  /**
   * Test browser fingerprint persist across sessions with the same browser and fingerprint context.
   */
  try {
    await runAsFirstTime();
    await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds
    await runAsSecondTime();
  } catch (error) {
    console.error("Error in main function:", error);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
