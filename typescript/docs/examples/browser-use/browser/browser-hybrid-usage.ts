/**
 * Browser Hybrid Usage Example - demonstrates combining BrowserUseAgent and BrowserOperator.
 * This example shows how to:
 * - Create AIBrowser session
 * - Initialize browser with AgentBay
 * - Use Playwright to connect via CDP protocol
 * - Execute tasks using BrowserUseAgent
 * - Extract data using BrowserOperator
 */

import {
  AgentBay,
  CreateSessionParams,
  BrowserOption,
  ExtractOptions,
  log,
} from "wuying-agentbay-sdk";

import { chromium } from "playwright";
import { z } from "zod";
import 'dotenv/config';

// Schema for weather query test
const WeatherSchema = z.object({
  Weather: z.string(),
  City: z.string(),
  Temperature: z.string(),
});
type WeatherType = z.infer<typeof WeatherSchema>;

// Schema for extract test
const DummySchema = z.object({
  title: z.string(),
});
type DummyType = z.infer<typeof DummySchema>;

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.error("Error: AGENTBAY_API_KEY environment variable not set");
    return;
  }

  const agentBay = new AgentBay({ apiKey });
  const params: CreateSessionParams = {
    imageId: "browser_latest",
  };

  const sessionResult = await agentBay.create(params);
  if (!sessionResult.success || !sessionResult.session) {
    console.error("Failed to create session");
    return;
  }

  const session = sessionResult.session;
  console.log(`Session created with ID: ${session.sessionId}`);

  if (!session.agent) {
    console.error("Session agent not available");
    return;
  }

  if (!session.browser) {
    console.error("Session browser not available");
    return;
  }

  log("🚀 Browser initialization");
  const initialized = await session.browser.initializeAsync({} as BrowserOption);
  if (!initialized) {
    console.error("Failed to initialize browser");
    return;
  }

  const endpointUrl = await session.browser.getEndpointUrl();
  log("endpoint_url =", endpointUrl);
  if (!endpointUrl) {
    console.error("Failed to get endpoint URL");
    return;
  }

  const browser = await chromium.connectOverCDP(endpointUrl);
  if (!browser) {
    console.error("Failed to connect to browser");
    return;
  }

  try {
    const context = browser.contexts().length > 0
      ? browser.contexts()[0]
      : await browser.newContext();

    const page = await context.newPage();
    await page.goto("http://www.baidu.com");
    
    const title = await page.title();
    if (title) {
      log(`Page title: ${title}`);
    }

    // Execute task using BrowserUseAgent
    const task = "在百度查询上海天气";
    log("🚀 task of Query the weather in Shanghai");

    const timeout = 300; // 5 minutes
    const result = await session.agent.browser.executeTaskAndWait(
      task,
      timeout,
      false, // use_vision
      WeatherSchema
    );

    if (!result.success) {
      console.error("Task execution failed:", result.errorMessage);
    } else {
      console.log(`✅ result ${result.taskResult}`);
    }

    // Extract data using BrowserOperator
    const extractOptions: ExtractOptions<typeof DummySchema> = {
      instruction: "Extract the title",
      schema: DummySchema,
    };

    const [extractSuccess, obj] = await session.browser.operator.extract(
      extractOptions,
      page
    );
    log(`✅ result of extract ${extractSuccess}\n${JSON.stringify(obj, null, 2)}`);

    await page.close();
    await browser.close();

    // Clean up session
    await agentBay.delete(session);
    log("Session deleted");

  } catch (error) {
    console.error("Error during execution:", error);
  }
}

if (require.main === module) {
  main().catch(console.error);
}
