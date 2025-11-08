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
   * Input text.
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
   * Press keys.
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
   * Release keys.
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