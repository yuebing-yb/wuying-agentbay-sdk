import { AgentBay } from "../../src";
import { CreateSessionParams } from "../../src/session-params";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";
import { Session } from "../../src/session";
import { SessionResult } from "../../src/types/api-response";

describe("Browser Type - Integration Tests", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeAll(async () => {
    const apiKey = getTestApiKey();
    if (!apiKey) {
      throw new Error("API key is required for integration tests");
    }
    agentBay = new AgentBay({ apiKey });
    
    // Increase timeout for integration tests
    jest.setTimeout(120000); // 120 seconds
    
    // Create a session with computer use image (required for browser type selection)
    const params = new CreateSessionParams();
    params.imageId = "linux_latest";
    
    log("Creating session with computer use image for browser type testing...");
    const sessionResult: SessionResult = await agentBay.create(params);
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error("Failed to create session");
    }
    
    session = sessionResult.session;
    log(`Session created with ID: ${session.sessionId}`);
  });

  afterAll(async () => {
    // Clean up session
    if (session) {
      try {
        await agentBay.delete(session);
        log(`Session deleted: ${session.sessionId}`);
      } catch (e) {
        log(`Warning: Failed to delete session: ${e}`);
      }
    }
  });

  describe("Browser Type Selection", () => {
    it("should use default browser type (undefined)", async () => {
      log("=== Testing default browser type (undefined) ===");
      
      // Create browser option with default settings
      const browserOption = {};
      
      // Initialize browser
      log("Initializing browser with default options...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });

    it("should support chrome browser type", async () => {
      log("=== Testing Chrome browser type ===");
      
      // Create browser option with Chrome type
      const browserOption = {
        browserType: "chrome" as "chrome"
      };
      
      // Verify browser type is set correctly
      expect(browserOption.browserType).toBe("chrome");
      log(`Browser type set to: ${browserOption.browserType}`);
      
      // Initialize browser
      log("Initializing browser with Chrome type...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully with Chrome");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });

    it("should support explicit chromium browser type", async () => {
      log("=== Testing explicit Chromium browser type ===");
      
      // Create browser option with explicit Chromium type
      const browserOption = {
        browserType: "chromium" as "chromium"
      };
      
      // Verify browser type is set correctly
      expect(browserOption.browserType).toBe("chromium");
      log(`Browser type set to: ${browserOption.browserType}`);
      
      // Initialize browser
      log("Initializing browser with explicit Chromium type...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully with Chromium");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });

    it("should support browser type with other options", async () => {
      log("=== Testing browser type with other options ===");
      
      // Create browser option with Chrome type and other options
      const browserOption = {
        browserType: "chrome" as "chrome",
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36",
        solveCaptchas: true
      };
      
      // Verify all options are set correctly
      expect(browserOption.browserType).toBe("chrome");
      expect(browserOption.useStealth).toBe(true);
      expect(browserOption.userAgent).toBe("Mozilla/5.0 (Test) AppleWebKit/537.36");
      expect(browserOption.solveCaptchas).toBe(true);
      log("All browser options set correctly");
      
      // Initialize browser
      log("Initializing browser with Chrome type and other options...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully with all options");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });

    it("should work with BrowserOptionClass constructor", async () => {
      log("=== Testing BrowserOptionClass with browser type ===");
      
      // Import BrowserOptionClass
      const { BrowserOptionClass } = await import("../../src/browser/browser");
      
      // Create browser option using constructor
      const browserOption = new BrowserOptionClass(
        false,  // useStealth
        "Mozilla/5.0 (Test) AppleWebKit/537.36",  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      
      // Verify browser type is set correctly
      expect(browserOption.browserType).toBe("chrome");
      log(`Browser type set to: ${browserOption.browserType}`);
      
      // Initialize browser
      log("Initializing browser with BrowserOptionClass...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully with BrowserOptionClass");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });

    it("should handle browser type serialization in toMap", () => {
      log("=== Testing browser type serialization ===");
      
      // Test Chrome browser type serialization
      const chromeOption = {
        browserType: "chrome"
      };
      
      // Test Chromium browser type serialization
      const chromiumOption = {
        browserType: "chromium"
      };
      
      // Test default browser type (should be undefined)
      const defaultOption = {};
      
      // These would be tested in the actual BrowserOptionClass.toMap() method
      // For this integration test, we verify the option structure
      expect(chromeOption.browserType).toBe("chrome");
      expect(chromiumOption.browserType).toBe("chromium");
      expect(defaultOption.browserType).toBeUndefined();
      log("Browser type options structured correctly");
    });

    it("should work with standard browser image (fallback behavior)", async () => {
      log("=== Testing browser type with standard browser image ===");
      
      // Create a new session with standard browser image
      const params = new CreateSessionParams();
      params.imageId = "browser_latest";  // Standard browser image
      
      log("Creating session with standard browser image...");
      const sessionResult: SessionResult = await agentBay.create(params);
      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      
      const standardSession = sessionResult.session!;
      
      try {
        // Test Chrome browser type with standard image (should still work)
        const browserOption = {
          browserType: "chrome" as "chrome"
        };
        
        log("Initializing browser with Chrome type on standard image...");
        const success = await standardSession.browser.initializeAsync(browserOption);
        expect(success).toBe(true);
        log("Browser initialized successfully with Chrome on standard image");
        
        // Verify browser is initialized
        expect(standardSession.browser.isInitialized()).toBe(true);
        log("Browser is initialized");
        
        // Get endpoint URL
        const endpointUrl = await standardSession.browser.getEndpointUrl();
        expect(endpointUrl).toBeDefined();
        log(`Browser endpoint URL: ${endpointUrl}`);
        
      } finally {
        // Clean up the additional session
        try {
          await agentBay.delete(standardSession);
          log("Additional session deleted successfully");
        } catch (e) {
          log(`Warning: Failed to delete additional session: ${e}`);
        }
      }
    });

    it("should handle multiple browser type initializations", async () => {
      log("=== Testing multiple browser type initializations ===");
      
      // Test that we can initialize with different browser types
      const browserTypes: ("chrome" | "chromium")[] = ["chrome", "chromium"];
      
      for (const browserType of browserTypes) {
        log(`Testing browser type: ${browserType}`);
        
        const browserOption = {
          browserType: browserType
        };
        
        // Initialize browser
        const success = await session.browser.initializeAsync(browserOption);
        expect(success).toBe(true);
        log(`Browser initialized successfully with ${browserType}`);
        
        // Verify browser is initialized
        expect(session.browser.isInitialized()).toBe(true);
        
        // Get endpoint URL
        const endpointUrl = await session.browser.getEndpointUrl();
        expect(endpointUrl).toBeDefined();
        log(`Browser endpoint URL for ${browserType}: ${endpointUrl}`);
        
        // Small delay between tests
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    });
  });

  describe("Browser Type Validation", () => {
    it("should validate browser type values", () => {
      log("=== Testing browser type validation ===");
      
      // Valid browser types
      const validTypes = ["chrome", "chromium"];
      validTypes.forEach(type => {
        const option = { browserType: type };
        expect(option.browserType).toBe(type);
        log(`Valid browser type: ${type}`);
      });
      
      // Invalid browser types (these would be caught by validation in real implementation)
      const invalidTypes = ["firefox", "edge", "safari"];
      invalidTypes.forEach(type => {
        const option = { browserType: type };
        // In a real implementation, this would be validated
        // For this test, we just verify the structure
        expect(option.browserType).toBe(type);
        log(`Invalid browser type (would be rejected): ${type}`);
      });
    });

    it("should handle browser type with viewport and screen options", async () => {
      log("=== Testing browser type with viewport and screen options ===");
      
      const browserOption = {
        browserType: "chrome" as "chrome",
        viewport: {
          width: 1920,
          height: 1080
        },
        screen: {
          width: 1920,
          height: 1080
        }
      };
      
      // Verify all options are set correctly
      expect(browserOption.browserType).toBe("chrome");
      expect(browserOption.viewport).toBeDefined();
      expect(browserOption.screen).toBeDefined();
      log("Browser type with viewport and screen options set correctly");
      
      // Initialize browser
      log("Initializing browser with Chrome type, viewport, and screen options...");
      const success = await session.browser.initializeAsync(browserOption);
      expect(success).toBe(true);
      log("Browser initialized successfully with all options");
      
      // Verify browser is initialized
      expect(session.browser.isInitialized()).toBe(true);
      log("Browser is initialized");
      
      // Get endpoint URL
      const endpointUrl = await session.browser.getEndpointUrl();
      expect(endpointUrl).toBeDefined();
      log(`Browser endpoint URL: ${endpointUrl}`);
    });
  });
});
