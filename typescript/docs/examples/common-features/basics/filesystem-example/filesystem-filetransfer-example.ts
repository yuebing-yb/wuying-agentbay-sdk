import { AgentBay } from "wuying-agentbay-sdk";
import { logError, log } from "wuying-agentbay-sdk";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

async function main() {
  // Get API key from environment variable or use default value for testing
  const apiKey = process.env.AGENTBAY_API_KEY || "akm-xxx"; // Replace with your actual API key
  if (!process.env.AGENTBAY_API_KEY) {
    log("Warning: Using placeholder API key. Set AGENTBAY_API_KEY environment variable for production use.");
  }

  // Initialize the AgentBay client
  const agentBay = new AgentBay({ apiKey });

  // Create a temporary directory for our test files
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "agentbay-filetransfer-"));
  log(`Created temporary directory: ${tempDir}`);

  try {
    // Create a test file to upload
    const localUploadPath = path.join(tempDir, "upload-test.txt");
    const testContent = "This is a test file for AgentBay FileTransfer functionality.\n".repeat(10);
    fs.writeFileSync(localUploadPath, testContent);
    log(`Created test file for upload: ${localUploadPath}`);

    // Create a session; backend manages file-transfer context automatically
    log("\nCreating a new session for file transfer...");
    const createResponse = await agentBay.create({
      imageId: "linux_latest"
    });

    if (!createResponse.success || !createResponse.session) {
      log(`Failed to create session: ${createResponse.errorMessage}`);
      return;
    }

    const session = createResponse.session;
    log(`\nSession created with ID: ${session.sessionId}`);
    log(`Create Session RequestId: ${createResponse.requestId}`);

    try {
      // 1. Upload a file
      // Resolve file-transfer context path
      const contextPath = await session.fileSystem.getFileTransferContextPath();
      if (!contextPath) {
        log("No file transfer context path available, aborting.");
        return;
      }

      const remotePath = `${contextPath}/uploaded-file.txt`;
      log(`\nUploading file from ${localUploadPath} to ${remotePath}`);

      // Upload the file with progress callback
      const uploadResult = await session.fileSystem.uploadFile(
        localUploadPath,
        remotePath,
        {
          progressCb: (bytesTransferred: number) => {
            log(`Upload progress: ${bytesTransferred} bytes transferred`);
          }
        }
      );

      if (uploadResult.success) {
        log(`Upload successful!`);
        log(`Bytes sent: ${uploadResult.bytesSent}`);
        log(`Request ID (upload URL): ${uploadResult.requestIdUploadUrl}`);
        log(`Request ID (sync): ${uploadResult.requestIdSync}`);

        // Verify the file exists in remote location
        const listResult = await session.fileSystem.listDirectory(contextPath);
        if (listResult.success) {
          const fileFound = listResult.entries.some((entry: any) => entry.name === 'uploaded-file.txt');
          if (fileFound) {
            log('File verified in remote directory');
          } else {
            log('Warning: File not found in remote directory');
          }
        }
      } else {
        log(`Upload failed: ${uploadResult.error_message || uploadResult.error}`);
      }

      // 2. Create a file in the remote location for download
      const remoteDownloadPath = `${contextPath}/download-test.txt`;
      const downloadContent = "This is a test file for AgentBay FileTransfer download functionality.\n".repeat(15);

      log(`\nCreating remote file for download: ${remoteDownloadPath}`);
      const writeResult = await session.fileSystem.writeFile(remoteDownloadPath, downloadContent);
      if (writeResult.success) {
        log('Remote file created successfully');
      } else {
        log(`Failed to create remote file: ${writeResult.errorMessage}`);
      }

      // 3. Download the file
      const localDownloadPath = path.join(tempDir, "downloaded-file.txt");
      log(`\nDownloading file from ${remoteDownloadPath} to ${localDownloadPath}`);

      const downloadResult = await session.fileSystem.downloadFile(
        remoteDownloadPath,
        localDownloadPath,
        {
          progressCb: (bytesReceived: number) => {
            log(`Download progress: ${bytesReceived} bytes received`);
          }
        }
      );

      if (downloadResult.success) {
        log(`Download successful!`);
        log(`Bytes received: ${downloadResult.bytesReceived}`);
        log(`Request ID (download URL): ${downloadResult.requestIdDownloadUrl}`);
        log(`Request ID (sync): ${downloadResult.requestIdSync}`);

        // Verify downloaded file content
        const downloadedContent = fs.readFileSync(localDownloadPath, "utf-8");
        if (downloadedContent === downloadContent) {
          log('Downloaded file content verified successfully');
        } else {
          log('Warning: Downloaded file content does not match');
        }
      } else {
        log(`Download failed: ${downloadResult.error_message || downloadResult.error}`);
      }

    } finally {
      // Clean up by deleting the session when we're done
      log('\nDeleting the session...');
      try {
        const deleteResponse = await agentBay.delete(session);
        log('Session deleted successfully');
        log(`Delete Session RequestId: ${deleteResponse.requestId}`);
      } catch (error) {
        log(`Error deleting session: ${error}`);
      }
    }
  } finally {
    // Clean up temporary files
    if (fs.existsSync(tempDir)) {
      fs.rmSync(tempDir, { recursive: true, force: true });
      log(`Cleaned up temporary directory: ${tempDir}`);
    }
  }
}

main().catch(error => {
  logError('Error in main execution:', error);
  process.exit(1);
});