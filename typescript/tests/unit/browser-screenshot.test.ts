import { expect } from "chai";
import * as sinon from "sinon";
import { Browser } from "../../src/browser/browser";
import { Session } from "../../src/session";
import { BrowserError } from "../../src/exceptions";

describe("Browser - Screenshot", () => {
  let mockSession: sinon.SinonStubbedInstance<Session>;
  let browser: Browser;

  beforeEach(() => {
    mockSession = sinon.createStubInstance(Session);
    browser = new Browser(mockSession as unknown as Session);
  });

  afterEach(() => {
    sinon.restore();
  });

  describe("screenshot", () => {
    it("should throw BrowserError when browser is not initialized", async () => {
      const mockPage = {};
      
      try {
        await browser.screenshot(mockPage);
        expect.fail("Should have thrown an error");
      } catch (error: any) {
        expect(error).to.be.instanceOf(BrowserError);
        expect(error.message).to.contain("Browser must be initialized before calling screenshot");
      }
    });

    it("should throw error when page is null", async () => {
      // Manually set browser as initialized for testing
      (browser as any)._initialized = true;
      
      try {
        await browser.screenshot(null);
        expect.fail("Should have thrown an error");
      } catch (error: any) {
        expect(error.message).to.contain("Page cannot be null or undefined");
      }
    });

    it("should throw error when page is undefined", async () => {
      // Manually set browser as initialized for testing
      (browser as any)._initialized = true;
      
      try {
        await browser.screenshot(undefined);
        expect.fail("Should have thrown an error");
      } catch (error: any) {
        expect(error.message).to.contain("Page cannot be null or undefined");
      }
    });

    it("should handle Playwright method errors correctly", async () => {
      // Manually set browser as initialized for testing
      (browser as any)._initialized = true;
      
      // Create a mock page that will fail when Playwright methods are called
      const mockPage = {};
      
      try {
        await browser.screenshot(mockPage);
        expect.fail("Should have thrown an error");
      } catch (error: any) {
        // Should get an error about missing Playwright methods
        expect(error.message).to.contain("Failed to capture screenshot");
      }
    });
  });
});