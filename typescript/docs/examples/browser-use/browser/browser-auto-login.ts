/**
 * Example: browser-auto-login.ts
 * This example demonstrates auto login and ly.com hotel booking flow
 * using browser notification callback from sandbox browser.
 *
 * 1. Create a new browser session with AgentBay SDK
 * 2. Use playwright to connect to AIBrowser instance through CDP protocol
 * 3. Set auto_login and solve_captchas, then run the ly.com hotel booking flow
 * 4. Handle call-for-user (pause/resume/takeover) during the flow.
 */

import { AgentBay, BrowserOption, BrowserNotifyMessage, BrowserProxy } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';
import { exec } from 'child_process';
import * as os from 'os';

let shouldTakeover = false;
let takeoverNotifyId: number | null = null;
let maxAutologinDetectTimeout = 5.0;
let maxAutologinSolvingTimeout = 60.0;
let maxTakeoverTimeout = 180.0;

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

const autologinPauseEvent = new EventEmitter();
const autologinResumeOrTakeoverEvent = new EventEmitter();

async function waitForAutologinSolving(
  autologinPauseEvent: EventEmitter,
  autologinResumeOrTakeoverEvent: EventEmitter,
  autologinDetectTimeout: number = 2.0
): Promise<boolean> {
  console.log(`Waiting for autologin pause event, timeout: ${autologinDetectTimeout}s`);
  const pauseDetected = await autologinPauseEvent.wait(autologinDetectTimeout * 1000);

  if (!pauseDetected) {
    console.log("No autologin pause event detected within timeout, proceeding next step");
    return true;
  }

  console.log(`Waiting for autologin resume event, timeout: ${maxAutologinSolvingTimeout}s`);
  const resumeDetected = await autologinResumeOrTakeoverEvent.wait(maxAutologinSolvingTimeout * 1000);

  if (!resumeDetected) {
    console.log("No autologin resume event detected within timeout, should takeover");
    return false;
  }

  if (shouldTakeover) {
    console.log("Autologin failed, takeover event detected");
    return false;
  } else {
    return true;
  }
}

function onBrowserCallback(msg: BrowserNotifyMessage): void {
  console.log(`🔔 Received browser callback: ${msg.type}, ${msg.id}, ${msg.code}, ${msg.message}, ${msg.action}, ${JSON.stringify(msg.extraParams)}`);
  try {
    if (msg.type === "call-for-user") {
      const action = msg.action;
      const code = msg.code;
      const extraParams = msg.extraParams || {};

      if (action === "pause" && code === 301) {
        maxAutologinSolvingTimeout = extraParams.max_wait_time || 60;
        console.log(`Autologin pause notification received, max wait time: ${maxAutologinSolvingTimeout}s`);
        autologinPauseEvent.set();
      } else if (action === "resume" && code === 302) {
        console.log("Autologin resume notification received");
        autologinResumeOrTakeoverEvent.set();
      } else if (action === "takeover") {
        shouldTakeover = true;
        takeoverNotifyId = msg.id ?? null;
        maxTakeoverTimeout = extraParams.max_wait_time || 180;
        console.log(`Autologin takeover notification received, notify_id: ${takeoverNotifyId}, max wait time: ${maxTakeoverTimeout}s`);
        autologinResumeOrTakeoverEvent.set();
      }
    }
  } catch (error) {
    console.error(`Error handling browser callback: ${error}`);
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
      autoLogin: true,
      useStealth: true,
      solveCaptchas: true,
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

    // Navigate to ly.com homepage
    console.log("🌐 Navigating to ly.com homepage...");
    await page.goto("https://www.ly.com/");
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Handle first-time login popup (if present)
    console.log("🔍 Checking for first-time login popup...");
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mask = page.locator("div.dt-mask.dt-mask-show");
      const maskCount = await mask.count();
      if (maskCount > 0) {
        console.log("✅ First-time login popup detected, closing...");
        const closeButton = page.locator("img.dt-close-icon.closeDtMask");
        const closeButtonCount = await closeButton.count();
        if (closeButtonCount > 0) {
          try {
            await closeButton.first().waitFor({ state: "visible", timeout: 3000 });
            await closeButton.first().click({ timeout: 3000 });
            console.log("✅ Close button clicked");
            try {
              await mask.waitFor({ state: "hidden", timeout: 3000 });
              console.log("✅ Popup closed");
            } catch {
              console.log("⚠️ Popup may have closed");
            }
          } catch (error) {
            console.log(`⚠️ Error closing popup: ${error}`);
          }
        } else {
          console.log("⚠️ Close button not found");
        }
      } else {
        console.log("ℹ️ No first-time login popup detected, continuing");
      }
    } catch (error) {
      console.log(`⚠️ Error checking popup: ${error}, continuing`);
    }

    // Click "Hotel" link
    console.log('🔍 Looking for "Hotel" link...');
    const hotelLink = page.locator("a#top_hotel, a.hotel_at.atop_hotel");
    const hotelLinkCount = await hotelLink.count();
    if (hotelLinkCount > 0) {
      await hotelLink.first().click();
      await new Promise(resolve => setTimeout(resolve, 1000));
    } else {
      console.log('⚠️ "Hotel" link not found, continuing');
    }

    // Enter "Beijing" in destination
    console.log("🔍 Looking for destination input...");
    const destinationInput = page.locator("input#txtHotelCity1");
    const destinationCount = await destinationInput.count();
    if (destinationCount > 0) {
      await destinationInput.fill("北京");
    } else {
      throw new Error("Destination input not found");
    }
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Enter hotel name input
    console.log("🔍 Looking for hotel name input...");
    const hotelNameInput = page.locator("input#txtHotelInfo");
    const hotelNameCount = await hotelNameInput.count();
    if (hotelNameCount > 0) {
      await hotelNameInput.fill("北京国贸大酒店");
    } else {
      throw new Error("Hotel name input not found");
    }
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Press Enter to submit search
    console.log("⌨️ Pressing Enter to submit search...");
    await hotelNameInput.press("Enter");
    try {
      await page.waitForLoadState("networkidle", { timeout: 10000 });
      console.log("✅ Page loaded");
    } catch {
      console.log("⚠️ Page load timeout, continuing");
    }
    await new Promise(resolve => setTimeout(resolve, 5000));
    await page.evaluate("() => window.scrollBy(0, 200)");
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Click "View details" button
    console.log('🔍 Looking for "View details" button...');
    try {
      await page.waitForSelector('div:has-text("查看详情")', { timeout: 10000, state: "visible" });
    } catch {
      console.log('⚠️ Timeout waiting for "View details" button, continuing to search...');
    }

    const detailSelector = 'div.flex.items-center.justify-center.w-\\[104px\\].h-\\[40px\\]:has-text("查看详情")';
    const detailButton = page.locator(detailSelector);
    const detailCount = await detailButton.count();
    let clicked = false;
    if (detailCount > 0) {
      try {
        const firstButton = detailButton.first();
        await firstButton.waitFor({ state: "visible", timeout: 5000 });
        await firstButton.scrollIntoViewIfNeeded();
        await new Promise(resolve => setTimeout(resolve, 500));
        await firstButton.click({ timeout: 5000, force: true });
        clicked = true;
      } catch (error) {
        console.log(`❌ click failed: ${error}`);
      }
    }
    if (!clicked) {
      console.log('⚠️ "View details" button not found or not clickable');
    }

    // Wait for autologin solving if needed
    const autologinSuccess = await waitForAutologinSolving(
      autologinPauseEvent,
      autologinResumeOrTakeoverEvent,
      maxAutologinDetectTimeout
    );

    if (!autologinSuccess) {
      console.log("🌍 Opening browser with takeover URL...");
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
      await new Promise(resolve => setTimeout(resolve, 30 * 1000));
      if (takeoverNotifyId !== null) {
        await session.browser.sendTakeoverDone(takeoverNotifyId);
      }
      console.log("✅ User takeover completed...");
    }

    console.log("🔍 Waiting for page to load...");
    await new Promise(resolve => setTimeout(resolve, 15000));
    try {
      await page.waitForLoadState("networkidle", { timeout: 10000 });
    } catch {
      console.log("⚠️ Page load timeout, continuing");
    }
    await page.evaluate("() => window.scrollBy(0, 2000)");
    await new Promise(resolve => setTimeout(resolve, 5000));

    // Click first "Book" button
    console.log('🔍 Looking for "Book" button...');
    const bookingButton = page.locator('div.btn-top:has-text("预订")').first();
    const bookingCount = await bookingButton.count();
    if (bookingCount > 0) {
      try {
        await bookingButton.waitFor({ state: "visible", timeout: 5000 });
        await bookingButton.scrollIntoViewIfNeeded();
        await new Promise(resolve => setTimeout(resolve, 500));
        await bookingButton.click({ timeout: 5000, force: true });
      } catch (error) {
        console.log(`❌ Failed to click "Book" button: ${error}`);
      }
    } else {
      console.log('⚠️ "Book" button not found');
    }

    await new Promise(resolve => setTimeout(resolve, 3000));
    await page.evaluate("() => window.scrollBy(0, 300)");

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
