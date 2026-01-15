import { AgentBay, CreateSessionParams } from "../../src/agent-bay";
import { ContextSync } from "../../src/context-sync";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import { log } from "../../src/utils/logger";
import { Session } from "../../src/session";

// Skip in CI if no API key, Jest will still collect but we handle at runtime
const apiKey = process.env.AGENTBAY_API_KEY || "";
log(`API Key: ${apiKey ? 'Present' : 'Missing'}`);
log(`CI Environment: ${process.env.CI ? 'Yes' : 'No'}`);

describe("File Transfer Integration", () => {
  let agentBay: AgentBay;
  let sessionId: string;
  let tempDir: string;
  let testContent: string;
  let session: Session;
  let contextPath: string | null;

  beforeAll(async () => {
    log("Starting beforeAll...");
    if (!apiKey || process.env.CI) {
      log("Skipping tests due to missing API key or CI environment");
      return;
    }
    log("Creating AgentBay instance...");
    agentBay = new AgentBay({ apiKey });

    // Create session; backend will manage file-transfer context automatically
    const params :CreateSessionParams = {
      imageId:'linux_latest',
      enableBrowserReplay:true,
    } 

    log("Creating session...");
    const sessionResult = await agentBay.create(params);
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error("Failed to create session");
    }

    sessionId = sessionResult.session.getSessionId();
    log(`Session created with ID: ${sessionId}`);

    // Create temporary directory for test files
    tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "file-transfer-test-"));
    session = sessionResult.session;

    // Get file transfer context path with retry mechanism
    log("Getting file transfer context path...");
    
    // Wait for session to be fully initialized
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Try to get file transfer context path with retry mechanism
    
    
      try {
        contextPath = await session.fileSystem.getFileTransferContextPath();
        log(`contextPath = ${contextPath}`);
        
        if (contextPath) {
          log(`✅ Successfully obtained file transfer context path: ${contextPath}`);
          
        } else {
          log(`⚠️ contextPath is null, retrying...`);
        }
      } catch (error) {
        log(`❌ Error getting file transfer context path : ${error}`);
       
      }
    
    if (!contextPath) {
      log("❌ Failed to obtain file transfer context path after all retries");
      log("Possible causes:");
      log("  1. Session not fully initialized");
      log("  2. File transfer feature not enabled for this session");
      log("  3. API key lacks file transfer permissions");
      log("  4. Backend configuration issue");
      
      // Try to get more diagnostic information
      try {
        const sessionId = session.getSessionId();
        log(`Session ID: ${sessionId}`);
      } catch (infoError) {
        log(`Failed to get session info: ${infoError}`);
      }
      
      throw new Error("File transfer context path is null - cannot proceed with file transfer tests");
    }
    
    log("beforeAll completed successfully");
  });

  afterAll(async () => {
    log("Starting afterAll...");
    if (!apiKey || process.env.CI) {
      log("Skipping cleanup due to missing API key or CI environment");
      return;
    }

    // Clean up temporary files
    if (tempDir && fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
      log(`Cleaned up temporary directory: ${tempDir}`);
    }

    // Clean up session
    if (session) {
      try {
        log('\nDeleting the session...');
        const deleteResponse = await agentBay.delete(session);
        log('Session deleted successfully');
        log(`Delete Session RequestId: ${deleteResponse.requestId}`);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    }

    log("afterAll completed");
  });

  it("should upload files successfully", async () => {
    log("Starting upload test...");
    if (!apiKey || process.env.CI) {
      log("Skipping upload test due to missing API key or CI environment");
      return;
    }

    // Create test content
    testContent = "This is a test file for AgentBay FileTransfer upload integration test.\n".repeat(10);
    const tempFilePath = path.join(tempDir, "upload_test.txt");
    fs.writeFileSync(tempFilePath, testContent);
    log(`Created test file at: ${tempFilePath}`);

    const remotePath = `${contextPath}/uploaded-file.txt`;
    log(`\nUploading file from ${tempFilePath} to ${remotePath}`);
    
    // Upload the file with progress callback
    log("Calling uploadFile...");
    const uploadResult = await session.fileSystem.uploadFile(
      tempFilePath,
      remotePath,
      {
        progressCb: (bytesTransferred: number) => {
          log(`Upload progress: ${bytesTransferred} bytes transferred`);
        }
      }
    );
    log(`Upload result: ${JSON.stringify(uploadResult, null, 2)}`);

    // Verify upload result
    expect(uploadResult.success).toBe(true);
    expect(uploadResult.bytesSent).toBeGreaterThan(0);
    expect(uploadResult.requestIdUploadUrl).toBeDefined();
    expect(uploadResult.requestIdSync).toBeDefined();

    log("Upload successful!");
    log(`Bytes sent: ${uploadResult.bytesSent}`);
    log(`Request ID (upload URL): ${uploadResult.requestIdUploadUrl}`);
    log(`Request ID (sync): ${uploadResult.requestIdSync}`);

    // Verify the file exists in remote location
    const listResult = await session.fileSystem.listDirectory(contextPath!);
    expect(listResult.success).toBe(true);
    expect(listResult.entries).toBeDefined();

    // Check if our uploaded file is in the directory listing
    const fileFound = listResult.entries.some((entry: any) => entry.name === 'uploaded-file.txt');
    expect(fileFound).toBe(true);

    log("File found in remote directory!");

    // Verify file content by reading it back
    const readResult = await session.fileSystem.readFile(remotePath);
    expect(readResult.success).toBe(true);
    expect(readResult.content).toBe(testContent);

    log("File content verified!");
  });

  it("should download files successfully", async () => {
    log("Starting download test...");
    if (!apiKey || process.env.CI) {
      log("Skipping download test due to missing API key or CI environment");
      return;
    }

    // Create a file in the remote location for download
    const remoteDownloadPath = `${contextPath!}/download-test.txt`;
    const downloadContent = "This is a test file for AgentBay FileTransfer download integration test.\n".repeat(15);

    log(`\nCreating remote file for download: ${remoteDownloadPath}`);
    const writeResult = await session.fileSystem.writeFile(remoteDownloadPath, downloadContent);
    if (writeResult.success) {
      log('Remote file created successfully');
    } else {
      log(`Failed to create remote file: ${writeResult.errorMessage}`);
    }
    expect(writeResult.success).toBe(true);

    // Create a temporary file path for download
    const tempFilePath = path.join(tempDir, "download_test.txt");
    log(`\nDownloading file from ${remoteDownloadPath} to ${tempFilePath}`);

    // Download the file with progress callback
    log("Calling downloadFile...");
    const downloadResult = await session.fileSystem.downloadFile(
      remoteDownloadPath,
      tempFilePath,
      {
        progressCb: (bytesReceived: number) => {
          log(`Download progress: ${bytesReceived} bytes received`);
        }
      }
    );
    log(`Download result: ${JSON.stringify(downloadResult, null, 2)}`);

    // Verify download result
    expect(downloadResult.success).toBe(true);
    expect(downloadResult.bytesReceived).toBeGreaterThan(0);
    expect(downloadResult.requestIdDownloadUrl).toBeDefined();
    expect(downloadResult.requestIdSync).toBeDefined();
    expect(downloadResult.localPath).toBe(tempFilePath);

    log(`Download successful!`);
    log(`Bytes received: ${downloadResult.bytesReceived}`);
    log(`Request ID (download URL): ${downloadResult.requestIdDownloadUrl}`);
    log(`Request ID (sync): ${downloadResult.requestIdSync}`);

    // Verify downloaded file content
    const downloadedContent = fs.readFileSync(tempFilePath, 'utf-8');
    log(`Downloaded file content length: ${downloadedContent.length} bytes`);
    if (downloadedContent === downloadContent) {
      log('Downloaded file content verified successfully');
    } else {
      log('Warning: Downloaded file content does not match');
    }
    expect(downloadedContent).toBe(downloadContent);

    log("Download test completed successfully!");
  });
});