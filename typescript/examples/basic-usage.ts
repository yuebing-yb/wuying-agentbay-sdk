import { AgentBay } from '../src';
import { log, logError } from '../src/utils/logger';
import { getTestApiKey } from '../tests/utils/test-helpers';
async function main() {
  try {
    // Use the test API key function from test-helpers
    const apiKey = getTestApiKey();
    log('Using test API key for demonstration purposes.');

    // Initialize the AgentBay client
    const agentBay = new AgentBay({ apiKey });

    // Create a new session
    log('Creating a new session...');
    const session = await agentBay.create();
    log(`Session created with ID: ${session.sessionId}`);

    // Execute a command
    log('\nExecuting a command...');
    const result = await session.command.executeCommand('ls -la');
    log('Command result:', result);

    // Read a file
    log('\nReading a file...');
    const content = await session.filesystem.readFile('/etc/hosts');
    log(`File content: ${content}`);


    // Get the session link
    log('\nGetting session link...');
    try {
      const link = await session.getLink();
      log(`Session link: ${link}`);
    } catch (error) {
      log(`Note: Failed to get session link: ${error}`);
    }
    
    // Use the UI module to take a screenshot
    log('\nTaking a screenshot...');
    try {
      const screenshot = await session.ui.screenshot();
      log(`Screenshot data length: ${screenshot.length} characters`);
    } catch (error) {
      log(`Note: Failed to take screenshot: ${error}`);
    }
    
    // List all sessions
    log('\nListing all sessions...');
    const sessions = await agentBay.list();
    log('Available sessions count:', sessions.length);
    log('Session IDs:', sessions.map(s => s.sessionId));

    // Delete the session
    log('\nDeleting the session...');
    await agentBay.delete(session);
    log('Session deleted successfully');

  } catch (error) {
    logError('Error:', error);
    // In a Node.js environment, you would use process.exit(1) here
    throw error;
  }
}

main();
