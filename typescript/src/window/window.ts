import { CallMcpToolRequest } from '../api/models/CallMcpToolRequest';
import { log, logError } from '../utils/logger';
import { APIError } from '../exceptions';

/**
 * Result object for a CallMcpTool operation
 */
interface CallMcpToolResult {
  data: Record<string, any>;
  content?: any[];
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
      }
      
      return result;
    } catch (error) {
      logError(`Error calling CallMcpTool - ${toolName}:`, error);
      throw new APIError(`Failed to call ${toolName}: ${error}`);
    }
  }

  /**
   * Lists all root windows in the system.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async listRootWindows(): Promise<any> {
    const args = {};

    const result = await this.callMcpTool('list_root_windows', args, 'Failed to list root windows');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Gets the currently active window.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async getActiveWindow(): Promise<any> {
    const args = {};

    const result = await this.callMcpTool('get_active_window', args, 'Failed to get active window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Activates a window by ID.
   * @param windowId The ID of the window to activate.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async activateWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('activate_window', args, 'Failed to activate window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Maximizes a window by ID.
   * @param windowId The ID of the window to maximize.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async maximizeWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('maximize_window', args, 'Failed to maximize window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Minimizes a window by ID.
   * @param windowId The ID of the window to minimize.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async minimizeWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('minimize_window', args, 'Failed to minimize window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Restores a window by ID.
   * @param windowId The ID of the window to restore.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async restoreWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('restore_window', args, 'Failed to restore window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Closes a window by ID.
   * @param windowId The ID of the window to close.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async closeWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('close_window', args, 'Failed to close window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Sets a window to fullscreen mode.
   * @param windowId The ID of the window to set to fullscreen.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async fullscreenWindow(windowId: number): Promise<any> {
    const args = {
      window_id: windowId
    };

    const result = await this.callMcpTool('fullscreen_window', args, 'Failed to set window to fullscreen');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Resizes a window by ID.
   * @param windowId The ID of the window to resize.
   * @param width The new width of the window.
   * @param height The new height of the window.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async resizeWindow(windowId: number, width: number, height: number): Promise<any> {
    const args = {
      window_id: windowId,
      width,
      height
    };

    const result = await this.callMcpTool('resize_window', args, 'Failed to resize window');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Enables or disables focus mode.
   * @param on Whether to enable (true) or disable (false) focus mode.
   * @returns The content field from the API response
   * @throws Error if the operation fails.
   */
  async focusMode(on: boolean): Promise<any> {
    const args = {
      on
    };

    const result = await this.callMcpTool('focus_mode', args, 'Failed to set focus mode');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }
}
