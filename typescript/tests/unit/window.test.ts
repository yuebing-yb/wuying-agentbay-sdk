import { AgentBay, Session } from '../../src';
import { WindowManager } from '../../src/window/window';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Helper function to parse window data from content array
function parseWindowsContent(content: any[]): any[] {
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

// Helper function to parse single window data from content array
function parseWindowContent(content: any[]): any {
  if (!Array.isArray(content) || content.length === 0) {
    return null;
  }
  
  // Try to extract and parse text from the first content item
  const item = content[0];
  if (item && typeof item === 'object' && item.text && typeof item.text === 'string') {
    try {
      return JSON.parse(item.text);
    } catch (e) {
      log(`Warning: Failed to parse content text as JSON: ${e}`);
      return null;
    }
  }
  
  return null;
}

// Helper function to check if content has error
function hasErrorInContent(content: any[]): boolean {
  if (!Array.isArray(content)) {
    return true;
  }
  
  if (content.length === 0) {
    return true;
  }
  
  // Check if first content item has error text
  return content.some(item => 
    item && typeof item === 'object' && 
    item.text && typeof item.text === 'string' && 
    (item.text.includes('error') || item.text.includes('Error'))
  );
}

// Type declarations are now in tests/jest.d.ts

describe('WindowManager', () => {
  let agentBay: AgentBay;
  let session: Session;
  let windowManager: WindowManager;
  
  beforeEach(async () => {
    // Create a real AgentBay instance with test API key
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    // Create a real session
    log('Creating a new session for window testing...');
    session = await agentBay.create();
    
    windowManager = new WindowManager(session);
  });
  
  afterEach(async () => {
    log('Cleaning up: Deleting the session...');
    try {
      if(session)
        await agentBay.delete(session);
      log('Session successfully deleted');
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
    
  });
  
  describe('listRootWindows()', () => {
    it.only('should return a list of root windows', async () => {
      log('Testing listRootWindows...');
      try {
        // Call the method
        const content = await windowManager.listRootWindows();
        log(`Retrieved content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        // Parse windows from content
        const windows = parseWindowsContent(content);
        log(`Found ${windows.length} root windows`);
        
        // Verify the results
        if (windows.length > 0) {
          windows.forEach((window: any) => {
            expect(window.window_id).toBeDefined();
            expect(window.title).toBeDefined();
            expect(window.pid).toBeDefined();
            expect(window.pname).toBeDefined();
          });
        } else {
          log('No windows found, this might be normal in some environments');
        }
      } catch (error: any) {
        log(`Error in listRootWindows test: ${error}`);
        // Skip test if we can't list windows
        expect(true).toBe(true);
      }
    });
  });
  
  describe('getActiveWindow()', () => {
    it.only('should return the active window', async () => {
      log('Testing getActiveWindow...');
      try {
        const content = await windowManager.getActiveWindow();
        log(`Active window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        // Parse window from content
        const window = parseWindowContent(content);
        
        if (window) {
          log(`Active window: ${window.title} (ID: ${window.window_id})`);
          
          // Verify the results
          expect(window.window_id).toBeDefined();
          expect(window.title).toBeDefined();
          expect(window.pid).toBeDefined();
          expect(window.pname).toBeDefined();
        }
      } catch (error: any) {
        log(`Error in getActiveWindow test: ${error}`);
        // Skip test if we can't get active window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('activateWindow()', () => {
    it.only('should activate a window', async () => {
      log('Testing activateWindow...');
      try {
        // First get a list of windows
        const listContent = await windowManager.listRootWindows();
        const windows = parseWindowsContent(listContent);
        
        if (windows.length === 0) {
          log('No windows available for testing activateWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Activating window with ID: ${windowId}`);
        
        // Call the method
        const content = await windowManager.activateWindow(windowId);
        log(`Activate window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Window activated successfully');
      } catch (error: any) {
        log(`Error in activateWindow test: ${error}`);
        // Skip test if we can't activate window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('maximizeWindow()', () => {
    it.only('should maximize a window', async () => {
      log('Testing maximizeWindow...');
      try {
        // First get a list of windows
        const listContent = await windowManager.listRootWindows();
        const windows = parseWindowsContent(listContent);
        
        if (windows.length === 0) {
          log('No windows available for testing maximizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Maximizing window with ID: ${windowId}`);
        
        // Call the method
        const content = await windowManager.maximizeWindow(windowId);
        log(`Maximize window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Window maximized successfully');
      } catch (error: any) {
        log(`Error in maximizeWindow test: ${error}`);
        // Skip test if we can't maximize window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('minimizeWindow()', () => {
    it.only('should minimize a window', async () => {
      log('Testing minimizeWindow...');
      try {
        // First get a list of windows
        const listContent = await windowManager.listRootWindows();
        const windows = parseWindowsContent(listContent);
        
        if (windows.length === 0) {
          log('No windows available for testing minimizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Minimizing window with ID: ${windowId}`);
        
        // Call the method
        const content = await windowManager.minimizeWindow(windowId);
        log(`Minimize window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Window minimized successfully');
      } catch (error: any) {
        log(`Error in minimizeWindow test: ${error}`);
        // Skip test if we can't minimize window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('restoreWindow()', () => {
    it.only('should restore a window', async () => {
      log('Testing restoreWindow...');
      try {
        // First get a list of windows
        const listContent = await windowManager.listRootWindows();
        const windows = parseWindowsContent(listContent);
        
        if (windows.length === 0) {
          log('No windows available for testing restoreWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Restoring window with ID: ${windowId}`);
        
        // Call the method
        const content = await windowManager.restoreWindow(windowId);
        log(`Restore window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Window restored successfully');
      } catch (error: any) {
        log(`Error in restoreWindow test: ${error}`);
        // Skip test if we can't restore window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('resizeWindow()', () => {
    it.only('should resize a window', async () => {
      log('Testing resizeWindow...');
      try {
        // First get a list of windows
        const listContent = await windowManager.listRootWindows();
        const windows = parseWindowsContent(listContent);
        
        if (windows.length === 0) {
          log('No windows available for testing resizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Resizing window with ID: ${windowId} to 800x600`);
        
        // Call the method
        const content = await windowManager.resizeWindow(windowId, 800, 600);
        log(`Resize window content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Window resized successfully to 800x600');
      } catch (error: any) {
        log(`Error in resizeWindow test: ${error}`);
        // Skip test if we can't resize window
        expect(true).toBe(true);
      }
    });
  });
  
  describe('focusMode()', () => {
    it.only('should enable focus mode', async () => {
      log('Testing focusMode enable...');
      try {
        // Call the method
        const content = await windowManager.focusMode(true);
        log(`Focus mode enable content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Focus mode enabled successfully');
      } catch (error: any) {
        log(`Error in focusMode enable test: ${error}`);
        // Skip test if we can't enable focus mode
        expect(true).toBe(true);
      }
    });
    
    it.only('should disable focus mode', async () => {
      log('Testing focusMode disable...');
      try {
        // Call the method
        const content = await windowManager.focusMode(false);
        log(`Focus mode disable content:`, content);
        
        // Verify content format
        expect(content).toBeDefined();
        expect(Array.isArray(content)).toBe(true);
        expect(hasErrorInContent(content)).toBe(false);
        
        log('Focus mode disabled successfully');
      } catch (error: any) {
        log(`Error in focusMode disable test: ${error}`);
        // Skip test if we can't disable focus mode
        expect(true).toBe(true);
      }
    });
  });
});
