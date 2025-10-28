import { AgentBay, logError, log, ContextSync } from 'wuying-agentbay-sdk';

/**
 * Context Management Example
 *
 * This example demonstrates how to use the Context API in TypeScript.
 */
async function main() {
  try {
    // Initialize the AgentBay client
    // You can provide the API key as a parameter or set the AGENTBAY_API_KEY environment variable
    const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key
    if (!process.env.AGENTBAY_API_KEY) {
      log('Warning: Using placeholder API key. Set AGENTBAY_API_KEY environment variable for production use.');
    }

    const agentBay = new AgentBay({ apiKey });

    // Example 1: List all contexts
    log('\nExample 1: Listing all contexts...');
    try {
      const listResult = await agentBay.context.list();
      log(`Found ${listResult.contexts.length} contexts (RequestID: ${listResult.requestId}):`);
      for (const ctx of listResult.contexts) {
        log(`- ${ctx.name} (${ctx.id}): state=${ctx.state}, os=${ctx.osType}`);
      }
    } catch (error) {
      log(`Error listing contexts: ${error}`);
    }

    // Example 2: Get a context (create if it doesn't exist)
    log('\nExample 2: Getting a context (creating if it doesn\'t exist)...');
    const contextName = 'my-test-context';
    const getResult = await agentBay.context.get(contextName, true);
    if (!getResult.contextId || getResult.contextId === '') {
      log('Context not found and could not be created');
      return;
    }

    log(`Got context: ${getResult.context.name} (${getResult.contextId}) with RequestID: ${getResult.requestId}`);

    // Use the Context object directly
    const context = getResult.context;

    // Example 3: Create a session with the context
    log('\nExample 3: Creating a session with the context...');
    const contextSync = new ContextSync(context.id, '/mnt/persistent');
    const sessionResult = await agentBay.create({
      contextSync: [contextSync],
      labels: {
        username: 'alice',
        project: 'my-project'
      }
    });

    if (!sessionResult.session) {
      log('Error creating session');
      return;
    }

    log(`Session created with ID: ${sessionResult.session.sessionId} (RequestID: ${sessionResult.requestId})`);
    log('Note: The create() method automatically monitored the context status');
    log('and only returned after all context operations were complete or reached maximum retries.');
    const session = sessionResult.session;

    // Example 4: Update the context
    log('\nExample 4: Updating the context...');
    context.name = 'renamed-test-context';
    try {
      const updateResult = await agentBay.context.update(context);
      if (!updateResult.success) {
        log('Context update was not successful');
      } else {
        log(`Context updated successfully to: ${context.name} (RequestID: ${updateResult.requestId})`);
      }
    } catch (error) {
      log(`Error updating context: ${error}`);
    }

    // Clean up
    log('\nCleaning up...');

    // Delete the session with context synchronization
    try {
      log('Deleting the session with context synchronization...');
      const deleteSessionResult = await agentBay.delete(session, true); // Using syncContext=true
      log(`Session deleted successfully with context synchronization (RequestID: ${deleteSessionResult.requestId})`);
      log('Note: The delete() method synchronized the context before session deletion');
      log('and monitored all context operations until completion.');

      // Alternative method using session's delete method:
      // const deleteSessionResult = await session.delete(true);
    } catch (error) {
      log(`Error deleting session: ${error}`);
    }

    // Example 5: Clear context data
    log('\nExample 5: Clearing context data...');
    log('Starting synchronous context clear (recommended approach)...');
    try {
      const clearResult = await agentBay.context.clear(context.id, 30, 2.0);
      log(`Clear result: Success=${clearResult.success}, Status=${clearResult.status}, RequestID=${clearResult.requestId}`);

      if (clearResult.success) {
        log('✅ Context data cleared successfully');
        log(`   Context ID: ${clearResult.contextId}`);
        log(`   Final Status: ${clearResult.status}`);
      } else {
        log(`❌ Context data clearing failed: ${clearResult.errorMessage}`);
      }
    } catch (clearError: any) {
      if (clearError.message.includes('timed out')) {
        log(`⏱️ Clear timed out: ${clearError.message}`);
      } else {
        log(`❌ Error during context clear: ${clearError.message}`);
      }
    }

    // Clean up
    log('\nCleaning up...');
    log('Note: Context data has been cleared, but the context itself still exists.');

    // Delete the context
    log('Deleting the context...');
    try {
      const deleteContextResult = await agentBay.context.delete(context);
      log(`Context deleted successfully (RequestID: ${deleteContextResult.requestId})`);
    } catch (error) {
      log(`Error deleting context: ${error}`);
    }
  } catch (error) {
    logError(`Error initializing AgentBay: ${error}`);
  }
}

// Execute the main function
main().catch(error => {
  logError('Error in main execution:', error);
  process.exit(1);
});
