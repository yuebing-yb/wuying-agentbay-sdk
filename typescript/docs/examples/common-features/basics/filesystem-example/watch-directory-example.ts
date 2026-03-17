/**
 * Watch Directory Example
 * 
 * This example demonstrates how to use the watch_directory functionality
 * to monitor file changes in a directory.
 */

import { AgentBay, CreateSessionParams } from "wuying-agentbay-sdk";
import { FileChangeEvent } from "wuying-agentbay-sdk";

async function main(): Promise<void> {
  // Get API key from environment variable
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.log("❌ Please set the AGENTBAY_API_KEY environment variable");
    return;
  }

  console.log("🚀 Watch Directory Example");
  console.log("=".repeat(50));

  try {
    // Initialize AgentBay client
    const agentbay = new AgentBay({ apiKey });
    console.log("✅ AgentBay client initialized");

    // Create session with code_latest ImageId
    const sessionParams = { imageId: "code_latest" };
    const sessionResult = await agentbay.create(sessionParams);

    if (!sessionResult.success) {
      console.log(`❌ Failed to create session: ${sessionResult.errorMessage}`);
      return;
    }

    const session = sessionResult.session;
    console.log(`✅ Session created: ${session.getSessionId()}`);

    try {
      // Create a test directory to monitor
      const testDir = "/tmp/watch_example";
      console.log(`\n📁 Creating test directory: ${testDir}`);

      const createResult = await session.fileSystem.createDirectory(testDir);
      if (!createResult.success) {
        console.log(`❌ Failed to create directory: ${createResult.errorMessage}`);
        return;
      }

      console.log("✅ Test directory created");

      // Set up file change monitoring
      const detectedChanges: FileChangeEvent[] = [];

      const onFileChange = (events: FileChangeEvent[]) => {
        console.log(`\n🔔 Detected ${events.length} file changes:`);
        for (const event of events) {
          console.log(`   📄 ${event.eventType.toUpperCase()}: ${event.path} (${event.pathType})`);
        }
        detectedChanges.push(...events);
      };

      console.log("\n👁️  Starting directory monitoring...");
      console.log("   Press Ctrl+C to stop monitoring");

      // Start monitoring
      const controller = new AbortController();
      const { monitoring, ready } = session.fileSystem.watchDirectory(
        testDir,
        onFileChange,
        1000, // Check every second
        controller.signal
      );

      console.log("✅ Directory monitoring started");

      // Wait for baseline to be established before performing file operations
      await ready;

      // Demonstrate file operations
      console.log("\n🔨 Demonstrating file operations...");

      // Create some files
      const filesToCreate = [
        { name: "example1.txt", content: "Hello, World!" },
        { name: "example2.txt", content: "This is a test file." },
        { name: "config.json", content: '{"setting": "value"}' }
      ];

      for (const file of filesToCreate) {
        const filepath = `${testDir}/${file.name}`;
        console.log(`   Creating: ${file.name}`);

        const writeResult = await session.fileSystem.writeFile(filepath, file.content);
        if (writeResult.success) {
          console.log(`   ✅ Created: ${file.name}`);
        } else {
          console.log(`   ❌ Failed to create ${file.name}: ${writeResult.errorMessage}`);
        }

        // Give time for monitoring to detect changes
        await new Promise(resolve => setTimeout(resolve, 1500));
      }

      // Modify a file
      console.log("\n   Modifying example1.txt...");
      const modifyResult = await session.fileSystem.writeFile(
        `${testDir}/example1.txt`,
        "Hello, World! - Modified content"
      );
      if (modifyResult.success) {
        console.log("   ✅ Modified example1.txt");
      } else {
        console.log(`   ❌ Failed to modify file: ${modifyResult.errorMessage}`);
      }

      // Wait a bit more to capture all events
      console.log("\n⏳ Waiting for final events...");
      await new Promise(resolve => setTimeout(resolve, 3000));

      // Stop monitoring
      console.log("\n🛑 Stopping directory monitoring...");
      controller.abort();
      await monitoring;
      console.log("✅ Directory monitoring stopped");

      // Summary
      console.log("\n📊 Summary:");
      console.log(`   Total events detected: ${detectedChanges.length}`);

      if (detectedChanges.length > 0) {
        console.log("   Event breakdown:");
        const eventTypes: Record<string, number> = {};
        for (const event of detectedChanges) {
          eventTypes[event.eventType] = (eventTypes[event.eventType] || 0) + 1;
        }

        for (const [eventType, count] of Object.entries(eventTypes)) {
          console.log(`     ${eventType}: ${count}`);
        }
      }

      console.log("\n✨ Example completed successfully!");

    } finally {
      // Clean up session
      console.log("\n🧹 Cleaning up...");
      const deleteResult = await agentbay.delete(session);
      if (deleteResult.success) {
        console.log("✅ Session cleaned up successfully");
      } else {
        console.log(`⚠️  Session cleanup warning: ${deleteResult.errorMessage}`);
      }
    }

  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      console.log("\n\n⏹️  Monitoring stopped by user");
    } else {
      console.log(`\n❌ An error occurred: ${error}`);
    }
  }
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
  console.log("\n\n⏹️  Received interrupt signal, stopping...");
  process.exit(0);
});

main().catch(console.error); 