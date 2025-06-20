import { AgentBay } from '../../src';

async function main() {
  // Get API key from environment variable or use default value for testing
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key for testing
  if (!process.env.AGENTBAY_API_KEY) {
    console.log('Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.');
  }

  // Initialize the AgentBay client
  const agentBay = new AgentBay({ apiKey });

  // Example 1: Create a session with custom labels
  console.log('\nExample 1: Creating a session with custom labels...');

  // Create parameters with labels
  const params = {
    labels: {
      username: 'alice',
      project: 'my-project'
    }
  };

  const session = await agentBay.create(params);
  console.log(`\nSession created with ID: ${session.sessionId} and labels: username=alice, project=my-project`);

  // Example 2: List sessions by labels
  console.log('\nExample 2: Listing sessions by labels...');

  // Query sessions with the "project" label set to "my-project"
  try {
    const sessionsByLabel = await agentBay.listByLabels({
      project: 'my-project'
    });

    console.log(`\nFound ${sessionsByLabel.length} sessions with project=my-project:`);
    sessionsByLabel.forEach((s, i) => {
      console.log(`  ${i + 1}. Session ID: ${s.sessionId}`);
    });
  } catch (error) {
    console.log(`\nError listing sessions by labels: ${error}`);
  }

  // Clean up
  console.log('\nCleaning up sessions...');

  try {
    await agentBay.delete(session);
    console.log('Session deleted successfully');
  } catch (error) {
    console.log(`Error deleting session: ${error}`);
  }
}

main().catch(error => {
  console.error('Error in main execution:', error);
  process.exit(1);
}); 