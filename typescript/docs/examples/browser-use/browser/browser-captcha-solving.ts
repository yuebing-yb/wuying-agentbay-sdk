/**
 * Example: browser-captcha-solving.ts
 * This example demonstrates how to deal with captcha automatically solving
 * using browser notification callback from sandbox browser.
 *
 * 1. Create a new browser session with AgentBay SDK
 * 2. Use playwright to connect to AIBrowser instance through CDP protocol
 * 3. Set solve_captchas to be True and goto jd.com website
 * 4. We will encounter a captcha and we will solve it automatically.
 */

import { AgentBay, BrowserOption, BrowserNotifyMessage } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';
import { exec } from 'child_process';
import * as os from 'os';

let shouldTakeover = false;
let takeoverNotifyId: number | null = null;
let maxCaptchaDetectTimeout = 5.0;
let maxCaptchaSolvingTimeout = 60.0;
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

const captchaPauseEvent = new EventEmitter();
const captchaResumeOrTakeoverEvent = new EventEmitter();

async function waitForCaptchaSolving(
  captchaPauseEvent: EventEmitter,
  captchaResumeOrTakeoverEvent: EventEmitter,
  captchaDetectTimeout: number = 2.0
): Promise<boolean> {
  console.log(`Waiting for captcha pause event, timeout: ${captchaDetectTimeout}s`);
  const pauseDetected = await captchaPauseEvent.wait(captchaDetectTimeout * 1000);

  if (!pauseDetected) {
    console.log("No captcha pause event detected within timeout, proceeding next step");
    return true;
  }

  console.log(`Waiting for captcha resume event, timeout: ${maxCaptchaSolvingTimeout}s`);
  const resumeDetected = await captchaResumeOrTakeoverEvent.wait(maxCaptchaSolvingTimeout * 1000);

  if (!resumeDetected) {
    console.log("No captcha resume event detected within timeout, should takeover");
    return false;
  }

  if (shouldTakeover) {
    console.log("Captcha solving failed, takeover event detected");
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
      const extraParams = msg.extraParams || {};
      
      if (action === "pause") {
        maxCaptchaSolvingTimeout = extraParams.max_wait_time || 60;
        console.log(`Captcha pause notification received, max wait time: ${maxCaptchaSolvingTimeout}s`);
        captchaPauseEvent.set();
      } else if (action === "resume") {
        console.log("Captcha resume notification received");
        captchaResumeOrTakeoverEvent.set();
      } else if (action === "takeover") {
        shouldTakeover = true;
        takeoverNotifyId = msg.id || null;
        maxTakeoverTimeout = extraParams.max_wait_time || 180;
        console.log(`Captcha takeover notification received, notify_id: ${takeoverNotifyId}, max wait time: ${maxTakeoverTimeout}s`);
        captchaResumeOrTakeoverEvent.set();
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
    const browserOption: BrowserOption = {
      useStealth: true,
      solveCaptchas: true,
      callForUser: true,
    };
    
    const initialized = await session.browser.initializeAsync(browserOption);
    if (!initialized) {
      throw new Error("Failed to initialize browser");
    }

    const endpointUrl = await session.browser.getEndpointUrl();
    console.log(`🌐 Browser endpoint URL: ${endpointUrl}`);

    await new Promise(resolve => setTimeout(resolve, 2000));

    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts()[0];
    const page = await context.newPage();

    console.log("🚀 Navigating to jd.com...");
    await page.goto('https://aq.jd.com/process/findPwd?s=1');
    
    console.log("📱 fill phone number...");
    await page.fill('input.field[placeholder="请输入账号名/邮箱/已验证手机号"]', '13000000000');
    await new Promise(resolve => setTimeout(resolve, 2000));

    console.log("🖱️ click next step button...");
    await page.click('button.btn-check-defaut.btn-xl');
    console.log("🔑 Captcha triggered, waiting for solving...");

    const captchaSolved = await waitForCaptchaSolving(
      captchaPauseEvent,
      captchaResumeOrTakeoverEvent,
      maxCaptchaDetectTimeout
    );

    if (!captchaSolved) {
      console.log("⏰ Captcha solving timeout or should takeover...");
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
      
      console.log(`Waiting for user task over completed or timeout, timeout: ${maxTakeoverTimeout}s`);
      await new Promise(resolve => setTimeout(resolve, maxTakeoverTimeout * 1000));
      
      if (takeoverNotifyId !== null) {
        await session.browser.sendTakeoverDone(takeoverNotifyId);
      }
      console.log("✅ User task over completed...");
    } else {
      console.log("✅ Captcha solved successfully...");
    }

    console.log("🔍 Checking for authentication success...");
    try {
      const successButton = await page.waitForSelector(
        'button.btn-check-succ:has-text("认证成功")',
        { timeout: 5000 }
      );
      
      if (successButton) {
        console.log("✅ Authentication successful - '认证成功' button found!");
        await page.screenshot({ path: "captcha_solving.png" });
      } else {
        console.log("⚠️ Authentication success button not found");
      }
    } catch (error) {
      console.log(`⚠️ Could not find authentication success button: ${error}`);
    }

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
