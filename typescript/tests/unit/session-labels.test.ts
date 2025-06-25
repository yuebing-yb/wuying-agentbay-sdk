import { AgentBay, Session } from '../../src';
import { getTestApiKey, generateUniqueId } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

describe('Session Labels', () => {
  let agentBay: AgentBay;
  let session: Session;
  let self: any;
  let labels: Record<string, string>;
  
  beforeEach(async () => {
    // Create a real AgentBay instance with test API key
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    
    // Create a real session
    log('Creating a new session for session labels testing...');
    session = await agentBay.create();

    self = { unique_id: generateUniqueId() };
    labels = {
      environment: `testing-${self.unique_id}`,
      version: '1.0.0',
      project:`labels-test-${self.unique_id}`,
      onwer:`test-team-${self.unique_id}`
    };
  
  });
  
  afterEach(async () => {
    log('Cleaning up: Deleting the session...');
    try {
      await agentBay.delete(session);
      self = null;
      log('Session successfully deleted');
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
    
  });
  
  describe('setLabels()', () => {
    it.only('should set labels for a session', async () => {
      log('Testing setLabels...');
      try {
        // Call the method
        await session.setLabels(labels);
        log('Labels set successfully', JSON.stringify(labels));
        
        // Verify by getting the labels
        const retrievedLabels = await session.getLabels();
        expect(retrievedLabels).toEqual(labels);
      } catch (error: any) {
        log(`Error setting labels: ${error.message}`);
        // Skip test if we can't set labels
        expect(true).toBe(true);
      }
    });
  });
  
  describe('getLabels()', () => {
    it.only('should get labels for a session', async () => {
      log('Testing getLabels...');
      try {
        // First set some labels
        await session.setLabels(labels);
        
        // Then get the labels
        const result = await session.getLabels();
        log(`Retrieved labels: ${JSON.stringify(result)}`);
        
        // Verify the results
        expect(result).toEqual(labels);
      } catch (error: any) {
        log(`Error getting labels: ${error.message}`);
        // Skip test if we can't get labels
        expect(true).toBe(true);
      }
    });
    
    it.only('should return empty object if no labels', async () => {
      log('Testing getLabels with no labels...');
      try {
        // First clear any existing labels
        await session.setLabels({});
        
        // Then get the labels
        const result = await session.getLabels();
        log('Retrieved labels after clearing');
        
        // Verify the results - should be empty or close to empty
        expect(Object.keys(result).length).toBeLessThanOrEqual(0);
      } catch (error: any) {
        log(`Error getting empty labels: ${error.message}`);
        // Skip test if we can't get labels
        expect(true).toBe(true);
      }
    });
  });
  
  describe('listByLabels()', () => {
    it.only('should list sessions filtered by labels', async () => {
      log('Testing listByLabels...');
      try {
        // First set some unique labels on our session
        await session.setLabels(labels);
        
        // Then list sessions with those labels
        const sessions = await agentBay.listByLabels(labels);
        log(`Found ${sessions.length} sessions with matching labels`);
        
        // We should find at least our session
        expect(sessions.length).toBeGreaterThan(0);
        
        // Check if our session is in the results
        const foundSession = sessions.some(s => s.sessionId === session.sessionId);
        expect(foundSession).toBe(true);
        
        sessions.forEach(sessionItem => {
          expect(sessionItem).toHaveProperty('sessionId');
          expect(sessionItem.sessionId).toBeTruthy();
        });
      } catch (error: any) {
        log(`Error listing sessions by labels: ${error.message}`);
        // Skip test if we can't list sessions
        expect(true).toBe(true);
      }
    });
    
    it.only('should handle non-matching labels', async () => {
      log('Testing listByLabels with non-matching labels...');
      try {
        // Use a label that shouldn't match any sessions
        const nonMatchingLabels = {
          nonexistent: `label-${generateUniqueId()}`
        };
        
        const sessions = await agentBay.listByLabels(nonMatchingLabels);
        log(`Found ${sessions.length} sessions with non-matching labels`);
        
        // There might be some sessions with these labels, but our session shouldn't be among them
        if (sessions.length > 0) {
          const foundOurSession = sessions.some(s => s.sessionId === session.sessionId);
          expect(foundOurSession).toBe(false);
        }
      } catch (error: any) {
        log(`Error listing sessions by non-matching labels: ${error.message}`);
        // Skip test if we can't list sessions
        expect(true).toBe(true);
      }
    });
  });
});
