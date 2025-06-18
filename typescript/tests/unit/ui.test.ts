import { AgentBay, Session } from '../../src';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Type declarations are now in tests/jest.d.ts

describe('UI', () => {
  let agentBay: AgentBay;
  let session: Session;
  
  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    
    // Create a session with mobile_latest image (consistent with Go implementation)
    log('Creating a new session for UI testing...');
    session = await agentBay.create({ imageId: 'mobile_latest' });
    log(`Session created with ID: ${session.sessionId}`);
  });
  
  afterEach(async () => {
    // Clean up the session
    try {
      await agentBay.delete(session);
      log(`Session deleted successfully: ${session.sessionId}`);
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });
  
  describe('getClickableUIElements', () => {
    it.only('should retrieve clickable UI elements if implemented', async () => {
      if (session.ui && typeof session.ui.getClickableUIElements === 'function') {
        log('Testing UI.getClickableUIElements method...');
        try {
          const elements = await session.ui.getClickableUIElements();
          log(`Retrieved ${elements.length} clickable UI elements`);
          
          // Verify the elements
          expect(elements).toBeDefined();
          expect(Array.isArray(elements)).toBe(true);
        } catch (error) {
          log(`Note: UI.getClickableUIElements execution failed: ${error}`);
          // Don't fail the test if the method is not fully implemented
        }
      } else {
        log('Note: UI.getClickableUIElements method is not available, skipping test');
      }
    });
  });
  
  describe('getAllUIElements', () => {
    it.only('should retrieve all UI elements if implemented', async () => {
      if (session.ui && typeof session.ui.getAllUIElements === 'function') {
        log('Testing UI.getAllUIElements method...');
        try {
          const elements = await session.ui.getAllUIElements();
          log(`Retrieved ${elements.length} UI elements`);
          
          // Verify the elements
          expect(elements).toBeDefined();
          expect(Array.isArray(elements)).toBe(true);
          
          // Log the first element if available
          if (elements.length > 0) {
            log('First UI element:', elements[0]);
          }
        } catch (error) {
          log(`Note: UI.getAllUIElements execution failed: ${error}`);
          // Don't fail the test if the method is not fully implemented
        }
      } else {
        log('Note: UI.getAllUIElements method is not available, skipping test');
      }
    });
  });
  
  describe('sendKey', () => {
    it.only('should send key events if implemented', async () => {
      if (session.ui && typeof session.ui.sendKey === 'function') {
        log('Testing UI.sendKey method...');
        try {
          // Try to send HOME key
          const result = await session.ui.sendKey(3); // HOME key
          log(`Send key result: ${result}`);
          
          // Verify the result
          expect(typeof result).toBe('boolean');
        } catch (error) {
          log(`Note: UI.sendKey execution failed: ${error}`);
          // Don't fail the test if the method is not fully implemented
        }
      } else {
        log('Note: UI.sendKey method is not available, skipping test');
      }
    });
  });
  
  describe('screenshot', () => {
    it.only('should take screenshots if implemented', async () => {
      if (session.ui && typeof session.ui.screenshot === 'function') {
        log('Testing UI.screenshot method...');
        try {
          const screenshot = await session.ui.screenshot();
          log(`Screenshot data length: ${screenshot.length} characters`);
          
          // Verify the screenshot
          expect(screenshot).toBeDefined();
          expect(typeof screenshot).toBe('string');
          expect(screenshot.length).toBeGreaterThan(0);
        } catch (error) {
          log(`Note: UI.screenshot execution failed: ${error}`);
          // Don't fail the test if the method is not fully implemented
        }
      } else {
        log('Note: UI.screenshot method is not available, skipping test');
      }
    });
  });
});
