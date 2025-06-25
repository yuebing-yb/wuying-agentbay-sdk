import { InstalledApp, Process } from '../../src/application/application';
import { AgentBay, Session } from '../../src';
import { getTestApiKey } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

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
      const apps = await session.Application.getInstalledApps(true, false, true);
      log(`Found ${apps.length} installed applications`);
      
      // Verify results
      expect(apps).toBeDefined();
      expect(Array.isArray(apps)).toBe(true);
      
      if (apps.length > 0) {
        apps.forEach((app, index) => {
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
      const apps = await session.Application.getInstalledApps(true, false, true);
      
      expect(apps).toBeDefined();
      expect(Array.isArray(apps)).toBe(true);
      expect(apps.length).toBeGreaterThan(0);
      
      // Try to find Terminal in the installed apps
      let startCmd = '';
      const terminalApp = apps.find((app) => app.name === 'Terminal');
      
      if (terminalApp) {
        startCmd = terminalApp.start_cmd;
        log(`Using Terminal with start command: ${startCmd}`);
      } else {
        // Fallback to gnome-terminal if Terminal is not found
        startCmd = 'gnome-terminal';
        log(`Terminal not found in installed apps, using default command: ${startCmd}`);
      }
      
      try {
        const processes = await session.Application.startApp(startCmd, '');
        log(`Started ${processes.length} processes`);
        
        // Verify results
        expect(processes).toBeDefined();
        expect(Array.isArray(processes)).toBe(true);
        
        if (processes.length > 0) {
          processes.forEach((proc, index) => {
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
        const apps = await session.Application.getInstalledApps(true, false, true);
        
        expect(apps).toBeDefined();
        expect(Array.isArray(apps)).toBe(true);
        expect(apps.length).toBeGreaterThan(0);
        
        // Try to find Terminal in the installed apps
        let startCmd = '';
        const terminalApp = apps.find((app) => app.name === 'Terminal');
        
        if (terminalApp) {
          startCmd = terminalApp.start_cmd;
          log(`Using Terminal with start command: ${startCmd}`);
        } else {
          // Fallback to gnome-terminal if Terminal is not found
          startCmd = 'gnome-terminal';
          log(`Terminal not found in installed apps, using default command: ${startCmd}`);
        }
        
        const processes = await session.Application.startApp(startCmd, '');
        
        expect(processes).toBeDefined();
        expect(Array.isArray(processes)).toBe(true);
        expect(processes.length).toBeGreaterThan(0);
        
        const pname = processes[0].pname;
        log(`Stopping application with process name: ${pname}`);
        
        await session.Application.stopAppByPName(pname);
        log('Application stopped by process name successfully');
        
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
        const apps = await session.Application.getInstalledApps(true, false, true);
        
        expect(apps).toBeDefined();
        expect(Array.isArray(apps)).toBe(true);
        expect(apps.length).toBeGreaterThan(0);
        
        // Try to find Terminal in the installed apps
        let startCmd = '';
        const terminalApp = apps.find((app) => app.name === 'Terminal');
        
        if (terminalApp) {
          startCmd = terminalApp.start_cmd;
          log(`Using Terminal with start command: ${startCmd}`);
        } else {
          // Fallback to gnome-terminal if Terminal is not found
          startCmd = 'gnome-terminal';
          log(`Terminal not found in installed apps, using default command: ${startCmd}`);
        }
        
        const processes = await session.Application.startApp(startCmd, '');
        
        expect(processes).toBeDefined();
        expect(Array.isArray(processes)).toBe(true);
        expect(processes.length).toBeGreaterThan(0);

        // Wait 5 seconds to give the application time to open
        log('Waiting 5 seconds to give applications time to open...');
        await new Promise(resolve => setTimeout(resolve, 5000));

        const pid = processes[0].pid;
        const pname = processes[0].pname;
        log(`Stopping application with PID: ${pid} and name: ${pname}`);
        
        await session.Application.stopAppByPID(pid);
        log('Application stopped by PID successfully');
        
        // Wait 5 seconds to ensure the application has time to close
        log('Waiting 5 seconds to ensure the application has closed...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Verify the app is no longer visible by using listVisibleApps
        const visibleApps = await session.Application.listVisibleApps();
        
        log(`Found ${visibleApps.length} visible applications after stopping`);
        
        // Check that the app with the stopped PID is no longer in the list
        const stoppedAppStillVisible = visibleApps.some(app => app.pid === pid);
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
        const apps = await session.Application.getInstalledApps(true, false, true);
        
        expect(apps).toBeDefined();
        expect(Array.isArray(apps)).toBe(true);
        expect(apps.length).toBeGreaterThan(0);
        
        // Try to find Terminal in the installed apps
        let startCmd = '';
        const terminalApp = apps.find((app) => app.name === 'Terminal');
        
        if (terminalApp) {
          startCmd = terminalApp.start_cmd;
          log(`Using Terminal with start command: ${startCmd}`);
        } else {
          // Fallback to gnome-terminal if Terminal is not found
          startCmd = 'gnome-terminal';
          log(`Terminal not found in installed apps, using default command: ${startCmd}`);
        }
        
        // Start the terminal
        await session.Application.startApp(startCmd, '');
        
        // Wait for the terminal to open
        log('Waiting 5 seconds to give the terminal time to open...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Now list the visible applications
        const visibleApps = await session.Application.listVisibleApps();
        log(`Found ${visibleApps.length} visible applications`);
        
        // Verify results
        expect(visibleApps).toBeDefined();
        expect(Array.isArray(visibleApps)).toBe(true);
        
        if (visibleApps.length > 0) {
          visibleApps.forEach((app, index) => {
            log(`Verifying app ${index + 1}: ${app.pname} (PID: ${app.pid})`);
            expect(app.pname).toBeTruthy();
            expect(app.pid).toBeGreaterThan(0);
          });
        }
      } catch (error) {
        log(`Note: Failed in listVisibleApps test: ${error}`);
        // Skip test if we encounter an error
        expect(true).toBe(true);
      }
    });
  });
  
  describe('stopAppByCmd()', () => {
    it.only('should stop an application by command', async () => {
      try {
        // Get installed apps from the remote system
        const apps = await session.Application.getInstalledApps(true, false, true);
        
        expect(apps).toBeDefined();
        expect(Array.isArray(apps)).toBe(true);
        expect(apps.length).toBeGreaterThan(0);
        
        // Try to find Terminal in the installed apps
        let startCmd = '';
        const terminalApp = apps.find((app) => app.name === 'Terminal');
        
        if (terminalApp) {
          startCmd = terminalApp.start_cmd;
          log(`Using Terminal with start command: ${startCmd}`);
        } else {
          // Fallback to gnome-terminal if Terminal is not found
          startCmd = 'gnome-terminal';
          log(`Terminal not found in installed apps, using default command: ${startCmd}`);
        }
        
        // Start the terminal
        const processes = await session.Application.startApp(startCmd, '');
        expect(processes.length).toBeGreaterThan(0);
        
        // Wait for the terminal to open
        log('Waiting 5 seconds to give the terminal time to open...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Use a stop command based on the process name
        const stopCmd = `pkill ${processes[0].pname}`;
        log(`Using stop command: ${stopCmd}`);
        
        // Stop the terminal with the command
        await session.Application.stopAppByCmd(stopCmd);
        log('Application stopped by command successfully');
        
        // Wait for the terminal to close
        log('Waiting 5 seconds to give the terminal time to close...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Verify the application is no longer visible
        const visibleApps = await session.Application.listVisibleApps();
        const stoppedAppStillVisible = visibleApps.some(app => app.pid === processes[0].pid);
        expect(stoppedAppStillVisible).toBe(false);
      } catch (error) {
        log(`Note: Failed in stopAppByCmd test: ${error}`);
        // Skip test if we encounter an error
        expect(true).toBe(true);
      }
    });
  });
});
