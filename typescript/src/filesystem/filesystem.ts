import { APIError } from '../exceptions';
import { Session } from '../session';
import { CallMcpToolRequest } from '../api/models/model';
import * as $_client from '../api';
import { log, logError } from '../utils/logger';

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
 * Handles file operations in the AgentBay cloud environment.
 */
export class FileSystem {
  private session: Session;
  private client!: $_client.Client;
  private baseUrl!: string;

  /**
   * Initialize a FileSystem object.
   * 
   * @param session - The Session instance that this FileSystem belongs to.
   */
  constructor(session: Session) {
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
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: toolName,
        args: argsJSON
      });
      
      // Log API request
      log(`API Call: CallMcpTool - ${toolName}`);
      log(`Request: SessionId=${this.session.getSessionId()}, Args=${argsJSON}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool - ${toolName}:`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract data from response
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
   * Creates a new directory at the specified path.
   * 
   * @param path - Path to the directory to create.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async createDirectory(path: string): Promise<any> {
    const args = {
      path
    };
    
    const result = await this.callMcpTool('create_directory', args, 'Failed to create directory');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Edits a file by replacing occurrences of oldText with newText.
   * 
   * @param path - Path to the file to edit.
   * @param edits - Array of edit operations, each containing oldText and newText.
   * @param dryRun - Optional: If true, preview changes without applying them.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async editFile(path: string, edits: Array<{oldText: string, newText: string}>, dryRun: boolean = false): Promise<any> {
    const args = {
      path,
      edits,
      dryRun
    };
    
    const result = await this.callMcpTool('edit_file', args, 'Failed to edit file');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Gets information about a file or directory.
   * 
   * @param path - Path to the file or directory to inspect.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async getFileInfo(path: string): Promise<any> {
    const args = {
      path
    };
    
    const result = await this.callMcpTool('get_file_info', args, 'Failed to get file info');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Lists the contents of a directory.
   * 
   * @param path - Path to the directory to list.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async listDirectory(path: string): Promise<any> {
    const args = {
      path
    };
    
    const result = await this.callMcpTool('list_directory', args, 'Failed to list directory');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Moves a file or directory from source to destination.
   * 
   * @param source - Path to the source file or directory.
   * @param destination - Path to the destination file or directory.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async moveFile(source: string, destination: string): Promise<any> {
    const args = {
      source,
      destination
    };
    
    const result = await this.callMcpTool('move_file', args, 'Failed to move file');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Reads the content of a file.
   * 
   * @param path - Path to the file to read.
   * @param offset - Optional: Line offset to start reading from.
   * @param length - Optional: Number of lines to read. If 0, reads the entire file.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async readFile(path: string, offset: number = 0, length: number = 0): Promise<any> {
    const args: Record<string, any> = {
      path
    };
    
    if (offset > 0) {
      args.offset = offset;
    }
    
    if (length > 0) {
      args.length = length;
    }
    
    const result = await this.callMcpTool('read_file', args, 'Failed to read file');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Reads the content of multiple files.
   * 
   * @param paths - Array of file paths to read.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async readMultipleFiles(paths: string[]): Promise<any> {
    const args = {
      paths
    };
    
    const result = await this.callMcpTool('read_multiple_files', args, 'Failed to read multiple files');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Searches for files in a directory that match a pattern.
   * 
   * @param path - Path to the directory to search in.
   * @param pattern - Pattern to search for. Supports glob patterns.
   * @param excludePatterns - Optional: Array of patterns to exclude.
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async searchFiles(path: string, pattern: string, excludePatterns: string[] = []): Promise<any> {
    const args: Record<string, any> = {
      path,
      pattern
    };
    
    if (excludePatterns.length > 0) {
      args.exclude_patterns = excludePatterns;
    }
    
    const result = await this.callMcpTool('search_files', args, 'Failed to search files');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Writes content to a file.
   * 
   * @param path - Path to the file to write.
   * @param content - Content to write to the file.
   * @param mode - Optional: Write mode. One of "overwrite", "append", or "create_new". Default is "overwrite".
   * @returns The content field from the API response
   * @throws APIError if the operation fails.
   */
  async writeFile(path: string, content: string, mode: string = 'overwrite'): Promise<any> {
    // Validate mode
    const validModes = ['overwrite', 'append', 'create_new'];
    if (!validModes.includes(mode)) {
      throw new APIError(`Invalid mode: ${mode}. Must be one of ${validModes.join(', ')}`);
    }
    
    const args = {
      path,
      content,
      mode
    };
    
    const result = await this.callMcpTool('write_file', args, 'Failed to write file');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }
}
