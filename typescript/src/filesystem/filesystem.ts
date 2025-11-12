import {
  BoolResult,
  FileInfoResult,
  DirectoryListResult,
  FileContentResult,
  MultipleFileContentResult,
  FileSearchResult,
  ApiResponse,
} from "../types/api-response";
import { UploadResult, DownloadResult } from "./file-transfer";
import { FileTransfer } from "./file-transfer";
import { Session } from "../session";
import { log, logWarn } from "../utils/logger";

// Default chunk size for large file operations (60KB)
const DEFAULT_CHUNK_SIZE = 60 * 1024;

/**
 * Represents a single file change event
 */
export interface FileChangeEvent {
  eventType: string; // "create", "modify", "delete"
  path: string;
  pathType: string;  // "file", "directory"
}

/**
 * Result of file change detection operations
 */
export interface FileChangeResult extends ApiResponse {
  events: FileChangeEvent[];
  rawData: string;
}

/**
 * Helper functions for FileChangeEvent
 */
export class FileChangeEventHelper {
  static toString(event: FileChangeEvent): string {
    return `FileChangeEvent(eventType='${event.eventType}', path='${event.path}', pathType='${event.pathType}')`;
  }

  static toDict(event: FileChangeEvent): Record<string, string> {
    return {
      eventType: event.eventType,
      path: event.path,
      pathType: event.pathType,
    };
  }

  static fromDict(data: Record<string, any>): FileChangeEvent {
    return {
      eventType: data.eventType || "",
      path: data.path || "",
      pathType: data.pathType || "",
    };
  }
}

/**
 * Helper functions for FileChangeResult
 */
export class FileChangeResultHelper {
  static hasChanges(result: FileChangeResult): boolean {
    return result.events.length > 0;
  }

  static getModifiedFiles(result: FileChangeResult): string[] {
    return result.events
      .filter(event => event.eventType === "modify" && event.pathType === "file")
      .map(event => event.path);
  }

  static getCreatedFiles(result: FileChangeResult): string[] {
    return result.events
      .filter(event => event.eventType === "create" && event.pathType === "file")
      .map(event => event.path);
  }

  static getDeletedFiles(result: FileChangeResult): string[] {
    return result.events
      .filter(event => event.eventType === "delete" && event.pathType === "file")
      .map(event => event.path);
  }
}

/**
 * FileInfo represents information about a file or directory
 */
export interface FileInfo {
  name: string;
  path: string;
  size: number;
  isDirectory: boolean;
  modTime: string;
  mode: string;
  owner?: string;
  group?: string;
}

/**
 * DirectoryEntry represents an entry in a directory listing
 */
export interface DirectoryEntry {
  name: string;
  isDirectory: boolean;
}

/**
 * Parse a file info string into a FileInfo object
 *
 * @param fileInfoStr - The file info string to parse
 * @returns A FileInfo object
 */
function parseFileInfo(fileInfoStr: string): FileInfo {
  const result: FileInfo = {
    name: "",
    path: "",
    size: 0,
    isDirectory: false,
    modTime: "",
    mode: "",
  };

  const lines = fileInfoStr.split("\n");
  for (const line of lines) {
    if (line.includes(":")) {
      const [key, value] = line.split(":", 2).map((part) => part.trim());

      switch (key) {
        case "name":
          result.name = value;
          break;
        case "path":
          result.path = value;
          break;
        case "size":
          result.size = parseInt(value, 10);
          break;
        case "isDirectory":
          result.isDirectory = value === "true";
          break;
        case "modTime":
          result.modTime = value;
          break;
        case "mode":
          result.mode = value;
          break;
        case "owner":
          result.owner = value;
          break;
        case "group":
          result.group = value;
          break;
      }
    }
  }

  return result;
}

/**
 * Parse a directory listing string into an array of DirectoryEntry objects
 *
 * @param text - The directory listing text to parse
 * @returns An array of DirectoryEntry objects
 */
function parseDirectoryListing(text: string): DirectoryEntry[] {
  const result: DirectoryEntry[] = [];
  const lines = text.split("\n");

  for (const line of lines) {
    const trimmedLine = line.trim();
    if (trimmedLine === "") {
      continue;
    }

    if (trimmedLine.startsWith("[DIR]")) {
      result.push({
        isDirectory: true,
        name: trimmedLine.replace("[DIR]", "").trim(),
      });
    } else if (trimmedLine.startsWith("[FILE]")) {
      result.push({
        isDirectory: false,
        name: trimmedLine.replace("[FILE]", "").trim(),
      });
    }
  }

  return result;
}

/**
 * Handles file operations in the AgentBay cloud environment.
 */
export class FileSystem {
  private session: Session;
  
  private _fileTransfer: FileTransfer | null = null;

  /**
   * Initialize a FileSystem object.
   *
   * @param session - The Session instance that this FileSystem belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Ensure FileTransfer is initialized with the current session.
   * 
   * @returns The FileTransfer instance
   */
  private _ensureFileTransfer(): FileTransfer {
    if (this._fileTransfer === null) {
      // Get the agent_bay instance from the session
      const agentBay = this.session.getAgentBay();
      if (agentBay === undefined) {
        throw new Error("FileTransfer requires an AgentBay instance");
      }
      
      this._fileTransfer = new FileTransfer(agentBay, this.session);
    }
    
    return this._fileTransfer;
  }

  /**
   * Creates a new directory at the specified path.
   * Corresponds to Python's create_directory() method
   *
   * @param path - Path to the directory to create.
   * @returns BoolResult with creation result and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateCreateDirectory() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a directory
   *       const createResult = await session.fileSystem.createDirectory('/tmp/mydir');
   *       if (createResult.success) {
   *         console.log('Directory created successfully');
   *         // Output: Directory created successfully
   *         console.log(`Request ID: ${createResult.requestId}`);
   *         // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
   *       }
   *
   *       // Create nested directories
   *       const nestedResult = await session.fileSystem.createDirectory('/tmp/parent/child/grandchild');
   *       if (nestedResult.success) {
   *         console.log('Nested directories created');
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateCreateDirectory().catch(console.error);
   * ```
   */
  async createDirectory(path: string): Promise<BoolResult> {
    try {
      const args = {
        path,
      };

      const result = await this.session.callMcpTool(
        "create_directory",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        data: true,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to create directory: ${error}`,
      };
    }
  }

  /**
   * Edits a file by replacing occurrences of oldText with newText.
   * Corresponds to Python's edit_file() method
   *
   * @param path - Path to the file to edit.
   * @param edits - Array of edit operations, each containing oldText and newText.
   * @param dryRun - Optional: If true, preview changes without applying them.
   * @returns BoolResult with edit result and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateEditFile() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a test file
   *       await session.fileSystem.writeFile('/tmp/config.txt', 'DEBUG=false\\nLOG_LEVEL=info');
   *
   *       // Edit the file with single replacement
   *       const edits = [{ oldText: 'DEBUG=false', newText: 'DEBUG=true' }];
   *       const editResult = await session.fileSystem.editFile('/tmp/config.txt', edits);
   *       if (editResult.success) {
   *         console.log('File edited successfully');
   *         // Output: File edited successfully
   *       }
   *
   *       // Edit with multiple replacements
   *       const multiEdits = [
   *         { oldText: 'DEBUG=true', newText: 'DEBUG=false' },
   *         { oldText: 'LOG_LEVEL=info', newText: 'LOG_LEVEL=debug' }
   *       ];
   *       const multiEditResult = await session.fileSystem.editFile('/tmp/config.txt', multiEdits);
   *       if (multiEditResult.success) {
   *         console.log('Multiple edits applied');
   *       }
   *
   *       // Preview changes with dry_run
   *       const dryRunResult = await session.fileSystem.editFile(
   *         '/tmp/config.txt',
   *         [{ oldText: 'debug', newText: 'trace' }],
   *         true
   *       );
   *       if (dryRunResult.success) {
   *         console.log('Dry run completed, no changes applied');
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateEditFile().catch(console.error);
   * ```
   */
  async editFile(
    path: string,
    edits: Array<{ oldText: string; newText: string }>,
    dryRun = false
  ): Promise<BoolResult> {
    try {
      const args = {
        path,
        edits,
        dryRun,
      };

      const result = await this.session.callMcpTool(
        "edit_file",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        data: true,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to edit file: ${error}`,
      };
    }
  }

  /**
   * Gets information about a file or directory.
   * Corresponds to Python's get_file_info() method
   *
   * @param path - Path to the file or directory to inspect.
   * @returns FileInfoResult with file info and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateGetFileInfo() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a test file
   *       await session.fileSystem.writeFile('/tmp/test.txt', 'Sample content');
   *
   *       // Get file information
   *       const infoResult = await session.fileSystem.getFileInfo('/tmp/test.txt');
   *       if (infoResult.success) {
   *         console.log(`File info: ${JSON.stringify(infoResult.fileInfo)}`);
   *         // Output: File info: {"size": 14, "isDirectory": false, ...}
   *         console.log(`Size: ${infoResult.fileInfo.size} bytes`);
   *         // Output: Size: 14 bytes
   *         console.log(`Is directory: ${infoResult.fileInfo.isDirectory}`);
   *         // Output: Is directory: false
   *       }
   *
   *       // Get directory information
   *       await session.fileSystem.createDirectory('/tmp/mydir');
   *       const dirInfo = await session.fileSystem.getFileInfo('/tmp/mydir');
   *       if (dirInfo.success) {
   *         console.log(`Is directory: ${dirInfo.fileInfo.isDirectory}`);
   *         // Output: Is directory: true
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetFileInfo().catch(console.error);
   * ```
   */
  async getFileInfo(path: string): Promise<FileInfoResult> {
    try {
      const args = {
        path,
      };

      const result = await this.session.callMcpTool(
        "get_file_info",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          fileInfo: {},
          errorMessage: result.errorMessage,
        };
      }

      // Parse and return the file info
      if (!result.data) {
        return {
          requestId: result.requestId,
          success: false,
          fileInfo: {},
          errorMessage: "Empty response from get_file_info",
        };
      }

      const fileInfo = parseFileInfo(result.data);

      return {
        requestId: result.requestId,
        success: true,
        fileInfo,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to get file info: ${error}`,
      };
    }
  }

  /**
   * Lists the contents of a directory.
   * Corresponds to Python's list_directory() method
   *
   * @param path - Path to the directory to list.
   * @returns DirectoryListResult with directory entries and requestId
   */
  /**
   * Lists the contents of a directory.
   *
   * @param path - Absolute path to the directory to list.
   *
   * @returns Promise resolving to DirectoryListResult containing array of entries.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   *
   * if (result.success) {
   *   const session = result.session;
   *
   *   // List directory contents
   *   const listResult = await session.fileSystem.listDirectory('/tmp');
   *   if (listResult.success) {
   *     console.log(`Found ${listResult.entries.length} entries`);
   *     for (const entry of listResult.entries) {
   *       console.log(`${entry.name} (${entry.isDirectory ? 'dir' : 'file'})`);
   *     }
   *   }
   *
   *   await session.delete();
   * }
   * ```
   *
   * @see {@link readFile}, {@link writeFile}
   */
  async listDirectory(path: string): Promise<DirectoryListResult> {
    try {
      const args = {
        path,
      };

      const result = await this.session.callMcpTool(
        "list_directory",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          entries: [],
          errorMessage: result.errorMessage,
        };
      }

      // Parse the text content into directory entries
      const entries = result.data
        ? parseDirectoryListing(result.data)
        : [];

      return {
        requestId: result.requestId,
        success: true,
        entries,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        entries: [],
        errorMessage: `Failed to list directory: ${error}`,
      };
    }
  }

  /**
   * Moves a file or directory from source to destination.
   * Corresponds to Python's move_file() method
   *
   * @param source - Path to the source file or directory.
   * @param destination - Path to the destination file or directory.
   * @returns BoolResult with move result and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateMoveFile() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a test file
   *       await session.fileSystem.writeFile('/tmp/original.txt', 'Test content');
   *
   *       // Move the file to a new location
   *       const moveResult = await session.fileSystem.moveFile('/tmp/original.txt', '/tmp/moved.txt');
   *       if (moveResult.success) {
   *         console.log('File moved successfully');
   *         // Output: File moved successfully
   *         console.log(`Request ID: ${moveResult.requestId}`);
   *         // Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
   *       }
   *
   *       // Verify the move
   *       const readResult = await session.fileSystem.readFile('/tmp/moved.txt');
   *       if (readResult.success) {
   *         console.log(`Content at new location: ${readResult.content}`);
   *         // Output: Content at new location: Test content
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateMoveFile().catch(console.error);
   * ```
   */
  async moveFile(source: string, destination: string): Promise<BoolResult> {
    try {
      const args = {
        source,
        destination,
      };

      const result = await this.session.callMcpTool(
        "move_file",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        data: true,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to move file: ${error}`,
      };
    }
  }

  /**
   * Internal method to read a file chunk. Used for chunked file operations.
   *
   * @param path - Path to the file to read.
   * @param offset - Optional: Byte offset to start reading from (0-based).
   * @param length - Optional: Number of bytes to read. If 0, reads the entire file from offset.
   * @returns FileContentResult with file content and requestId
   */
  private async readFileChunk(
    path: string,
    offset = 0,
    length = 0
  ): Promise<FileContentResult> {
    try {
      const args: any = {
        path,
      };

      if (offset > 0) {
        args.offset = offset;
      }

      if (length > 0) {
        args.length = length;
      }

      const result = await this.session.callMcpTool(
        "read_file",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          content: "",
          errorMessage: result.errorMessage,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        content: result.data || "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to read file: ${error}`,
      };
    }
  }

  /**
   * Reads the content of multiple files.
   * Corresponds to Python's read_multiple_files() method
   *
   * @param paths - Array of file paths to read.
   * @returns MultipleFileContentResult with file contents and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateReadMultipleFiles() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create multiple test files
   *       await session.fileSystem.writeFile('/tmp/file1.txt', 'Content of file 1');
   *       await session.fileSystem.writeFile('/tmp/file2.txt', 'Content of file 2');
   *       await session.fileSystem.writeFile('/tmp/file3.txt', 'Content of file 3');
   *
   *       // Read multiple files at once
   *       const paths = ['/tmp/file1.txt', '/tmp/file2.txt', '/tmp/file3.txt'];
   *       const readResult = await session.fileSystem.readMultipleFiles(paths);
   *       if (readResult.success) {
   *         console.log(`Read ${Object.keys(readResult.contents).length} files`);
   *         // Output: Read 3 files
   *         for (const [path, content] of Object.entries(readResult.contents)) {
   *           console.log(`${path}: ${content}`);
   *         }
   *         // Output: /tmp/file1.txt: Content of file 1
   *         // Output: /tmp/file2.txt: Content of file 2
   *         // Output: /tmp/file3.txt: Content of file 3
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateReadMultipleFiles().catch(console.error);
   * ```
   */
  async readMultipleFiles(paths: string[]): Promise<MultipleFileContentResult> {
    try {
      const args = {
        paths,
      };

      const result = await this.session.callMcpTool(
        "read_multiple_files",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          contents: {},
          errorMessage: result.errorMessage,
        };
      }

      const fileContents: Record<string, string> = {};

      if (result.data) {
        // Parse the response into a map of file paths to contents
        const lines = result.data.split("\n");
        let currentPath = "";
        let currentContent: string[] = [];

        for (const line of lines) {
          // Check if this line contains a file path (ends with a colon)
          const colonIndex = line.indexOf(":");
          if (
            colonIndex > 0 &&
            currentPath === "" &&
            !line.substring(0, colonIndex).includes(" ")
          ) {
            // Extract path (everything before the first colon)
            const path = line.substring(0, colonIndex).trim();

            // Start collecting content (everything after the colon)
            currentPath = path;

            // If there's content on the same line after the colon, add it
            if (line.length > colonIndex + 1) {
              const contentStart = line.substring(colonIndex + 1).trim();
              if (contentStart) {
                currentContent.push(contentStart);
              }
            }
          } else if (line === "---") {
            // Save the current file content
            if (currentPath) {
              fileContents[currentPath] = currentContent.join("\n");
              currentPath = "";
              currentContent = [];
            }
          } else if (currentPath) {
            // If we're collecting content for a path, add this line
            currentContent.push(line);
          }
        }

        // Save the last file content if exists
        if (currentPath) {
          fileContents[currentPath] = currentContent.join("\n");
        }

        // Trim trailing newlines from file contents to match expected test values
        for (const path in fileContents) {
          fileContents[path] = fileContents[path].replace(/\n+$/, "");
        }
      }

      return {
        requestId: result.requestId,
        success: true,
        contents: fileContents,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        contents: {},
        errorMessage: `Failed to read multiple files: ${error}`,
      };
    }
  }

  /**
   * Searches for files in a directory that match a pattern.
   * Corresponds to Python's search_files() method
   *
   * @param path - Path to the directory to search in.
   * @param pattern - Pattern to search for. Supports glob patterns.
   * @param excludePatterns - Optional: Array of patterns to exclude.
   * @returns FileSearchResult with search results and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateSearchFiles() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create test files
   *       await session.fileSystem.createDirectory('/tmp/test');
   *       await session.fileSystem.writeFile('/tmp/test/file1.py', "print('hello')");
   *       await session.fileSystem.writeFile('/tmp/test/file2.py', "print('world')");
   *       await session.fileSystem.writeFile('/tmp/test/file3.txt', 'text content');
   *
   *       // Search for Python files (using partial name matching, NOT wildcards)
   *       const searchResult = await session.fileSystem.searchFiles('/tmp/test', '.py');
   *       if (searchResult.success) {
   *         console.log(`Found ${searchResult.matches.length} Python files:`);
   *         // Output: Found 2 Python files:
   *         for (const match of searchResult.matches) {
   *           console.log(`  - ${match}`);
   *         }
   *         // Output:   - /tmp/test/file1.py
   *         // Output:   - /tmp/test/file2.py
   *       }
   *
   *       // Search with exclusion pattern (exclude files containing ".txt")
   *       const excludeResult = await session.fileSystem.searchFiles(
   *         '/tmp/test',
   *         'file',
   *         ['.txt']
   *       );
   *       if (excludeResult.success) {
   *         console.log(`Found ${excludeResult.matches.length} files (excluding .txt)`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateSearchFiles().catch(console.error);
   * ```
   */
  async searchFiles(
    path: string,
    pattern: string,
    excludePatterns: string[] = []
  ): Promise<FileSearchResult> {
    try {
      const args: any = {
        path,
        pattern,
      };

      if (excludePatterns.length > 0) {
        args.excludePatterns = excludePatterns;
      }

      const result = await this.session.callMcpTool(
        "search_files",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          matches: [],
          errorMessage: result.errorMessage,
        };
      }

      // Parse the text content into search results
      let searchResults: string[] = [];
      if (result.data) {
        // Split by newlines and filter out empty lines
        searchResults = result.data
          .split("\n")
          .map((line) => line.trim())
          .filter((line) => line !== "");
      }

      return {
        requestId: result.requestId,
        success: true,
        matches: searchResults,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        matches: [],
        errorMessage: `Failed to search files: ${error}`,
      };
    }
  }

  /**
   * Internal method to write a file chunk. Used for chunked file operations.
   *
   * @param path - Path to the file to write.
   * @param content - Content to write to the file.
   * @param mode - Optional: Write mode. One of "overwrite", "append", or "create_new". Default is "overwrite".
   * @returns BoolResult with write result and requestId
   */
  private async writeFileChunk(
    path: string,
    content: string,
    mode = "overwrite"
  ): Promise<BoolResult> {
    try {
      // Validate mode
      const validModes = ["overwrite", "append", "create_new"];
      if (!validModes.includes(mode)) {
        return {
          requestId: "",
          success: false,
          errorMessage: `Invalid mode: ${mode}. Must be one of ${validModes.join(
            ", "
          )}`,
        };
      }

      const args = {
        path,
        content,
        mode,
      };

      const result = await this.session.callMcpTool(
        "write_file",
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        data: true,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to write file: ${error}`,
      };
    }
  }

  /**
   * Reads the contents of a file. Automatically handles large files by chunking.
   *
   * @param path - Path to the file to read.
   * @returns FileContentResult with complete file content and requestId
   */
  /**
   * Reads the entire content of a file.
   *
   * @param path - Absolute path to the file to read.
   *
   * @returns Promise resolving to FileContentResult containing:
   *          - success: Whether the read operation succeeded
   *          - content: String content of the file
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if read failed
   *
   * @throws Error if the API call fails.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   *
   * if (result.success) {
   *   const session = result.session;
   *
   *   // Read a text file
   *   const fileResult = await session.fileSystem.readFile('/etc/hostname');
   *   if (fileResult.success) {
   *     console.log(`Content: ${fileResult.content}`);
   *     // Output: Content: agentbay-session-xyz
   *   }
   *
   *   await session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Automatically handles large files by reading in 60KB chunks
   * - Returns empty string for empty files
   * - Fails if path is a directory or doesn't exist
   * - Content is returned as UTF-8 string
   *
   * @see {@link writeFile}, {@link listDirectory}
   */
  async readFile(
    path: string
  ): Promise<FileContentResult> {
    const chunkSize = DEFAULT_CHUNK_SIZE;
    try {
      // First get the file info
      const fileInfoResult = await this.getFileInfo(path);

      if (!fileInfoResult.success) {
        return {
          requestId: fileInfoResult.requestId,
          success: false,
          content: "",
          errorMessage: fileInfoResult.errorMessage,
        };
      }

      // Check if file exists and is a file (not a directory)
      if (!fileInfoResult.fileInfo || fileInfoResult.fileInfo.isDirectory) {
        return {
          requestId: fileInfoResult.requestId,
          success: false,
          content: "",
          errorMessage: `Path does not exist or is a directory: ${path}`,
        };
      }

      // Get size from the fileInfo object
      const fileSize = fileInfoResult.fileInfo.size || 0;

      if (fileSize === 0) {
        return {
          requestId: fileInfoResult.requestId,
          success: true,
          content: "",
        };
      }

      // Read the file in chunks
      let result = "";
      let offset = 0;
      let chunkCount = 0;

      while (offset < fileSize) {
        // Calculate how much to read in this chunk
        let length = chunkSize;
        if (offset + length > fileSize) {
          length = fileSize - offset;
        }

        try {
          // Read the chunk
          const chunkResult = await this.readFileChunk(path, offset, length);

          if (!chunkResult.success) {
            return chunkResult; // Return the error
          }

          // Extract the actual content from the response
          result += chunkResult.content;

          // Move to the next chunk
          offset += length;
          chunkCount++;
        } catch (error) {
          return {
            requestId: fileInfoResult.requestId,
            success: false,
            content: "",
            errorMessage: `Error reading chunk at offset ${offset}: ${error}`,
          };
        }
      }

      return {
        requestId: fileInfoResult.requestId,
        success: true,
        content: result,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to read large file: ${error}`,
      };
    }
  }

  /**
   * Writes content to a file. Automatically handles large files by chunking.
   *
   * @param path - Path to the file to write.
   * @param content - Content to write to the file.
   * @param mode - Optional: Write mode. One of "overwrite", "append", or "create_new". Default is "overwrite".
   * @returns BoolResult indicating success or failure with requestId
   */
  /**
   * Writes content to a file.
   *
   * @param path - Absolute path to the file to write.
   * @param content - String content to write to the file.
   * @param mode - Write mode: "overwrite" (default) or "append".
   *
   * @returns Promise resolving to BoolResult with success status.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   *
   * if (result.success) {
   *   const session = result.session;
   *
   *   // Write to a file (overwrite mode)
   *   const writeResult = await session.fileSystem.writeFile(
   *     '/tmp/test.txt',
   *     'Hello, AgentBay!'
   *   );
   *   if (writeResult.success) {
   *     console.log('File written successfully');
   *   }
   *
   *   // Append to a file
   *   const appendResult = await session.fileSystem.writeFile(
   *     '/tmp/test.txt',
   *     '\nNew line',
   *     'append'
   *   );
   *
   *   await session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Automatically handles large files by writing in 60KB chunks
   * - Creates parent directories if they don't exist
   * - "overwrite" mode replaces existing file content
   * - "append" mode adds content to the end of the file
   *
   * @see {@link readFile}, {@link listDirectory}
   */
  async writeFile(
    path: string,
    content: string,
    mode = "overwrite"
  ): Promise<BoolResult> {
    const chunkSize = DEFAULT_CHUNK_SIZE;
    try {
      const contentLen = content.length;

      // If content is small enough, use the regular writeFileChunk method
      if (contentLen <= chunkSize) {
        return await this.writeFileChunk(path, content, mode);
      }

      // Write the first chunk with the specified mode
      const firstChunkEnd = Math.min(chunkSize, contentLen);

      const firstResult = await this.writeFileChunk(
        path,
        content.substring(0, firstChunkEnd),
        mode
      );

      if (!firstResult.success) {
        return firstResult;
      }

      // Write the remaining chunks with "append" mode
      let chunkCount = 1; // Already wrote first chunk
      for (let offset = firstChunkEnd; offset < contentLen; ) {
        const end = Math.min(offset + chunkSize, contentLen);

        const chunkResult = await this.writeFileChunk(
          path,
          content.substring(offset, end),
          "append"
        );

        if (!chunkResult.success) {
          return chunkResult;
        }

        offset = end;
        chunkCount++;
      }

      return {
        requestId: firstResult.requestId,
        success: true,
        data: true,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to write large file: ${error}`,
      };
    }
  }

  /**
   * Get file change information for the specified directory path
   *
   * @param path - Directory path to monitor
   * @returns Promise resolving to result containing detected file changes
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateGetFileChange() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create test directory
   *       await session.fileSystem.createDirectory('/tmp/watch_dir');
   *
   *       // Check for file changes
   *       const changeResult = await session.fileSystem.getFileChange('/tmp/watch_dir');
   *       if (changeResult.success) {
   *         console.log(`Detected ${changeResult.events.length} changes`);
   *         // Output: Detected 0 changes
   *
   *         if (changeResult.events.length > 0) {
   *           changeResult.events.forEach(event => {
   *             console.log(`- ${event.eventType}: ${event.path} (${event.pathType})`);
   *           });
   *         } else {
   *           console.log('No changes detected');
   *           // Output: No changes detected
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
   * demonstrateGetFileChange().catch(console.error);
   * ```
   */
  async getFileChange(path: string): Promise<FileChangeResult> {
    try {
      const args = { path };
      const result = await this.session.callMcpTool("get_file_change", args);

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          events: [],
          rawData: result.data || "",
          errorMessage: result.errorMessage,
        };
      }

      // Parse the file change events
      const events = this.parseFileChangeData(result.data);

      return {
        requestId: result.requestId,
        success: true,
        events,
        rawData: result.data,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        events: [],
        rawData: "",
        errorMessage: `Failed to get file change: ${error}`,
      };
    }
  }

  /**
   * Parse raw JSON data into FileChangeEvent array
   */
  private parseFileChangeData(rawData: string): FileChangeEvent[] {
    const events: FileChangeEvent[] = [];
    
    try {
      const changeData = JSON.parse(rawData);
      if (Array.isArray(changeData)) {
        for (const eventDict of changeData) {
          if (typeof eventDict === "object" && eventDict !== null) {
            const event = FileChangeEventHelper.fromDict(eventDict);
            events.push(event);
          }
        }
      }
    } catch (error) {
      console.warn(`Failed to parse JSON data: ${error}`);
    }
    
    return events;
  }

  /**
   * Watch a directory for file changes and call the callback function when changes occur
   *
   * @param path - Directory path to monitor
   * @param callback - Function called when changes are detected
   * @param interval - Polling interval in milliseconds (default: 500, minimum: 100)
   * @param signal - Signal to abort the monitoring
   * @returns Promise that resolves when monitoring stops
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateWatchDirectory() {
   *   try {
   *     const result = await agentBay.create();
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create test directory
   *       const testDir = '/tmp/agentbay_watch_test';
   *       await session.fileSystem.createDirectory(testDir);
   *
   *       // Set up callback function
   *       const callback = (events) => {
   *         console.log(`Detected ${events.length} file changes:`);
   *         events.forEach(event => {
   *           console.log(`- ${event.eventType}: ${event.path} (${event.pathType})`);
   *         });
   *       };
   *
   *       // Create AbortController for stopping the watch
   *       const controller = new AbortController();
   *
   *       // Start monitoring
   *       const watchPromise = session.fileSystem.watchDirectory(
   *         testDir,
   *         callback,
   *         1000, // 1 second interval
   *         controller.signal
   *       );
   *
   *       // Simulate file operations after a delay
   *       setTimeout(async () => {
   *         // Create a file
   *         const testFile = `${testDir}/test.txt`;
   *         await session.fileSystem.writeFile(testFile, 'Hello, AgentBay!');
   *
   *         // Stop monitoring after another delay
   *         setTimeout(() => {
   *           controller.abort();
   *         }, 2000);
   *       }, 2000);
   *
   *       // Wait for monitoring to complete
   *       await watchPromise;
   *       console.log('Monitoring stopped');
   *       // Output: Monitoring stopped
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateWatchDirectory().catch(console.error);
   * ```
   */
  async watchDirectory(
    path: string,
    callback: (events: FileChangeEvent[]) => void,
    interval = 500,
    signal?: AbortSignal
  ): Promise<void> {
    console.log(`Starting directory monitoring for: ${path}`);
    console.log(`Polling interval: ${interval} ms`);

    const monitor = async () => {
      while (!signal?.aborted) {
        try {
          const result = await this.getFileChange(path);

          if (result.success && result.events.length > 0) {
            console.log(`Detected ${result.events.length} file changes:`);
            for (const event of result.events) {
              console.log(`  - ${FileChangeEventHelper.toString(event)}`);
            }

            try {
              callback(result.events);
            } catch (error) {
              console.error(`Error in callback function: ${error}`);
            }
          } else if (!result.success) {
            console.error(`Error monitoring directory: ${result.errorMessage}`);
          }

          // Wait for next poll
          await new Promise((resolve) => {
            const timeoutId = setTimeout(resolve, interval);
            signal?.addEventListener("abort", () => {
              clearTimeout(timeoutId);
              resolve(void 0);
            });
          });
        } catch (error) {
          console.error(`Unexpected error in directory monitoring: ${error}`);
          await new Promise((resolve) => setTimeout(resolve, interval));
        }
      }

      console.log(`Stopped monitoring directory: ${path}`);
    };

    return monitor();
  }

  /**
   * Upload a file from local to remote path using pre-signed URLs.
   * This is a synchronous wrapper around the FileTransfer.upload method.
   *
   * @param localPath - Local file path to upload
   * @param remotePath - Remote file path to upload to
   * @param options - Optional parameters
   * @returns UploadResult with upload result and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   * import * as fs from 'fs';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateUploadFile() {
   *   try {
   *     // Create session with context sync for file transfer
   *     const result = await agentBay.create({
   *       imageId: 'code_latest'
   *     });
   *
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a local test file
   *       const localPath = '/tmp/local_upload_test.txt';
   *       fs.writeFileSync(localPath, 'Test upload content');
   *
   *       // Upload the file
   *       const uploadResult = await session.fileSystem.uploadFile(
   *         localPath,
   *         '/workspace/uploaded_file.txt'
   *       );
   *
   *       if (uploadResult.success) {
   *         console.log('File uploaded successfully');
   *         // Output: File uploaded successfully
   *         console.log(`Bytes sent: ${uploadResult.bytesSent}`);
   *         console.log(`Request ID (upload URL): ${uploadResult.requestIdUploadUrl}`);
   *         console.log(`Request ID (sync): ${uploadResult.requestIdSync}`);
   *       } else {
   *         console.error(`Upload failed: ${uploadResult.error}`);
   *       }
   *
   *       // Verify the uploaded file exists in the session
   *       const readResult = await session.fileSystem.readFile('/workspace/uploaded_file.txt');
   *       if (readResult.success) {
   *         console.log(`File content in session: ${readResult.content}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateUploadFile().catch(console.error);
   * ```
   */
  async uploadFile(
    localPath: string,
    remotePath: string,
    options?: {
      contentType?: string;
      wait?: boolean;
      waitTimeout?: number;
      pollInterval?: number;
      progressCb?: (bytesTransferred: number) => void;
    }
  ): Promise<any> {
    try {
      // Ensure FileTransfer is initialized
      const fileTransfer = this._ensureFileTransfer();
      
      // Perform upload
      const result = await fileTransfer.upload(localPath, remotePath, options);
      
      // If upload was successful, delete the file from OSS
      if (result.success && (this.session as any).fileTransferContextId) {
        const contextId = (this.session as any).fileTransferContextId;
        if (contextId) {
          try {
            // Delete the uploaded file from OSS
            const deleteResult = await (this.session as any).agentBay.context.deleteFile(contextId, remotePath);
            if (!deleteResult.success) {
              logWarn(`Warning: Failed to delete uploaded file from OSS: ${deleteResult}`);
            }
          } catch (deleteError: any) {
            logWarn(`Warning: Error deleting uploaded file from OSS: ${deleteError}`);
          }
        }
      }
      
      return result;
    } catch (error) {
      return {
        success: false,
        bytesSent: 0,
        path: remotePath,
        error: `Upload failed: ${error}`,
      };
    }
  }

  /**
   * Download a file from remote path to local path using pre-signed URLs.
   * This is a synchronous wrapper around the FileTransfer.download method.
   *
   * @param remotePath - Remote file path to download from
   * @param localPath - Local file path to download to
   * @param options - Optional parameters
   * @returns DownloadResult with download result and requestId
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   * import * as fs from 'fs';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateDownloadFile() {
   *   try {
   *     // Create session
   *     const result = await agentBay.create({
   *       imageId: 'code_latest'
   *     });
   *
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Create a file in the session
   *       await session.fileSystem.writeFile(
   *         '/workspace/remote_file.txt',
   *         'Content to download'
   *       );
   *
   *       // Download the file
   *       const localPath = '/tmp/downloaded_file.txt';
   *       const downloadResult = await session.fileSystem.downloadFile(
   *         '/workspace/remote_file.txt',
   *         localPath
   *       );
   *
   *       if (downloadResult.success) {
   *         console.log('File downloaded successfully');
   *         // Output: File downloaded successfully
   *         console.log(`Bytes received: ${downloadResult.bytesReceived}`);
   *         console.log(`Request ID (download URL): ${downloadResult.requestIdDownloadUrl}`);
   *         console.log(`Request ID (sync): ${downloadResult.requestIdSync}`);
   *
   *         // Verify the downloaded file
   *         const content = fs.readFileSync(localPath, 'utf8');
   *         console.log(`Downloaded content: ${content}`);
   *         // Output: Downloaded content: Content to download
   *       } else {
   *         console.error(`Download failed: ${downloadResult.error}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateDownloadFile().catch(console.error);
   * ```
   */
  async downloadFile(
    remotePath: string,
    localPath: string,
    options?: {
      overwrite?: boolean;
      wait?: boolean;
      waitTimeout?: number;
      pollInterval?: number;
      progressCb?: (bytesReceived: number) => void;
    }
  ): Promise<any> {
    try {
      // Ensure FileTransfer is initialized
      const fileTransfer = this._ensureFileTransfer();
      
      // Perform download
      const result = await fileTransfer.download(remotePath, localPath, options);
      
      // If download was successful, delete the file from OSS
      if (result.success && (this.session as any).fileTransferContextId) {
        const contextId = (this.session as any).fileTransferContextId;
        if (contextId) {
          try {
            // Delete the downloaded file from OSS
            const deleteResult = await (this.session as any).agentBay.context.deleteFile(contextId, remotePath);
            if (!deleteResult.success) {
              logWarn(`Warning: Failed to delete downloaded file from OSS: ${deleteResult}`);
            }
          } catch (deleteError: any) {
            logWarn(`Warning: Error deleting downloaded file from OSS: ${deleteError}`);
          }
        }
      }
      
      return result;
    } catch (error) {
      return {
        success: false,
        bytesReceived: 0,
        path: remotePath,
        localPath,
        error: `Download failed: ${error}`,
      };
    }
  }
}
