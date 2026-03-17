/**
 * Example: browser-login-takeover.ts
 * This example demonstrates the call-for-user (login takeover) flow
 * on JD.com using browser notification callback from sandbox browser.
 *
 * 1. Create a new browser session with AgentBay SDK
 * 2. Use playwright to connect to AIBrowser instance through CDP protocol
 * 3. Set auto_login, solve_captchas and call_for_user, then run the JD search flow
 * 4. Handle call-for-user (pause/resume/takeover) during login/captcha
 */

import { AgentBay, BrowserOption, BrowserNotifyMessage, BrowserProxy } from 'wuying-agentbay-sdk';
import { chromium, type Page } from 'playwright';
import { exec } from 'child_process';
import * as os from 'os';

let shouldTakeover = false;
let takeoverNotifyId: number | null = null;
let maxLoginDetectTimeout = 5.0;
let maxLoginTakeoverTimeout = 180.0;

// Simple Event implementation using Promise
class EventEmitter {
  private isSet = false;
  private waiters: Array<() => void> = [];

  set(): void {
    this.isSet = true;
    this.waiters.forEach(resolve => resolve());
    this.waiters = [];
  }

  wait(timeoutMs?: number): Promise<boolean> {
    if (this.isSet) {
      return Promise.resolve(true);
    }

    return new Promise<boolean>((resolve) => {
      const waiter = () => resolve(true);
      this.waiters.push(waiter);

      if (timeoutMs !== undefined) {
        setTimeout(() => {
          const index = this.waiters.indexOf(waiter);
          if (index > -1) {
            this.waiters.splice(index, 1);
            resolve(false);
          }
        }, timeoutMs);
      }
    });
  }
}

const takeoverEvent = new EventEmitter();

function onBrowserCallback(msg: BrowserNotifyMessage): void {
  console.log(`on_browser_callback: ${msg.type}, ${msg.id}, ${msg.code}, ${msg.message}, ${msg.action}, ${JSON.stringify(msg.extraParams)}`);
  try {
    if (msg.type === "call-for-user") {
      const action = msg.action;
      const code = msg.code;
      const extraParams = msg.extraParams || {};

      if (action === "takeover" && code === 102) {
        shouldTakeover = true;
        takeoverNotifyId = msg.id ?? null;
        maxLoginTakeoverTimeout = extraParams.max_wait_time || 180;
        console.log(`Call-for-user takeover received, notify_id: ${takeoverNotifyId}, max wait time: ${maxLoginTakeoverTimeout}s`);
        takeoverEvent.set();
      }
    }
  } catch (error) {
    console.error(`Error handling browser callback: ${error}`);
  }
}

async function waitAndDoTakeoverIfNeeded(
  session: { browser: { sendTakeoverDone: (id: number) => Promise<boolean> } },
  takeoverUrl: string
): Promise<void> {
  const detected = await takeoverEvent.wait(maxLoginDetectTimeout * 1000);
  if (!detected) {
    console.log("ℹ️ No takeover event within timeout, proceeding...");
    return;
  }
  if (shouldTakeover) {
    console.log("⏰ Login should takeover...");
    const platformName = os.platform();
    let command: string;
    if (platformName === 'win32') {
      command = `start "" "${takeoverUrl}"`;
    } else if (platformName === 'darwin') {
      command = `open "${takeoverUrl}"`;
    } else {
      command = `xdg-open "${takeoverUrl}"`;
    }
    exec(command);
    console.log(`Waiting for user takeover completed or timeout, timeout: ${maxLoginTakeoverTimeout}s`);
    await new Promise(resolve => setTimeout(resolve, maxLoginTakeoverTimeout * 1000));
    if (takeoverNotifyId !== null) {
      await session.browser.sendTakeoverDone(takeoverNotifyId);
    }
    console.log("✅ User takeover completed...");
  } else {
    console.log("ℹ️ No takeover event within timeout, proceeding...");
  }
}

async function runJdHomepageFlow(page: Page): Promise<void> {
  console.log("🔍 Checking for login popup...");
  try {
    const closeButton = page.locator("#login2025-dialog-close");
    await closeButton.waitFor({ state: "visible", timeout: 2000 });
    await closeButton.click({ timeout: 3000 });
    console.log("✅ Login popup closed");
    await new Promise(resolve => setTimeout(resolve, 500));
  } catch {
    // Popup not present, continue
  }

  console.log("🔍 Entering search keyword...");
  const searchInput = page.locator("input#key");
  await searchInput.fill("iphone 17价格京东自营");
  await page.locator('button[aria-label="搜索"]').click();

  console.log("⏳ Waiting for search results to load...");
  try {
    await page.waitForLoadState("networkidle", { timeout: 15000 });
    console.log("✅ Search results loaded");
  } catch {
    // ignore
  }
  await new Promise(resolve => setTimeout(resolve, 2000));
}

async function runPostLoginFlow(page: Page): Promise<void> {
  console.log("📜 Scrolling down 500px so products are visible...");
  await page.evaluate("() => window.scrollBy(0, 500)");
  await new Promise(resolve => setTimeout(resolve, 1000));

  try {
    const firstCard = page.locator("div.plugin_goodsCardWrapper").first;
    await firstCard.waitFor({ state: "visible", timeout: 8000 });
    await firstCard.scrollIntoViewIfNeeded();
    await firstCard.locator("button._addCart_d0rf6_71").click({ timeout: 5000, force: true });
    console.log("✅ Clicked add to cart");
    await new Promise(resolve => setTimeout(resolve, 3000));
    const cartLink = page.locator("li#Cart a.Cart").first;
    await cartLink.scrollIntoViewIfNeeded();
    await cartLink.click({ timeout: 5000, force: true });
    console.log("✅ Clicked cart");
    await new Promise(resolve => setTimeout(resolve, 2000));
  } catch (error) {
    console.log(`⚠️ Add to cart or open cart failed: ${error}`);
  }
}

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable is required");
  }

  const agentBay = new AgentBay({ apiKey });
  const sessionResult = await agentBay.create({ imageId: "browser_latest" });

  if (!sessionResult.success || !sessionResult.session) {
    throw new Error("Failed to create session");
  }

  const session = sessionResult.session;
  const sessionInfo = await session.info();
  const takeoverUrl = sessionInfo.data.resourceUrl;

  await session.browser.registerCallback(onBrowserCallback);

  try {
    const wuyingProxy: BrowserProxy = {
      type: 'wuying',
      strategy: 'restricted',
      toMap(): Record<string, any> {
        return { type: this.type, strategy: this.strategy };
      },
    };

    const browserOption: BrowserOption = {
      useStealth: true,
      autoLogin: false,
      callForUser: true,
      proxies: [wuyingProxy],
    };

    const initialized = await session.browser.initializeAsync(browserOption);
    if (!initialized) {
      throw new Error("Failed to initialize browser");
    }

    const endpointUrl = await session.browser.getEndpointUrl();
    console.log(`🌐 Browser endpoint URL: ${endpointUrl}`);

    await new Promise(resolve => setTimeout(resolve, 2000));

    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts()[0] ?? await browser.newContext();
    const page = await context.newPage();

    console.log("🌐 Navigating to JD homepage...");
    await page.goto("https://www.jd.com/");
    await new Promise(resolve => setTimeout(resolve, 2000));

    const currentUrl = page.url();

    if (currentUrl.includes("passport.jd.com")) {
      console.log("🔐 Detected passport.jd.com login page, waiting for takeover...");
      await new Promise(resolve => setTimeout(resolve, 5000));
      await waitAndDoTakeoverIfNeeded(session, takeoverUrl);
      await runJdHomepageFlow(page);
    } else {
      await new Promise(resolve => setTimeout(resolve, 10000));
      await runJdHomepageFlow(page);
      console.log("⏳ Waiting for takeover event (user may log in manually)...");
      await waitAndDoTakeoverIfNeeded(session, takeoverUrl);
    }

    await runPostLoginFlow(page);

    console.log("✅ Test completed");
    await new Promise(resolve => setTimeout(resolve, 10000));

    await session.browser.unregisterCallback();
  } catch (error) {
    console.error(`❌ error: ${error}`);
  } finally {
    console.log("🗑️ Deleting session");
    await agentBay.delete(session);
  }
}

if (typeof require !== 'undefined' && require.main === module) {
  main().catch(console.error);
}
