import { APIError } from '../exceptions';
import { Session } from '../session';
import { CallMcpToolRequest } from '../api/models/model';
import * as $_client from '../api';
import { log, logError } from '../utils/logger';

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
   * Creates a new directory at the specified path.
   * 
   * @param path - Path to the directory to create.
   * @returns True if the directory was created successfully.
   * @throws APIError if the operation fails.
   */
  async createDirectory(path: string): Promise<boolean> {
    try {
      const args = {
        path
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'create_directory',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (create_directory)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=create_directory, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (create_directory):`, response.body);
      
      return true;
    } catch (error) {
      logError("Error calling CallMcpTool (create_directory):", error);
      throw new APIError(`Failed to create directory: ${error}`);
    }
  }

  /**
   * Edits a file by replacing occurrences of oldText with newText.
   * 
   * @param path - Path to the file to edit.
   * @param edits - Array of edit operations, each containing oldText and newText.
   * @param dryRun - Optional: If true, preview changes without applying them.
   * @returns True if the file was edited successfully.
   * @throws APIError if the operation fails.
   */
  async editFile(path: string, edits: Array<{oldText: string, newText: string}>, dryRun: boolean = false): Promise<boolean> {
    try {
      const args = {
        path,
        edits,
        dryRun
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'edit_file',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (edit_file)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=edit_file, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (edit_file):`, response.body);
      
      return true;
    } catch (error) {
      logError("Error calling CallMcpTool (edit_file):", error);
      throw new APIError(`Failed to edit file: ${error}`);
    }
  }

  /**
   * Gets information about a file or directory.
   * 
   * @param path - Path to the file or directory to inspect.
   * @returns Information about the file or directory.
   * @throws APIError if the operation fails.
   */
  async getFileInfo(path: string): Promise<Record<string, any>> {
    try {
      const args = {
        path
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'get_file_info',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (get_file_info)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=get_file_info, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (get_file_info):`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      const data = response.body.data as any;
      
      // Check if there's an error in the response
      if (data.isError) {
        const contentArray = data.content;
        if (contentArray && Array.isArray(contentArray) && contentArray.length > 0) {
          const contentItem = contentArray[0];
          if (contentItem && typeof contentItem === 'object' && 'text' in contentItem) {
            const text = contentItem.text;
            if (text && text.includes('No such file or directory')) {
              throw new Error(`File not found: ${path}`);
            } else {
              throw new Error(text);
            }
          }
        }
        throw new Error('Error getting file info');
      }
      
      // Try to parse file info from the content field
      const contentArray = data.content;
      if (contentArray && Array.isArray(contentArray) && contentArray.length > 0) {
        const contentItem = contentArray[0];
        if (contentItem && typeof contentItem === 'object' && 'text' in contentItem) {
          const text = contentItem.text;
          
          // Parse the text to extract file info
          const result: Record<string, any> = {};
          
          // Extract the file name from the path
          const parts = path.split('/');
          if (parts.length > 0) {
            result.name = parts[parts.length - 1];
          }
          
          const lines = text.split('\n');
          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine === '') {
              continue;
            }
            
            const parts = trimmedLine.split(':');
            if (parts.length !== 2) {
              continue;
            }
            
            const key = parts[0].trim();
            const value = parts[1].trim();
            
            switch (key) {
              case 'size':
                result.size = parseFloat(value);
                break;
              case 'isDirectory':
                result.isDirectory = value === 'true';
                break;
              case 'isFile':
                result.isFile = value === 'true';
                break;
              case 'modified':
                result.modifiedTime = value;
                break;
              case 'created':
                if (value !== 'N/A') {
                  result.createdTime = value;
                }
                break;
              case 'accessed':
                if (value !== 'N/A') {
                  result.accessedTime = value;
                }
                break;
              case 'permissions':
                result.permissions = value;
                break;
            }
          }
          
          return result;
        }
      }
      
      return data;
    } catch (error) {
      logError("Error calling CallMcpTool (get_file_info):", error);
      throw new APIError(`Failed to get file info: ${error}`);
    }
  }

  /**
   * Lists the contents of a directory.
   * 
   * @param path - Path to the directory to list.
   * @returns Array of directory entries.
   * @throws APIError if the operation fails.
   */
  async listDirectory(path: string): Promise<Array<Record<string, any>>> {
    try {
      const args = {
        path
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'list_directory',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (list_directory)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=list_directory, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (list_directory):`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      const data = response.body.data as any;
      
      // First try to get the entries field
      if (data.entries && Array.isArray(data.entries)) {
        return data.entries;
      }
      
      // If entries field is not found, try to parse from content field
      const contentArray = data.content;
      if (!contentArray || !Array.isArray(contentArray)) {
        throw new Error('Neither entries nor content field found in response');
      }
      
      // Parse the content from the text chunks
      const result: Array<Record<string, any>> = [];
      for (const item of contentArray) {
        if (!item || typeof item !== 'object' || !('text' in item)) {
          continue;
        }
        
        const text = item.text;
        if (typeof text !== 'string') {
          continue;
        }
        
        // Parse the text to extract directory entries
        const lines = text.split('\n');
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine === '') {
            continue;
          }
          
          const entryMap: Record<string, any> = {};
          if (trimmedLine.startsWith('[DIR]')) {
            entryMap.isDirectory = true;
            entryMap.name = trimmedLine.substring('[DIR]'.length).trim();
          } else if (trimmedLine.startsWith('[FILE]')) {
            entryMap.isDirectory = false;
            entryMap.name = trimmedLine.substring('[FILE]'.length).trim();
          } else {
            // Skip lines that don't match the expected format
            continue;
          }
          
          result.push(entryMap);
        }
      }
      
      // If we couldn't parse any entries, return an error
      if (result.length === 0) {
        throw new Error('Could not parse directory entries from response');
      }
      
      return result;
    } catch (error) {
      logError("Error calling CallMcpTool (list_directory):", error);
      throw new APIError(`Failed to list directory: ${error}`);
    }
  }

  /**
   * Moves a file or directory from source to destination.
   * 
   * @param source - Path to the source file or directory.
   * @param destination - Path to the destination file or directory.
   * @returns True if the file was moved successfully.
   * @throws APIError if the operation fails.
   */
  async moveFile(source: string, destination: string): Promise<boolean> {
    try {
      const args = {
        source,
        destination
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'move_file',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (move_file)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=move_file, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (move_file):`, response.body);
      
      return true;
    } catch (error) {
      logError("Error calling CallMcpTool (move_file):", error);
      throw new APIError(`Failed to move file: ${error}`);
    }
  }

  /**
   * Read the contents of a file in the cloud environment.
   * 
   * @param path - Path to the file to read.
   * @param offset - Optional: Start reading from this byte offset.
   * @param length - Optional: Number of bytes to read. If 0, read to end of file.
   * @returns The contents of the file.
   * @throws APIError if the operation fails.
   */
  async readFile(path: string, offset: number = 0, length: number = 0): Promise<string> {
    try {
      const args: Record<string, any> = {
        path
      };
      
      // Only include optional parameters if they are non-default values
      if (offset > 0) {
        args.offset = offset;
      }
      if (length > 0) {
        args.length = length;
      }
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'read_file',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (read_file)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=read_file, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (read_file):`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract content from response
      const data = response.body.data as any;
      
      // First try to get the content as a string
      if (typeof data.content === 'string') {
        return data.content;
      }
      
      // If content is not a string, try to handle it as an array of text chunks
      if (Array.isArray(data.content)) {
        let fullText = '';
        for (const item of data.content) {
          if (item && typeof item === 'object' && 'text' in item) {
            fullText += item.text;
            // Only add newline if not the last item
            if (item !== data.content[data.content.length - 1]) {
              fullText += '\n';
            }
          }
        }
        return fullText;
      }
      
      throw new Error('Content field not found or has unexpected format');
    } catch (error) {
      logError("Error calling CallMcpTool (read_file):", error);
      throw new APIError(`Failed to read file: ${error}`);
    }
  }
  
  /**
   * Reads the contents of multiple files.
   * 
   * @param paths - Array of paths to the files to read.
   * @returns Object mapping file paths to their contents.
   * @throws APIError if the operation fails.
   */
  async readMultipleFiles(paths: string[]): Promise<Record<string, string>> {
    try {
      const args = {
        paths
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'read_multiple_files',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (read_multiple_files)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=read_multiple_files, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (read_multiple_files):`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      const data = response.body.data as any;
      
      // First try to get the files field
      if (data.files && typeof data.files === 'object') {
        return data.files;
      }
      
      // If files field is not found, try to parse from content field
      const contentArray = data.content;
      if (!contentArray || !Array.isArray(contentArray)) {
        throw new Error('Neither files nor content field found in response');
      }
      
      // Parse the content from the text chunks
      const result: Record<string, string> = {};
      for (const item of contentArray) {
        if (!item || typeof item !== 'object' || !('text' in item)) {
          continue;
        }
        
        const text = item.text;
        if (typeof text !== 'string') {
          continue;
        }
        
        // Parse the text to extract file contents
        const lines = text.split('\n');
        let currentPath = '';
        let currentContent = '';
        let inContent = false;
        
        for (const line of lines) {
          if (line.endsWith(':')) {
            // This is a file path line
            if (currentPath !== '' && currentContent.length > 0) {
              // Save the previous file content
              result[currentPath] = currentContent.trim();
              currentContent = '';
            }
            currentPath = line.substring(0, line.length - 1);
            inContent = true;
          } else if (line === '---') {
            // This is a separator line
            if (currentPath !== '' && currentContent.length > 0) {
              // Save the previous file content
              result[currentPath] = currentContent.trim();
              currentContent = '';
            }
            inContent = false;
          } else if (inContent) {
            // This is a content line
            if (currentContent.length > 0) {
              currentContent += '\n';
            }
            currentContent += line;
          }
        }
        
        // Save the last file content
        if (currentPath !== '' && currentContent.length > 0) {
          result[currentPath] = currentContent.trim();
        }
      }
      
      // If we couldn't parse any files, return an error
      if (Object.keys(result).length === 0) {
        throw new Error('Could not parse file contents from response');
      }
      
      return result;
    } catch (error) {
      logError("Error calling CallMcpTool (read_multiple_files):", error);
      throw new APIError(`Failed to read multiple files: ${error}`);
    }
  }
  
  /**
   * Searches for files matching a pattern in a directory.
   * 
   * @param path - Path to the directory to start the search.
   * @param pattern - Pattern to match.
   * @param excludePatterns - Optional: Patterns to exclude.
   * @returns Array of search results.
   * @throws APIError if the operation fails.
   */
  async searchFiles(path: string, pattern: string, excludePatterns: string[] = []): Promise<Array<Record<string, any>>> {
    try {
      const args: Record<string, any> = {
        path,
        pattern
      };
      
      // Only include excludePatterns if non-empty
      if (excludePatterns.length > 0) {
        args.excludePatterns = excludePatterns;
      }
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'search_files',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (search_files)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=search_files, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (search_files):`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      const data = response.body.data as any;
      
      // First try to get the results field
      if (data.results && Array.isArray(data.results)) {
        return data.results;
      }
      
      // If results field is not found, try to parse from content field
      const contentArray = data.content;
      if (!contentArray || !Array.isArray(contentArray)) {
        throw new Error('Neither results nor content field found in response');
      }
      
      // Parse the content from the text chunks
      const searchResults: Array<Record<string, any>> = [];
      for (const item of contentArray) {
        if (!item || typeof item !== 'object' || !('text' in item)) {
          continue;
        }
        
        const text = item.text;
        if (typeof text !== 'string') {
          continue;
        }
        
        // Check if no matches were found
        if (text.includes('No matches found')) {
          // Return an empty array for no matches
          return searchResults;
        }
        
        // First, try to parse as a simple list of file paths
        if (!text.includes('File:') && !text.includes('Line')) {
          const lines = text.split('\n');
          for (const line of lines) {
            const trimmedLine = line.trim();
            if (trimmedLine === '') {
              continue;
            }
            
            // Create a result entry for each file path
            const resultMap: Record<string, any> = {
              path: trimmedLine
            };
            searchResults.push(resultMap);
          }
          
          // If we found any results in this format, return them
          if (searchResults.length > 0) {
            return searchResults;
          }
        }
        
        // If not a simple list of paths, try the more complex format
        const lines = text.split('\n');
        let currentFile = '';
        let matches: Array<Record<string, any>> = [];
        
        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine === '') {
            continue;
          }
          
          if (trimmedLine.startsWith('File:')) {
            // This is a file path line
            if (currentFile !== '' && matches.length > 0) {
              // Save the previous file's matches
              const resultMap: Record<string, any> = {
                path: currentFile,
                matches
              };
              searchResults.push(resultMap);
              matches = [];
            }
            currentFile = trimmedLine.substring('File:'.length).trim();
            matches = [];
          } else if (trimmedLine.startsWith('Line') && currentFile !== '') {
            // This is a match line
            const parts = trimmedLine.split(':', 2);
            if (parts.length === 2) {
              const lineNum = parts[0].substring('Line'.length).trim();
              const lineContent = parts[1].trim();
              
              // Try to parse line number
              const lineNumber = parseInt(lineNum, 10);
              
              const match: Record<string, any> = {
                line: lineNumber,
                content: lineContent
              };
              matches.push(match);
            }
          }
        }
        
        // Save the last file's matches
        if (currentFile !== '' && matches.length > 0) {
          const resultMap: Record<string, any> = {
            path: currentFile,
            matches
          };
          searchResults.push(resultMap);
        }
      }
      
      return searchResults;
    } catch (error) {
      logError("Error calling CallMcpTool (search_files):", error);
      throw new APIError(`Failed to search files: ${error}`);
    }
  }
  
  /**
   * Writes content to a file.
   * 
   * @param path - Path to the file to write.
   * @param content - Content to write to the file.
   * @param mode - Optional: "overwrite" (default) or "append".
   * @returns True if the file was written successfully.
   * @throws APIError if the operation fails.
   */
  async writeFile(path: string, content: string, mode: string = 'overwrite'): Promise<boolean> {
    try {
      const args = {
        path,
        content,
        mode
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'write_file',
        args: JSON.stringify(args)
      });
      
      // Log API request
      log("API Call: CallMcpTool (write_file)");
      log(`Request: SessionId=${this.session.getSessionId()}, Name=write_file, Args=${JSON.stringify({
        path,
        mode,
        contentLength: content.length
      })}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool (write_file):`, response.body);
      
      return true;
    } catch (error) {
      logError("Error calling CallMcpTool (write_file):", error);
      throw new APIError(`Failed to write file: ${error}`);
    }
  }
}
