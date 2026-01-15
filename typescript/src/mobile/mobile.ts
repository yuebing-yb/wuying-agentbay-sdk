/**
 * Mobile module for mobile UI automation.
 * Provides touch, input, and app management operations for mobile environments.
 */

import { OperationResult } from "../types/api-response";
import { MobileExtraConfig } from "../types/extra-configs";
import { log, logError } from "../utils/logger";
import { getMobileCommandTemplate, replaceTemplatePlaceholders } from "../command/command-templates";

export interface BoolResult extends OperationResult {
  data?: boolean;
}

export interface UIBounds {
  left: number;
  top: number;
  right: number;
  bottom: number;
}

export interface UIElement {
  text: string;
  className: string;
  bounds: UIBounds | string;  // Can be either object or string format "left,top,right,bottom"
}

export interface UIElementsResult extends OperationResult {
  elements: UIElement[];
  raw: string;
  format: 'json' | 'xml';
}

export interface InstalledApp {
  name: string;
  startCmd: string;
  workDirectory: string;
}

export interface InstalledAppsResult extends OperationResult {
  apps: InstalledApp[];
}

export interface Process {
  pid: number;
  pname: string;
}

export interface ProcessResult extends OperationResult {
  processes: Process[];
}

export interface ScreenshotResult extends OperationResult {
  data: string; // Screenshot URL
}

export interface BetaScreenshotResult extends OperationResult {
  data: Uint8Array;
  format: string;
}

export interface AdbUrlResult extends OperationResult {
  data?: string; // ADB connection URL (e.g., "adb connect xx.xx.xx.xx:xxxxx")
  url?: string; // Alternative field name for compatibility
}

// Session interface for Mobile module
interface MobileSession {
  callMcpTool(
    toolName: string,
    args: Record<string, any>,
    autoGenSession?: boolean
  ): Promise<any>;
  sessionId: string;
  getAPIKey(): string;
  getAgentBay(): any;
  imageId?: string;
  getLink(protocolType?: string, port?: number, options?: string): Promise<any>;
}

/**
 * Parse bounds string format "left,top,right,bottom" to UIBounds object
 */
function parseBoundsString(boundsStr: string): UIBounds | null {
  const parts = boundsStr.split(',');
  if (parts.length !== 4) {
    return null;
  }

  const [left, top, right, bottom] = parts.map(p => parseInt(p.trim(), 10));
  if (isNaN(left) || isNaN(top) || isNaN(right) || isNaN(bottom)) {
    return null;
  }

  return { left, top, right, bottom };
}

/**
 * Normalize UIElement bounds field from string to object format if needed
 */
function normalizeUIElement(element: any): UIElement {
  if (element.bounds && typeof element.bounds === 'string') {
    const parsedBounds = parseBoundsString(element.bounds);
    if (parsedBounds) {
      element.bounds = parsedBounds;
    }
  }

  // Recursively normalize children if present
  if (element.children && Array.isArray(element.children)) {
    element.children = element.children.map(normalizeUIElement);
  }

  return element;
}

const PNG_MAGIC = new Uint8Array([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const JPEG_MAGIC = new Uint8Array([0xff, 0xd8, 0xff]);

function normalizeImageFormat(format: string, defaultValue: string): string {
  const f = String(format || "").trim().toLowerCase();
  if (!f) {
    return defaultValue;
  }
  if (f === "jpg") {
    return "jpeg";
  }
  return f;
}

function validateBase64String(base64String: string): void {
  const s = String(base64String || "");
  if (!s) {
    throw new Error("Empty base64 string");
  }

  const base64WithoutPadding = s.replace(/=+$/, "");
  if (!/^[A-Za-z0-9+/]+$/.test(base64WithoutPadding)) {
    throw new Error("Invalid base64 string format");
  }

  if (s.length % 4 !== 0) {
    throw new Error("Invalid base64 string length");
  }

  const paddingMatch = s.match(/=+$/);
  if (paddingMatch && paddingMatch[0].length > 2) {
    throw new Error("Invalid base64 padding format");
  }
}

function base64ToUint8ArrayStrict(input: string): Uint8Array {
  const s = String(input || "").trim();
  validateBase64String(s);

  if (typeof Buffer !== "undefined") {
    return new Uint8Array(Buffer.from(s, "base64"));
  }

  const binary = atob(s);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    out[i] = binary.charCodeAt(i);
  }
  return out;
}

function startsWithMagic(bytes: Uint8Array, magic: Uint8Array): boolean {
  if (bytes.length < magic.length) {
    return false;
  }
  for (let i = 0; i < magic.length; i++) {
    if (bytes[i] !== magic[i]) {
      return false;
    }
  }
  return true;
}

function detectImageFormat(bytes: Uint8Array): string {
  if (startsWithMagic(bytes, PNG_MAGIC)) {
    return "png";
  }
  if (startsWithMagic(bytes, JPEG_MAGIC)) {
    return "jpeg";
  }
  return "";
}

function decodeBase64Image(input: string, expectedFormat: string): { bytes: Uint8Array; format: string } {
  const s = String(input || "").trim();
  if (!s) {
    throw new Error("Empty image data");
  }
  if (!s.startsWith("{")) {
    throw new Error("Screenshot tool returned non-JSON data");
  }

  let obj: any;
  try {
    obj = JSON.parse(s);
  } catch (e) {
    throw new Error(`Invalid screenshot JSON: ${e instanceof Error ? e.message : String(e)}`);
  }
  if (!obj || typeof obj !== "object" || Array.isArray(obj)) {
    throw new Error("Invalid screenshot JSON: expected object");
  }
  const b64 = (obj as any).data;
  if (typeof b64 !== "string" || !b64.trim()) {
    throw new Error("Screenshot JSON missing base64 field");
  }

  const bytes = base64ToUint8ArrayStrict(b64);
  const detected = detectImageFormat(bytes);
  return { bytes, format: detected || expectedFormat };
}

export class Mobile {
  private session: MobileSession;

  constructor(session: MobileSession) {
    this.session = session;
  }


  /**
   * Tap at specified coordinates on the mobile screen.
   *
   * @param x - X coordinate for the tap
   * @param y - Y coordinate for the tap
   * @returns Promise resolving to BoolResult with success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const tapResult = await result.session.mobile.tap(100, 100);
   *   console.log('Tap success:', tapResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async tap(x: number, y: number): Promise<BoolResult> {
    const args = { x, y };
    try {
      const result = await this.session.callMcpTool('tap', args, false);
      return {
        success: result.success || false,
        requestId: result.requestId || '',
        errorMessage: result.errorMessage || '',
        data: result.success || false
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to tap: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Swipe from one position to another on the mobile screen.
   *
   * @param startX - Starting X coordinate
   * @param startY - Starting Y coordinate
   * @param endX - Ending X coordinate
   * @param endY - Ending Y coordinate
   * @param durationMs - Swipe duration in milliseconds. Default is 300
   * @returns Promise resolving to BoolResult with success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const swipeResult = await result.session.mobile.swipe(200, 400, 200, 100, 300);
   *   console.log('Swipe success:', swipeResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async swipe(startX: number, startY: number, endX: number, endY: number, durationMs = 300): Promise<BoolResult> {
    const args = { start_x: startX, start_y: startY, end_x: endX, end_y: endY, duration_ms: durationMs };
    try {
      const result = await this.session.callMcpTool('swipe', args, false);
      return {
        success: result.success || false,
        requestId: result.requestId || '',
        errorMessage: result.errorMessage || '',
        data: result.success || false
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to swipe: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Input text at the current focus position.
   *
   * @param text - Text to input
   * @returns Promise resolving to BoolResult with success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const inputResult = await result.session.mobile.inputText('Hello Mobile');
   *   console.log('Text input successfully:', inputResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async inputText(text: string): Promise<BoolResult> {
    const args = { text };
    try {
      const result = await this.session.callMcpTool('input_text', args, false);
      return {
        success: result.success || false,
        requestId: result.requestId || '',
        errorMessage: result.errorMessage || '',
        data: result.success || false
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to input text: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Send Android key code.
   *
   * @param key - Android key code (e.g., 4 for BACK, 3 for HOME, 24 for VOLUME_UP)
   * @returns Promise resolving to BoolResult with success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const keyResult = await result.session.mobile.sendKey(4);
   *   console.log('BACK key sent:', keyResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async sendKey(key: number): Promise<BoolResult> {
    const args = { key };
    try {
      const result = await this.session.callMcpTool('send_key', args, false);
      return {
        success: result.success || false,
        requestId: result.requestId || '',
        errorMessage: result.errorMessage || '',
        data: result.success || false
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to send key: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Get clickable UI elements.
   */
  async getClickableUIElements(timeoutMs = 5000): Promise<UIElementsResult> {
    const args = { timeout_ms: timeoutMs };
    try {
      const result = await this.session.callMcpTool('get_clickable_ui_elements', args, false);

      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to get clickable UI elements',
          elements: [],
          raw: result.data || '',
          format: 'json'
        };
      }

      if (!result.data) {
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          elements: [],
          raw: '',
          format: 'json'
        };
      }

      try {
        const elements = JSON.parse(result.data);
        // Normalize bounds from string to object format if needed
        const normalizedElements = (elements || []).map(normalizeUIElement);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          elements: normalizedElements,
          raw: result.data || '',
          format: 'json'
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse UI elements: ${parseError}`,
          elements: [],
          raw: result.data || '',
          format: 'json'
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to get clickable UI elements: ${error instanceof Error ? error.message : String(error)}`,
        elements: [],
        raw: '',
        format: 'json'
      };
    }
  }

  /**
   * Get all UI elements.
   */
  async getAllUIElements(timeoutMs = 3000, format: 'json' | 'xml' = 'json'): Promise<UIElementsResult> {
    const formatNorm = ((format || 'json') as string).trim().toLowerCase() || 'json';
    const args = { timeout_ms: timeoutMs, format: formatNorm };
    try {
      const result = await this.session.callMcpTool('get_all_ui_elements', args, false);

      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to get all UI elements',
          elements: [],
          raw: result.data || '',
          format: (formatNorm === 'xml' ? 'xml' : 'json')
        };
      }

      if (!result.data) {
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          elements: [],
          raw: '',
          format: (formatNorm === 'xml' ? 'xml' : 'json')
        };
      }

      if (formatNorm === 'xml') {
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          elements: [],
          raw: result.data || '',
          format: 'xml'
        };
      }

      if (formatNorm !== 'json') {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Unsupported UI elements format: ${JSON.stringify(format)}. Supported values: "json", "xml".`,
          elements: [],
          raw: result.data || '',
          format: 'json'
        };
      }

      try {
        const elements = JSON.parse(result.data);
        // Normalize bounds from string to object format if needed
        const normalizedElements = (elements || []).map(normalizeUIElement);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          elements: normalizedElements,
          raw: result.data || '',
          format: 'json'
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse UI elements: ${parseError}`,
          elements: [],
          raw: result.data || '',
          format: 'json'
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to get all UI elements: ${error instanceof Error ? error.message : String(error)}`,
        elements: [],
        raw: '',
        format: (formatNorm === 'xml' ? 'xml' : 'json')
      };
    }
  }

  /**
   * Get installed apps.
   */
  async getInstalledApps(startMenu = false, desktop = true, ignoreSystemApps = true): Promise<InstalledAppsResult> {
    const args = { start_menu: startMenu, desktop, ignore_system_apps: ignoreSystemApps };
    try {
      const result = await this.session.callMcpTool('get_installed_apps', args, false);
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to get installed apps',
          apps: []
        };
      }

      if (!result.data) {
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          apps: []
        };
      }

      try {
        const apps = JSON.parse(result.data);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          apps: apps || []
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse installed apps: ${parseError}`,
          apps: []
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to get installed apps: ${error instanceof Error ? error.message : String(error)}`,
        apps: []
      };
    }
  }

  /**
   * Start an app.
   *
   * @param startCmd - Start command using "monkey -p" format (e.g., 'monkey -p com.android.settings')
   * @param workDirectory - Optional working directory for the app
   * @param activity - Optional activity name to launch
   * @returns Promise resolving to ProcessResult containing launched process information
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const startResult = await result.session.mobile.startApp('monkey -p com.android.settings');
   *   console.log('App started:', startResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async startApp(startCmd: string, workDirectory = '', activity = ''): Promise<ProcessResult> {
    const args = { start_cmd: startCmd, work_directory: workDirectory, activity };
    try {
      const result = await this.session.callMcpTool('start_app', args, false);
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to start app',
          processes: []
        };
      }

      if (!result.data) {
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          processes: []
        };
      }

      try {
        const processes = JSON.parse(result.data);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          processes: processes || []
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse process result: ${parseError}`,
          processes: []
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to start app: ${error instanceof Error ? error.message : String(error)}`,
        processes: []
      };
    }
  }

  /**
   * Stop app by command.
   *
   * @param stopCmd - Package name of the app to stop (e.g., 'com.android.settings')
   * @returns Promise resolving to BoolResult with success status
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   await result.session.mobile.startApp('monkey -p com.android.settings');
   *   const stopResult = await result.session.mobile.stopAppByCmd('com.android.settings');
   *   console.log('App stopped:', stopResult.success);
   *   await result.session.delete();
   * }
   * ```
   */
  async stopAppByCmd(stopCmd: string): Promise<BoolResult> {
    const args = { stop_cmd: stopCmd };
    try {
      const result = await this.session.callMcpTool('stop_app_by_cmd', args, false);
      return {
        success: result.success || false,
        requestId: result.requestId || '',
        errorMessage: result.errorMessage || '',
        data: result.success || false
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to stop app: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Take a screenshot of the current mobile screen.
   *
   * @returns Promise resolving to ScreenshotResult containing screenshot URL
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const screenshotResult = await result.session.mobile.screenshot();
   *   console.log('Screenshot URL:', screenshotResult.data);
   *   await result.session.delete();
   * }
   * ```
   */
  async screenshot(): Promise<ScreenshotResult> {
    try {
      const result = await this.session.callMcpTool('system_screenshot', {}, false);
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to take screenshot',
          data: ''
        };
      }

      return {
        success: true,
        requestId: result.requestId || '',
        errorMessage: '',
        data: result.data || ''
      };
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to take screenshot: ${error instanceof Error ? error.message : String(error)}`,
        data: ''
      };
    }
  }

  /**
   * Capture the current screen as a PNG image and return raw image bytes.
   *
   * @returns Promise resolving to BetaScreenshotResult containing PNG bytes
   */
  async betaTakeScreenshot(): Promise<BetaScreenshotResult> {
    try {
      const result = await this.session.callMcpTool("screenshot", { format: "png" }, false);
      const requestId = result.requestId || "";
      if (!result.success) {
        return {
          success: false,
          requestId,
          errorMessage: result.errorMessage || "Failed to take screenshot",
          data: new Uint8Array(),
          format: "png",
        };
      }
      const decoded = decodeBase64Image(String(result.data || ""), "png");
      return {
        success: true,
        requestId,
        errorMessage: "",
        data: decoded.bytes,
        format: decoded.format || "png",
      };
    } catch (error) {
      return {
        success: false,
        requestId: "",
        errorMessage: `Failed to take screenshot: ${error instanceof Error ? error.message : String(error)}`,
        data: new Uint8Array(),
        format: "png",
      };
    }
  }

  /**
   * Capture a long screenshot and return raw image bytes.
   *
   * @param maxScreens - Number of screens to stitch (range: [2, 10])
   * @param format - Output image format ("png", "jpeg", or "jpg"). Default is "png"
   * @param quality - JPEG quality (range: [1, 100])
   */
  async betaTakeLongScreenshot(
    maxScreens = 4,
    format: string = "png",
    quality?: number
  ): Promise<BetaScreenshotResult> {
    const formatNorm = normalizeImageFormat(format, "png");
    if (!Number.isInteger(maxScreens) || maxScreens < 2 || maxScreens > 10) {
      return {
        success: false,
        requestId: "",
        errorMessage: "Invalid maxScreens: must be an integer in the range [2, 10]",
        data: new Uint8Array(),
        format: formatNorm,
      };
    }
    if (formatNorm !== "png" && formatNorm !== "jpeg") {
      return {
        success: false,
        requestId: "",
        errorMessage: `Unsupported format: ${JSON.stringify(format)}. Supported values: "png", "jpeg".`,
        data: new Uint8Array(),
        format: formatNorm,
      };
    }
    if (quality !== undefined) {
      if (!Number.isInteger(quality) || quality < 1 || quality > 100) {
        return {
          success: false,
          requestId: "",
          errorMessage: "Invalid quality: must be an integer in the range [1, 100]",
          data: new Uint8Array(),
          format: formatNorm,
        };
      }
    }

    try {
      const args: Record<string, any> = {
        max_screens: maxScreens,
        format: formatNorm,
      };
      if (quality !== undefined) {
        args.quality = quality;
      }

      const result = await this.session.callMcpTool("long_screenshot", args, false);
      const requestId = result.requestId || "";
      if (!result.success) {
        return {
          success: false,
          requestId,
          errorMessage: result.errorMessage || "Failed to take long screenshot",
          data: new Uint8Array(),
          format: formatNorm,
        };
      }

      const decoded = decodeBase64Image(String(result.data || ""), formatNorm);
      return {
        success: true,
        requestId,
        errorMessage: "",
        data: decoded.bytes,
        format: decoded.format || formatNorm,
      };
    } catch (error) {
      return {
        success: false,
        requestId: "",
        errorMessage: `Failed to take long screenshot: ${error instanceof Error ? error.message : String(error)}`,
        data: new Uint8Array(),
        format: formatNorm,
      };
    }
  }

  /**
   * Retrieves the ADB connection URL for the mobile environment.
   * This method is only supported in mobile environments (mobile_latest image).
   * It uses the provided ADB public key to establish the connection and returns
   * the ADB connect URL.
   * 
   * @param adbkeyPub - ADB public key for authentication
   * @returns AdbUrlResult containing the ADB connection URL
   */
  async getAdbUrl(adbkeyPub: string): Promise<AdbUrlResult> {
    try {
      // Build options JSON with adbkey_pub
      const optionsJson = JSON.stringify({ adbkey_pub: adbkeyPub });

      // Call get_adb_link API
      const { GetAdbLinkRequest } = await import('../api/models/model');
      const request = new GetAdbLinkRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.sessionId,
        option: optionsJson
      });

      const response = await this.session.getAgentBay().getClient().getAdbLink(request);

      // Check response
      if (response.body && response.body.success && response.body.data) {
        const adbUrl = response.body.data.url;
        const requestId = response.body.requestId || '';
        log(`✅ get_adb_url completed successfully. RequestID: ${requestId}`);
        return {
          success: true,
          requestId: requestId,
          errorMessage: '',
          data: adbUrl,
          url: adbUrl
        };
      } else {
        const errorMsg = response.body?.message || 'Unknown error';
        const requestId = response.body?.requestId || '';
        logError(`❌ Failed to get ADB URL: ${errorMsg}`);
        return {
          success: false,
          requestId: requestId,
          errorMessage: errorMsg,
          data: undefined,
          url: undefined
        };
      }
    } catch (error) {
      const errorMsg = `Failed to get ADB URL: ${error instanceof Error ? error.message : String(error)}`;
      logError(`❌ ${errorMsg}`);
      return {
        success: false,
        requestId: '',
        errorMessage: errorMsg,
        data: undefined,
        url: undefined
      };
    }
  }

  /**
   * Configure mobile device settings based on MobileExtraConfig.
   * This method applies various mobile configuration settings including
   * resolution lock and app access management.
   * 
   * @param config - The mobile configuration to apply
   * @returns OperationResult indicating success or failure
   */
  async configure(config: MobileExtraConfig): Promise<OperationResult> {
    try {
      if (!config) {
        return {
          success: false,
          requestId: '',
          errorMessage: 'No mobile configuration provided'
        };
      }

      // Configure resolution lock
      const resolutionResult = await this.setResolutionLock(config.lockResolution);
      if (!resolutionResult.success) {
        return {
          success: false,
          requestId: resolutionResult.requestId,
          errorMessage: `Failed to set resolution lock: ${resolutionResult.errorMessage}`
        };
      }

      // Configure app management rules
      if (config.appManagerRule && config.appManagerRule.ruleType) {
        const appRule = config.appManagerRule;
        const packageNames = appRule.appPackageNameList;

        if (packageNames && packageNames.length > 0 && 
            (appRule.ruleType === "White" || appRule.ruleType === "Black")) {
          
          let appResult: OperationResult;
          if (appRule.ruleType === "White") {
            appResult = await this.setAppWhitelist(packageNames);
          } else {
            appResult = await this.setAppBlacklist(packageNames);
          }

          if (!appResult.success) {
            return {
              success: false,
              requestId: appResult.requestId,
              errorMessage: `Failed to set app ${appRule.ruleType.toLowerCase()}list: ${appResult.errorMessage}`
            };
          }
        } else if (packageNames && packageNames.length === 0) {
          return {
            success: false,
            requestId: '',
            errorMessage: `No package names provided for ${appRule.ruleType} list`
          };
        }
      }

      // Configure navigation bar visibility
      if (config.hideNavigationBar !== undefined) {
        const navResult = await this.setNavigationBarVisibility(config.hideNavigationBar);
        if (!navResult.success) {
          return {
            success: false,
            requestId: navResult.requestId,
            errorMessage: `Failed to set navigation bar visibility: ${navResult.errorMessage}`
          };
        }
      }

      // Configure uninstall blacklist
      if (config.uninstallBlacklist && config.uninstallBlacklist.length > 0) {
        const uninstallResult = await this.setUninstallBlacklist(config.uninstallBlacklist);
        if (!uninstallResult.success) {
          return {
            success: false,
            requestId: uninstallResult.requestId,
            errorMessage: `Failed to set uninstall blacklist: ${uninstallResult.errorMessage}`
          };
        }
      }

      log("Mobile configuration applied successfully");
      return {
        success: true,
        requestId: '',
        errorMessage: ''
      };
    } catch (error) {
      const errorMsg = `Failed to configure mobile: ${error instanceof Error ? error.message : String(error)}`;
      logError(errorMsg);
      return {
        success: false,
        requestId: '',
        errorMessage: errorMsg
      };
    }
  }

  /**
   * Set display resolution lock for mobile devices.
   * 
   * @param enable - Whether to enable resolution lock
   * @returns OperationResult indicating success or failure
   */
  async setResolutionLock(enable: boolean): Promise<OperationResult> {
    try {
      const templateName = enable ? "resolution_lock_enable" : "resolution_lock_disable";
      const template = getMobileCommandTemplate(templateName);
      
      if (!template) {
        return {
          success: false,
          requestId: '',
          errorMessage: `Resolution lock template not found: ${templateName}`
        };
      }

      const description = `Resolution lock ${enable ? 'enable' : 'disable'}`;
      return await this.executeCommand(template, description);
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to set resolution lock: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Set app whitelist configuration.
   * 
   * @param packageNames - List of package names to whitelist
   * @returns OperationResult indicating success or failure
   */
  async setAppWhitelist(packageNames: string[]): Promise<OperationResult> {
    try {
      const template = getMobileCommandTemplate("app_whitelist");
      if (!template) {
        return {
          success: false,
          requestId: '',
          errorMessage: "App whitelist template not found"
        };
      }

      // Replace placeholder with actual package names (newline-separated for file content)
      const packageList = packageNames.join('\n');
      const command = replaceTemplatePlaceholders(template, { package_list: packageList });
      
      const description = `App whitelist configuration (${packageNames.length} packages)`;
      return await this.executeCommand(command, description);
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to set app whitelist: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Set app blacklist configuration.
   * 
   * @param packageNames - List of package names to blacklist
   * @returns OperationResult indicating success or failure
   */
  async setAppBlacklist(packageNames: string[]): Promise<OperationResult> {
    try {
      const template = getMobileCommandTemplate("app_blacklist");
      if (!template) {
        return {
          success: false,
          requestId: '',
          errorMessage: "App blacklist template not found"
        };
      }

      // Replace placeholder with actual package names (newline-separated for file content)
      const packageList = packageNames.join('\n');
      const command = replaceTemplatePlaceholders(template, { package_list: packageList });
      
      const description = `App blacklist configuration (${packageNames.length} packages)`;
      return await this.executeCommand(command, description);
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to set app blacklist: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Set navigation bar visibility for mobile devices.
   * 
   * @param hide - True to hide navigation bar, false to show navigation bar
   * @returns OperationResult indicating success or failure
   */
  async setNavigationBarVisibility(hide: boolean): Promise<OperationResult> {
    try {
      const templateName = hide ? "hide_navigation_bar" : "show_navigation_bar";
      const template = getMobileCommandTemplate(templateName);
      
      if (!template) {
        return {
          success: false,
          requestId: '',
          errorMessage: `Navigation bar template not found: ${templateName}`
        };
      }

      const description = `Navigation bar visibility (hide: ${hide})`;
      return await this.executeCommand(template, description);
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to set navigation bar visibility: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Set uninstall protection blacklist for mobile devices.
   * 
   * @param packageNames - List of Android package names to protect from uninstallation
   * @returns OperationResult indicating success or failure
   */
  async setUninstallBlacklist(packageNames: string[]): Promise<OperationResult> {
    try {
      const template = getMobileCommandTemplate("uninstall_blacklist");
      if (!template) {
        return {
          success: false,
          requestId: '',
          errorMessage: "Uninstall blacklist template not found"
        };
      }

      // Use newline-separated format for uninstall blacklist file content
      const packageList = packageNames.join('\n');
      const timestamp = Math.floor(Date.now() / 1000).toString();
      const command = replaceTemplatePlaceholders(template, { 
        package_list: packageList,
        timestamp: timestamp
      });
      
      const description = `Uninstall blacklist configuration (${packageNames.length} packages)`;
      return await this.executeCommand(command, description);
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to set uninstall blacklist: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * Execute a command template for mobile configuration.
   * 
   * @param command - The command to execute
   * @param description - Description of the operation
   * @returns OperationResult indicating success or failure
   */
  private async executeCommand(command: string, description: string): Promise<OperationResult> {
    try {
      log(`Executing ${description}`);
      
      // Use the session's command module to execute the command with longer timeout for mobile operations
      const result = await (this.session as any).command.executeCommand(command, 10000);
      
      if (result && result.success) {
        log(`✅ ${description} completed successfully`);
        if (result.output) {
          log(`Command output: ${result.output}`);
        }
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: ''
        };
      } else {
        const errorMessage = result?.errorMessage || `Failed to execute ${description}`;
        logError(`Failed to execute ${description}: ${errorMessage}`);
        return {
          success: false,
          requestId: result?.requestId || '',
          errorMessage: errorMessage
        };
      }
    } catch (error) {
      const errorMsg = `Failed to execute ${description}: ${error instanceof Error ? error.message : String(error)}`;
      logError(errorMsg);
      return {
        success: false,
        requestId: '',
        errorMessage: errorMsg
      };
    }
  }
} 