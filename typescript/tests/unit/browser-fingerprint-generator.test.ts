import { BrowserFingerprintGenerator, FingerprintFormat } from '../../src/browser/fingerprint';
import * as fs from 'fs';
import * as path from 'path';

// Mock Playwright
jest.mock('playwright', () => ({
  chromium: {
    launch: jest.fn()
  }
}));

// Mock fs module
jest.mock('fs', () => ({
  writeFileSync: jest.fn(),
  readFileSync: jest.fn()
}));

describe('BrowserFingerprintGenerator Unit Tests', () => {
  describe('Constructor', () => {
  test('should create generator with default options', () => {
    const generator = new BrowserFingerprintGenerator();
      
    expect(generator).toBeInstanceOf(BrowserFingerprintGenerator);
    expect(generator).toBeDefined();
    });

  test('should create generator with custom options', () => {
    const generator = new BrowserFingerprintGenerator({
        headless: true,
        useChromeChannel: false
      });
      
    expect(generator).toBeInstanceOf(BrowserFingerprintGenerator);
    });

  test('should create generator with partial options', () => {
    const generator = new BrowserFingerprintGenerator({
        headless: true
      });
      
    expect(generator).toBeInstanceOf(BrowserFingerprintGenerator);
    });
  });

  describe('generateFingerprint', () => {
    let mockBrowser: any;
    let mockContext: any;
    let mockPage: any;

    beforeEach(() => {
      // Reset mocks
      jest.clearAllMocks();

      // Setup mock objects
      mockPage = {
        goto: jest.fn().mockResolvedValue(undefined),
        evaluate: jest.fn().mockResolvedValue({
          screen: { width: 1920, height: 1080 },
          navigator: { userAgent: 'test-agent' },
          videoCard: { renderer: 'test-renderer', vendor: 'test-vendor' }
        })
      };

      mockContext = {
        newPage: jest.fn().mockResolvedValue(mockPage)
      };

      mockBrowser = {
        newContext: jest.fn().mockResolvedValue(mockContext),
        close: jest.fn().mockResolvedValue(undefined)
      };

    const { chromium } = require('playwright');
      chromium.launch.mockResolvedValue(mockBrowser);
    });

  test('should generate fingerprint successfully', async () => {
    const generator = new BrowserFingerprintGenerator();
      
    const result = await generator.generateFingerprint();
      
    expect(result).toBeInstanceOf(FingerprintFormat);
    expect(mockBrowser.close).toHaveBeenCalled();
    });

  test('should generate fingerprint with headless mode', async () => {
    const generator = new BrowserFingerprintGenerator({ headless: true });
      
    const result = await generator.generateFingerprint();
      
    expect(result).toBeInstanceOf(FingerprintFormat);
    const { chromium } = require('playwright');
    expect(chromium.launch).toHaveBeenCalled();
    const callArgs = chromium.launch.mock.calls[0][0];
    expect(callArgs.headless).toBe(true);
    });

  test('should generate fingerprint without chrome channel', async () => {
    const generator = new BrowserFingerprintGenerator({ useChromeChannel: false });
      
    const result = await generator.generateFingerprint();
      
    expect(result).toBeInstanceOf(FingerprintFormat);
    const { chromium } = require('playwright');
    const callArgs = chromium.launch.mock.calls[0][0];
    expect(callArgs.channel).toBeUndefined();
    });

  test('should handle browser launch error', async () => {
    const { chromium } = require('playwright');
      chromium.launch.mockRejectedValue(new Error('Browser launch failed'));
      
    const generator = new BrowserFingerprintGenerator();
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
    const result = await generator.generateFingerprint();
      
    expect(result).toBeNull();
    expect(consoleSpy).toHaveBeenCalled();
    const errorMessage = consoleSpy.mock.calls[0][0];
    expect(errorMessage).toContain('Error generating fingerprint');
      
      consoleSpy.mockRestore();
    });

  test('should handle page evaluation error', async () => {
      mockPage.evaluate.mockRejectedValue(new Error('Evaluation failed'));
      
    const generator = new BrowserFingerprintGenerator();
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
    const result = await generator.generateFingerprint();
      
    expect(result).toBeNull();
    expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });
  });

  describe('generateFingerprintToFile', () => {
    let generator: BrowserFingerprintGenerator;
    let mockFingerprintFormat: FingerprintFormat;

    beforeEach(() => {
      generator = new BrowserFingerprintGenerator();
      
      // Mock FingerprintFormat
      mockFingerprintFormat = {
        toJson: jest.fn().mockReturnValue('{"test": "data"}')
      } as any;

      // Mock generateFingerprint method
      jest.spyOn(generator, 'generateFingerprint').mockResolvedValue(mockFingerprintFormat);
      
      // Mock fs
    const fs = require('fs');
      fs.writeFileSync.mockImplementation(() => {});
    });

  test('should generate fingerprint to file successfully', async () => {
    const result = await generator.generateFingerprintToFile('test-output.json');
      
    expect(result).toBe(true);
    expect(generator.generateFingerprint).toHaveBeenCalled();
    expect(mockFingerprintFormat.toJson).toHaveBeenCalledWith(2);
      
    const fs = require('fs');
    expect(fs.writeFileSync).toHaveBeenCalledWith(
        'test-output.json',
        '{"test": "data"}',
        'utf8'
      );
    });

  test('should use default filename when not provided', async () => {
    const result = await generator.generateFingerprintToFile();
      
    expect(result).toBe(true);
      
    const fs = require('fs');
    expect(fs.writeFileSync).toHaveBeenCalledWith(
        'fingerprint_output.json',
        '{"test": "data"}',
        'utf8'
      );
    });

  test('should handle fingerprint generation failure', async () => {
      jest.spyOn(generator, 'generateFingerprint').mockResolvedValue(null);
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
    const result = await generator.generateFingerprintToFile('test.json');
      
    expect(result).toBe(false);
    expect(consoleSpy).toHaveBeenCalledWith('Failed to generate fingerprint data');
      
      consoleSpy.mockRestore();
    });

  test('should handle file save error', async () => {
    const fs = require('fs');
      fs.writeFileSync.mockImplementation(() => {
        throw new Error('File write failed');
      });
      
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
    const result = await generator.generateFingerprintToFile('test.json');
      
    expect(result).toBe(false);
    expect(consoleSpy).toHaveBeenCalled();
    const errorMessage = consoleSpy.mock.calls[0][0];
    expect(errorMessage).toContain('Failed to save fingerprint data');
      
      consoleSpy.mockRestore();
    });

  test('should handle browser environment (no fs)', async () => {
      // Create a new generator to avoid interference from previous mocks
    const browserGenerator = new BrowserFingerprintGenerator();
      
      // Mock generateFingerprint to return a valid fingerprint
    const mockFingerprintFormat = {
        toJson: jest.fn().mockReturnValue('{"test": "data"}')
      } as any;
      jest.spyOn(browserGenerator, 'generateFingerprint').mockResolvedValue(mockFingerprintFormat);
      
      // Mock the private saveToFile method to simulate browser environment
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
      (browserGenerator as any).saveToFile = jest.fn().mockImplementation(() => {
        console.warn('File saving not supported in browser environment');
        return Promise.resolve(false);
      });
      
    const result = await browserGenerator.generateFingerprintToFile('test.json');
      
    expect(result).toBe(false);
    expect(consoleSpy).toHaveBeenCalledWith('File saving not supported in browser environment');
      
      consoleSpy.mockRestore();
    });
  });

  describe('Error Handling', () => {
  test('should handle unexpected errors gracefully', async () => {
    const generator = new BrowserFingerprintGenerator();
      
      // Mock an unexpected error in generateFingerprint
      jest.spyOn(generator, 'generateFingerprint').mockImplementation(() => {
        throw new Error('Unexpected error');
      });
      
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
    const result = await generator.generateFingerprintToFile();
      
    expect(result).toBe(false);
    expect(consoleSpy).toHaveBeenCalled();
      
      consoleSpy.mockRestore();
    });

  test('should handle console logging', async () => {
    const generator = new BrowserFingerprintGenerator();
    const consoleSpy = jest.spyOn(console, 'log').mockImplementation();
      
      // Mock successful generation
    const mockFingerprintFormat = {
        toJson: jest.fn().mockReturnValue('{"test": "data"}')
      } as any;
      
      jest.spyOn(generator, 'generateFingerprint').mockResolvedValue(mockFingerprintFormat);
      
    const fs = require('fs');
      fs.writeFileSync.mockImplementation(() => {});
      
      await generator.generateFingerprintToFile('test.json');
      
    expect(consoleSpy).toHaveBeenCalled();
    const logMessages = consoleSpy.mock.calls.map(call => call[0]);
    expect(logMessages.some(msg => msg.includes('Starting fingerprint generation'))).toBe(true);
    expect(logMessages.some(msg => msg.includes('Fingerprint generation completed successfully'))).toBe(true);
      
      consoleSpy.mockRestore();
    });
  });
});

describe('FingerprintFormat Unit Tests', () => {
  const sampleFingerprintData = {
    fingerprint: {
      screen: {
        availTop: 25,
        availLeft: 0,
        pageXOffset: 0,
        pageYOffset: 0,
        screenX: 0,
        hasHDR: false,
        width: 2560,
        height: 1440,
        availWidth: 2560,
        availHeight: 1345,
        clientWidth: 2560,
        clientHeight: 1258,
        innerWidth: 2560,
        innerHeight: 1258,
        outerWidth: 2560,
        outerHeight: 1345,
        colorDepth: 24,
        pixelDepth: 24,
        devicePixelRatio: 2
      },
      navigator: {
        userAgent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        userAgentData: null,
        language: "zh-CN",
        languages: ["zh-CN"],
        platform: "MacIntel",
        deviceMemory: 8,
        hardwareConcurrency: 8,
        maxTouchPoints: 0,
        product: "Gecko",
        productSub: "20030107",
        vendor: "Google Inc.",
        vendorSub: "",
        doNotTrack: null,
        appCodeName: "Mozilla",
        appName: "Netscape",
        appVersion: "5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        oscpu: null,
        extraProperties: {
          vendorFlavors: ["chrome"],
          isBluetoothSupported: true,
          globalPrivacyControl: null,
          pdfViewerEnabled: true,
          installedApps: []
        },
        webdriver: false
      },
      audioCodecs: {
        ogg: "probably",
        mp3: "probably",
        wav: "probably",
        m4a: "maybe",
        aac: "probably"
      },
      videoCodecs: {
        ogg: "",
        h264: "probably",
        webm: "probably"
      },
      pluginsData: {
        plugins: [],
        mimeTypes: []
      },
      battery: {
        charging: true,
        chargingTime: 0,
        dischargingTime: null,
        level: 1
      },
      videoCard: {
        renderer: "ANGLE (Apple, ANGLE Metal Renderer: Apple M1, Unspecified Version)",
        vendor: "Google Inc. (Apple)"
      },
      multimediaDevices: {
        speakers: [],
        micros: [],
        webcams: []
      },
      fonts: ["Arial", "Helvetica", "Times New Roman"],
      mockWebRTC: false,
      slim: false
    },
    headers: {
      "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
      "sec-ch-ua-mobile": "?0",
      "sec-ch-ua-platform": "\"macOS\"",
      "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
      "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    }
  };

  test('should create FingerprintFormat from dictionary', () => {
    const fingerprintFormat = FingerprintFormat.fromDict(sampleFingerprintData);
    
    expect(fingerprintFormat).toBeInstanceOf(FingerprintFormat);
    expect(fingerprintFormat.fingerprint).toBeDefined();
    expect(fingerprintFormat.headers).toBeDefined();
    expect(fingerprintFormat.fingerprint.screen.width).toBe(2560);
    expect(fingerprintFormat.fingerprint.navigator.userAgent).toContain('Chrome/142.0.0.0');
    expect(fingerprintFormat.headers['sec-ch-ua-platform']).toBe('"macOS"');
  });

  test('should create FingerprintFormat from JSON string', () => {
    const jsonString = JSON.stringify(sampleFingerprintData);
    const fingerprintFormat = FingerprintFormat.fromJson(jsonString);
      
    expect(fingerprintFormat).toBeInstanceOf(FingerprintFormat);
    expect(fingerprintFormat.fingerprint.screen.height).toBe(1440);
    expect(fingerprintFormat.fingerprint.navigator.platform).toBe('MacIntel');
    });

  test('should convert FingerprintFormat to JSON string', () => {
    const fingerprintFormat = FingerprintFormat.fromDict(sampleFingerprintData);
    const jsonString = fingerprintFormat.toJson();
      
    expect(typeof jsonString).toBe('string');
    const parsedData = JSON.parse(jsonString);
    expect(parsedData.fingerprint).toBeDefined();
    expect(parsedData.headers).toBeDefined();
    expect(parsedData.fingerprint.screen.width).toBe(2560);
    });

  test('should convert FingerprintFormat to JSON string with custom indent', () => {
    const fingerprintFormat = FingerprintFormat.fromDict(sampleFingerprintData);
    const jsonString = fingerprintFormat.toJson(4);
      
    expect(typeof jsonString).toBe('string');
    expect(jsonString).toContain('    '); // Should contain 4-space indentation
    });

  test('should load fingerprint from example file', () => {
      // Mock the file system to return the example fingerprint data
    const mockFs = fs as jest.Mocked<typeof fs>;
    const examplePath = path.join(__dirname, '../../../resource/fingerprint.example.json');
      mockFs.readFileSync.mockReturnValue(JSON.stringify(sampleFingerprintData));
      
      // Simulate loading from file
    const fileContent = mockFs.readFileSync(examplePath, 'utf8');
    const fingerprintFormat = FingerprintFormat.fromJson(fileContent);
      
    expect(fingerprintFormat).toBeInstanceOf(FingerprintFormat);
    expect(fingerprintFormat.fingerprint.screen.width).toBe(2560);
    expect(fingerprintFormat.fingerprint.navigator.deviceMemory).toBe(8);
    expect(fingerprintFormat.headers['sec-ch-ua-mobile']).toBe('?0');
      
      // Verify the file was read from the correct path
    expect(mockFs.readFileSync).toHaveBeenCalledWith(examplePath, 'utf8');
    });

  test('should handle malformed JSON gracefully', () => {
    const malformedJson = '{"fingerprint": {"screen": invalid json}';
      
    expect(() => {
        FingerprintFormat.fromJson(malformedJson);
      }).toThrow();
    });

  test('should handle missing fingerprint data', () => {
    const incompleteData = {
        headers: {
          "user-agent": "test-agent"
        }
      };
      
    const fingerprintFormat = FingerprintFormat.fromDict(incompleteData);
      
    expect(fingerprintFormat).toBeInstanceOf(FingerprintFormat);
    expect(fingerprintFormat.headers).toBeDefined();
    expect(fingerprintFormat.headers['user-agent']).toBe('test-agent');
    });

  test('should create FingerprintFormat using static create method', () => {
    const screen = {
        availTop: 0,
        availLeft: 0,
        pageXOffset: 0,
        pageYOffset: 0,
        screenX: 0,
        hasHDR: false,
        width: 1920,
        height: 1080,
        availWidth: 1920,
        availHeight: 1080,
        clientWidth: 1920,
        clientHeight: 1080,
        innerWidth: 1920,
        innerHeight: 1080,
        outerWidth: 1920,
        outerHeight: 1080,
        colorDepth: 24,
        pixelDepth: 24,
        devicePixelRatio: 1
      };

    const navigator = {
        userAgent: "Test User Agent",
        userAgentData: {
          brands: [{ brand: "Test Browser", version: "1.0" }],
          mobile: false,
          platform: "Win32",
          architecture: "x86",
          bitness: "64",
          fullVersionList: [{ brand: "Test Browser", version: "1.0.0" }],
          model: "",
          platformVersion: "10.0",
          uaFullVersion: "1.0.0"
        },
        language: "en-US",
        languages: ["en-US"],
        platform: "Win32",
        deviceMemory: 4,
        hardwareConcurrency: 4,
        maxTouchPoints: 0,
        product: "Gecko",
        productSub: "20030107",
        vendor: "Test Vendor",
        vendorSub: "",
        doNotTrack: "",
        appCodeName: "Mozilla",
        appName: "Netscape",
        appVersion: "5.0 Test",
        oscpu: "",
        extraProperties: {
          vendorFlavors: [],
          isBluetoothSupported: false,
          globalPrivacyControl: null,
          pdfViewerEnabled: false,
          installedApps: []
        },
        webdriver: ""
      };

    const videoCard = {
        renderer: "Test Renderer",
        vendor: "Test Vendor"
      };

    const headers = {
        "user-agent": "Test User Agent",
        "accept": "text/html"
      };

    const fingerprintFormat = FingerprintFormat.create(
        screen,
        navigator,
        videoCard,
        headers
      );

    expect(fingerprintFormat).toBeInstanceOf(FingerprintFormat);
    expect(fingerprintFormat.fingerprint.screen.width).toBe(1920);
    expect(fingerprintFormat.fingerprint.navigator.userAgent).toBe("Test User Agent");
    expect(fingerprintFormat.fingerprint.videoCard.renderer).toBe("Test Renderer");
    expect(fingerprintFormat.headers['user-agent']).toBe("Test User Agent");
  });
});