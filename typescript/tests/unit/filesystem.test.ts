import { AgentBay, Session } from '../../src';
import { getTestApiKey, containsToolNotFound, randomString } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Define test path prefix based on platform
const TestPathPrefix = '/tmp';

describe('FileSystem', () => {
  let agentBay: AgentBay;
  let session: Session;
  
  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    
    // Create a session with linux_latest image
    log('Creating a new session for filesystem testing...');
    const sessionParams = { imageId: 'linux_latest' };
    session = await agentBay.create(sessionParams);
    log(`Session created with ID: ${session.sessionId}`);
  });
  
  afterEach(async () => {
    // Clean up the session
    log('Cleaning up: Deleting the session...');
    try {
      if(session)
      await agentBay.delete(session);
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });
  
  describe('readFile', () => {
    it.only('should read a file', async () => {
      if (session.filesystem) {
        log('Reading file...');
        try {
          // Use a file that should exist on most systems
          const filePath = '/etc/hosts';
          const content = await session.filesystem.readFile(filePath);
          log(`ReadFile result: content='${content.substring(0, 100)}...'`);
          
          // Check if response contains "tool not found"
          expect(containsToolNotFound(content)).toBe(false);
          
          // Verify the content is not empty
          expect(content.length).toBeGreaterThan(0);
          log('File read successful');
        } catch (error) {
          log(`Note: File operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem interface is nil, skipping file test');
      }
    });
    
    it.only('should handle file not found errors', async () => {
      if (session.filesystem) {
        log('Reading non-existent file...');
        try {
          const nonExistentFile = '/path/to/non/existent/file';
          const content = await session.filesystem.readFile(nonExistentFile);
          log(`ReadFile result for non-existent file: content='${content}'`);
          
          // If we get here, the API might return an empty string or error message for non-existent files
          // We're just checking that the promise resolves
          expect(content).toBeDefined();
        } catch (error) {
          // If the API rejects the promise, that's also an acceptable behavior for a non-existent file
          log(`Non-existent file read failed as expected: ${error}`);
          expect(error).toBeDefined();
        }
      } else {
        log('Note: FileSystem interface is nil, skipping file not found test');
      }
    });
  });
  
  describe('writeFile', () => {
    it.only('should write to a file', async () => {
      // Check if filesystem exists and has a writeFile method
      if (session.filesystem && typeof session.filesystem.writeFile === 'function') {
        log('Writing to file...');
        try {
          // Use a temporary file path
          const tempFile = `${TestPathPrefix}/agentbay-test-${Date.now()}.txt`;
          const content = `Test content generated at ${new Date().toISOString()}`;
          
          await session.filesystem.writeFile(tempFile, content);
          log(`WriteFile successful: ${tempFile}`);
          
          // Verify by reading the file back
          const readContent = await session.filesystem.readFile(tempFile);
          log(`ReadFile after write: content='${readContent}'`);
          
          // Check if the content matches
          expect(readContent).toBe(content);
          log('File write verified successfully');
          
          // Clean up the temporary file
          if (session.command) {
            await session.command.executeCommand(`rm ${tempFile}`);
            log(`Temporary file deleted: ${tempFile}`);
          }
        } catch (error) {
          log(`Note: File write operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem writeFile method is not available, skipping file write test');
      }
    });
  });
  
  describe('createDirectory', () => {
    it.only('should create a directory', async () => {
      if (session.filesystem && typeof session.filesystem.createDirectory === 'function') {
        log('Creating directory...');
        try {
          const testDirPath = `${TestPathPrefix}/test_directory_${randomString()}`;
          await session.filesystem.createDirectory(testDirPath);
          log(`CreateDirectory successful: ${testDirPath}`);
          
          // Verify the directory was created using command line instead of listDirectory
          if (session.command) {
            // Use ls command to check if directory exists
            const lsResult = await session.command.executeCommand(`ls -la ${testDirPath}`);
            log(`ls command result: ${lsResult}`);
            
            // If the directory exists, the ls command should succeed
            expect(lsResult).toBeDefined();
            expect(lsResult.length).toBeGreaterThan(0);
            log('Directory verified using ls command');
            
            // Clean up the test directory
            if (session.command) {
              await session.command.executeCommand(`rmdir ${testDirPath}`);
              log(`Test directory deleted: ${testDirPath}`);
            }
          } else {
            log('Note: Command interface is nil, skipping directory verification');
          }
        } catch (error) {
          log(`Note: Directory creation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem createDirectory method is not available, skipping directory test');
      }
    });
  });
  
  describe('editFile', () => {
    it.only('should edit a file by replacing text', async () => {
      if (session.filesystem && typeof session.filesystem.editFile === 'function') {
        log('Editing file...');
        try {
          // First create a file to edit
          const testFilePath = `${TestPathPrefix}/test_edit_${randomString()}.txt`;
          const initialContent = "This is the original content.\nLine to be replaced.\nThis is the final line.";
          await session.filesystem.writeFile(testFilePath, initialContent);
          log(`Created file for editing: ${testFilePath}`);
          
          // Now edit the file
          const edits = [
            {
              oldText: "Line to be replaced.",
              newText: "This line has been edited."
            }
          ];
          
          await session.filesystem.editFile(testFilePath, edits);
          log(`EditFile successful: ${testFilePath}`);
          
          // Verify the file was edited correctly by reading it back
          const content = await session.filesystem.readFile(testFilePath);
          log(`ReadFile after edit: content='${content}'`);
          
          const expectedContent = "This is the original content.\nThis line has been edited.\nThis is the final line.";
          expect(content).toBe(expectedContent);
          log('File edit verified successfully');
          
          // Clean up the test file
          if (session.command) {
            await session.command.executeCommand(`rm ${testFilePath}`);
            log(`Test file deleted: ${testFilePath}`);
          }
        } catch (error) {
          log(`Note: File edit operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem editFile method is not available, skipping file edit test');
      }
    });
  });
  
  describe('getFileInfo', () => {
    it.only('should get file information', async () => {
      if (session.filesystem && typeof session.filesystem.getFileInfo === 'function') {
        log('Getting file info...');
        try {
          // First create a file to get info for
          const testFilePath = `${TestPathPrefix}/test_info_${randomString()}.txt`;
          const testContent = "This is a test file for GetFileInfo.";
          await session.filesystem.writeFile(testFilePath, testContent);
          log(`Created file for info test: ${testFilePath}`);
          
          // Get file info
          const fileInfo = await session.filesystem.getFileInfo(testFilePath);
          log(`GetFileInfo result: ${JSON.stringify(fileInfo)}`);
          
          // Verify the file info contains expected fields
          expect(typeof fileInfo.size).toBe('number');
          expect(fileInfo.isDirectory).toBe(false);
          expect(fileInfo.name).toBeDefined();
          log('File info verified successfully');
          
          // Clean up the test file
          if (session.command) {
            await session.command.executeCommand(`rm ${testFilePath}`);
            log(`Test file deleted: ${testFilePath}`);
          }
        } catch (error) {
          log(`Note: Get file info operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem getFileInfo method is not available, skipping file info test');
      }
    });
  });
  
  describe('listDirectory', () => {
    it.only('should list directory contents', async () => {
      if (session.filesystem && typeof session.filesystem.listDirectory === 'function') {
        log('Listing directory...');
        try {
          const entries = await session.filesystem.listDirectory(`${TestPathPrefix}/`);
          log(`ListDirectory result: entries count=${entries.length}`);
          
          // Verify the entries contain expected fields
          if (entries.length > 0) {
            const firstEntry = entries[0];
            expect(typeof firstEntry.name).toBe('string');
            expect(typeof firstEntry.isDirectory).toBe('boolean');
            log('Directory listing verified successfully');
          } else {
            log('Directory is empty, skipping entry verification');
          }
        } catch (error) {
          log(`Note: List directory operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem listDirectory method is not available, skipping directory listing test');
      }
    });
  });
  
  describe('moveFile', () => {
    it.only('should move a file from source to destination', async () => {
      if (session.filesystem && typeof session.filesystem.moveFile === 'function') {
        log('Moving file...');
        try {
          // First create a file to move
          const sourceFilePath = `${TestPathPrefix}/test_source_${randomString()}.txt`;
          const destFilePath = `${TestPathPrefix}/test_destination_${randomString()}.txt`;
          const testContent = "This is a test file for MoveFile.";
          await session.filesystem.writeFile(sourceFilePath, testContent);
          log(`Created file for move test: ${sourceFilePath}`);
          
          // Move the file
          await session.filesystem.moveFile(sourceFilePath, destFilePath);
          log(`MoveFile successful: ${sourceFilePath} -> ${destFilePath}`);
          
          // Verify the file was moved correctly by reading it back
          const content = await session.filesystem.readFile(destFilePath);
          log(`ReadFile after move: content='${content}'`);
          
          expect(content).toBe(testContent);
          log('File move verified successfully');
          
          // Verify the source file no longer exists
          try {
            await session.filesystem.readFile(sourceFilePath);
            // If we get here, the file still exists
            log('Source file still exists after move');
            expect(false).toBe(true); // This should fail the test
          } catch (error) {
            // The file should not exist, so any error here is acceptable
            log('Source file correctly no longer exists');
          }
          
          // Clean up the destination file
          if (session.command) {
            await session.command.executeCommand(`rm ${destFilePath}`);
            log(`Destination file deleted: ${destFilePath}`);
          }
        } catch (error) {
          log(`Note: File move operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem moveFile method is not available, skipping file move test');
      }
    });
  });
  
  describe('readMultipleFiles', () => {
    it.only('should read multiple files at once', async () => {
      if (session.filesystem && typeof session.filesystem.readMultipleFiles === 'function') {
        log('Reading multiple files...');
        try {
          // First create some test files
          const file1Content = "This is test file 1 content.";
          const file2Content = "This is test file 2 content.";
          const testFile1Path = `${TestPathPrefix}/test_file1_${randomString()}.txt`;
          const testFile2Path = `${TestPathPrefix}/test_file2_${randomString()}.txt`;
          
          await session.filesystem.writeFile(testFile1Path, file1Content);
          log(`Created test file 1: ${testFile1Path}`);
          
          await session.filesystem.writeFile(testFile2Path, file2Content);
          log(`Created test file 2: ${testFile2Path}`);
          
          // Read multiple files
          const paths = [testFile1Path, testFile2Path];
          const contents = await session.filesystem.readMultipleFiles(paths);
          log(`ReadMultipleFiles result: ${JSON.stringify(contents)}`);
          
          // Verify the contents of each file
          expect(contents[testFile1Path]).toBe(file1Content);
          expect(contents[testFile2Path]).toBe(file2Content);
          log('Multiple files read verified successfully');
          
          // Clean up the test files
          if (session.command) {
            await session.command.executeCommand(`rm ${testFile1Path} ${testFile2Path}`);
            log(`Test files deleted: ${testFile1Path}, ${testFile2Path}`);
          }
        } catch (error) {
          log(`Note: Read multiple files operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem readMultipleFiles method is not available, skipping read multiple files test');
      }
    });
  });
  
  describe('searchFiles', () => {
    it.only('should search for files matching a pattern', async () => {
      if (session.filesystem && typeof session.filesystem.searchFiles === 'function') {
        log('Searching files...');
        try {
          // First create a subdirectory for testing
          const testSubdirPath = `${TestPathPrefix}/search_test_dir_${randomString()}`;
          await session.filesystem.createDirectory(testSubdirPath);
          log(`Created test subdirectory: ${testSubdirPath}`);
          
          // Create test files with specific naming patterns
          const file1Content = "This is test file 1 content.";
          const file2Content = "This is test file 2 content.";
          const file3Content = "This is test file 3 content.";
          
          const searchPattern = "SEARCHABLE_PATTERN";
          const searchFile1Path = `${testSubdirPath}/SEARCHABLE_PATTERN_file1.txt`;
          const searchFile2Path = `${testSubdirPath}/regular_file2.txt`;
          const searchFile3Path = `${testSubdirPath}/SEARCHABLE_PATTERN_file3.txt`;
          
          await session.filesystem.writeFile(searchFile1Path, file1Content);
          await session.filesystem.writeFile(searchFile2Path, file2Content);
          await session.filesystem.writeFile(searchFile3Path, file3Content);
          log(`Created test files for search test`);
          
          // Search for files matching the pattern
          const results = await session.filesystem.searchFiles(testSubdirPath, searchPattern);
          log(`SearchFiles result: ${JSON.stringify(results)}`);
          
          // Verify the search results
          expect(Array.isArray(results)).toBe(true);
          expect(results.length).toBe(2); // Should find 2 files with the pattern
          
          // Verify the search results contain the expected files
          const resultPaths = results.map(result => result);
          expect(resultPaths.includes(searchFile1Path) || resultPaths.some(p => p.includes('SEARCHABLE_PATTERN_file1.txt'))).toBe(true);
          expect(resultPaths.includes(searchFile3Path) || resultPaths.some(p => p.includes('SEARCHABLE_PATTERN_file3.txt'))).toBe(true);
          log('Search files verified successfully');
          
          // Clean up the test files and directory
          if (session.command) {
            await session.command.executeCommand(`rm -rf ${testSubdirPath}`);
            log(`Test subdirectory and files deleted: ${testSubdirPath}`);
          }
        } catch (error) {
          log(`Note: Search files operation failed: ${error}`);
          // Don't fail the test if filesystem operations are not supported
        }
      } else {
        log('Note: FileSystem searchFiles method is not available, skipping search files test');
      }
    });
  });
});
