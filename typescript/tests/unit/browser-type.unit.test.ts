import { expect } from "chai";
import { BrowserOptionClass } from "../../src/browser/browser";

describe("Browser Type - Unit Tests", () => {
  describe("BrowserOptionClass - Browser Type", () => {
    it("should default to chromium browser type", () => {
      const option = new BrowserOptionClass();
      expect(option.browserType).to.equal("chromium");
    });

    it("should accept chrome browser type", () => {
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      expect(option.browserType).to.equal("chrome");
    });

    it("should accept chromium browser type", () => {
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chromium"  // browserType
      );
      expect(option.browserType).to.equal("chromium");
    });

    it("should validate browser type in constructor", () => {
      // Test invalid browser type - this should be caught by validation
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          "firefox"  // invalid browserType
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });

    it("should validate browser type in constructor with edge", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          "edge"  // invalid browserType
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });

    it("should validate browser type in constructor with safari", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          "safari"  // invalid browserType
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });

    it("should validate browser type in constructor with empty string", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          ""  // invalid browserType
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });

    it("should validate browser type case sensitivity", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          "Chrome"  // invalid case
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });
  });

  describe("BrowserOptionClass - toMap with Browser Type", () => {
    it("should include browserType in toMap for chrome", () => {
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      
      const optionMap = option.toMap();
      expect(optionMap).to.have.property("browserType");
      expect(optionMap.browserType).to.equal("chrome");
    });

    it("should include browserType in toMap for chromium", () => {
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chromium"  // browserType
      );
      
      const optionMap = option.toMap();
      expect(optionMap).to.have.property("browserType");
      expect(optionMap.browserType).to.equal("chromium");
    });

    it("should include browserType in toMap with other options", () => {
      const option = new BrowserOptionClass(
        true,  // useStealth
        "Mozilla/5.0 (Test) AppleWebKit/537.36",  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        true,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      
      const optionMap = option.toMap();
      expect(optionMap).to.have.property("browserType");
      expect(optionMap.browserType).to.equal("chrome");
      expect(optionMap).to.have.property("useStealth");
      expect(optionMap.useStealth).to.be.true;
      expect(optionMap).to.have.property("userAgent");
      expect(optionMap.userAgent).to.equal("Mozilla/5.0 (Test) AppleWebKit/537.36");
      expect(optionMap).to.have.property("solveCaptchas");
      expect(optionMap.solveCaptchas).to.be.true;
    });
  });

  describe("BrowserOptionClass - fromMap with Browser Type", () => {
    it("should parse browserType from map for chrome", () => {
      const optionMap = {
        browserType: "chrome",
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36"
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(optionMap);
      
      expect(option.browserType).to.equal("chrome");
      expect(option.useStealth).to.be.true;
      expect(option.userAgent).to.equal("Mozilla/5.0 (Test) AppleWebKit/537.36");
    });

    it("should parse browserType from map for chromium", () => {
      const optionMap = {
        browserType: "chromium",
        useStealth: false,
        solveCaptchas: true
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(optionMap);
      
      expect(option.browserType).to.equal("chromium");
      expect(option.useStealth).to.be.false;
      expect(option.solveCaptchas).to.be.true;
    });

    it("should default to chromium when browserType not in map", () => {
      const optionMap = {
        useStealth: true,
        userAgent: "Mozilla/5.0 (Test) AppleWebKit/537.36"
      };
      
      const option = new BrowserOptionClass();
      option.fromMap(optionMap);
      
      // Should default to chromium when not specified
      expect(option.browserType).to.equal("chromium");
      expect(option.useStealth).to.be.true;
      expect(option.userAgent).to.equal("Mozilla/5.0 (Test) AppleWebKit/537.36");
    });

    it("should validate browserType from map", () => {
      const optionMap = {
        browserType: "firefox",
        useStealth: true
      };
      
      const option = new BrowserOptionClass();
      expect(() => {
        option.fromMap(optionMap);
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });
  });

  describe("BrowserOptionClass - Browser Type with Complex Options", () => {
    it("should handle browserType with viewport and screen", () => {
      const viewport = { width: 1920, height: 1080 };
      const screen = { width: 1920, height: 1080 };
      
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        viewport,  // viewport
        screen,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      
      expect(option.browserType).to.equal("chrome");
      expect(option.viewport).to.deep.equal(viewport);
      expect(option.screen).to.deep.equal(screen);
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).to.equal("chrome");
      expect(optionMap.viewport).to.deep.equal(viewport);
      expect(optionMap.screen).to.deep.equal(screen);
    });

    it("should handle browserType with fingerprint", () => {
      const fingerprint = {
        devices: ["desktop", "mobile"],
        operatingSystems: ["windows", "macos"],
        locales: ["en-US", "zh-CN"]
      };
      
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        fingerprint,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        "chrome"  // browserType
      );
      
      expect(option.browserType).to.equal("chrome");
      expect(option.fingerprint).to.deep.equal(fingerprint);
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).to.equal("chrome");
      expect(optionMap.fingerprint).to.deep.equal(fingerprint);
    });

    it("should handle browserType with proxies", () => {
      const proxies = [{
        type: "custom",
        server: "127.0.0.1:8080",
        username: "user",
        password: "pass"
      }];
      
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        proxies,  // proxies
        "chrome"  // browserType
      );
      
      expect(option.browserType).to.equal("chrome");
      expect(option.proxies).to.deep.equal(proxies);
      
      const optionMap = option.toMap();
      expect(optionMap.browserType).to.equal("chrome");
      expect(optionMap.proxies).to.deep.equal(proxies);
    });
  });

  describe("BrowserOptionClass - Validation Order", () => {
    it("should validate browserType before other validations", () => {
      // This test ensures that browserType validation is checked first
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          [{}, {}],  // This would also cause an error, but browserType should be caught first
          "invalid"  // invalid browserType
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });
  });

  describe("BrowserOptionClass - Edge Cases", () => {
    it("should handle undefined browserType in constructor", () => {
      const option = new BrowserOptionClass(
        false,  // useStealth
        undefined,  // userAgent
        undefined,  // viewport
        undefined,  // screen
        undefined,  // fingerprint
        false,  // solveCaptchas
        undefined,  // proxies
        undefined  // browserType - should default to chromium
      );
      
      expect(option.browserType).to.equal("chromium");
    });

    it("should handle null browserType in constructor", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          null  // browserType - should be invalid
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });

    it("should handle browserType with special characters", () => {
      expect(() => {
        new BrowserOptionClass(
          false,  // useStealth
          undefined,  // userAgent
          undefined,  // viewport
          undefined,  // screen
          undefined,  // fingerprint
          false,  // solveCaptchas
          undefined,  // proxies
          "chrome-v2"  // browserType with special characters
        );
      }).to.throw("browserType must be 'chrome' or 'chromium'");
    });
  });
});
