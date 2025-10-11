// @ts-nocheck - Suppress TypeScript errors for browser globals in page.evaluate contexts
import { chromium, Browser, BrowserContext, Page } from 'playwright';

/**
 * Screen fingerprint data structure.
 */
export interface ScreenFingerprint {
  availHeight: number;
  availWidth: number;
  availTop: number;
  availLeft: number;
  colorDepth: number;
  height: number;
  pixelDepth: number;
  width: number;
  devicePixelRatio: number;
  pageXOffset: number;
  pageYOffset: number;
  innerHeight: number;
  outerHeight: number;
  outerWidth: number;
  innerWidth: number;
  screenX: number;
  clientWidth: number;
  clientHeight: number;
  hasHDR: boolean;
}

/**
 * Brand information data structure.
 */
export interface Brand {
  brand: string;
  version: string;
}

/**
 * User agent data structure.
 */
export interface UserAgentData {
  brands: Brand[];
  mobile: boolean;
  platform: string;
  architecture: string;
  bitness: string;
  fullVersionList: Brand[];
  model: string;
  platformVersion: string;
  uaFullVersion: string;
}

/**
 * Navigator extra properties data structure.
 */
export interface ExtraProperties {
  vendorFlavors: string[];
  isBluetoothSupported: boolean;
  globalPrivacyControl?: any;
  pdfViewerEnabled: boolean;
  installedApps: any[];
}

/**
 * Navigator fingerprint data structure.
 */
export interface NavigatorFingerprint {
  userAgent: string;
  userAgentData: UserAgentData;
  doNotTrack: string;
  appCodeName: string;
  appName: string;
  appVersion: string;
  oscpu: string;
  webdriver: string;
  language: string;
  languages: string[];
  platform: string;
  deviceMemory?: number;
  hardwareConcurrency: number;
  product: string;
  productSub: string;
  vendor: string;
  vendorSub: string;
  maxTouchPoints?: number;
  extraProperties: ExtraProperties;
}

/**
 * Video card information data structure.
 */
export interface VideoCard {
  renderer: string;
  vendor: string;
}

/**
 * Main fingerprint data structure.
 */
export interface Fingerprint {
  screen: ScreenFingerprint;
  navigator: NavigatorFingerprint;
  videoCodecs: Record<string, string>;
  audioCodecs: Record<string, string>;
  pluginsData: Record<string, string>;
  battery?: Record<string, string>;
  videoCard: VideoCard;
  multimediaDevices: string[];
  fonts: string[];
  mockWebRTC: boolean;
  slim?: boolean;
}

/**
 * Complete fingerprint format including fingerprint data and headers.
 */
export class FingerprintFormat {
  public fingerprint: Fingerprint;
  public headers: Record<string, string>;

  constructor(fingerprint: Fingerprint, headers: Record<string, string>) {
    this.fingerprint = fingerprint;
    this.headers = headers;
  }

  /**
   * Convert to dictionary format.
   */
  toDict(): Record<string, any> {
    return {
      fingerprint: this.fingerprint,
      headers: this.headers
    };
  }

  /**
   * Convert to JSON string format.
   */
  toJson(indent: number = 2): string {
    return JSON.stringify(this.toDict(), null, indent);
  }

  /**
   * Create FingerprintFormat from dictionary data.
   */
  static fromDict(data: Record<string, any>): FingerprintFormat {
    if (!data || typeof data !== 'object') {
      throw new Error('Invalid data: expected an object');
    }

    const fingerprintDict = data.fingerprint || {};
    const headersDict = data.headers || {};

    // Convert nested objects to proper interfaces
    const screenDict = fingerprintDict.screen || {};
    const screen: ScreenFingerprint = {
      availHeight: screenDict.availHeight || 0,
      availWidth: screenDict.availWidth || 0,
      availTop: screenDict.availTop || 0,
      availLeft: screenDict.availLeft || 0,
      colorDepth: screenDict.colorDepth || 24,
      height: screenDict.height || 0,
      pixelDepth: screenDict.pixelDepth || 24,
      width: screenDict.width || 0,
      devicePixelRatio: screenDict.devicePixelRatio || 1,
      pageXOffset: screenDict.pageXOffset || 0,
      pageYOffset: screenDict.pageYOffset || 0,
      innerHeight: screenDict.innerHeight || 0,
      outerHeight: screenDict.outerHeight || 0,
      outerWidth: screenDict.outerWidth || 0,
      innerWidth: screenDict.innerWidth || 0,
      screenX: screenDict.screenX || 0,
      clientWidth: screenDict.clientWidth || 0,
      clientHeight: screenDict.clientHeight || 0,
      hasHDR: screenDict.hasHDR || false
    };

    // Handle UserAgentData - safely get navigator data
    const navDict = fingerprintDict.navigator || {};
    const userAgentDataDict = navDict.userAgentData || {};

    // Handle brands and fullVersionList safely
    const brandsData = userAgentDataDict.brands || [];
    const brands: Brand[] = [];
    if (Array.isArray(brandsData)) {
      for (const brandData of brandsData) {
        if (typeof brandData === 'object' && brandData !== null) {
          brands.push({
            brand: brandData.brand || '',
            version: brandData.version || ''
          });
        }
      }
    }

    const fullVersionListData = userAgentDataDict.fullVersionList || [];
    const fullVersionList: Brand[] = [];
    if (Array.isArray(fullVersionListData)) {
      for (const brandData of fullVersionListData) {
        if (typeof brandData === 'object' && brandData !== null) {
          fullVersionList.push({
            brand: brandData.brand || '',
            version: brandData.version || ''
          });
        }
      }
    }

    const userAgentData: UserAgentData = {
      brands: brands,
      mobile: userAgentDataDict.mobile || false,
      platform: userAgentDataDict.platform || '',
      architecture: userAgentDataDict.architecture || '',
      bitness: userAgentDataDict.bitness || '',
      fullVersionList: fullVersionList,
      model: userAgentDataDict.model || '',
      platformVersion: userAgentDataDict.platformVersion || '',
      uaFullVersion: userAgentDataDict.uaFullVersion || ''
    };

    // Handle ExtraProperties
    const extraPropsDict = navDict.extraProperties || {};
    const extraProps: ExtraProperties = {
      vendorFlavors: extraPropsDict.vendorFlavors || [],
      isBluetoothSupported: extraPropsDict.isBluetoothSupported || false,
      globalPrivacyControl: extraPropsDict.globalPrivacyControl,
      pdfViewerEnabled: extraPropsDict.pdfViewerEnabled !== false,
      installedApps: extraPropsDict.installedApps || []
    };

    // Create NavigatorFingerprint
    const navigator: NavigatorFingerprint = {
      userAgent: navDict.userAgent || '',
      userAgentData: userAgentData,
      doNotTrack: navDict.doNotTrack || '',
      appCodeName: navDict.appCodeName || '',
      appName: navDict.appName || '',
      appVersion: navDict.appVersion || '',
      oscpu: navDict.oscpu || '',
      webdriver: navDict.webdriver || '',
      language: navDict.language || '',
      languages: navDict.languages || [],
      platform: navDict.platform || '',
      deviceMemory: navDict.deviceMemory,
      hardwareConcurrency: navDict.hardwareConcurrency || 8,
      product: navDict.product || '',
      productSub: navDict.productSub || '',
      vendor: navDict.vendor || '',
      vendorSub: navDict.vendorSub || '',
      maxTouchPoints: navDict.maxTouchPoints,
      extraProperties: extraProps
    };

    // Create VideoCard
    const videoCardDict = fingerprintDict.videoCard || {};
    const videoCard: VideoCard = {
      renderer: videoCardDict.renderer || 'Unknown',
      vendor: videoCardDict.vendor || 'Unknown'
    };

    // Create main Fingerprint
    const fingerprint: Fingerprint = {
      screen: screen,
      navigator: navigator,
      videoCodecs: fingerprintDict.videoCodecs || {},
      audioCodecs: fingerprintDict.audioCodecs || {},
      pluginsData: fingerprintDict.pluginsData || {},
      battery: fingerprintDict.battery,
      videoCard: videoCard,
      multimediaDevices: fingerprintDict.multimediaDevices || [],
      fonts: fingerprintDict.fonts || [],
      mockWebRTC: fingerprintDict.mockWebRTC || false,
      slim: fingerprintDict.slim
    };

    return new FingerprintFormat(fingerprint, headersDict);
  }

  /**
   * Create FingerprintFormat from JSON string.
   */
  static fromJson(jsonStr: string): FingerprintFormat {
    const data = JSON.parse(jsonStr);
    return FingerprintFormat.fromDict(data);
  }

  /**
   * Create FingerprintFormat directly using component interfaces.
   */
  static create(
    screen: ScreenFingerprint,
    navigator: NavigatorFingerprint,
    videoCard: VideoCard,
    headers: Record<string, string>,
    videoCodecs?: Record<string, string>,
    audioCodecs?: Record<string, string>,
    pluginsData?: Record<string, string>,
    battery?: Record<string, string>,
    multimediaDevices?: string[],
    fonts?: string[],
    mockWebRTC: boolean = false,
    slim?: boolean
  ): FingerprintFormat {
    const fingerprint: Fingerprint = {
      screen: screen,
      navigator: navigator,
      videoCodecs: videoCodecs || {},
      audioCodecs: audioCodecs || {},
      pluginsData: pluginsData || {},
      battery: battery,
      videoCard: videoCard,
      multimediaDevices: multimediaDevices || [],
      fonts: fonts || [],
      mockWebRTC: mockWebRTC,
      slim: slim
    };

    return new FingerprintFormat(fingerprint, headers);
  }
}

/**
 * Browser fingerprint generator class.
 */
export class BrowserFingerprintGenerator {
  private headless: boolean;
  private useChromeChannel: boolean;

  constructor(options: { headless?: boolean; useChromeChannel?: boolean } = {}) {
    this.headless = options.headless ?? false;
    this.useChromeChannel = options.useChromeChannel ?? true;
  }

  /**
   * Extract comprehensive browser fingerprint using Playwright.
   */
  async generateFingerprint(): Promise<FingerprintFormat | null> {
    try {
      console.log('Starting fingerprint generation');

      const launchOptions: any = {
        headless: this.headless,
        args: ['--start-maximized']
      };

      if (this.useChromeChannel) {
        launchOptions.channel = 'chrome';
      }

      const browser = await chromium.launch(launchOptions);
      const context = await browser.newContext({ viewport: null });
      const page = await context.newPage();

      // Navigate to a test page to ensure proper loading
      await page.goto('about:blank');

      console.log('Extracting comprehensive browser fingerprint...');

      // Extract comprehensive fingerprint data
      const fingerprintData = await this.extractFingerprintData(page);

      // Get request headers
      const headersData = await this.extractHeadersData(page);

      await browser.close();

      // Combine fingerprint and headers using FingerprintFormat
      const fingerprintFormat = FingerprintFormat.fromDict({
        fingerprint: fingerprintData,
        headers: headersData
      });

      console.log('Fingerprint generation completed successfully!');
      return fingerprintFormat;

    } catch (error) {
      console.error(`Error generating fingerprint: ${error}`);
      return null;
    }
  }

  /**
   * Extract comprehensive browser fingerprint and save to file.
   */
  async generateFingerprintToFile(outputFilename: string = 'fingerprint_output.json'): Promise<boolean> {
    try {
      console.log(`Starting fingerprint generation, output file: ${outputFilename}`);

      // Generate fingerprint data (FingerprintFormat object)
      const fingerprintFormat = await this.generateFingerprint();

      if (fingerprintFormat === null) {
        console.error('Failed to generate fingerprint data');
        return false;
      }

      // Convert to JSON string and save to file
      const fingerprintJson = fingerprintFormat.toJson(2);
      const success = await this.saveToFile(fingerprintJson, outputFilename);

      if (success) {
        console.log(`Fingerprint generation completed successfully! Saved to ${outputFilename}`);
        return true;
      } else {
        console.error('Failed to save fingerprint data');
        return false;
      }

    } catch (error) {
      console.error(`Error generating fingerprint to file: ${error}`);
      return false;
    }
  }

  /**
   * Extract fingerprint data from the page.
   */
  private async extractFingerprintData(page: Page): Promise<any> {
    // Define the fingerprint extraction function as a string to avoid bundling issues
    const extractionFunction = `
      async function() {
        // Helper function to get audio codec support
        function getAudioCodecs() {
          const audio = document.createElement('audio');
          return {
            ogg: audio.canPlayType('audio/ogg; codecs="vorbis"') || '',
            mp3: audio.canPlayType('audio/mpeg') || '',
            wav: audio.canPlayType('audio/wav; codecs="1"') || '',
            m4a: audio.canPlayType('audio/x-m4a') || '',
            aac: audio.canPlayType('audio/aac') || ''
          };
        }

        // Helper function to get video codec support
        function getVideoCodecs() {
          const video = document.createElement('video');
          return {
            ogg: video.canPlayType('video/ogg; codecs="theora"') || '',
            h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') || '',
            webm: video.canPlayType('video/webm; codecs="vp8, vorbis"') || ''
          };
        }

        // Helper function to get plugins data
        function getPluginsData() {
          const plugins = [];
          const mimeTypes = [];

          for (let i = 0; i < navigator.plugins.length; i++) {
            const plugin = navigator.plugins[i];
            const pluginData = {
              name: plugin.name,
              description: plugin.description,
              filename: plugin.filename,
              mimeTypes: []
            };

            for (let j = 0; j < plugin.length; j++) {
              const mimeType = plugin[j];
              pluginData.mimeTypes.push({
                type: mimeType.type,
                suffixes: mimeType.suffixes,
                description: mimeType.description,
                enabledPlugin: plugin.name
              });

              mimeTypes.push(mimeType.description + '~~' + mimeType.type + '~~' + mimeType.suffixes);
            }

            plugins.push(pluginData);
          }

          return { plugins, mimeTypes };
        }

        // Helper function to get battery info
        async function getBatteryInfo() {
          try {
            if ('getBattery' in navigator) {
              const battery = await navigator.getBattery();
              return {
                charging: battery.charging,
                chargingTime: battery.chargingTime,
                dischargingTime: battery.dischargingTime,
                level: battery.level
              };
            }
          } catch (e) {
            console.log('Battery API not supported');
          }

          return {
            charging: true,
            chargingTime: 0,
            dischargingTime: null,
            level: 1
          };
        }

        // Helper function to get WebGL info
        function getWebGLInfo() {
          try {
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

            if (gl) {
              const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
              return {
                renderer: debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
                vendor: debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR)
              };
            }
          } catch (e) {
            console.log('WebGL not supported');
          }

          return {
            renderer: "Adreno (TM) 735",
            vendor: "Qualcomm"
          };
        }

        // Helper function to get multimedia devices
        async function getMultimediaDevices() {
          try {
            if ('mediaDevices' in navigator && 'enumerateDevices' in navigator.mediaDevices) {
              const devices = await navigator.mediaDevices.enumerateDevices();
              const speakers = [];
              const micros = [];
              const webcams = [];

              devices.forEach(function(device) {
                const deviceInfo = {
                  deviceId: device.deviceId || '',
                  kind: device.kind,
                  label: device.label || '',
                  groupId: device.groupId || ''
                };

                if (device.kind === 'audiooutput') {
                  speakers.push(deviceInfo);
                } else if (device.kind === 'audioinput') {
                  micros.push(deviceInfo);
                } else if (device.kind === 'videoinput') {
                  webcams.push(deviceInfo);
                }
              });

              return { speakers: speakers, micros: micros, webcams: webcams };
            }
          } catch (e) {
            console.log('Media devices not accessible');
          }

          return {
            speakers: [{ deviceId: '', kind: 'audiooutput', label: '', groupId: '' }],
            micros: [{ deviceId: '', kind: 'audioinput', label: '', groupId: '' }],
            webcams: []
          };
        }

        // Helper function to get available fonts
        function getFonts() {
          const testFonts = [
            'Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana',
            'Georgia', 'Palatino', 'Garamond', 'Bookman', 'Comic Sans MS',
            'Trebuchet MS', 'Arial Black', 'Impact'
          ];

          const availableFonts = [];
          const testString = 'mmmmmmmmmmlli';
          const testSize = '72px';
          const baseWidth = {};
          const baseHeight = {};

          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          if (!context) return availableFonts;

          const defaultFonts = ['monospace', 'sans-serif', 'serif'];
          defaultFonts.forEach(function(font) {
            context.font = testSize + ' ' + font;
            const metrics = context.measureText(testString);
            baseWidth[font] = metrics.width;
            baseHeight[font] = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;
          });

          testFonts.forEach(function(font) {
            let detected = false;
            defaultFonts.forEach(function(baseFont) {
              context.font = testSize + ' ' + font + ', ' + baseFont;
              const metrics = context.measureText(testString);
              const width = metrics.width;
              const height = metrics.actualBoundingBoxAscent + metrics.actualBoundingBoxDescent;

              if (width !== baseWidth[baseFont] || height !== baseHeight[baseFont]) {
                detected = true;
              }
            });

            if (detected) {
              availableFonts.push(font);
            }
          });

          return availableFonts;
        }

        // Get battery info
        const batteryInfo = await getBatteryInfo();

        // Get multimedia devices
        const multimediaDevices = await getMultimediaDevices();

        // Build the complete fingerprint object
        const fingerprint = {
          screen: {
            availTop: screen.availTop,
            availLeft: screen.availLeft,
            pageXOffset: window.pageXOffset,
            pageYOffset: window.pageYOffset,
            screenX: window.screenX,
            hasHDR: screen.colorDepth > 24,
            width: screen.width,
            height: screen.height,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight,
            clientWidth: document.documentElement.clientWidth,
            clientHeight: document.documentElement.clientHeight,
            innerWidth: window.innerWidth,
            innerHeight: window.innerHeight,
            outerWidth: window.outerWidth,
            outerHeight: window.outerHeight,
            colorDepth: screen.colorDepth,
            pixelDepth: screen.pixelDepth,
            devicePixelRatio: window.devicePixelRatio
          },
          navigator: {
            userAgent: navigator.userAgent,
            userAgentData: navigator.userAgentData ? {
              brands: navigator.userAgentData.brands || [],
              mobile: navigator.userAgentData.mobile || false,
              platform: navigator.userAgentData.platform || ''
            } : null,
            language: navigator.language,
            languages: navigator.languages || [],
            platform: navigator.platform,
            deviceMemory: navigator.deviceMemory || 8,
            hardwareConcurrency: navigator.hardwareConcurrency || 8,
            maxTouchPoints: navigator.maxTouchPoints || 0,
            product: navigator.product,
            productSub: navigator.productSub,
            vendor: navigator.vendor,
            vendorSub: navigator.vendorSub,
            doNotTrack: navigator.doNotTrack,
            appCodeName: navigator.appCodeName,
            appName: navigator.appName,
            appVersion: navigator.appVersion,
            oscpu: navigator.oscpu,
            extraProperties: {
              vendorFlavors: ['chrome'],
              globalPrivacyControl: navigator.globalPrivacyControl || null,
              pdfViewerEnabled: navigator.pdfViewerEnabled || true,
              installedApps: []
            },
            webdriver: false
          },
          audioCodecs: getAudioCodecs(),
          videoCodecs: getVideoCodecs(),
          pluginsData: getPluginsData(),
          battery: batteryInfo,
          videoCard: getWebGLInfo(),
          multimediaDevices: multimediaDevices,
          fonts: getFonts(),
          mockWebRTC: false,
          slim: false
        };

        return fingerprint;
      }
    `;

    return await page.evaluate(extractionFunction);
  }

  /**
   * Extract headers data from httpbin.
   */
  private async extractHeadersData(page: Page): Promise<Record<string, string>> {
    try {
      console.log('Getting request headers...');
      await page.goto('https://httpbin.org/headers', { waitUntil: 'networkidle' });

      // Extract headers from the response
      const allHeaders = await page.evaluate(() => {
        try {
          const preElement = document.querySelector('pre');
          if (preElement) {
            const data = JSON.parse(preElement.textContent || '{}');
            return data.headers || {};
          }
        } catch (e) {
          console.log('Failed to parse headers:', e);
        }
        return {};
      });

      // Filter only the key headers from the example
      const keyHeaders = [
        'sec-ch-ua',
        'sec-ch-ua-mobile',
        'sec-ch-ua-platform',
        'upgrade-insecure-requests',
        'user-agent',
        'accept',
        'sec-fetch-site',
        'sec-fetch-mode',
        'sec-fetch-user',
        'sec-fetch-dest',
        'accept-encoding',
        'accept-language'
      ];

      const headersData: Record<string, string> = {};
      // Convert all_headers keys to lowercase for case-insensitive matching
      const allHeadersLower: Record<string, string> = {};
      for (const [key, value] of Object.entries(allHeaders)) {
        allHeadersLower[key.toLowerCase()] = value as string;
      }

      for (const header of keyHeaders) {
        const headerLower = header.toLowerCase();
        if (headerLower in allHeadersLower) {
          headersData[header] = allHeadersLower[headerLower];
        }
      }

      return headersData;

    } catch (error) {
      console.warn(`Failed to extract headers: ${error}`);
      return {};
    }
  }

  /**
   * Save JSON string data to a file.
   */
  private async saveToFile(jsonData: string, filename: string): Promise<boolean> {
    try {
      // In Node.js environment
      if (typeof require !== 'undefined') {
        const fs = require('fs');
        fs.writeFileSync(filename, jsonData, 'utf8');
        console.log(`Fingerprint data saved to ${filename}`);
        return true;
      } else {
        // In browser environment, we can't save files directly
        console.warn('File saving not supported in browser environment');
        return false;
      }
    } catch (error) {
      console.error(`Failed to save fingerprint data: ${error}`);
      return false;
    }
  }
}
