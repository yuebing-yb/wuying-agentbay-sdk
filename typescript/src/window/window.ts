import { CallMcpToolRequest } from '../api/models/CallMcpToolRequest';
import { log, logError } from '../utils/logger';
import { APIError } from '../exceptions';

/**
 * Result object for a CallMcpTool operation
 */
interface CallMcpToolResult {
  data: Record<string, any>;
  content?: any[];
  textContent?: string;
  isError: boolean;
  errorMsg?: string;
  statusCode: number;
}

/**
 * Represents a window in the system.
 */
export interface Window {
  window_id: number;
  title: string;
  absolute_upper_left_x?: number;
  absolute_upper_left_y?: number;
  width?: number;
  height?: number;
  pid?: number;
  pname?: string;
  child_windows?: Window[];
}

/**
 * Handles window management operations in the AgentBay cloud environment.
 */
export class WindowManager {
  private session: {
    getAPIKey(): string;
    getClient(): any;
    getSessionId(): string;
  };

  /**
   * Creates a new WindowManager instance.
   * @param session The session object that provides access to the AgentBay API.
   */
  constructor(session: {
    getAPIKey(): string;
    getClient(): any;
    getSessionId(): string;
  }) {
    this.session = session;
  }

  /**
   * Helper method to call MCP tools and handle common response processing
   * 
   * @param toolName - Name of the MCP tool to call
   * @param args - Arguments to pass to the tool
   * @param defaultErrorMsg - Default error message if specific error details are not available
   * @returns A CallMcpToolResult with the response data
   * @throws APIError if the call fails
   */
  private async callMcpTool(
    toolName: string, 
    args: Record<string, any>,
    defaultErrorMsg: string
  ): Promise<CallMcpToolResult> {
    try {
      const argsJSON = JSON.stringify(args);
      const request = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: toolName,
        args: argsJSON
      });
      
      // Log API request
      log(`API Call: CallMcpTool - ${toolName}`);
      log(`Request: SessionId=${request.sessionId}, Args=${request.args}`);
      
      const response = await this.session.getClient().callMcpTool(request);
      
      // Log API response
      if (response && response.body) {
        log(`Response from CallMcpTool - ${toolName}:`, response.body);
      }
      
      // Extract data from response
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      const data = response.body.data as Record<string, any>;
      
      // Create result object
      const result: CallMcpToolResult = {
        data,
        statusCode: response.statusCode || 0,
        isError: false
      };
      
      // Check if there's an error in the response
      if (data.isError === true) {
        result.isError = true;
        
        // Try to extract the error message from the content field
        const contentArray = data.content as any[] | undefined;
        if (contentArray && contentArray.length > 0) {
          result.content = contentArray;
          
          // Extract error message from the first content item
          if (contentArray[0]?.text) {
            result.errorMsg = contentArray[0].text;
            throw new Error(contentArray[0].text);
          }
        }
        throw new Error(defaultErrorMsg);
      }
      
      // Extract content array if it exists
      if (Array.isArray(data.content)) {
        result.content = data.content;
        
        // Extract textContent from content items
        if (result.content.length > 0) {
          const textParts: string[] = [];
          for (const item of result.content) {
            if (item && typeof item === 'object' && item.text && typeof item.text === 'string') {
              textParts.push(item.text);
            }
          }
          result.textContent = textParts.join('\n');
        }
      }
      
      return result;
    } catch (error) {
      logError(`Error calling CallMcpTool - ${toolName}:`, error);
      throw new APIError(`Failed to call ${toolName}: ${error}`);
    }
  }

  /**
   * Helper method to parse JSON string into Window objects
   * @param jsonStr - JSON string to parse
   * @returns Array of Window objects or single Window object
   */
  private parseWindowsFromJSON(jsonStr: string): Window[] {
    try {
      const parsed = JSON.parse(jsonStr);
      return Array.isArray(parsed) ? parsed : [parsed];
    } catch (error) {
      throw new Error(`Failed to parse window data: ${error}`);
    }
  }

  /**
   * Lists all root windows in the system.
   * @returns Array of Window objects
   * @throws Error if the operation fails.
   */
  async listRootWindows(): Promise<Window[]> {
    const args = {};

    const result = await this.callMcpTool('list_root_windows', args, 'Failed to list root windows');
    
    if (!result.textContent) {
      return [];
    }
    
    return this.parseWindowsFromJSON(result.textContent);
  }

  /**
   * Gets the currently active window.
   * @returns Window object or null if no active window
   * @throws Error if the operation fails.
   */
  async getActiveWindow(): Promise<Window | null> {
    const args = {};

    const result = await this.callMcpTool('get_active_window', args, 'Failed to get active window');
    
    if (!result.textContent) {
      return null;
    }
    
    const windows = this.parseWindowsFromJSON(result.textContent);
    return windows.length > 0 ? windows[0] : null;
  }

  /**
   * Activates a window by ID.
   * @param windowId The ID of the window to activate.
   * @throws Error if the operation fails.
   */
  async activateWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('activate_window', args, 'Failed to activate window');
  }

  /**
   * Maximizes a window by ID.
   * @param windowId The ID of the window to maximize.
   * @throws Error if the operation fails.
   */
  async maximizeWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('maximize_window', args, 'Failed to maximize window');
  }

  /**
   * Minimizes a window by ID.
   * @param windowId The ID of the window to minimize.
   * @throws Error if the operation fails.
   */
  async minimizeWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('minimize_window', args, 'Failed to minimize window');
  }

  /**
   * Restores a window by ID.
   * @param windowId The ID of the window to restore.
   * @throws Error if the operation fails.
   */
  async restoreWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('restore_window', args, 'Failed to restore window');
  }

  /**
   * Closes a window by ID.
   * @param windowId The ID of the window to close.
   * @throws Error if the operation fails.
   */
  async closeWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('close_window', args, 'Failed to close window');
  }

  /**
   * Sets a window to fullscreen by ID.
   * @param windowId The ID of the window to set to fullscreen.
   * @throws Error if the operation fails.
   */
  async fullscreenWindow(windowId: number): Promise<void> {
    const args = {
      window_id: windowId
    };

    await this.callMcpTool('fullscreen_window', args, 'Failed to set window to fullscreen');
  }

  /**
   * Resizes a window by ID.
   * @param windowId The ID of the window to resize.
   * @param width The new width of the window.
   * @param height The new height of the window.
   * @throws Error if the operation fails.
   */
  async resizeWindow(windowId: number, width: number, height: number): Promise<void> {
    const args = {
      window_id: windowId,
      width,
      height
    };

    await this.callMcpTool('resize_window', args, 'Failed to resize window');
  }

  /**
   * Enables or disables focus mode.
   * @param on Whether to enable focus mode.
   * @throws Error if the operation fails.
   */
  async focusMode(on: boolean): Promise<void> {
    const args = {
      on
    };

    await this.callMcpTool('focus_mode', args, 'Failed to set focus mode');
  }
}
