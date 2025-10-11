import { BrowserOption, BrowserOptionClass, BrowserProxyClass } from "../../src/browser/browser";

describe("Browser Type - Unit Tests", () => {
  describe("BrowserOptionClass - Browser Type", () => {
    test("should default to undefined browser type", () => {
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Default Test Agent',
        viewport: { width: 1024, height: 768 },
        screen: { width: 1024, height: 768 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] }
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBeUndefined();
      expect(option.useStealth).toBe(false);
      expect(option.userAgent).toBe('Default Test Agent');
    });

    test("should accept chrome browser type", () => {
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: 'Chrome Test Agent',
        viewport: { width: 1920, height: 1080 },
        screen: { width: 1920, height: 1080 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['macos'], locales: ['en-US'] },
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chrome");
      expect(option.useStealth).toBe(true);
      expect(option.userAgent).toBe('Chrome Test Agent');
    });

    test("should accept chromium browser type", () => {
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Chromium Test Agent',
        viewport: { width: 1366, height: 768 },
        screen: { width: 1366, height: 768 },
        fingerprint: { devices: ['mobile'], operatingSystems: ['linux'], locales: ['zh-CN'] },
        browserType: 'chromium'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chromium");
      expect(option.useStealth).toBe(false);
      expect(option.userAgent).toBe('Chromium Test Agent');
    });

    test("should validate browser type in constructor", () => {
      // Test invalid browser type - this should be caught by validation
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "firefox" as any  // invalid browserType
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should validate browser type in constructor with edge", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "edge" as any  // invalid browserType
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should validate browser type in constructor with safari", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "safari" as any  // invalid browserType
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should validate browser type in constructor with empty string", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "" as any  // invalid browserType
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should validate browser type case sensitivity", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "Chrome" as any  // invalid case
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });
  });

  describe("BrowserOptionClass - toMap with Browser Type", () => {
    test("should include browserType in toMap for chrome", () => {
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: 'Chrome toMap Test Agent',
        viewport: { width: 1600, height: 900 },
        screen: { width: 1600, height: 900 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] },
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      const optionMap = option.toMap();
      expect(optionMap).toHaveProperty("browserType");
      expect(optionMap.browserType).toBe("chrome");
      expect(optionMap.useStealth).toBe(true);
      expect(optionMap.userAgent).toBe('Chrome toMap Test Agent');
    });

    test("should include browserType in toMap for chromium", () => {
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Chromium toMap Test Agent',
        viewport: { width: 1280, height: 720 },
        screen: { width: 1280, height: 720 },
        fingerprint: { devices: ['mobile'], operatingSystems: ['linux'], locales: ['zh-CN'] },
        browserType: 'chromium'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      const optionMap = option.toMap();
      expect(optionMap).toHaveProperty("browserType");
      expect(optionMap.browserType).toBe("chromium");
      expect(optionMap.useStealth).toBe(false);
      expect(optionMap.userAgent).toBe('Chromium toMap Test Agent');
    });

    test("should not include browserType in toMap when undefined", () => {
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: 'Undefined browserType Test Agent',
        viewport: { width: 800, height: 600 },
        screen: { width: 800, height: 600 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['macos'], locales: ['fr-FR'] }
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      const optionMap = option.toMap();
      expect(optionMap).not.toHaveProperty("browserType");
      expect(optionMap.useStealth).toBe(true);
    });

    test("should include browserType in toMap with other options", () => {
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36",
        viewport: { width: 1920, height: 1080 },
        screen: { width: 1920, height: 1080 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] },
        solveCaptchas: true,
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      const optionMap = option.toMap();
      expect(optionMap).toHaveProperty("browserType");
      expect(optionMap.browserType).toBe("chrome");
      expect(optionMap).toHaveProperty("useStealth");
      expect(optionMap.useStealth).toBe(true);
      expect(optionMap).toHaveProperty("userAgent");
      expect(optionMap.userAgent).toBe("Mozilla/5.0 (Test) AppleWebKit/537.36");
      expect(optionMap).toHaveProperty("solveCaptchas");
      expect(optionMap.solveCaptchas).toBe(true);
    });
  });

  describe("BrowserOptionClass - fromMap with Browser Type", () => {
    test("should parse browserType from map for chrome", () => {
      const browserOption: BrowserOption = {
        browserType: "chrome",
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36",
        viewport: { width: 1440, height: 900 },
        screen: { width: 1440, height: 900 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['macos'], locales: ['en-US'] }
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chrome");
      expect(option.useStealth).toBe(true);
      expect(option.userAgent).toBe("Mozilla/5.0 (Test) AppleWebKit/537.36");
      expect(option.viewport?.width).toBe(1440);
    });

    test("should parse browserType from map for chromium", () => {
      const browserOption: BrowserOption = {
        browserType: "chromium",
        useStealth: false,
        solveCaptchas: true,
        viewport: { width: 1024, height: 768 },
        screen: { width: 1024, height: 768 },
        fingerprint: { devices: ['mobile'], operatingSystems: ['android'], locales: ['ja-JP'] }
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chromium");
      expect(option.useStealth).toBe(false);
      expect(option.solveCaptchas).toBe(true);
      expect(option.viewport?.width).toBe(1024);
    });

    test("should remain undefined when browserType not in map", () => {
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36",
        viewport: { width: 1366, height: 768 },
        screen: { width: 1366, height: 768 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['linux'], locales: ['de-DE'] }
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      // Should remain undefined when not specified
      expect(option.browserType).toBeUndefined();
      expect(option.useStealth).toBe(true);
      expect(option.userAgent).toBe("Mozilla/5.0 (Test) AppleWebKit/537.36");
    });

    test("should parse invalid browserType from map without validation", () => {
      // Note: fromMap doesn't validate, it just sets values
      // Validation happens in the constructor
      const browserOption: BrowserOption = {
        browserType: "firefox" as any,
        useStealth: true,
        viewport: { width: 800, height: 600 },
        screen: { width: 800, height: 600 },
        fingerprint: { devices: ['mobile'], operatingSystems: ['ios'], locales: ['es-ES'] }
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      // fromMap sets the value even if it's invalid
      expect(option.browserType).toBe("firefox");
      expect(option.useStealth).toBe(true);
    });
  });

  describe("BrowserOptionClass - Browser Type with Complex Options", () => {
    test("should handle browserType with viewport and screen", () => {
      const viewport = { width: 1920, height: 1080 };
      const screen = { width: 1920, height: 1080 };
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Complex Options Test Agent',
        viewport: viewport,
        screen: screen,
        fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] },
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chrome");
      expect(option.viewport).toEqual(viewport);
      expect(option.screen).toEqual(screen);
      expect(option.userAgent).toBe('Complex Options Test Agent');
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).toBe("chrome");
      expect(optionMap.viewport).toEqual(viewport);
      expect(optionMap.screen).toEqual(screen);
    });

    test("should handle browserType with fingerprint", () => {
      const fingerprint = {
        devices: ["desktop", "mobile"] as ("desktop" | "mobile")[],
        operatingSystems: ["windows", "macos"] as ("windows" | "macos" | "linux" | "android" | "ios")[],
        locales: ["en-US", "zh-CN"]
      };
      const browserOption: BrowserOption = {
        useStealth: true,
        userAgent: 'Fingerprint Test Agent',
        viewport: { width: 1280, height: 720 },
        screen: { width: 1280, height: 720 },
        fingerprint: fingerprint,
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chrome");
      expect(option.fingerprint).toEqual(fingerprint);
      expect(option.useStealth).toBe(true);
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).toBe("chrome");
      expect(optionMap.fingerprint).toEqual(fingerprint);
    });

    test("should handle browserType with proxies", () => {
      const proxy = new BrowserProxyClass(
        "custom",
        "127.0.0.1:8080",
        "user",
        "pass"
      );
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Proxy Test Agent',
        viewport: { width: 1600, height: 900 },
        screen: { width: 1600, height: 900 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['linux'], locales: ['fr-FR'] },
        proxies: [proxy],
        browserType: 'chrome'
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBe("chrome");
      expect(option.proxies).toEqual([proxy]);
      expect(option.userAgent).toBe('Proxy Test Agent');
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).toBe("chrome");
      expect(optionMap.proxies).toBeDefined();
    });
  });

  describe("BrowserOptionClass - Validation Order", () => {
    test("should validate browserType in constructor before other checks", () => {
      // In the constructor, browserType validation happens first
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies - use valid proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "invalid" as any  // invalid browserType
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should validate proxies length in fromMap", () => {
      // In fromMap, proxies validation happens during processing
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Validation Test Agent',
        viewport: { width: 1024, height: 768 },
        screen: { width: 1024, height: 768 },
        fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] },
        proxies: [
          new BrowserProxyClass('custom', 'http://proxy1.com'),
          new BrowserProxyClass('custom', 'http://proxy2.com')
        ],  // Multiple proxies
        browserType: "chrome"
      };
      const option = new BrowserOptionClass();
      expect(() => {
        option.fromMap(browserOption as Record<string, any>);
      }).toThrow("proxies list length must be limited to 1");
    });
  });

  describe("BrowserOptionClass - Edge Cases", () => {
    test("should handle undefined browserType in constructor", () => {
      const browserOption: BrowserOption = {
        useStealth: false,
        userAgent: 'Edge Case Test Agent',
        viewport: { width: 800, height: 600 },
        screen: { width: 800, height: 600 },
        fingerprint: { devices: ['mobile'], operatingSystems: ['android'], locales: ['ko-KR'] }
        // browserType intentionally omitted
      };
      const option = new BrowserOptionClass();
      option.fromMap(browserOption as Record<string, any>);
      
      expect(option.browserType).toBeUndefined();
      expect(option.useStealth).toBe(false);
    });

    test("should handle null browserType in constructor", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          null as any  // browserType - should be invalid
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });

    test("should handle browserType with special characters", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          undefined,  // fingerprintFormat
          false,  // fingerprintPersistent
          false,  // solveCaptchas
          undefined,  // proxies
          [],         // cmdArgs
          undefined,  // defaultNavigateUrl
          "chrome-v2" as any  // browserType with special characters
        );
      }).toThrow("browserType must be 'chrome' or 'chromium'");
    });
  });
});
