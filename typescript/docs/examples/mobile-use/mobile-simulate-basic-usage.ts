/**
 * Mobile Simulate Example
 * 
 * This example demonstrates how to use the mobile simulate feature to simulate
 * different mobile devices across sessions.
 */

// @ts-nocheck
import { AgentBay, Session, MobileSimulateService, MobileSimulateMode } from 'wuying-agentbay-sdk';
import { readFileSync } from 'fs';
import { join } from 'path';

let session1: Session | null = null;
let session2: Session | null = null;
let mobileSimContextId: string | null = null;

async function runOnFirstMobileSession(client: AgentBay): Promise<void> {
  console.log('=== First Mobile Session ===');
  
  try {
    // Upload mobile info file for first time
    // How to get the mobile info file please contact the support team.
    console.log('Uploading mobile info file for first time...');
    
    // Get the path to mobile_info_model_a.json
    // Navigate from typescript/docs/examples/mobile-use/mobile-simulate-example to resource/
    const mobileInfoFilePath = join(
      __dirname,
      '..',
      '..',
      '..',
      '..',
      'resource',
      'mobile_info_model_a.json'
    );
    
    // Read the mobile info file
    const mobileInfoContent = readFileSync(mobileInfoFilePath, 'utf-8');
    
    // Upload mobile info
    const simulateService = new MobileSimulateService(client);
    simulateService.setSimulateEnable(true);
    simulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);
    const uploadResult = await simulateService.uploadMobileInfo(mobileInfoContent);
    if (!uploadResult.success) {
      throw new Error(`Failed to upload mobile info file: ${uploadResult.errorMessage}`);
    }
    
    mobileSimContextId = uploadResult.mobileSimulateContextId!;
    console.log(`Mobile simulate context id uploaded successfully: ${mobileSimContextId}`);
    
    // Create session with mobile simulate configuration
    console.log('Creating first session...');
    const sessionResult = await client.create({
      imageId: 'mobile_latest',
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
    
    session1 = sessionResult.session;
    console.log(`Session created with ID: ${session1!.sessionId}`);
    
    // Wait for mobile simulate to complete
    console.log('Waiting for mobile simulate to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get device model after mobile simulate
    console.log('Getting device model after mobile simulate...');
    const result = await session1!.command.executeCommand('getprop ro.product.model');
    if (!result.success) {
      throw new Error(`Failed to get device model: ${result.errorMessage}`);
    }
    
    const productModel = result.output.trim();
    console.log(`First session device model: ${productModel}`);
    
  } catch (error) {
    throw new Error(`Error during run_on_first_mobile_session: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function runOnSecondMobileSession(client: AgentBay): Promise<void> {
  console.log('\n=== Second Mobile Session ===');
  
  try {
    // Use the same mobile simulate context id as the first session
    console.log('Creating second session...');
    const simulateService = new MobileSimulateService(client);
    simulateService.setSimulateEnable(true);
    simulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);
    simulateService.setSimulateContextId(mobileSimContextId!);
    const sessionResult = await client.create({
      imageId: 'mobile_latest',
      extraConfigs: {
        mobile: {
          lockResolution: false,
          // Set mobile simulate config
          simulateConfig: simulateService.getSimulateConfig(),
        },
      },
    });
    
    if (!sessionResult.success || !sessionResult.session) {
      throw new Error(`Failed to create session: ${sessionResult.errorMessage}`);
    }
    
    session2 = sessionResult.session;
    console.log(`Session created with ID: ${session2!.sessionId}`);
    
    // Wait for mobile simulate to complete
    console.log('Waiting for mobile simulate to complete...');
    await new Promise(resolve => setTimeout(resolve, 5000));
    
    // Get device model after mobile simulate
    console.log('Getting device model after mobile simulate...');
    const result = await session2!.command.executeCommand('getprop ro.product.model');
    if (!result.success) {
      throw new Error(`Failed to get device model: ${result.errorMessage}`);
    }
    
    const productModel = result.output.trim();
    console.log(`Second session device model: ${productModel}`);
    
  } catch (error) {
    throw new Error(`Error during run_on_second_mobile_session: ${error instanceof Error ? error.message : String(error)}`);
  }
}

async function main() {
  console.log('=== Mobile Simulate Example ===\n');
  
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
    // Run on first mobile session
    await runOnFirstMobileSession(client);
    
    // Delete first session
    console.log('\nDeleting first session...');
    const deleteResult1 = await session1!.delete();
    if (!deleteResult1.success) {
      throw new Error(`Failed to delete first session: ${deleteResult1.errorMessage}`);
    }
    console.log(`First session deleted successfully (RequestID: ${deleteResult1.requestId})`);
    
    // Run on second mobile session
    await runOnSecondMobileSession(client);
    
    // Delete second session
    console.log('\nDeleting second session...');
    const deleteResult2 = await session2!.delete();
    if (!deleteResult2.success) {
      throw new Error(`Failed to delete second session: ${deleteResult2.errorMessage}`);
    }
    console.log(`Second session deleted successfully (RequestID: ${deleteResult2.requestId})`);
    
    console.log('\n=== Example completed successfully ===');
    
  } catch (error) {
    console.error('Error:', error instanceof Error ? error.message : String(error));
    
    // Cleanup sessions on error
    if (session1) {
      try {
        await session1.delete();
      } catch (e) {
        console.warn('Warning: Failed to cleanup first session');
      }
    }
    if (session2) {
      try {
        await session2.delete();
      } catch (e) {
        console.warn('Warning: Failed to cleanup second session');
      }
    }
    
    process.exit(1);
  }
}

// Run the example
main();

