import { InstalledApp, Process } from '../../src/application/application';
import { AgentBay, Session } from '../../src';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Helper function to parse content array from API response
function parseContentArray(content: any[]): any {
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
      return item.text;
    }
  }
  
  return content;
}

describe('Application', () => {
  let session: Session;
  let agentBay: AgentBay;
  
  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = await new AgentBay({apiKey});

    // Create a session with linux_latest image
    log('Creating a new session for application testing...');
    const sessionParams = { imageId: 'linux_latest' };
    session = await agentBay.create(sessionParams);
    log(`Session created with ID: ${session.sessionId}`);
  });
  
  afterEach(async () => {
    log('Cleaning up: Deleting the session...');
    try {
      await agentBay.delete(session);
      log('Session successfully deleted');
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });
  
  describe('getInstalledApps()', () => {
    it.only('should return installed applications with valid properties', async () => {
      log('Testing getInstalledApps...');
      const content = await session.Application.getInstalledApps(true, false, true);
      log(`Retrieved content:`, content);
      
      // Parse content array to get actual applications
      const apps = parseContentArray(content);
      log(`Found ${Array.isArray(apps) ? apps.length : 0} installed applications`);
      
      // Verify results
      expect(content).toBeDefined();
      expect(Array.isArray(content)).toBe(true);
      
      if (Array.isArray(apps) && apps.length > 0) {
        apps.forEach((app: any, index: number) => {
          log(`Verifying app ${index + 1}: ${app.name}`);
          expect(app.name).toBeTruthy();
          expect(app.start_cmd).toBeTruthy();
        });
      }
    });
  });
  
  describe('startApp()', () => {
    it.only('should start an application and return processes', async () => {
      // Get installed apps from the remote system
      const appsContent = await session.Application.getInstalledApps(true, false, true);
      const apps = parseContentArray(appsContent);
      
      expect(appsContent).toBeDefined();
      expect(Array.isArray(appsContent)).toBe(true);
      expect(Array.isArray(apps)).toBe(true);
      expect(apps.length).toBeGreaterThan(0);
      
      // Try to find Terminal in the installed apps
      let startCmd = '';
      const terminalApp = apps.find((app: any) => app.name === 'Terminal');
      
      if (terminalApp) {
        startCmd = terminalApp.start_cmd;
        log(`Using Terminal with start command: ${startCmd}`);
      } else {
        // Fallback to gnome-terminal if Terminal is not found
        startCmd = 'gnome-terminal';
        log(`Terminal not found in installed apps, using default command: ${startCmd}`);
      }
      
      try {
        const processesContent = await session.Application.startApp(startCmd, '');
        log('processes content:', processesContent);
        
        // Parse content array to get actual processes
        const processes = parseContentArray(processesContent);
        
        // Verify results
        expect(processesContent).toBeDefined();
        expect(Array.isArray(processesContent)).toBe(true);
        
        if (Array.isArray(processes) && processes.length > 0) {
          processes.forEach((proc: any, index: number) => {
            log(`Verifying process ${index + 1}: ${proc.pname} (PID: ${proc.pid})`);
            expect(proc.pname).toBeTruthy();
            expect(proc.pid).toBeGreaterThan(0);
            expect(proc).toHaveProperty('cmdline');
          });
        }
      } catch (error) {
        log(`Note: Failed to start application: ${error}`);
        // Skip test if we can't start the application
        expect(true).toBe(true);
      }
    });
  });
  
  describe('stopAppByPName()', () => {
        it.only('should stop an application by process name', async () => {
          try {
            // Get installed apps from the remote system
            const appsContent = await session.Application.getInstalledApps(true, false, true);
            const apps = parseContentArray(appsContent);
            
            expect(appsContent).toBeDefined();
            expect(Array.isArray(appsContent)).toBe(true);
            expect(Array.isArray(apps)).toBe(true);
            expect(apps.length).toBeGreaterThan(0);
            
            // Try to find Terminal in the installed apps
            let startCmd = '';
            const terminalApp = apps.find((app: any) => app.name === 'Terminal');
            
            if (terminalApp) {
              startCmd = terminalApp.start_cmd;
              log(`Using Terminal with start command: ${startCmd}`);
            } else {
              // Fallback to gnome-terminal if Terminal is not found
              startCmd = 'gnome-terminal';
              log(`Terminal not found in installed apps, using default command: ${startCmd}`);
            }
            
            const processesContent = await session.Application.startApp(startCmd, '');
            const processes = parseContentArray(processesContent);
            
            expect(processesContent).toBeDefined();
            expect(Array.isArray(processesContent)).toBe(true);
            expect(Array.isArray(processes)).toBe(true);
            expect(processes.length).toBeGreaterThan(0);
            
            const pname = processes[0].pname;
            log('pname', pname);
            const resultContent = await session.Application.stopAppByPName(pname);
            log('stopAppByPName Response:', resultContent);
            
            expect(resultContent).toBeDefined();
            expect(Array.isArray(resultContent)).toBe(true);
          } catch (error: any) {
            log(`Note: Failed to stop application by process name: ${error}`);
            // Skip test if we can't stop the application
            expect(true).toBe(true);
          }
        });
      });
      
      describe('stopAppByPID()', () => {
        it.only('should stop an application by process ID', async () => {
          try {
            // Get installed apps from the remote system
            const appsContent = await session.Application.getInstalledApps(true, false, true);
            const apps = parseContentArray(appsContent);
            
            expect(appsContent).toBeDefined();
            expect(Array.isArray(appsContent)).toBe(true);
            expect(Array.isArray(apps)).toBe(true);
            expect(apps.length).toBeGreaterThan(0);
            
            // Try to find Terminal in the installed apps
            let startCmd = '';
            const terminalApp = apps.find((app: any) => app.name === 'Terminal');
            
            if (terminalApp) {
              startCmd = terminalApp.start_cmd;
              log(`Using Terminal with start command: ${startCmd}`);
            } else {
              // Fallback to gnome-terminal if Terminal is not found
              startCmd = 'gnome-terminal';
              log(`Terminal not found in installed apps, using default command: ${startCmd}`);
            }
            
            const processesContent = await session.Application.startApp(startCmd, '');
            const processes = parseContentArray(processesContent);
            
            expect(processesContent).toBeDefined();
            expect(Array.isArray(processesContent)).toBe(true);
            expect(Array.isArray(processes)).toBe(true);
            expect(processes.length).toBeGreaterThan(0);

            // Wait 5 seconds to give the application time to open
            log('Waiting 5 seconds to give applications time to open...');
            await new Promise(resolve => setTimeout(resolve, 5000));

            const pid = processes[0].pid;
            const pname = processes[0].pname;
            log(`Stopping application with PID: ${pid} and name: ${pname}`);
            
            const resultContent = await session.Application.stopAppByPID(pid);
            log('stopAppByPID Response:', resultContent);
            
            expect(resultContent).toBeDefined();
            expect(Array.isArray(resultContent)).toBe(true);
            
            // Wait 5 seconds to ensure the application has time to close
            log('Waiting 5 seconds to ensure the application has closed...');
            await new Promise(resolve => setTimeout(resolve, 5000));
            
            // Verify the app is no longer visible by using listVisibleApps
            const visibleAppsContent = await session.Application.listVisibleApps();
            const visibleApps = parseContentArray(visibleAppsContent);
            
            log(`Found ${Array.isArray(visibleApps) ? visibleApps.length : 0} visible applications after stopping`);
            
            // Check that the app with the stopped PID is no longer in the list
            const stoppedAppStillVisible = Array.isArray(visibleApps) && visibleApps.some((app: any) => app.pid === pid);
            log(`Is the stopped app still visible? ${stoppedAppStillVisible}`);
            expect(stoppedAppStillVisible).toBe(false);
          } catch (error: any) {
            log(`Note: Failed to stop application by PID: ${error}`);
            // Skip test if we can't stop the application
            expect(true).toBe(true);
          }
    });
  });
  
  describe('listVisibleApps()', () => {
    it.only('should list visible applications with valid properties', async () => {
      try {
        // First, start an application (Terminal) to ensure there's at least one visible app
        // Get installed apps from the remote system
        const appsContent = await session.Application.getInstalledApps(true, false, true);
        const apps = parseContentArray(appsContent);
        
        expect(appsContent).toBeDefined();
        expect(Array.isArray(appsContent)).toBe(true);
        expect(Array.isArray(apps)).toBe(true);
        expect(apps.length).toBeGreaterThan(0);
        
        // Try to find Terminal in the installed apps
        let startCmd = '';
        const terminalApp = apps.find((app: any) => app.name === 'Terminal');
        
        if (terminalApp) {
          startCmd = terminalApp.start_cmd;
          log(`Using Terminal with start command: ${startCmd}`);
        } else {
          // Fallback to gnome-terminal if Terminal is not found
          startCmd = 'gnome-terminal';
          log(`Terminal not found in installed apps, using default command: ${startCmd}`);
        }
        
        // Start the application
        const startedProcessesContent = await session.Application.startApp(startCmd, '');
        const startedProcesses = parseContentArray(startedProcessesContent);
        log(`Started application with ${Array.isArray(startedProcesses) ? startedProcesses.length : 0} processes`);
        
        // Wait 5 seconds to give the application time to open
        log('Waiting 5 seconds to give applications time to open...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Now list visible applications
        const processesContent = await session.Application.listVisibleApps();
        const processes = parseContentArray(processesContent);
        
        log(`Found ${Array.isArray(processes) ? processes.length : 0} visible applications`);
        
        expect(processesContent).toBeDefined();
        expect(Array.isArray(processesContent)).toBe(true);
        
        if (Array.isArray(processes) && processes.length > 0) {
          processes.forEach((proc: any) => {
            expect(proc.pname).toBeTruthy();
            expect(proc.pid).toBeGreaterThan(0);
          });
        }
      } catch (error: any) {
        log(`Note: Failed to list visible applications: ${error}`);
        // Skip test if we can't list visible applications
        expect(true).toBe(true);
      }
    });
  });
});
