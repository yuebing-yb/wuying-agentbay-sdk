/**
 * Mobile Simulate with User Specific Context Example
 * 
 * This example demonstrates how to use the mobile simulate feature with a user specific context 
 * to simulate mobile devices across sessions.
 * 
 * Steps:
 * 1. Get a user specific context
 * 2. Check if the mobile dev info file exists in user's specific context, if not, get a mobile dev info file from DumpSDK or real device
 * 3. Upload mobile dev info file to user's specific context
 * 4. Create a session with mobile simulate configuration and user's specific context
 * 5. Wait for mobile simulate to complete
 * 6. Get device model after mobile simulate
 * 7. Delete session
 */

// @ts-nocheck
import { AgentBay, Session, MobileSimulateService, MobileSimulateMode, ContextSync, SyncPolicy, BWList, WhiteList } from 'wuying-agentbay-sdk';
import { readFileSync } from 'fs';
import { join } from 'path';

let session: Session | null = null;

async function runOnMobileSession(client: AgentBay): Promise<void> {
  try {
    console.log('Getting a user specific context...');
    const contextResult = await client.context.get('13000000001', true);
    if (!contextResult.success || !contextResult.context) {
      throw new Error(`Failed to get context: ${contextResult.errorMessage}`);
    }
    
    const context = contextResult.context;
    console.log(`context.id = ${context.id}, context.name = ${context.name}`);
    
    // Create sync policy with white list
    const syncPolicy: SyncPolicy = {
      bwList: {
        whiteLists: [
          {
            path: '/com.wuying.devinfo',
            excludePaths: []
          }
        ]
      }
    };
    
    const contextSync: ContextSync = {
      contextId: context.id,
      path: '/data/data',
      policy: syncPolicy
    };
    
    console.log('Checking or uploading mobile dev info file...');

    const simulateService = new MobileSimulateService(client);
    simulateService.setSimulateEnable(true);
    simulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);
    
    // Check if the mobile dev info file exists in user's specific context
    const hasMobileInfo = await simulateService.hasMobileInfo(contextSync);
    if (!hasMobileInfo) {
      // If not, get a mobile dev info file from DumpSDK or real device
      const mobileInfoFilePath = join(
        __dirname,
        '..',
        '..',
        '..',
        '..',
        'resource',
        'mobile_info_model_a.json'
      );
      
      const mobileInfoContent = readFileSync(mobileInfoFilePath, 'utf-8');
      
      const uploadResult = await simulateService.uploadMobileInfo(mobileInfoContent, contextSync);
      if (!uploadResult.success) {
        throw new Error(`Failed to upload mobile dev info: ${uploadResult.errorMessage}`);
      }
      console.log('Mobile dev info uploaded successfully');
    } else {
      console.log(`Mobile dev info already exists: ${hasMobileInfo}`);
    }
    
    // Create session with mobile simulate configuration and user's specific context
    console.log('Creating session...');
    const sessionResult = await client.create({
      imageId: 'mobile_latest',
      contextSync: [contextSync],
      extraConfigs: {
        mobile: {
          // Set mobile simulate config
          simulateConfig: simulateService.getSimulateConfig(),
        },
      },
    });
    
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(`Failed to create session: ${sessionResult.errorMessage}`);
    }
    
    session = sessionResult.session;
    console.log(`Session created with ID: ${session.sessionId}`);
    
    // Wait for mobile simulate to complete
    console.log('Waiting for mobile simulate to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get device model after mobile simulate
    console.log('Getting device model after mobile simulate...');
    const result = await session.command.executeCommand('getprop ro.product.model');
    if (!result.success) {
      throw new Error(`Failed to get device model: ${result.errorMessage}`);
    }
    
    const productModel = result.output.trim();
    console.log(`Session device model: ${productModel}`);
    
  } catch (error) {
    throw new Error(`Error during runOnMobileSession: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function main() {
  console.log('=== Mobile Simulate with User Specific Context Example ===\n');
  
  // Get API key from environment variable
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.error('Error: AGENTBAY_API_KEY environment variable is not set');
    console.error('Please set it with: export AGENTBAY_API_KEY=your_api_key');
    process.exit(1);
  }
  
  // Initialize AgentBay client
  const client = new AgentBay({ apiKey });
  console.log('AgentBay client initialized');
  
  try {
    // Run on mobile session
    await runOnMobileSession(client);
    
    // Delete session
    console.log('\nDeleting session...');
    const deleteResult = await session!.delete({ syncContext: true });
    if (!deleteResult.success) {
      throw new Error(`Failed to delete session: ${deleteResult.errorMessage}`);
    }
    console.log(`Session deleted successfully (RequestID: ${deleteResult.requestId})`);
    
    console.log('\n=== Example completed successfully ===');
    
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    
    // Cleanup session on error
    if (session) {
      try {
        await session.delete({ syncContext: true });
      } catch (e) {
        console.warn('Warning: Failed to cleanup session');
      }
    }
    
    process.exit(1);
  }
}

// Run the example
main();

