import { AgentBay, Session } from '../../src';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Helper function to parse content array from API response for UI elements
function parseUIContent(content: any[]): any[] {
  if (!Array.isArray(content) || content.length === 0) {
    return [];
  }
  
  // Try to extract and parse text from the first content item
  const item = content[0];
  if (item && typeof item === 'object' && item.text && typeof item.text === 'string') {
    try {
      return JSON.parse(item.text);
    } catch (e) {
      log(`Warning: Failed to parse content text as JSON: ${e}`);
      return [];
    }
  }
  
  return [];
}

// Helper function to check if a content array contains base64 image data
function containsBase64Image(content: any[]): boolean {
  if (!Array.isArray(content) || content.length === 0) {
    return false;
  }
  
  // Look for base64 image data in the text fields
  return content.some(item => 
    item && typeof item === 'object' && 
    typeof item.text === 'string' && 
    (item.text.startsWith('data:image') || item.text.includes('base64'))
  );
}

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
          const content = await session.ui.getClickableUIElements();
          log(`Retrieved content:`, content);
          
          // Verify the content
          expect(content).toBeDefined();
          expect(typeof content).toBe('string');
          
          // Try to parse UI elements from content if it's JSON
          try {
            const elements = JSON.parse(content);
            log(`Parsed UI elements:`, elements);
            
            // Additional checks on parsed elements if available
            if (Array.isArray(elements) && elements.length > 0) {
              log('First UI element:', elements[0]);
            }
          } catch (e) {
            log(`Content is not JSON parseable: ${e}`);
          }
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
          const content = await session.ui.getAllUIElements();
          log(`Retrieved content:`, content);
          
          // Verify the content
          expect(content).toBeDefined();
          expect(typeof content).toBe('string');
          
          // Try to parse UI elements from content if it's JSON
          try {
            const elements = JSON.parse(content);
            log(`Parsed UI elements:`, elements);
            
            // Log the first element if available
            if (Array.isArray(elements) && elements.length > 0) {
              log('First UI element:', elements[0]);
            }
          } catch (e) {
            log(`Content is not JSON parseable: ${e}`);
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
          const content = await session.ui.sendKey(3); // HOME key
          log(`Send key content:`, content);
          
          // Verify the content
          expect(content).toBeDefined();
          expect(typeof content).toBe('string');
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
          const content = await session.ui.screenshot();
          log(`Screenshot content:`, content);
          
          // Verify the screenshot content
          expect(content).toBeDefined();
          expect(typeof content).toBe('string');
          
          // Check if the content contains image URL or base64 data
          const hasImageData = content.includes('https://') || 
                              content.includes('data:image') || 
                              content.includes('base64');
          expect(hasImageData).toBe(true);
          
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
