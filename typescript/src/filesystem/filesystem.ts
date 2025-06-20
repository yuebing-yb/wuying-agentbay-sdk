import { APIError } from '../exceptions';
import { Session } from '../session';
import { CallMcpToolRequest } from '../api/models/model';
import * as $_client from '../api';
import { log, logError } from '../utils/logger';

// Default chunk size for large file operations (60KB)
const DEFAULT_CHUNK_SIZE = 60 * 1024;

// File operations that might contain large content
const FILE_OPERATIONS: { [key: string]: boolean } = {
  'read_file': true,
  'write_file': true,
  'read_multiple_files': true
};

/**
 * Checks if the tool operation is file-related and might contain large content
 * 
 * @param toolName - Name of the MCP tool
 * @returns True if the operation is file-related
 */
function isFileOperation(toolName: string): boolean {
  return FILE_OPERATIONS[toolName] === true;
}

/**
 * Replaces large content with size information in JSON args for logging
 * 
 * @param args - Arguments object to truncate
 * @returns Truncated arguments object for logging
 */
function truncateContentForLogging(args: Record<string, any>): Record<string, any> {
  const truncatedArgs = { ...args };
  
  // Check for content field and replace with length info
  if (typeof truncatedArgs.content === 'string') {
    const contentLength = truncatedArgs.content.length;
    truncatedArgs.content = `[Content length: ${contentLength} bytes]`;
  }
  
  // Check for paths array and log number of paths instead of all paths
  if (Array.isArray(truncatedArgs.paths) && truncatedArgs.paths.length > 3) {
    truncatedArgs.paths = `[${truncatedArgs.paths.length} paths, first few: ${truncatedArgs.paths[0]}, ${truncatedArgs.paths[1]}, ${truncatedArgs.paths[2]}, ...]`;
  }
  
  return truncatedArgs;
}

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
      // Handle logging differently based on operation type
      let loggableArgs = args;
      if (isFileOperation(toolName)) {
        // For file operations, truncate content for logging
        loggableArgs = truncateContentForLogging(args);
      }
      
      const argsJSON = JSON.stringify(args);
      const loggableArgsJSON = JSON.stringify(loggableArgs);
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: toolName,
        args: argsJSON
      });
      
      // Log API request
      log(`API Call: CallMcpTool - ${toolName}`);
      log(`Request: SessionId=${this.session.getSessionId()}, Args=${loggableArgsJSON}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response differently based on operation type
      if (isFileOperation(toolName)) {
        // Log content size for file operations instead of full content
        log(`Response from CallMcpTool - ${toolName} - status: ${response.statusCode}`);
        
        // Log only relevant response information without content
        if (response.body?.data) {
          const data = response.body.data as Record<string, any>;
          if (data.isError === true) {
            log(`Response contains error: ${data.isError}`);
          } else {
            // For successful responses, don't log the content at all
            log('Response successful, content length info provided separately');
            
            // If there's content, log its size instead of the actual content
            if (Array.isArray(data.content) && data.content.length > 0) {
              let totalSize = 0;
              for (const item of data.content) {
                if (item && typeof item === 'object' && item.text && typeof item.text === 'string') {
                  totalSize += item.text.length;
                }
              }
              log(`Content size: ${totalSize} bytes`);
            }
          }
        }
      } else {
        // For non-file operations, create a sanitized version of the response body
        // that doesn't include large content fields
        const sanitizedBody = { ...response.body };
        if (sanitizedBody.data && typeof sanitizedBody.data === 'object') {
          const sanitizedData = { ...sanitizedBody.data };
          if (Array.isArray(sanitizedData.content)) {
            sanitizedData.content = `[Array with ${sanitizedData.content.length} items]`;
          }
          sanitizedBody.data = sanitizedData;
        }
        log(`Response from CallMcpTool - ${toolName}:`, sanitizedBody);
      }
      
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

  /**
   * Reads a large file in chunks to handle size limitations of the underlying API.
   * It automatically splits the read operation into multiple requests of chunkSize bytes each.
   * 
   * @param path - Path to the file to read.
   * @param chunkSize - Optional: Size of each chunk in bytes. Default is 60KB.
   * @returns The complete file content as a string
   * @throws APIError if the operation fails.
   */
  async readLargeFile(path: string, chunkSize: number = DEFAULT_CHUNK_SIZE): Promise<string> {
    // First get the file size
    const fileInfo = await this.getFileInfo(path);
    
    // Extract file size from the content array
    if (!Array.isArray(fileInfo) || fileInfo.length === 0) {
      throw new APIError('Invalid file info format');
    }
    
    // Get the first content item
    const contentItem = fileInfo[0];
    if (!contentItem || typeof contentItem !== 'object' || !contentItem.text || typeof contentItem.text !== 'string') {
      throw new APIError('Invalid file info content item format');
    }
    
    // Extract the text field which contains the file info
    const infoText = contentItem.text;
    
    // Parse the size from the text
    let fileSize = 0;
    for (const line of infoText.split('\n')) {
      if (line.startsWith('size:')) {
        const sizeStr = line.substring('size:'.length).trim();
        fileSize = parseInt(sizeStr, 10);
        if (isNaN(fileSize)) {
          throw new APIError(`Couldn't parse file size: ${sizeStr}`);
        }
        break;
      }
    }
    
    if (fileSize === 0) {
      throw new APIError('Couldn\'t determine file size');
    }
    
    // Prepare to read the file in chunks
    let result = '';
    let offset = 0;
    
    log(`ReadLargeFile: Starting chunked read of ${path} (total size: ${fileSize} bytes, chunk size: ${chunkSize} bytes)`);
    
    let chunkCount = 0;
    while (offset < fileSize) {
      // Calculate how much to read in this chunk
      let length = chunkSize;
      if (offset + length > fileSize) {
        length = fileSize - offset;
      }
      
      log(`ReadLargeFile: Reading chunk ${chunkCount + 1} (${length} bytes at offset ${offset}/${fileSize})`);
      
      try {
        // Read the chunk
        const chunk = await this.readFile(path, offset, length);
        
        // Extract text from the content array
        if (!Array.isArray(chunk) || chunk.length === 0) {
          throw new APIError(`Invalid chunk format at offset ${offset}`);
        }
        
        // Process each content item
        for (const item of chunk) {
          if (item && typeof item === 'object' && item.text && typeof item.text === 'string') {
            result += item.text;
          }
        }
        
        // Move to the next chunk
        offset += length;
        chunkCount++;
      } catch (error) {
        logError(`Error reading chunk at offset ${offset}: ${error}`);
        throw new APIError(`Error reading chunk at offset ${offset}: ${error}`);
      }
    }
    
    log(`ReadLargeFile: Successfully read ${path} in ${chunkCount} chunks (total: ${fileSize} bytes)`);
    
    return result;
  }
  
  /**
   * Writes a large file in chunks to handle size limitations of the underlying API.
   * It automatically splits the write operation into multiple requests of chunkSize bytes each.
   * 
   * @param path - Path to the file to write.
   * @param content - Content to write to the file.
   * @param chunkSize - Optional: Size of each chunk in bytes. Default is 60KB.
   * @returns True if the operation was successful
   * @throws APIError if the operation fails.
   */
  async writeLargeFile(path: string, content: string, chunkSize: number = DEFAULT_CHUNK_SIZE): Promise<boolean> {
    const contentLen = content.length;
    
    log(`WriteLargeFile: Starting chunked write to ${path} (total size: ${contentLen} bytes, chunk size: ${chunkSize} bytes)`);
    
    // If content is small enough, use the regular WriteFile method
    if (contentLen <= chunkSize) {
      log(`WriteLargeFile: Content size (${contentLen} bytes) is smaller than chunk size, using normal WriteFile`);
      await this.writeFile(path, content, 'overwrite');
      return true;
    }
    
    // Write the first chunk with "overwrite" mode to create/clear the file
    const firstChunkEnd = Math.min(chunkSize, contentLen);
    
    log(`WriteLargeFile: Writing first chunk (0-${firstChunkEnd} bytes) with overwrite mode`);
    await this.writeFile(path, content.substring(0, firstChunkEnd), 'overwrite');
    
    // Write the remaining chunks with "append" mode
    let chunkCount = 1; // Already wrote first chunk
    for (let offset = firstChunkEnd; offset < contentLen;) {
      const end = Math.min(offset + chunkSize, contentLen);
      
      log(`WriteLargeFile: Writing chunk ${chunkCount + 1} (${offset}-${end} bytes) with append mode`);
      await this.writeFile(path, content.substring(offset, end), 'append');
      
      offset = end;
      chunkCount++;
    }
    
    log(`WriteLargeFile: Successfully wrote ${path} in ${chunkCount} chunks (total: ${contentLen} bytes)`);
    
    return true;
  }
}
