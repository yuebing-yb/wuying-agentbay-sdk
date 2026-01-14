/**
 * Example: List MCP Tools and Call a Tool
 *
 * This example demonstrates:
 * 1. Creating a session
 * 2. Listing all available MCP tools
 * 3. Calling a specific tool (shell command)
 * 4. Cleaning up the session
 */

import { AgentBay, CreateSeesionWithParams } from 'wuying-agentbay-sdk';

async function main() {
  // Initialize AgentBay client
  console.log('Initializing AgentBay client...');
  const agentBay = new AgentBay();

  // Create a session
  console.log('\n1. Creating session...');
  const params : CreateSeesionWithParams ={
    imageId: "linux_latest",
  };
  const sessionResult = await agentBay.create(params);
  const session = sessionResult.session;
  console.log('✓ Session created successfully');
  console.log(`  Session ID: ${session.getSessionId()}`);
  console.log(`  Request ID: ${sessionResult.requestId}`);

  try {
    // List all available MCP tools
    console.log('\n2. Listing available MCP tools...');
    const toolsResult = await session.listMcpTools();
    console.log(`✓ Found ${toolsResult.tools.length} MCP tools`);
    console.log(`  Request ID: ${toolsResult.requestId}`);

    // Display first 10 tools
    console.log('\n  Available tools (showing first 10):');
    for (let i = 0; i < Math.min(10, toolsResult.tools.length); i++) {
      const tool = toolsResult.tools[i];
      console.log(`  ${i + 1}. ${tool.name}`);
      console.log(`     Description: ${tool.description}`);
      console.log(`     Server: ${tool.server}`);
      if (tool.inputSchema.required) {
        console.log(`     Required params: ${tool.inputSchema.required.join(', ')}`);
      }
      console.log();
    }

    // Find and display the shell tool details
    console.log("\n3. Finding 'shell' tool details...");
    const shellTool = toolsResult.tools.find((tool: any) => tool.name === 'shell');

    if (shellTool) {
      console.log("✓ Found 'shell' tool");
      console.log(`  Description: ${shellTool.description}`);
      console.log(`  Server: ${shellTool.server}`);
      console.log(`  Input Schema:`);
      console.log(`    ${JSON.stringify(shellTool.inputSchema, null, 4)}`);
    } else {
      console.log("✗ 'shell' tool not found");
      return;
    }

    // Call the shell tool
    console.log("\n4. Calling 'shell' tool...");
    const result = await session.callMcpTool('shell', {
      command: "echo 'Hello from MCP Tool!'",
      timeout_ms: 1000
    });

    if (result.success) {
      console.log('✓ Tool call successful');
      console.log(`  Request ID: ${result.requestId}`);
      console.log(`  Output:`);
      console.log(`    ${result.data}`);
    } else {
      console.log('✗ Tool call failed');
      console.log(`  Error: ${result.errorMessage}`);
      console.log(`  Request ID: ${result.requestId}`);
    }

    // Call another command to demonstrate flexibility
    console.log("\n5. Calling 'shell' tool with different command...");
    const result2 = await session.callMcpTool('shell', {
      command: 'pwd',
      timeout_ms: 1000
    });

    if (result2.success) {
      console.log('✓ Tool call successful');
      console.log(`  Request ID: ${result2.requestId}`);
      console.log(`  Current directory:`);
      console.log(`    ${result2.data}`);
    } else {
      console.log('✗ Tool call failed');
      console.log(`  Error: ${result2.errorMessage}`);
    }

    // Demonstrate error handling
    console.log('\n6. Demonstrating error handling (invalid command)...');
    const result3 = await session.callMcpTool('shell', {
      command: 'this_command_does_not_exist_12345',
      timeout_ms: 1000
    });

    if (result3.success) {
      console.log('✓ Command executed');
      console.log(`  Output: ${result3.data}`);
    } else {
      console.log('✓ Error handled correctly');
      console.log(`  Request ID: ${result3.requestId}`);
      console.log(`  Error message: ${result3.errorMessage.substring(0, 100)}...`);
    }

  } finally {
    // Clean up - delete the session
    console.log('\n7. Cleaning up...');
    const deleteResult = await agentBay.delete(session);
    if (deleteResult.success) {
      console.log('✓ Session deleted successfully');
      console.log(`  Request ID: ${deleteResult.requestId}`);
    } else {
      console.log('✗ Failed to delete session');
      console.log(`  Error: ${deleteResult.errorMessage}`);
    }
  }

  console.log('\n' + '='.repeat(60));
  console.log('Example completed successfully!');
  console.log('='.repeat(60));
}

// Run the example
main().catch((error) => {
  console.error('Error running example:', error);
  process.exit(1);
});

