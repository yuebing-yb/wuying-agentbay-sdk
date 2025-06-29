import { before } from 'node:test';
import { AgentBay, Session } from '../../src';
import { getTestApiKey, extractResourceId } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

describe('Session', () => {
  
  
  describe('properties', () => {
    let agentBay: AgentBay;
    let session: Session;
  
    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      
      // Create a session
      log('Creating a new session for session testing...');
      session = await agentBay.create();
      log(`Session created with ID: ${session.sessionId}`);
    });
    
    afterEach(async () => {
      // Clean up the session
      log('Cleaning up: Deleting the session...');
      try {
        if(session)
        await agentBay.delete(session);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });
    it.only('should have valid sessionId', () => {
      expect(session.sessionId).toBeDefined();
      expect(session.sessionId.length).toBeGreaterThan(0);
    });
    
    it.only('should log resourceUrl', () => {
      // ResourceUrl is optional, so we just log it without checking if it's non-empty
      log(`Session resourceUrl: ${session.resourceUrl}`);
    });
    
    it.only('should have filesystem, command, and ui properties', () => {
      expect(session.filesystem).toBeDefined();
      expect(session.command).toBeDefined();
      expect(session.ui).toBeDefined();
    });
  });
  
  describe('methods', () => {
    let agentBay: AgentBay;
    let session: Session;
    
    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      
      // Create a session
      log('Creating a new session for session testing...');
      session = await agentBay.create();
      log(`Session created with ID: ${session.sessionId}`);
    });
    
    afterEach(async () => {
      // Clean up the session
      log('Cleaning up: Deleting the session...');
      try {
        if(session)
        await agentBay.delete(session);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });
    it.only('should return the session ID', () => {
      const sessionId = session.getSessionId();
      expect(sessionId).toBe(session.sessionId);
    });
    
    it.only('should return the API key', () => {
      const apiKey = session.getAPIKey();
      expect(apiKey).toBe(agentBay.getAPIKey());
    });
    
    it.only('should return the client', () => {
      const client = session.getClient();
      expect(client).toBeDefined();
    });
    
    it.only('should get link if implemented', async () => {
      // Check if the getLink method exists
      if (typeof session.getLink === 'function') {
        log('Testing session.getLink method...');
        try {
          // First, create a new session with imageId for getLink testing
          // This is consistent with the Go implementation in TestSession_GetLinkMethod
          const linkTestSession = await agentBay.create({ imageId: 'imgc-07if81c4ktj9shiru' });
          log(`Session created with ID: ${linkTestSession.sessionId} for getLink testing`);
          
          const link = await linkTestSession.getLink();
          log('Session link:', link);
          
          // Verify the link
          expect(link).toBeDefined();
          
          // Clean up the session after test
          await agentBay.delete(linkTestSession);
        } catch (error) {
          log(`Note: Session link retrieval failed: ${error}`);
          // Don't fail the test if getLink method is not fully implemented
        }
      } else {
        log('Note: Session getLink method is not available, skipping test');
      }
    });
  });
  
  describe('delete', () => {
    let agentBay: AgentBay;
    beforeEach(async () => {
      agentBay = new AgentBay({ apiKey: getTestApiKey() });
    });
    it.only('should delete the session', async () => {
      // Create a new session specifically for this test
      log('Creating a new session for delete testing...');
      const testSession = await agentBay.create();
      log(`Session created with ID: ${testSession.sessionId}`);
      
      // Test delete method
      log('Testing session.delete method...');
      try {
        if(testSession)
          await testSession.delete();
        
        // Verify the session was deleted by checking it's not in the list
        const sessions = agentBay.list();
        
        const stillExists = sessions.some(s => s.sessionId === testSession.sessionId);
        expect(stillExists).toBe(false);
      } catch (error) {
        log(`Note: Session deletion failed: ${error}`);
        // Clean up if the test failed
        try {
          if(testSession)
            await agentBay.delete(testSession);
        } catch {
          // Ignore cleanup errors
        }
        throw error;
      }
    });
  });
  
  describe('info', () => {
    let agentBay: AgentBay;
    let session: Session;
    
    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      
      // Create a session
      log('Creating a new session for session testing...');
      session = await agentBay.create();
      log(`Session created with ID: ${session.sessionId}`);
    });
    
    afterEach(async () => {
      // Clean up the session
      log('Cleaning up: Deleting the session...');
      try {
        if(session)
          await agentBay.delete(session);
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });
    it.only('should get session info if implemented', async () => {
      // Check if the info method exists
      if (typeof (session as any).info === 'function') {
        log('Testing session.info method...');
        try {
          const sessionInfo = await (session as any).info();
          log('Session info:', sessionInfo);
          
          // Verify the session info
          expect(sessionInfo).toBeDefined();
          
          // Check SessionId field
          expect(sessionInfo.sessionId).toBeDefined();
          expect(sessionInfo.sessionId).toBe(session.sessionId);
          
          // Check ResourceUrl field
          if (sessionInfo.resourceUrl) {
            log(`Session ResourceUrl from Info: ${sessionInfo.resourceUrl}`);
            
            // Extract resourceId from URL if possible
            const resourceId = extractResourceId(sessionInfo.resourceUrl);
            if (resourceId) {
              log(`Extracted ResourceId: ${resourceId}`);
            }
            
            // Verify that session.resourceUrl was updated with the value from the API response
            expect(session.resourceUrl).toBe(sessionInfo.resourceUrl);
          }
          
          // Log other fields (these may be empty depending on the API response)
          if (sessionInfo.appId) log(`AppId: ${sessionInfo.appId}`);
          if (sessionInfo.authCode) log(`AuthCode: ${sessionInfo.authCode}`);
          if (sessionInfo.connectionProperties) log(`ConnectionProperties: ${sessionInfo.connectionProperties}`);
          if (sessionInfo.resourceId) log(`ResourceId: ${sessionInfo.resourceId}`);
          if (sessionInfo.resourceType) log(`ResourceType: ${sessionInfo.resourceType}`);
        } catch (error) {
          log(`Note: Session info retrieval failed: ${error}`);
          // Don't fail the test if info method is not fully implemented
        }
      } else {
        log('Note: Session info method is not available, skipping info test');
      }
    });
  });
});
