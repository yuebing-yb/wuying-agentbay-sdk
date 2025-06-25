import { AgentBay, Context } from '../src';
import { log, logError } from '../src/utils/logger';

/**
 * Example demonstrating how to use the Context API in TypeScript.
 */
async function main() {
  try {
    // Initialize the AgentBay client
    // You can provide the API key as a parameter or set the AGENTBAY_API_KEY environment variable
    const agentBay = new AgentBay({
      apiKey: process.env.AGENTBAY_API_KEY || 'your_api_key_here', // Replace with your actual API key
    });

    // Example 1: List all contexts
    log('\nExample 1: Listing all contexts...');
    const contexts = await agentBay.context.list();
    log(`Found ${contexts.length} contexts:`);
    for (const context of contexts) {
      log(`- ${context.name} (${context.id}): state=${context.state}, os=${context.osType}`);
    }

    // Example 2: Get a context (create if it doesn't exist)
    log('\nExample 2: Getting a context (creating if it doesn\'t exist)...');
    const contextName = 'my-test-context';
    const context = await agentBay.context.get(contextName, true);
    if (context) {
      log(`Got context: ${context.name} (${context.id})`);
    } else {
      log('Context not found and could not be created');
      return;
    }

    // Example 3: Create a session with the context
    log('\nExample 3: Creating a session with the context...');
    const session = await agentBay.create({
      contextId: context.id,
      labels: {
        username: 'alice',
        project: 'my-project',
      },
    });
    log(`Session created with ID: ${session.sessionId}`);

    // Example 4: Update the context
    log('\nExample 4: Updating the context...');
    context.name = 'renamed-test-context';
    const updatedContext = await agentBay.context.update(context);
    log(`Context updated: ${updatedContext.name} (${updatedContext.id})`);

    // Clean up
    log('\nCleaning up...');

    // Delete the session
    await agentBay.delete(session);
    log('Session deleted successfully');

    // Delete the context
    log('Deleting the context...');
    await agentBay.context.delete(context);
    log('Context deleted successfully');
  } catch (error) {
    logError('Error:', error);
  }
}

// Run the example
main().catch(logError);
