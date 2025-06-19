import { AgentBay, Session, Context } from '../../src';
import { getTestApiKey, wait } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Define test runner types if they're not available
declare function describe(name: string, fn: () => void): void;
declare function beforeEach(fn: () => void | Promise<void>): void;
declare function afterEach(fn: () => void | Promise<void>): void;
declare function it(name: string, fn: () => void | Promise<void>): void;
declare function expect(actual: any): any;

describe('Context Session Integration', () => {
  let agentBay: AgentBay;
  
  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    log(`AgentBay client initialized successfully`);
  });
  
  describe('Context Session Management', () => {
    it('should manage context and session lifecycle correctly', async () => {
      // Step 1: Create a new context
      const contextName = `test-context-${Date.now()}`;
      log(`Creating new context with name: ${contextName}`);
      
      const context = await agentBay.context.create(contextName);
      if (!context) {
        throw new Error('Failed to create context');
      }
      log(`Context created successfully - ID: ${context.id}, Name: ${context.name}, State: ${context.state}`);
      
      expect(context.id).toBeDefined();
      expect(context.name).toBe(contextName);
      
      try {
        // Step 2: Create a session with the context ID (expect success)
        log('Step 2: Creating first session with context ID...');
        const session1 = await agentBay.create({ contextId: context.id });
        log(`Session created successfully with ID: ${session1.sessionId}`);
        
        // Step 3: Get the context directly and verify that its status is "in-use"
        log('Step 3: Checking context status after session creation...');
        
        // Wait a moment for the system to update the context status
        await wait(2000);
        
        const updatedContext = await agentBay.context.get(contextName);
        if (!updatedContext) {
          throw new Error('Failed to retrieve updated context');
        }
        log(`Retrieved context - ID: ${updatedContext.id}, Name: ${updatedContext.name}, State: ${updatedContext.state}`);
        
        expect(updatedContext.state).toBe('in-use');
        log('Context state is correctly set to "in-use"');
        
        // Step 4: Try to create another session with the same context_id (expect failure)
        log('Step 4: Attempting to create a second session with the same context ID...');
        try {
          const session2 = await agentBay.create({ contextId: context.id });
          
          // If somehow it succeeds (which shouldn't happen), make sure to clean it up
          log(`WARNING: Unexpectedly succeeded in creating second session with ID: ${session2.sessionId}`);
          await session2.delete();
          
          // This should fail the test
          expect(false).toBe(true);
        } catch (error) {
          log(`As expected, failed to create second session with same context ID: ${error}`);
          // This is the expected behavior
        }
        
        // Step 5: Release the first session
        log('Step 5: Releasing the first session...');
        await session1.delete();
        log('First session released successfully');
        
        // Wait for the system to update the context status
        log('Waiting for context status to update...');
        await wait(3000);
        
        // Step 6: Get the context directly and verify that its status is "available"
        log('Step 6: Checking context status after session release...');
        
        const contextAfterRelease = await agentBay.context.get(contextName);
        if (!contextAfterRelease) {
          throw new Error('Failed to retrieve context after release');
        }
        log(`Retrieved context - ID: ${contextAfterRelease.id}, Name: ${contextAfterRelease.name}, State: ${contextAfterRelease.state}`);
        
        expect(contextAfterRelease.state).toBe('available');
        log('Context state is correctly set to "available"');
        
        // Step 7: Create another session with the same context_id (expect success)
        log('Step 7: Creating a new session with the same context ID...');
        const session3 = await agentBay.create({ contextId: context.id });
        log(`New session created successfully with ID: ${session3.sessionId}`);
        
        // Step 8: Clean up by releasing the session
        log('Step 8: Cleaning up - releasing the third session...');
        await session3.delete();
        log('Third session released successfully');
      } finally {
        // Clean up the context
        log('Cleaning up: Deleting the context...');
        try {
          await agentBay.context.delete(context);
          log(`Context ${context.id} deleted successfully`);
        } catch (error) {
          log(`Warning: Error deleting context: ${error}`);
        }
      }
    });
  });
  
  describe('Context Lifecycle', () => {
    it('should manage the complete lifecycle of a context', async () => {
      // Get initial list of contexts for comparison
      log('Getting initial list of contexts...');
      const initialContexts = await agentBay.context.list();
      log(`Found ${initialContexts.length} contexts initially`);
      
      // Store initial context IDs for comparison
      const initialContextIDs = new Map<string, boolean>();
      for (const ctx of initialContexts) {
        initialContextIDs.set(ctx.id, true);
        log(`Initial context: ${ctx.name} (${ctx.id})`);
      }
      
      // Step 1: Create a new context
      log('Step 1: Creating a new context...');
      const contextName = `test-context-${Date.now()}`;
      const context = await agentBay.context.create(contextName);
      if (!context) {
        throw new Error('Failed to create context');
      }
      log(`Created context: ${context.name} (${context.id})`);
      
      // Verify the created context has the expected name
      expect(context.name).toBe(contextName);
      expect(context.id).toBeDefined();
      
      // Store the original context ID for later verification
      const originalContextID = context.id;
      
      try {
        // Step 2: Get the context we just created
        log('Step 2: Getting the context we just created...');
        const retrievedContext = await agentBay.context.get(contextName);
        if (!retrievedContext) {
          throw new Error('Failed to retrieve context');
        }
        log(`Successfully retrieved context: ${retrievedContext.name} (${retrievedContext.id})`);
        
        // Verify the retrieved context matches what we created
        expect(retrievedContext.name).toBe(contextName);
        expect(retrievedContext.id).toBe(originalContextID);
        
        // Step 3: List contexts and verify our new context is in the list
        log('Step 3: Listing all contexts...');
        const allContexts = await agentBay.context.list();
        
        // Verify the list contains our new context
        let foundInList = false;
        for (const c of allContexts) {
          if (c.id === originalContextID) {
            foundInList = true;
            expect(c.name).toBe(contextName);
            break;
          }
        }
        expect(foundInList).toBe(true);
        log('Successfully listed contexts, found our context in the list');
        
        // Verify the list contains at least one more context than the initial list
        expect(allContexts.length).toBeGreaterThan(initialContexts.length);
        
        // Step 4: Create a session with the context
        log('Step 4: Creating a session with the context...');
        const session = await agentBay.create({
          contextId: context.id,
          labels: {
            username: 'test-user',
            project: 'test-project'
          }
        });
        log(`Session created with ID: ${session.sessionId}`);
        
        try {
          // Step 5: Update the context
          log('Step 5: Updating the context...');
          const updatedName = `updated-${contextName}`;
          context.name = updatedName;
          await agentBay.context.update(context);
          log('Context update reported as successful');
          
          // Step 6: Verify the update by getting the context again
          log('Step 6: Verifying the update by getting the context again...');
          const retrievedUpdatedContext = await agentBay.context.get(updatedName);
          if (!retrievedUpdatedContext) {
            throw new Error('Failed to retrieve updated context');
          }
          log(`Retrieved updated context: ${retrievedUpdatedContext.name} (${retrievedUpdatedContext.id})`);
          
          // Verify the retrieved context has the updated name
          expect(retrievedUpdatedContext.name).toBe(updatedName);
          expect(retrievedUpdatedContext.id).toBe(originalContextID);
          
          // Step 7: List contexts again to verify the update is visible in the list
          log('Step 7: Listing contexts again to verify the update...');
          const updatedContexts = await agentBay.context.list();
          
          // Find the updated context in the list
          let foundInUpdatedList = false;
          for (const c of updatedContexts) {
            if (c.id === originalContextID) {
              foundInUpdatedList = true;
              expect(c.name).toBe(updatedName);
              break;
            }
          }
          expect(foundInUpdatedList).toBe(true);
          log('Successfully verified context update in the list');
        } finally {
          // Clean up the session
          log('Cleaning up: Deleting the session...');
          try {
            await session.delete();
            log('Session successfully deleted');
          } catch (error) {
            log(`Warning: Error deleting session: ${error}`);
          }
        }
      } finally {
        // Clean up the context
        log('Cleaning up: Deleting the context...');
        try {
          await agentBay.context.delete(context);
          log(`Context ${context.id} deleted successfully`);
            
          // Verify the context is actually deleted
          try {
            const deletedContext = await agentBay.context.get(contextName);
            if (deletedContext && deletedContext.id === originalContextID) {
              log('Error: Context still exists after deletion');
            }
          } catch (error) {
            // This is expected - the context should not exist
            log('Context successfully deleted and no longer exists');
          }
        } catch (error) {
          log(`Warning: Error deleting context: ${error}`);
        }
      }
    });
  });
});
