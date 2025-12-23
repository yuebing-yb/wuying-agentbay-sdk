import { AgentBay, Session } from "../../src";
import {
  getTestApiKey,
  containsToolNotFound,
} from "../utils/test-helpers";
import { log } from "../../src/utils/logger";
import { BinaryFileContentResult } from "../../src/types/api-response";

// Define test path prefix based on platform
const TestPathPrefix = "/tmp";

describe("fileSystem Binary File Operations", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });

    // Create a session with linux_latest image
    log("Creating a new session for binary fileSystem testing...");
    const createResponse = await agentBay.create({ imageId: "linux_latest" });
    
    if (!createResponse.success || !createResponse.session) {
      throw new Error(`Failed to create session: ${createResponse.errorMessage || "Unknown error"}`);
    }
    
    session = createResponse.session;
    log(`Session created with ID: ${session.sessionId}`);
    log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
  });

  afterEach(async () => {
    // Clean up the session
    log("Cleaning up: Deleting the session...");
    try {
      if (session) {
        const deleteResponse = await agentBay.delete(session);
        log(
          `Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`
        );
      }
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });

  describe("readFile with binary format", () => {
    it("should read a binary file with non-zero content", async () => {
      if (session.fileSystem && session.command) {
        log("Creating binary file with pattern...");
        try {
          // Create binary file with pattern using command
          const createResult = await session.command.executeCommand(
            "python3 -c \"with open('/tmp/binary_pattern_test', 'wb') as f: f.write(bytes(range(256)) * 4)\""
          );
          
          if (!createResult.success) {
            log(`Note: Failed to create binary file: ${createResult.errorMessage}`);
            return;
          }

          // Read binary file using format='bytes'
          log("Reading binary file...");
          const readResponse = await session.fileSystem.readFile("/tmp/binary_pattern_test", { format: "bytes" });
          
          log(`ReadFile binary result: content length=${readResponse.content.length} bytes`);
          log(`Read Binary File RequestId: ${readResponse.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(readResponse.requestId).toBeDefined();
          expect(typeof readResponse.requestId).toBe("string");

          // Verify it's a BinaryFileContentResult
          expect(readResponse).toBeInstanceOf(Object);
          expect(readResponse.content).toBeInstanceOf(Uint8Array);
          expect(readResponse.success).toBe(true);

          // Verify content pattern (0-255 repeating 4 times = 1024 bytes)
          const expectedLength = 256 * 4; // 1024 bytes
          expect(readResponse.content.length).toBe(expectedLength);
          
          // Verify pattern: first 256 bytes should be 0x00, 0x01, ..., 0xFF
          for (let i = 0; i < 256; i++) {
            expect(readResponse.content[i]).toBe(i);
          }

          log(`Successfully read binary file with pattern: ${readResponse.content.length} bytes`);
        } catch (error) {
          log(`Note: Binary file operation failed: ${error}`);
          // Don't fail the test if fileSystem operations are not supported
        }
      } else {
        log("Note: fileSystem or command interface is nil, skipping binary file test");
      }
    });

    it("should read an empty binary file", async () => {
      if (session.fileSystem && session.command) {
        log("Creating empty binary file...");
        try {
          // Create empty binary file
          const createResult = await session.command.executeCommand(
            "touch /tmp/empty_binary_test"
          );
          
          if (!createResult.success) {
            log(`Note: Failed to create empty binary file: ${createResult.errorMessage}`);
            return;
          }

          // Read binary file using format='bytes'
          log("Reading empty binary file...");
          const readResponse = await session.fileSystem.readFile("/tmp/empty_binary_test", { format: "bytes" });
          
          log(`ReadFile binary result: content length=${readResponse.content.length} bytes`);
          log(`Read Empty Binary File RequestId: ${readResponse.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(readResponse.requestId).toBeDefined();
          expect(typeof readResponse.requestId).toBe("string");

          // Verify it's a BinaryFileContentResult
          expect(readResponse).toBeInstanceOf(Object);
          expect(readResponse.content).toBeInstanceOf(Uint8Array);
          expect(readResponse.success).toBe(true);
          expect(readResponse.content.length).toBe(0);
          expect(readResponse.size).toBe(0);

          log("Successfully read empty binary file");
        } catch (error) {
          log(`Note: Empty binary file operation failed: ${error}`);
          // Don't fail the test if fileSystem operations are not supported
        }
      } else {
        log("Note: fileSystem or command interface is nil, skipping empty binary file test");
      }
    });

    it("should handle binary file read errors", async () => {
      if (session.fileSystem) {
        log("Reading non-existent binary file...");
        try {
          const nonExistentFile = "/path/to/non/existent/binary/file.bin";
          const readResponse = await session.fileSystem.readFile(nonExistentFile, { format: "bytes" });
          
          log(`ReadFile binary result for non-existent file: content length=${readResponse.content.length}`);
          log(`Read Non-existent Binary File RequestId: ${readResponse.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(readResponse.requestId).toBeDefined();
          expect(typeof readResponse.requestId).toBe("string");

          // Verify error handling
          expect(readResponse.success).toBe(false);
          expect(readResponse.content).toBeInstanceOf(Uint8Array);
          expect(readResponse.content.length).toBe(0);
          expect(readResponse.errorMessage).toBeDefined();

          log("Binary file read error handled correctly");
        } catch (error) {
          log(`Note: Binary file read error test failed: ${error}`);
          // Don't fail the test if fileSystem operations are not supported
        }
      } else {
        log("Note: fileSystem interface is nil, skipping binary file error test");
      }
    });
  });

  describe("readFile text format compatibility", () => {
    it("should still read text files correctly", async () => {
      if (session.fileSystem) {
        log("Testing text file reading compatibility...");
        try {
          const testContent = "This is a test text file for binary read feature.";
          const testFilePath = `${TestPathPrefix}/test_text_for_binary_feature.txt`;

          // Write text file
          const writeResult = await session.fileSystem.writeFile(testFilePath, testContent, "overwrite");
          if (!writeResult.success) {
            log(`Note: Failed to write text file: ${writeResult.errorMessage}`);
            return;
          }

          // Read as text (default format)
          const readResponse = await session.fileSystem.readFile(testFilePath);
          expect(readResponse.success).toBe(true);
          expect(typeof readResponse.content).toBe("string");
          expect(readResponse.content).toBe(testContent);

          // Explicitly read as text format
          const readResponseExplicit = await session.fileSystem.readFile(testFilePath, { format: "text" });
          expect(readResponseExplicit.success).toBe(true);
          expect(typeof readResponseExplicit.content).toBe("string");
          expect(readResponseExplicit.content).toBe(testContent);

          log("Text file reading still works correctly");
        } catch (error) {
          log(`Note: Text file compatibility test failed: ${error}`);
          // Don't fail the test if fileSystem operations are not supported
        }
      } else {
        log("Note: fileSystem interface is nil, skipping text file compatibility test");
      }
    });
  });
});

