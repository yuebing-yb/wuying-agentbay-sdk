import { AgentBay } from '../../src';

// Define test path prefix
const TestPathPrefix = '/tmp';

async function main() {
  // Get API key from environment variable or use default value for testing
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key for testing
  if (!process.env.AGENTBAY_API_KEY) {
    console.log('Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.');
  }

  // Initialize the AgentBay client
  const agentBay = new AgentBay({ apiKey });

  // Create a new session
  console.log('\nCreating a new session...');
  const session = await agentBay.create();
  console.log(`\nSession created with ID: ${session.sessionId}`);

  try {
    // 1. Create a directory
    const testDirPath = `${TestPathPrefix}/test_directory`;
    console.log(`\nCreating directory: ${testDirPath}`);
    try {
      const success = await session.filesystem.createDirectory(testDirPath);
      console.log(`Directory created: ${success}`);
    } catch (error) {
      console.log(`Error creating directory: ${error}`);
    }

    // 2. Write a file
    const testFilePath = `${TestPathPrefix}/test_directory/sample.txt`;
    const testContent = "This is a sample file content.\nThis is the second line.\nThis is the third line.";
    console.log(`\nWriting file: ${testFilePath}`);
    try {
      const success = await session.filesystem.writeFile(testFilePath, testContent, "overwrite");
      console.log(`File written successfully: ${success}`);
    } catch (error) {
      console.log(`Error writing file: ${error}`);
    }

    // 3. Read the file we just created
    console.log(`\nReading file: ${testFilePath}`);
    try {
      const content = await session.filesystem.readFile(testFilePath);
      console.log(`File content:\n${content}`);

      // Verify content matches what we wrote
      if (content === testContent) {
        console.log('Content verification successful!');
      } else {
        console.log('Content verification failed!');
      }
    } catch (error) {
      console.log(`Error reading file: ${error}`);
    }

    // 4. Get file info
    console.log(`\nGetting file info for: ${testFilePath}`);
    try {
      const fileInfo = await session.filesystem.getFileInfo(testFilePath);
      console.log(`File info: Name=${fileInfo.name}, Path=${fileInfo.path}, Size=${fileInfo.size}, IsDirectory=${fileInfo.isDirectory}`);
    } catch (error) {
      console.log(`Error getting file info: ${error}`);
    }

    // 5. List directory
    console.log(`\nListing directory: ${testDirPath}`);
    try {
      const entries = await session.filesystem.listDirectory(testDirPath);
      console.log('Directory entries:');
      entries.forEach(entry => {
        console.log(`${entry.isDirectory ? '[DIR]' : '[FILE]'} ${entry.name}`);
      });
    } catch (error) {
      console.log(`Error listing directory: ${error}`);
    }

    // 6. Edit file
    console.log(`\nEditing file: ${testFilePath}`);
    try {
      const edits = [
        {
          oldText: "second line",
          newText: "MODIFIED second line"
        }
      ];
      const success = await session.filesystem.editFile(testFilePath, edits, false);
      console.log(`File edited successfully: ${success}`);

      // Read the file again to verify the edit
      const content = await session.filesystem.readFile(testFilePath);
      console.log(`Edited file content:\n${content}`);
    } catch (error) {
      console.log(`Error editing file: ${error}`);
    }

    // 7. Search files
    console.log(`\nSearching for files in ${TestPathPrefix} containing 'sample'`);
    try {
      const searchResults = await session.filesystem.searchFiles(TestPathPrefix, "sample", undefined);
      console.log(`Search results: ${searchResults.length} files found`);
      searchResults.forEach(path => {
        console.log(`- ${path}`);
      });
    } catch (error) {
      console.log(`Error searching files: ${error}`);
    }

    // 8. Move/Rename file
    const newFilePath = `${TestPathPrefix}/test_directory/renamed.txt`;
    console.log(`\nMoving file from ${testFilePath} to ${newFilePath}`);
    try {
      const success = await session.filesystem.moveFile(testFilePath, newFilePath);
      console.log(`File moved successfully: ${success}`);

      // List directory again to verify the move
      const entries = await session.filesystem.listDirectory(testDirPath);
      console.log('Directory entries after move:');
      entries.forEach(entry => {
        console.log(`${entry.isDirectory ? '[DIR]' : '[FILE]'} ${entry.name}`);
      });
    } catch (error) {
      console.log(`Error moving file: ${error}`);
    }
  } finally {
    // Clean up by deleting the session when we're done
    console.log('\nDeleting the session...');
    try {
      await agentBay.delete(session);
      console.log('Session deleted successfully');
    } catch (error) {
      console.log(`Error deleting session: ${error}`);
    }
  }
}

main().catch(error => {
  console.error('Error in main execution:', error);
  process.exit(1);
}); 