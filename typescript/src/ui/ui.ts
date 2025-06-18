import { APIError } from '../exceptions';
import { Session } from '../session';
import { CallMcpToolRequest } from '../api/models/model';
import { log, logError } from '../utils/logger';

/**
 * KeyCode constants for mobile device input
 */
export const KeyCode = {
  HOME: 3,
  BACK: 4,
  VOLUME_UP: 24,
  VOLUME_DOWN: 25,
  POWER: 26,
  MENU: 82
};

/**
 * UI handles UI operations in the AgentBay cloud environment.
 */
export class UI {
  private session: Session;

  /**
   * Initialize a UI object.
   * 
   * @param session - The Session instance that this UI belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Internal helper to call MCP tool and handle errors.
   * 
   * @param name - The name of the tool to call.
   * @param args - The arguments to pass to the tool.
   * @returns The response from the tool.
   * @throws Error if the tool call fails.
   */
  private async callMcpTool(name: string, args: any): Promise<string> {
    try {
      const argsJSON = JSON.stringify(args);
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name,
        args: argsJSON
      });
      
      // Log API request
      log(`API Call: CallMcpTool - ${name}`);
      log(`Request: SessionId=${this.session.getSessionId()}, Args=${argsJSON}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool - ${name}:`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Check if there's an error in the response
      const data = response.body.data as any;
      if (data.isError) {
        // Try to extract the error message from the content field
        if (data.content && Array.isArray(data.content) && data.content.length > 0) {
          const errorMessages: string[] = [];
          for (const item of data.content) {
            if (item && typeof item === 'object' && 'text' in item) {
              errorMessages.push(item.text);
            }
          }
          if (errorMessages.length > 0) {
            throw new Error(`Error in response: ${errorMessages.join('; ')}`);
          }
        }
        throw new Error('Error in response');
      }
      
      // Extract content array
      const content = data.content;
      if (!content || !Array.isArray(content) || content.length === 0) {
        throw new Error('No content found in response');
      }
      
      // Extract text field from the first content item
      const contentItem = content[0];
      if (!contentItem || typeof contentItem !== 'object') {
        throw new Error('Invalid content item format');
      }
      
      const jsonText = contentItem.text;
      
      // Handle empty text field as a valid response
      if (jsonText === '') {
        log('Empty text field received, returning empty string');
        return ''; // Return empty string for operations with empty response
      }
      
      if (typeof jsonText !== 'string') {
        throw new Error('Text field not found or not a string');
      }
      
      return jsonText;
    } catch (error) {
      logError(`Error calling CallMcpTool - ${name}:`, error);
      throw new APIError(`Failed to call MCP tool ${name}: ${error}`);
    }
  }

  /**
   * Retrieves all clickable UI elements within the specified timeout.
   * 
   * @param timeoutMs - The timeout in milliseconds. Default is 2000ms.
   * @returns A list of clickable UI elements.
   * @throws Error if the operation fails.
   */
  async getClickableUIElements(timeoutMs: number = 2000): Promise<any[]> {
    const args = {
      timeout_ms: timeoutMs
    };
    
    try {
      const result = await this.callMcpTool('get_clickable_ui_elements', args);
      return JSON.parse(result);
    } catch (error) {
      throw new APIError(`Failed to get clickable UI elements: ${error}`);
    }
  }

  /**
   * Helper function to recursively parse a UI element and its children.
   * 
   * @param element - The UI element to parse.
   * @returns The parsed UI element.
   */
  private parseElement(element: any): any {
    const parsed: any = {
      bounds: element.bounds || '',
      className: element.className || '',
      text: element.text || '',
      type: element.type || '',
      resourceId: element.resourceId || '',
      index: element.index !== undefined ? element.index : -1,
      isParent: element.isParent !== undefined ? element.isParent : false
    };
    
    if (element.children && Array.isArray(element.children) && element.children.length > 0) {
      parsed.children = element.children.map((child: any) => this.parseElement(child));
    } else {
      parsed.children = [];
    }
    
    return parsed;
  }

  /**
   * Retrieves all UI elements within the specified timeout.
   * 
   * @param timeoutMs - The timeout in milliseconds. Default is 2000ms.
   * @returns A list of all UI elements.
   * @throws Error if the operation fails.
   */
  async getAllUIElements(timeoutMs: number = 2000): Promise<any[]> {
    const args = {
      timeout_ms: timeoutMs
    };
    
    try {
      const result = await this.callMcpTool('get_all_ui_elements', args);
      const elements = JSON.parse(result);
      
      // Parse each element
      return elements.map((element: any) => this.parseElement(element));
    } catch (error) {
      throw new APIError(`Failed to get all UI elements: ${error}`);
    }
  }

  /**
   * Sends a key press event.
   * 
   * @param key - The key code to send.
   * @returns True if the key press was successful.
   * @throws Error if the operation fails.
   */
  async sendKey(key: number): Promise<boolean> {
    const args = {
      key
    };
    
    try {
      const result = await this.callMcpTool('send_key', args);
      return result === 'true' || result === 'True';
    } catch (error) {
      throw new APIError(`Failed to send key: ${error}`);
    }
  }

  /**
   * Inputs text into the active field.
   * 
   * @param text - The text to input.
   * @throws Error if the operation fails.
   */
  async inputText(text: string): Promise<void> {
    const args = {
      text
    };
    
    try {
      await this.callMcpTool('input_text', args);
    } catch (error) {
      throw new APIError(`Failed to input text: ${error}`);
    }
  }

  /**
   * Performs a swipe gesture on the screen.
   * 
   * @param startX - The starting X coordinate.
   * @param startY - The starting Y coordinate.
   * @param endX - The ending X coordinate.
   * @param endY - The ending Y coordinate.
   * @param durationMs - The duration of the swipe in milliseconds. Default is 300ms.
   * @throws Error if the operation fails.
   */
  async swipe(startX: number, startY: number, endX: number, endY: number, durationMs: number = 300): Promise<void> {
    const args = {
      start_x: startX,
      start_y: startY,
      end_x: endX,
      end_y: endY,
      duration_ms: durationMs
    };
    
    try {
      await this.callMcpTool('swipe', args);
    } catch (error) {
      throw new APIError(`Failed to perform swipe: ${error}`);
    }
  }

  /**
   * Clicks on the screen at the specified coordinates.
   * 
   * @param x - The X coordinate.
   * @param y - The Y coordinate.
   * @param button - The mouse button to use. Default is 'left'.
   * @throws Error if the operation fails.
   */
  async click(x: number, y: number, button: string = 'left'): Promise<void> {
    const args = {
      x,
      y,
      button
    };
    
    try {
      await this.callMcpTool('click', args);
    } catch (error) {
      throw new APIError(`Failed to perform click: ${error}`);
    }
  }

  /**
   * Takes a screenshot of the current screen.
   * 
   * @returns The screenshot data.
   * @throws Error if the operation fails.
   */
  async screenshot(): Promise<string> {
    const args = {};
    
    try {
      return await this.callMcpTool('system_screenshot', args);
    } catch (error) {
      throw new APIError(`Failed to take screenshot: ${error}`);
    }
  }
}
