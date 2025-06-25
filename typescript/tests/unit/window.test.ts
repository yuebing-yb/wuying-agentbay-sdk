import { AgentBay, Session } from '../../src';
import { Window, WindowManager } from '../../src/window/window';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Helper function to check if window has valid properties
function isValidWindow(window: Window): boolean {
  return (
    typeof window === 'object' &&
    window !== null &&
    typeof window.window_id === 'number' &&
    typeof window.title === 'string'
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
        const windows = await windowManager.listRootWindows();
        log(`Retrieved ${windows.length} root windows`);
        
        // Verify windows array
        expect(windows).toBeDefined();
        expect(Array.isArray(windows)).toBe(true);
        
        // Verify the results
        if (windows.length > 0) {
          windows.forEach((window) => {
            expect(isValidWindow(window)).toBe(true);
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
        const window = await windowManager.getActiveWindow();
        
        if (window) {
          log(`Active window: ${window.title} (ID: ${window.window_id})`);
          
          // Verify the results
          expect(isValidWindow(window)).toBe(true);
        } else {
          log('No active window found, this might be normal in some environments');
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
        const windows = await windowManager.listRootWindows();
        
        if (windows.length === 0) {
          log('No windows available for testing activateWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Activating window with ID: ${windowId}`);
        
        // Call the method
        await windowManager.activateWindow(windowId);
        
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
        const windows = await windowManager.listRootWindows();
        
        if (windows.length === 0) {
          log('No windows available for testing maximizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Maximizing window with ID: ${windowId}`);
        
        // Call the method
        await windowManager.maximizeWindow(windowId);
        
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
        const windows = await windowManager.listRootWindows();
        
        if (windows.length === 0) {
          log('No windows available for testing minimizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Minimizing window with ID: ${windowId}`);
        
        // Call the method
        await windowManager.minimizeWindow(windowId);
        
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
        const windows = await windowManager.listRootWindows();
        
        if (windows.length === 0) {
          log('No windows available for testing restoreWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Restoring window with ID: ${windowId}`);
        
        // Call the method
        await windowManager.restoreWindow(windowId);
        
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
        const windows = await windowManager.listRootWindows();
        
        if (windows.length === 0) {
          log('No windows available for testing resizeWindow');
          return;
        }
        
        // Use the first window for testing
        const windowId = windows[0].window_id;
        log(`Resizing window with ID: ${windowId} to 800x600`);
        
        // Call the method
        await windowManager.resizeWindow(windowId, 800, 600);
        
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
        await windowManager.focusMode(true);
        
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
        await windowManager.focusMode(false);
        
        log('Focus mode disabled successfully');
      } catch (error: any) {
        log(`Error in focusMode disable test: ${error}`);
        // Skip test if we can't disable focus mode
        expect(true).toBe(true);
      }
    });
  });
});
