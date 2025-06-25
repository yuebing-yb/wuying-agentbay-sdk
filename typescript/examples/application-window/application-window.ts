import { AgentBay } from '../../src';

// Window represents a window in the system
interface Window {
  window_id: number;
  title: string;
  absolute_upper_left_x?: number;
  absolute_upper_left_y?: number;
  width?: number;
  height?: number;
  pid?: number;
  pname?: string;
  child_windows?: Window[];
}

// App represents an application in the system
interface App {
  name: string;
  path?: string;
  description?: string;
}

// Process represents a running process in the system
interface Process {
  pid: number;
  pname: string;
}

async function main() {
  // Get API key from environment variable or use default value for testing
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx'; // Replace with your actual API key for testing
  if (!process.env.AGENTBAY_API_KEY) {
    console.log('Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.');
  }

  // Initialize the AgentBay client
  const agentBay = new AgentBay({ apiKey });

  // Create a new session with default parameters
  console.log('\nCreating a new session...');
  const session = await agentBay.create();
  console.log(`\nSession created with ID: ${session.sessionId}`);

  try {
    // Application Management Examples
    console.log('\n=== Application Management Examples ===');

    // Get installed applications
    console.log('\nGetting installed applications...');
    try {
      const apps = await session.Application.getInstalledApps(true, false, true);
      console.log(`Found ${apps.length} installed applications`);
      
      // Print the first 3 apps or fewer if less than 3 are available
      const count = Math.min(apps.length, 3);
      for (let i = 0; i < count; i++) {
        console.log(`App ${i + 1}: ${apps[i].name}`);
      }
    } catch (error) {
      console.log(`Error getting installed apps: ${error}`);
    }

    // List visible applications
    console.log('\nListing visible applications...');
    try {
      const visibleApps = await session.Application.listVisibleApps();
      console.log(`Found ${visibleApps.length} visible applications`);
      
      // Print the first 3 apps or fewer if less than 3 are available
      const count = Math.min(visibleApps.length, 3);
      for (let i = 0; i < count; i++) {
        console.log(`Process ${i + 1}: ${visibleApps[i].pname} (PID: ${visibleApps[i].pid})`);
      }
    } catch (error) {
      console.log(`Error listing visible apps: ${error}`);
    }

    // Window Management Examples
    console.log('\n=== Window Management Examples ===');

    // List root windows
    console.log('\nListing root windows...');
    try {
      const rootWindows = await session.window.listRootWindows();
      console.log(`Found ${rootWindows.length} root windows`);
      
      // Print the first 3 windows or fewer if less than 3 are available
      const count = Math.min(rootWindows.length, 3);
      for (let i = 0; i < count; i++) {
        console.log(`Window ${i + 1}: ${rootWindows[i].title} (ID: ${rootWindows[i].window_id})`);
      }
    } catch (error) {
      console.log(`Error listing root windows: ${error}`);
    }

    // Get active window
    console.log('\nGetting active window...');
    try {
      const activeWindow = await session.window.getActiveWindow();
      if (activeWindow) {
        console.log(`Active window: ${activeWindow.title} (ID: ${activeWindow.window_id})`);
      } else {
        console.log('No active window found');
      }
    } catch (error) {
      console.log(`Error getting active window: ${error}`);
    }

    // Use the active window info instead of trying to get window by ID
    console.log('\nGetting window details from active window...');
    try {
      const activeWindow = await session.window.getActiveWindow();
      
      if (activeWindow) {
        console.log(`Window details: ${activeWindow.title} (ID: ${activeWindow.window_id})`);
        if (activeWindow.width && activeWindow.height) {
          console.log(`Window dimensions: ${activeWindow.width}x${activeWindow.height}`);
        }
      } else {
        console.log('No active window details available');
      }
    } catch (error) {
      console.log(`Error getting window details: ${error}`);
    }

  } finally {
    // Clean up by deleting the session when we're done
    console.log('\nDeleting the session...');
    try {
      await agentBay.delete(session);
      console.log('Session deleted successfully');
    } catch (error) {
      console.log(`Error deleting session: ${error}`);
    }
  }
}

main().catch(error => {
  console.error('Error in main execution:', error);
  process.exit(1);
}); 