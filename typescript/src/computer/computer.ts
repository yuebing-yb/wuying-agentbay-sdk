/**
 * Computer module for desktop UI automation.
 * Provides mouse, keyboard, and screen operations for desktop environments.
 */

import { OperationResult, WindowListResult, WindowInfoResult, BoolResult as WindowBoolResult } from "../types/api-response";

export enum MouseButton {
  LEFT = 'left',
  RIGHT = 'right',
  MIDDLE = 'middle',
  DOUBLE_LEFT = 'double_left'
}

export enum ScrollDirection {
  UP = 'up',
  DOWN = 'down',
  LEFT = 'left',
  RIGHT = 'right'
}

export interface BoolResult extends OperationResult {
  data?: boolean;
}

export interface CursorPosition extends OperationResult {
  x: number;
  y: number;
}

export interface ScreenSize extends OperationResult {
  width: number;
  height: number;
  dpiScalingFactor: number;
}

export interface ScreenshotResult extends OperationResult {
  data: string; // Screenshot URL
}

// Session interface for Computer module
// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface ComputerSession {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  callMcpTool(toolName: string, args: Record<string, any>): Promise<any>;
  sessionId: string;
  getAPIKey(): string;
  getSessionId(): string;
}

export class Computer {
  private session: ComputerSession;

  constructor(session: ComputerSession) {
    this.session = session;
  }

  /**
   * Click mouse at specified coordinates.
   *
   * @param x - X coordinate for the click
   * @param y - Y coordinate for the click
   * @param button - Mouse button to click (default: 'left'). Valid values: 'left', 'right', 'middle', 'double_left'
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateClickMouse() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Click at coordinates (100, 100) with left button
   *       const clickResult = await session.computer.clickMouse(100, 100, 'left');
   *       if (clickResult.success) {
   *         console.log('Mouse clicked successfully');
   *       } else {
   *         console.log(`Click failed: ${clickResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateClickMouse().catch(console.error);
   * ```
   */
  async clickMouse(x: number, y: number, button: MouseButton | string = MouseButton.LEFT): Promise<BoolResult> {
    const buttonStr = typeof button === 'string' ? button : button;
    const validButtons = Object.values(MouseButton);
    if (!validButtons.includes(buttonStr as MouseButton)) {
      throw new Error(`Invalid button '${buttonStr}'. Must be one of ${validButtons.join(', ')}`);
    }

    const args = { x, y, button: buttonStr };
    try {
      const result = await this.session.callMcpTool('click_mouse', args);
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
        errorMessage: `Failed to click mouse: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Move mouse to specified coordinates.
   *
   * @param x - X coordinate to move to
   * @param y - Y coordinate to move to
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateMoveMouse() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Move mouse to coordinates (300, 400)
   *       const moveResult = await session.computer.moveMouse(300, 400);
   *       if (moveResult.success) {
   *         console.log('Mouse moved successfully');
   *
   *         // Verify new position
   *         const pos = await session.computer.getCursorPosition();
   *         console.log(`New position: (${pos.x}, ${pos.y})`);
   *       } else {
   *         console.log(`Move failed: ${moveResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateMoveMouse().catch(console.error);
   * ```
   */
  async moveMouse(x: number, y: number): Promise<BoolResult> {
    const args = { x, y };
    try {
      const result = await this.session.callMcpTool('move_mouse', args);
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
        errorMessage: `Failed to move mouse: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Drag mouse from one position to another.
   *
   * @param fromX - Starting X coordinate
   * @param fromY - Starting Y coordinate
   * @param toX - Ending X coordinate
   * @param toY - Ending Y coordinate
   * @param button - Mouse button to use for drag (default: 'left'). Valid values: 'left', 'right', 'middle'
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateDragMouse() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Drag from (100, 100) to (300, 300) with left button
   *       const dragResult = await session.computer.dragMouse(100, 100, 300, 300, 'left');
   *       if (dragResult.success) {
   *         console.log('Drag operation completed successfully');
   *       } else {
   *         console.log(`Drag failed: ${dragResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateDragMouse().catch(console.error);
   * ```
   */
  async dragMouse(fromX: number, fromY: number, toX: number, toY: number, button: MouseButton | string = MouseButton.LEFT): Promise<BoolResult> {
    const buttonStr = typeof button === 'string' ? button : button;
    const validButtons = [MouseButton.LEFT, MouseButton.RIGHT, MouseButton.MIDDLE];
    if (!validButtons.includes(buttonStr as MouseButton)) {
      throw new Error(`Invalid button '${buttonStr}'. Must be one of ${validButtons.join(', ')}`);
    }

    const args = { from_x: fromX, from_y: fromY, to_x: toX, to_y: toY, button: buttonStr };
    try {
      const result = await this.session.callMcpTool('drag_mouse', args);
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
        errorMessage: `Failed to drag mouse: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Scroll at specified coordinates.
   *
   * @param x - X coordinate to scroll at
   * @param y - Y coordinate to scroll at
   * @param direction - Scroll direction (default: 'up'). Valid values: 'up', 'down', 'left', 'right'
   * @param amount - Scroll amount (default: 1)
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateScroll() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Scroll up at center of screen, amount 3
   *       const scrollResult = await session.computer.scroll(400, 300, 'up', 3);
   *       if (scrollResult.success) {
   *         console.log('Scroll completed successfully');
   *       } else {
   *         console.log(`Scroll failed: ${scrollResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateScroll().catch(console.error);
   * ```
   */
  async scroll(x: number, y: number, direction: ScrollDirection | string = ScrollDirection.UP, amount = 1): Promise<BoolResult> {
    const directionStr = typeof direction === 'string' ? direction : direction;
    const validDirections = Object.values(ScrollDirection);
    if (!validDirections.includes(directionStr as ScrollDirection)) {
      throw new Error(`Invalid direction '${directionStr}'. Must be one of ${validDirections.join(', ')}`);
    }

    const args = { x, y, direction: directionStr, amount };
    try {
      const result = await this.session.callMcpTool('scroll', args);
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
        errorMessage: `Failed to scroll: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Input text at the current cursor position.
   *
   * @param text - Text to input
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateInputText() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Input text at current cursor position
   *       const inputResult = await session.computer.inputText('Hello AgentBay!');
   *       if (inputResult.success) {
   *         console.log('Text input successfully');
   *       } else {
   *         console.log(`Input failed: ${inputResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateInputText().catch(console.error);
   * ```
   */
  async inputText(text: string): Promise<BoolResult> {
    const args = { text };
    try {
      const result = await this.session.callMcpTool('input_text', args);
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
   * Press one or more keys.
   *
   * @param keys - Array of key names to press
   * @param hold - Whether to hold the keys down (default: false)
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstratePressKeys() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Press Enter key
   *       const enterResult = await session.computer.pressKeys(['Enter']);
   *       if (enterResult.success) {
   *         console.log('Enter key pressed successfully');
   *       }
   *
   *       // Press Ctrl+C (hold the keys)
   *       const ctrlCResult = await session.computer.pressKeys(['Ctrl', 'c'], true);
   *       if (ctrlCResult.success) {
   *         console.log('Ctrl+C pressed successfully');
   *         // Remember to release the keys
   *         await session.computer.releaseKeys(['Ctrl', 'c']);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstratePressKeys().catch(console.error);
   * ```
   */
  async pressKeys(keys: string[], hold = false): Promise<BoolResult> {
    const args = { keys, hold };
    try {
      const result = await this.session.callMcpTool('press_keys', args);
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
        errorMessage: `Failed to press keys: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Release previously pressed keys.
   *
   * @param keys - Array of key names to release
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateReleaseKeys() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Press and hold Ctrl key
   *       await session.computer.pressKeys(['Ctrl'], true);
   *
   *       // Release Ctrl key
   *       const releaseResult = await session.computer.releaseKeys(['Ctrl']);
   *       if (releaseResult.success) {
   *         console.log('Ctrl key released successfully');
   *       } else {
   *         console.log(`Release failed: ${releaseResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateReleaseKeys().catch(console.error);
   * ```
   */
  async releaseKeys(keys: string[]): Promise<BoolResult> {
    const args = { keys };
    try {
      const result = await this.session.callMcpTool('release_keys', args);
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
        errorMessage: `Failed to release keys: ${error instanceof Error ? error.message : String(error)}`,
        data: false
      };
    }
  }

  /**
   * Get cursor position.
   *
   * @returns Promise resolving to result containing cursor coordinates
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateGetCursorPosition() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Get current cursor position
   *       const positionResult = await session.computer.getCursorPosition();
   *       if (positionResult.success) {
   *         console.log(`Cursor at: (${positionResult.x}, ${positionResult.y})`);
   *       } else {
   *         console.log(`Failed to get cursor position: ${positionResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetCursorPosition().catch(console.error);
   * ```
   */
  async getCursorPosition(): Promise<CursorPosition> {
    try {
      const result = await this.session.callMcpTool('get_cursor_position', {});
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to get cursor position',
          x: 0,
          y: 0
        };
      }

      // Parse JSON response from data field (callMcpTool already extracts content[0].text to data)
      const content = result.data;
      if (!content) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: 'No content in response',
          x: 0,
          y: 0
        };
      }

      try {
        const position = JSON.parse(content);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          x: position.x || 0,
          y: position.y || 0
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse cursor position: ${parseError}`,
          x: 0,
          y: 0
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to get cursor position: ${error instanceof Error ? error.message : String(error)}`,
        x: 0,
        y: 0
      };
    }
  }

  /**
   * Get screen size.
   *
   * @returns Promise resolving to result containing screen dimensions and DPI scaling
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateGetScreenSize() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Get screen size and DPI information
   *       const sizeResult = await session.computer.getScreenSize();
   *       if (sizeResult.success) {
   *         console.log(`Screen: ${sizeResult.width}x${sizeResult.height}, DPI: ${sizeResult.dpiScalingFactor}`);
   *       } else {
   *         console.log(`Failed to get screen size: ${sizeResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetScreenSize().catch(console.error);
   * ```
   */
  async getScreenSize(): Promise<ScreenSize> {
    try {
      const result = await this.session.callMcpTool('get_screen_size', {});
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to get screen size',
          width: 0,
          height: 0,
          dpiScalingFactor: 1.0
        };
      }

      // Parse JSON response from data field (callMcpTool already extracts content[0].text to data)
      const content = result.data;
      if (!content) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: 'No content in response',
          width: 0,
          height: 0,
          dpiScalingFactor: 1.0
        };
      }

      try {
        const screenInfo = JSON.parse(content);
        return {
          success: true,
          requestId: result.requestId || '',
          errorMessage: '',
          width: screenInfo.width || 0,
          height: screenInfo.height || 0,
          dpiScalingFactor: screenInfo.dpiScalingFactor || 1.0
        };
      } catch (parseError) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: `Failed to parse screen size: ${parseError}`,
          width: 0,
          height: 0,
          dpiScalingFactor: 1.0
        };
      }
    } catch (error) {
      return {
        success: false,
        requestId: '',
        errorMessage: `Failed to get screen size: ${error instanceof Error ? error.message : String(error)}`,
        width: 0,
        height: 0,
        dpiScalingFactor: 1.0
      };
    }
  }

  /**
   * Take a screenshot.
   *
   * @returns Promise resolving to result containing screenshot URL
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateScreenshot() {
   *     try {
   *         const result = await agentBay.create({
   *             imageId: 'windows_latest'
   *         });
   *         if (result.success && result.session) {
   *             const session = result.session;
   *
   *             // Take a screenshot
   *             const screenshotResult = await session.computer.screenshot();
   *             if (screenshotResult.success) {
   *                 console.log('Screenshot taken successfully');
   *                 console.log(`Screenshot URL: ${screenshotResult.data}`);
   *             } else {
   *                 console.log(`Screenshot failed: ${screenshotResult.errorMessage}`);
   *             }
   *
   *             await session.delete();
   *         }
   *     } catch (error) {
   *         console.error('Error:', error);
   *     }
   * }
   *
   * demonstrateScreenshot().catch(console.error);
   * ```
   */
  async screenshot(): Promise<ScreenshotResult> {
    try {
      const result = await this.session.callMcpTool('system_screenshot', {});
      
      if (!result.success) {
        return {
          success: false,
          requestId: result.requestId || '',
          errorMessage: result.errorMessage || 'Failed to take screenshot',
          data: ''
        };
      }

      const screenshotUrl = result.content?.[0]?.text || '';
      return {
        success: true,
        requestId: result.requestId || '',
        errorMessage: '',
        data: screenshotUrl
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
   * Lists all root windows.
   *
   * @param timeoutMs - Timeout in milliseconds (default: 3000)
   * @returns Promise resolving to result containing array of root windows
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateListRootWindows() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // List all root windows
   *       const windowsResult = await session.computer.listRootWindows();
   *       if (windowsResult.success) {
   *         console.log(`Found ${windowsResult.windows.length} root windows`);
   *         windowsResult.windows.forEach(win => {
   *           console.log(`  - Window ${win.id}: ${win.title}`);
   *         });
   *       } else {
   *         console.log(`Failed to list windows: ${windowsResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateListRootWindows().catch(console.error);
   * ```
   */
  async listRootWindows(timeoutMs = 3000): Promise<WindowListResult> {
    try {
      const args = { timeout_ms: timeoutMs };
      const response = await this.session.callMcpTool('list_root_windows', args);

      if (!response.success) {
        return {
          requestId: response.requestId,
          success: false,
          windows: [],
          errorMessage: response.errorMessage,
        };
      }

      const windows = response.data ? JSON.parse(response.data) : [];
      return {
        requestId: response.requestId,
        success: true,
        windows,
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        windows: [],
        errorMessage: `Failed to list root windows: ${error}`,
      };
    }
  }

  /**
   * Gets the currently active window.
   *
   * @param timeoutMs - Timeout in milliseconds (default: 3000)
   * @returns Promise resolving to result containing active window information
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateGetActiveWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Get the currently active window
   *       const activeWindowResult = await session.computer.getActiveWindow();
   *       if (activeWindowResult.success && activeWindowResult.window) {
   *         console.log(`Active window ID: ${activeWindowResult.window.id}`);
   *         console.log(`Active window title: ${activeWindowResult.window.title}`);
   *       } else {
   *         console.log(`Failed to get active window: ${activeWindowResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetActiveWindow().catch(console.error);
   * ```
   */
  async getActiveWindow(timeoutMs = 3000): Promise<WindowInfoResult> {
    try {
      const args = { timeout_ms: timeoutMs };
      const response = await this.session.callMcpTool('get_active_window', args);

      if (!response.success) {
        return {
          requestId: response.requestId,
          success: false,
          window: null,
          errorMessage: response.errorMessage,
        };
      }

      const window = response.data ? JSON.parse(response.data) : null;
      return {
        requestId: response.requestId,
        success: true,
        window,
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        window: null,
        errorMessage: `Failed to get active window: ${error}`,
      };
    }
  }

  /**
   * Activates the specified window.
   *
   * @param windowId - ID of the window to activate
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateActivateWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // List all windows
   *       const windows = await session.computer.listRootWindows();
   *       if (windows.success && windows.windows.length > 0) {
   *         const windowId = windows.windows[0].id;
   *
   *         // Activate the first window
   *         const activateResult = await session.computer.activateWindow(windowId);
   *         if (activateResult.success) {
   *           console.log(`Window ${windowId} activated successfully`);
   *           // Output: Window 12345 activated successfully
   *         } else {
   *           console.log(`Failed to activate window: ${activateResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateActivateWindow().catch(console.error);
   * ```
   */
  async activateWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('activate_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to activate window: ${error}`,
      };
    }
  }

  /**
   * Closes the specified window.
   *
   * @param windowId - ID of the window to close
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateCloseWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Get the active window
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         // Close the window
   *         const closeResult = await session.computer.closeWindow(activeWindow.window.id);
   *         if (closeResult.success) {
   *           console.log('Window closed successfully');
   *         } else {
   *           console.log(`Failed to close window: ${closeResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateCloseWindow().catch(console.error);
   * ```
   */
  async closeWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('close_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to close window: ${error}`,
      };
    }
  }

  /**
   * Maximizes the specified window.
   *
   * @param windowId - ID of the window to maximize
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateMaximizeWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Get the active window
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         // Maximize the window
   *         const maxResult = await session.computer.maximizeWindow(activeWindow.window.id);
   *         if (maxResult.success) {
   *           console.log('Window maximized successfully');
   *         } else {
   *           console.log(`Failed to maximize window: ${maxResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateMaximizeWindow().catch(console.error);
   * ```
   */
  async maximizeWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('maximize_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to maximize window: ${error}`,
      };
    }
  }

  /**
   * Minimizes the specified window.
   *
   * @param windowId - ID of the window to minimize
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateMinimizeWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Get the active window
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         // Minimize the window
   *         const minResult = await session.computer.minimizeWindow(activeWindow.window.id);
   *         if (minResult.success) {
   *           console.log('Window minimized successfully');
   *         } else {
   *           console.log(`Failed to minimize window: ${minResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateMinimizeWindow().catch(console.error);
   * ```
   */
  async minimizeWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('minimize_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to minimize window: ${error}`,
      };
    }
  }

  /**
   * Restores the specified window.
   *
   * @param windowId - ID of the window to restore
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateRestoreWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application and minimize it
   *       await session.computer.startApp('notepad.exe');
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         await session.computer.minimizeWindow(activeWindow.window.id);
   *
   *         // Restore the window
   *         const restoreResult = await session.computer.restoreWindow(activeWindow.window.id);
   *         if (restoreResult.success) {
   *           console.log('Window restored successfully');
   *         } else {
   *           console.log(`Failed to restore window: ${restoreResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateRestoreWindow().catch(console.error);
   * ```
   */
  async restoreWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('restore_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to restore window: ${error}`,
      };
    }
  }

  /**
   * Resizes the specified window.
   *
   * @param windowId - ID of the window to resize
   * @param width - New width of the window
   * @param height - New height of the window
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateResizeWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Get the active window
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         // Resize the window to 800x600
   *         const resizeResult = await session.computer.resizeWindow(activeWindow.window.id, 800, 600);
   *         if (resizeResult.success) {
   *           console.log('Window resized successfully to 800x600');
   *         } else {
   *           console.log(`Failed to resize window: ${resizeResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateResizeWindow().catch(console.error);
   * ```
   */
  async resizeWindow(windowId: number, width: number, height: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId, width, height };
      const response = await this.session.callMcpTool('resize_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to resize window: ${error}`,
      };
    }
  }

  /**
   * Makes the specified window fullscreen.
   *
   * @param windowId - ID of the window to make fullscreen
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateFullscreenWindow() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Start an application
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Get the active window
   *       const activeWindow = await session.computer.getActiveWindow();
   *       if (activeWindow.success && activeWindow.window) {
   *         // Make the window fullscreen
   *         const fullscreenResult = await session.computer.fullscreenWindow(activeWindow.window.id);
   *         if (fullscreenResult.success) {
   *           console.log('Window set to fullscreen successfully');
   *         } else {
   *           console.log(`Failed to set window fullscreen: ${fullscreenResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateFullscreenWindow().catch(console.error);
   * ```
   */
  async fullscreenWindow(windowId: number): Promise<WindowBoolResult> {
    try {
      const args = { window_id: windowId };
      const response = await this.session.callMcpTool('fullscreen_window', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to make window fullscreen: ${error}`,
      };
    }
  }

  /**
   * Toggles focus mode on or off.
   *
   * @param on - Whether to enable (true) or disable (false) focus mode
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   *
   * async function demonstrateFocusMode() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success && result.session) {
   *       const session = result.session;
   *
   *       // Enable focus mode
   *       const enableResult = await session.computer.focusMode(true);
   *       if (enableResult.success) {
   *         console.log('Focus mode enabled');
   *       }
   *
   *       // Do some work...
   *
   *       // Disable focus mode
   *       const disableResult = await session.computer.focusMode(false);
   *       if (disableResult.success) {
   *         console.log('Focus mode disabled');
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateFocusMode().catch(console.error);
   * ```
   */
  async focusMode(on: boolean): Promise<WindowBoolResult> {
    try {
      const args = { on };
      const response = await this.session.callMcpTool('focus_mode', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to toggle focus mode: ${error}`,
      };
    }
  }

  // Application Management Operations

  /**
   * Gets the list of installed applications.
   *
   * @param startMenu - Whether to include applications from start menu (default: true)
   * @param desktop - Whether to include applications from desktop (default: false)
   * @param ignoreSystemApps - Whether to exclude system applications (default: true)
   * @returns Promise resolving to result containing array of installed applications
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateGetInstalledApps() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Get installed applications from start menu
   *       const appsResult = await session.computer.getInstalledApps();
   *       if (appsResult.success) {
   *         console.log(`Found ${appsResult.data.length} installed applications`);
   *         // Output: Found 15 installed applications
   *         appsResult.data.forEach(app => {
   *           console.log(`  - ${app.name}: ${app.path}`);
   *         });
   *         // Output:   - Notepad: C:\Windows\System32\notepad.exe
   *         // Output:   - Calculator: calculator:
   *       }
   *
   *       // Get applications including desktop shortcuts
   *       const desktopAppsResult = await session.computer.getInstalledApps(true, true, true);
   *       if (desktopAppsResult.success) {
   *         console.log(`Found ${desktopAppsResult.data.length} applications (including desktop)`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetInstalledApps().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async getInstalledApps(startMenu = true, desktop = false, ignoreSystemApps = true): Promise<any> {
    try {
      const args = {
        start_menu: startMenu,
        desktop,
        ignore_system_apps: ignoreSystemApps,
      };

      const response = await this.session.callMcpTool('get_installed_apps', args);

      if (!response.success) {
        return {
          requestId: response.requestId,
          success: false,
          data: [],
          errorMessage: response.errorMessage,
        };
      }

      const apps = response.data ? JSON.parse(response.data) : [];
      return {
        requestId: response.requestId,
        success: true,
        data: apps,
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        data: [],
        errorMessage: `Failed to get installed apps: ${error}`,
      };
    }
  }

  /**
   * Starts the specified application.
   *
   * @param startCmd - The command to start the application (e.g., 'notepad.exe', 'calculator:')
   * @param workDirectory - The working directory for the application (optional)
   * @param activity - The activity parameter (optional, primarily for mobile use)
   * @returns Promise resolving to result containing array of started processes
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateStartApp() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start Notepad application
   *       const startResult = await session.computer.startApp('notepad.exe');
   *       if (startResult.success) {
   *         console.log(`Started ${startResult.data.length} process(es)`);
   *         // Output: Started 1 process(es)
   *         startResult.data.forEach(proc => {
   *           console.log(`  - PID ${proc.pid}: ${proc.name}`);
   *         });
   *         // Output:   - PID 1234: notepad.exe
   *       } else {
   *         console.log(`Failed to start app: ${startResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateStartApp().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async startApp(startCmd: string, workDirectory = "", activity = ""): Promise<any> {
    try {
      const args: Record<string, string> = { start_cmd: startCmd };
      if (workDirectory) args.work_directory = workDirectory;
      if (activity) args.activity = activity;

      const response = await this.session.callMcpTool('start_app', args);

      if (!response.success) {
        return {
          requestId: response.requestId,
          success: false,
          data: [],
          errorMessage: response.errorMessage,
        };
      }

      const processes = response.data ? JSON.parse(response.data) : [];
      return {
        requestId: response.requestId,
        success: true,
        data: processes,
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        data: [],
        errorMessage: `Failed to start app: ${error}`,
      };
    }
  }

  /**
   * Stops an application by process name.
   *
   * @param pname - The process name to stop (e.g., 'notepad.exe', 'chrome.exe')
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateStopAppByPName() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start an application first
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Stop the application by process name
   *       const stopResult = await session.computer.stopAppByPName('notepad.exe');
   *       if (stopResult.success) {
   *         console.log('Application stopped successfully');
   *         // Output: Application stopped successfully
   *       } else {
   *         console.log(`Failed to stop app: ${stopResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateStopAppByPName().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async stopAppByPName(pname: string): Promise<any> {
    try {
      const args = { pname };
      const response = await this.session.callMcpTool('stop_app_by_pname', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to stop app by pname: ${error}`,
      };
    }
  }

  /**
   * Stops an application by process ID.
   *
   * @param pid - The process ID to stop
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateStopAppByPID() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start an application and get its PID
   *       const startResult = await session.computer.startApp('notepad.exe');
   *       if (startResult.success && startResult.data.length > 0) {
   *         const pid = startResult.data[0].pid;
   *         console.log(`Started application with PID: ${pid}`);
   *
   *         // Stop the application by PID
   *         const stopResult = await session.computer.stopAppByPID(pid);
   *         if (stopResult.success) {
   *           console.log(`Application with PID ${pid} stopped successfully`);
   *           // Output: Application with PID 1234 stopped successfully
   *         } else {
   *           console.log(`Failed to stop app: ${stopResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateStopAppByPID().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async stopAppByPID(pid: number): Promise<any> {
    try {
      const args = { pid };
      const response = await this.session.callMcpTool('stop_app_by_pid', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to stop app by pid: ${error}`,
      };
    }
  }

  /**
   * Stops an application by stop command.
   *
   * @param cmd - The command to stop the application
   * @returns Promise resolving to result with success status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateStopAppByCmd() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start an application first
   *       await session.computer.startApp('notepad.exe');
   *
   *       // Stop the application using a command
   *       const stopResult = await session.computer.stopAppByCmd('taskkill /IM notepad.exe /F');
   *       if (stopResult.success) {
   *         console.log('Application stopped successfully using command');
   *         // Output: Application stopped successfully using command
   *       } else {
   *         console.log(`Failed to stop app: ${stopResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateStopAppByCmd().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async stopAppByCmd(cmd: string): Promise<any> {
    try {
      const args = { stop_cmd: cmd };
      const response = await this.session.callMcpTool('stop_app_by_cmd', args);

      return {
        requestId: response.requestId,
        success: response.success,
        errorMessage: response.errorMessage || '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to stop app by cmd: ${error}`,
      };
    }
  }

  /**
   * Lists all visible applications.
   *
   * @returns Promise resolving to result containing array of visible application processes
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateListVisibleApps() {
   *   try {
   *     const result = await agentBay.create({
   *       imageId: 'windows_latest'
   *     });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // List all visible applications
   *       const appsResult = await session.computer.listVisibleApps();
   *       if (appsResult.success) {
   *         console.log(`Found ${appsResult.data.length} visible applications`);
   *         // Output: Found 5 visible applications
   *         appsResult.data.forEach(app => {
   *           console.log(`  - PID ${app.pid}: ${app.name}`);
   *         });
   *         // Output:   - PID 1234: notepad.exe
   *         // Output:   - PID 5678: chrome.exe
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateListVisibleApps().catch(console.error);
   * ```
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async listVisibleApps(): Promise<any> {
    try {
      const response = await this.session.callMcpTool('list_visible_apps', {});

      if (!response.success) {
        return {
          requestId: response.requestId,
          success: false,
          data: [],
          errorMessage: response.errorMessage,
        };
      }

      const processes = response.data ? JSON.parse(response.data) : [];
      return {
        requestId: response.requestId,
        success: true,
        data: processes,
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        data: [],
        errorMessage: `Failed to list visible apps: ${error}`,
      };
    }
  }
} 