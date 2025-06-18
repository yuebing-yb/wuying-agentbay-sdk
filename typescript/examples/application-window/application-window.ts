import { AgentBay } from '../../src/agent-bay';
import { Session } from '../../src/session';
import { log } from '../../src/utils/logger';

// Helper function to get the minimum of two numbers
function min(x: number, y: number): number {
  return x < y ? x : y;
}

async function main() {
  try {
    // Get API key from environment variable or use a default value for testing
    const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key for testing
    if (!process.env.AGENTBAY_API_KEY) {
      log('Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.');
    }

    // Initialize the AgentBay client
    const agentBay = new AgentBay({ apiKey });

    // Create a new session with default parameters
    log('\nCreating a new session...');
    const session = await agentBay.create();
    log(`\nSession created with ID: ${session.sessionId}`);

    // Application Management Examples
    log('\n=== Application Management Examples ===');

    // Get installed applications
    log('\nGetting installed applications...');
    try {
      const apps = await session.application.getInstalledApps(true, false, true);
      log(`Found ${apps.length} installed applications`);
      // Print the first 3 apps or fewer if less than 3 are available
      const count = min(apps.length, 3);
      for (let i = 0; i < count; i++) {
        log(`App ${i + 1}: ${apps[i].name}`);
      }
    } catch (error) {
      log(`Error getting installed apps: ${error}`);
    }

    // List visible applications
    log('\nListing visible applications...');
    try {
      const visibleApps = await session.application.listVisibleApps();
      log(`Found ${visibleApps.length} visible applications`);
      // Print the first 3 apps or fewer if less than 3 are available
      const count = min(visibleApps.length, 3);
      for (let i = 0; i < count; i++) {
        log(`Process ${i + 1}: ${visibleApps[i].pname} (PID: ${visibleApps[i].pid})`);
      }
    } catch (error) {
      log(`Error listing visible apps: ${error}`);
    }

    // Window Management Examples
    log('\n=== Window Management Examples ===');

    // List root windows
    log('\nListing root windows...');
    let rootWindows: any[] = [];
    try {
      rootWindows = await session.window.listRootWindows();
      log(`Found ${rootWindows.length} root windows`);
      // Print the first 3 windows or fewer if less than 3 are available
      const count = min(rootWindows.length, 3);
      for (let i = 0; i < count; i++) {
        log(`Window ${i + 1}: ${rootWindows[i].title} (ID: ${rootWindows[i].window_id})`);
      }
    } catch (error) {
      log(`Error listing root windows: ${error}`);
    }

    // Get active window
    log('\nGetting active window...');
    try {
      const activeWindow = await session.window.getActiveWindow();
      log(`Active window: ${activeWindow.title} (ID: ${activeWindow.window_id}, Process: ${activeWindow.pname}, PID: ${activeWindow.pid})`);
    } catch (error) {
      log(`Error getting active window: ${error}`);
    }

    // Window operations
    if (rootWindows.length > 0) {
      const windowId = rootWindows[0].window_id;

      // Activate window
      log(`\nActivating window with ID ${windowId}...`);
      try {
        await session.window.activateWindow(windowId);
        log('Window activated successfully');
      } catch (error) {
        log(`Error activating window: ${error}`);
      }

      // Maximize window
      log(`\nMaximizing window with ID ${windowId}...`);
      try {
        await session.window.maximizeWindow(windowId);
        log('Window maximized successfully');
      } catch (error) {
        log(`Error maximizing window: ${error}`);
      }

      // Minimize window
      log(`\nMinimizing window with ID ${windowId}...`);
      try {
        await session.window.minimizeWindow(windowId);
        log('Window minimized successfully');
      } catch (error) {
        log(`Error minimizing window: ${error}`);
      }

      // Restore window
      log(`\nRestoring window with ID ${windowId}...`);
      try {
        await session.window.restoreWindow(windowId);
        log('Window restored successfully');
      } catch (error) {
        log(`Error restoring window: ${error}`);
      }

      // Resize window
      log(`\nResizing window with ID ${windowId} to 800x600...`);
      try {
        await session.window.resizeWindow(windowId, 800, 600);
        log('Window resized successfully');
      } catch (error) {
        log(`Error resizing window: ${error}`);
      }
    }

    // Focus mode
    // Enable focus mode
    log('\nEnabling focus mode...');
    try {
      await session.window.focusMode(true);
      log('Focus mode enabled successfully');
    } catch (error) {
      log(`Error enabling focus mode: ${error}`);
    }

    // Disable focus mode
    log('\nDisabling focus mode...');
    try {
      await session.window.focusMode(false);
      log('Focus mode disabled successfully');
    } catch (error) {
      log(`Error disabling focus mode: ${error}`);
    }

    // Delete the session
    log('\nDeleting the session...');
    try {
      await agentBay.delete(session);
      log('Session deleted successfully');
    } catch (error) {
      log(`Error deleting session: ${error}`);
      process.exit(1);
    }
  } catch (error) {
    log(`Error: ${error}`);
    process.exit(1);
  }
}

main();
