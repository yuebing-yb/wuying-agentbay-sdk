import { AgentBay, CreateSessionParams, Session } from "../../src";
import { ContextSync, newContextSync, newUploadPolicy, newSyncPolicy } from "../../src/context-sync";
import { FileSystem } from "../../src/filesystem/filesystem";
import { log } from "../../src/utils/logger";

function getTestAPIKey(): string {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    log(
      "Warning: AGENTBAY_API_KEY environment variable not set. Using default test key."
    );
    return "akm-xxx"; // Replace with your test API key
  }
  return apiKey;
}

function generateUniqueId(): string {
  const timestamp = Date.now() * 1000 + Math.floor(Math.random() * 1000);
  const randomPart = Math.floor(Math.random() * 10000);
  return `${timestamp}-${randomPart}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

describe("Context Sync Upload Mode Integration Tests", () => {
  let agentBay: AgentBay;
  let uniqueId: string;
  let testSessions: Session[] = [];

  beforeAll(async () => {
    const apiKey = getTestAPIKey();
    agentBay = new AgentBay({ apiKey });
    uniqueId = generateUniqueId();

    log(`Using unique ID for test: ${uniqueId}`);
  });

  afterAll(async () => {
    log("Cleaning up: Deleting all test sessions...");
    for (const session of testSessions) {
      try {
        const result = await agentBay.delete(session,true);
        log(
          `Session ${session.sessionId} deleted. Success: ${result.success}, Request ID: ${result.requestId}`
        );
      } catch (error) {
        log(
          `Warning: Error deleting session ${session.sessionId}: ${error}`
        );
      }
    }
  });

  describe("Basic Functionality Tests", () => {
    test("should create session with default File upload mode and write file", async () => {
      log("\n=== Testing basic functionality with default File upload mode ===");

      // Step 1: Use context.get method to generate contextId
      const contextName = `test-context-${uniqueId}`;
      log(`Creating context with name: ${contextName}`);
      
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);
      expect(contextResult.contextId).toBeDefined();
      expect(contextResult.contextId).not.toBe("");
      
      log(`Generated contextId: ${contextResult.contextId}`);
      log(`Context get request ID: ${contextResult.requestId}`);

      // Step 2: Create session with contextSync using default File uploadMode
      const syncPolicy = newSyncPolicy(); // Uses default uploadMode "File"

      const contextSync = new ContextSync(
        contextResult.contextId,
        "/tmp/test",
        syncPolicy
      );

      const sessionParams: CreateSessionParams = {
        labels: {
          test: `upload-mode-${uniqueId}`,
          type: "basic-functionality"
        },
        contextSync: [contextSync]
      };

      log("Creating session with default File upload mode...");
      const sessionResult = await agentBay.create(sessionParams);

      // Step 3: Verify session creation success
      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.requestId).toBeDefined();
      expect(sessionResult.requestId).not.toBe("");

      const session = sessionResult.session!;
      testSessions.push(session);

      log(`✅ Session created successfully!`);
      log(`Session ID: ${session.sessionId}`);
      log(`Session creation request ID: ${sessionResult.requestId}`);

      // Get session info to verify appInstanceId
      const sessionInfo = await agentBay.getSession(session.sessionId);
      expect(sessionInfo.success).toBe(true);
      expect(sessionInfo.data).toBeDefined();
      
      log(`App Instance ID: ${sessionInfo.data?.appInstanceId}`);
      log(`Get session request ID: ${sessionInfo.requestId}`);

      log("✅ All basic functionality tests passed!");
    });
  });

  describe("Upload Mode Validation Tests", () => {
    test("should work with contextId and path using Archive mode and write file", async () => {
      log("\n=== Testing contextId and path usage with Archive mode and code execution ===");

      const contextName = `archive-mode-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      
      expect(contextResult.success).toBe(true);
      expect(contextResult.contextId).toBeDefined();
      expect(contextResult.contextId).not.toBe("");

      log(`Generated contextId: ${contextResult.contextId}`);

      // Use newSyncPolicy and modify uploadMode to Archive
      const syncPolicy = newSyncPolicy();
      syncPolicy.uploadPolicy!.uploadMode = "Archive"; // Set uploadMode to Archive

      const contextSync = newContextSync(
        contextResult.contextId,
        "/tmp/archive-mode-test",
        syncPolicy
      );

      expect(contextSync.contextId).toBe(contextResult.contextId);
      expect(contextSync.path).toBe("/tmp/archive-mode-test");
      expect(contextSync.policy?.uploadPolicy?.uploadMode).toBe("Archive");

      log("✅ newContextSync works correctly with contextId and path using Archive mode");

      // Create session with the contextSync
      const sessionParams: CreateSessionParams = {
        labels: {
          test: `archive-mode-${uniqueId}`,
          type: "contextId-path-validation"
        },
        contextSync: [contextSync]
      };

      log("Creating session with Archive mode contextSync...");
      const sessionResult = await agentBay.create(sessionParams);

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.requestId).toBeDefined();

      const session = sessionResult.session!;
      testSessions.push(session);
      // Get session info to verify appInstanceId
      const sessionInfo = await agentBay.getSession(session.sessionId);
      expect(sessionInfo.success).toBe(true);
      expect(sessionInfo.data).toBeDefined();
      
      log(`App Instance ID: ${sessionInfo.data?.appInstanceId}`);

      log(`✅ Session created successfully with ID: ${session.sessionId}`);
      log(`Session creation request ID: ${sessionResult.requestId}`);

      // Write a 5KB file using FileSystem
      log("Writing 5KB file using FileSystem...");
      
      const fileSystem = new FileSystem(session);
      
      // Generate 5KB content (approximately 5120 bytes)
      const contentSize = 5 * 1024; // 5KB
      const baseContent = "Archive mode test successful! This is a test file created in the session path. ";
      const repeatedContent = baseContent.repeat(Math.ceil(contentSize / baseContent.length));
      const fileContent = repeatedContent.substring(0, contentSize);
      
      // Create file path in the session path directory
      const filePath = "/tmp/archive-mode-test/test-file-5kb.txt";
      
      log(`Creating file: ${filePath}`);
      log(`File content size: ${fileContent.length} bytes`);

      const writeResult = await fileSystem.writeFile(filePath, fileContent, "overwrite");

      // Verify file write success
      expect(writeResult.success).toBe(true);
      expect(writeResult.requestId).toBeDefined();
      expect(writeResult.requestId).not.toBe("");

      log(`✅ File write successful!`);
      log(`Write file request ID: ${writeResult.requestId}`);

      
    

      // Test context sync and info functionality
      log("Testing context info functionality...");
      // Call context info after sync
      log("Calling context info after sync...");
      const infoResult = await session.context.info();
      
      expect(infoResult.success).toBe(true);
      expect(infoResult.requestId).toBeDefined();
      expect(infoResult.contextStatusData).toBeDefined();
      
      log(`✅ Context info successful!`);
      log(`Info request ID: ${infoResult.requestId}`);
      log(`Context status data count: ${infoResult.contextStatusData.length}`);
      
      // Log context status details
      if (infoResult.contextStatusData.length > 0) {
        log("Context status details:");
        infoResult.contextStatusData.forEach((status:any, index:number) => {
          log(`  [${index}] ContextId: ${status.contextId}, Path: ${status.path}, Status: ${status.status}, TaskType: ${status.taskType}`);
        });
      }
    // Get file information
      log("Getting file information...");
      
      const fileInfoResult = await fileSystem.getFileInfo(filePath);

      // Verify getFileInfo success
      expect(fileInfoResult.success).toBe(true);
      expect(fileInfoResult.fileInfo).toBeDefined();
      expect(fileInfoResult.requestId).toBeDefined();
      expect(fileInfoResult.requestId).not.toBe("");

      log(`✅ Get file info successful!`);
      log(`Get file info request ID: ${fileInfoResult.requestId}`);
      log(`File info:`, JSON.stringify(fileInfoResult.fileInfo, null, 2));

      // Verify file information (use non-null assertion since we've already verified it's defined)
      expect(fileInfoResult.fileInfo!.size).toBe(contentSize);
      expect(fileInfoResult.fileInfo!.isDirectory).toBe(false);
      log("✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully");
    });
  });
  describe("Upload Mode Validation Tests", () => {
    test("should throw error when using invalid uploadMode with newContextSync", async () => {
      log("\n=== Testing invalid uploadMode with newContextSync ===");

      const contextName = `invalid-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Create invalid upload policy
      const invalidUploadPolicy = newUploadPolicy();
      (invalidUploadPolicy as any).uploadMode = "InvalidMode"; // Invalid value

      const invalidSyncPolicy = newSyncPolicy();
      invalidSyncPolicy.uploadPolicy = invalidUploadPolicy;

      // Test with newContextSync - should throw error during validation
      expect(() => {
        newContextSync(
          contextResult.contextId,
          "/tmp/test",
          invalidSyncPolicy
        );
      }).toThrow("Invalid uploadMode value: InvalidMode. Valid values are: \"File\", \"Archive\"");

      log("✅ newContextSync correctly threw error for invalid uploadMode");
    });

    test("should throw error when using invalid uploadMode with withPolicy", async () => {
      log("\n=== Testing invalid uploadMode with withPolicy ===");

      const contextName = `invalid-policy-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Create a valid context sync first
      const contextSync = new ContextSync(
        contextResult.contextId,
        "/tmp/test"
      );

      // Create invalid upload policy
      const invalidUploadPolicy = newUploadPolicy();
      (invalidUploadPolicy as any).uploadMode = "WrongValue"; // Invalid value

      const invalidSyncPolicy = newSyncPolicy();
      invalidSyncPolicy.uploadPolicy = invalidUploadPolicy;

      // Test with withPolicy - should throw error during validation
      expect(() => {
        contextSync.withPolicy(invalidSyncPolicy);
      }).toThrow("Invalid uploadMode value: WrongValue. Valid values are: \"File\", \"Archive\"");

      log("✅ withPolicy correctly threw error for invalid uploadMode");
    });

    test("should accept valid uploadMode values", async () => {
      log("\n=== Testing valid uploadMode values ===");

      const contextName = `valid-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Test "File" mode
      const fileUploadPolicy = newUploadPolicy();
      fileUploadPolicy.uploadMode = "File";
      
      const fileSyncPolicy = newSyncPolicy();
      fileSyncPolicy.uploadPolicy = fileUploadPolicy;

      expect(() => {
        newContextSync(
          contextResult.contextId,
          "/tmp/test-file",
          fileSyncPolicy
        );
      }).not.toThrow();

      log("✅ 'File' uploadMode accepted successfully");

      // Test "Archive" mode
      const archiveUploadPolicy = newUploadPolicy();
      archiveUploadPolicy.uploadMode = "Archive";
      
      const archiveSyncPolicy = newSyncPolicy();
      archiveSyncPolicy.uploadPolicy = archiveUploadPolicy;

      expect(() => {
        newContextSync(
          contextResult.contextId,
          "/tmp/test-archive",
          archiveSyncPolicy
        );
      }).not.toThrow();

      log("✅ 'Archive' uploadMode accepted successfully");
    });

    
  });
});

  