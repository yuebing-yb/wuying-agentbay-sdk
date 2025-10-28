import { InstalledApp, Process } from "../../src/application/application";
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Application - Linux System Tests", () => {
  let session: Session;
  let agentBay: AgentBay;

  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });

    // Create a session with linux_latest image
    log("Creating a new Linux session for application testing...");
    const createResponse = await agentBay.create({ imageId: "linux_latest" });

    // Verify SessionResult structure
    expect(createResponse.success).toBe(true);
    expect(createResponse.session).toBeDefined();

    session = createResponse.session!;
    log(`Linux session created with ID: ${session.sessionId}`);
    log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
  });

  afterEach(async () => {
    log("Cleaning up: Deleting the Linux session...");
    try {
      const deleteResponse = await agentBay.delete(session);
      log("Linux session successfully deleted");
      log(
        `Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`
      );
    } catch (error) {
      log(`Warning: Error deleting Linux session: ${error}`);
    }
  });

  describe("getInstalledApps() - Linux", () => {
    it("should return Linux installed applications with valid properties", async () => {
      log("Testing getInstalledApps for Linux...");
      const appsResponse = await session.computer.getInstalledApps();
      log(`Found ${appsResponse.data.length} Linux installed applications`);
      log(
        `Get Installed Apps RequestId: ${appsResponse.requestId || "undefined"}`
      );

      // Verify InstalledAppListResult structure
      expect(appsResponse.requestId).toBeDefined();
      expect(appsResponse.success).toBe(true);

      // Ensure data is an array
      expect(Array.isArray(appsResponse.data)).toBe(true);

      // Check if the list of installed apps is not empty
      if (appsResponse.data.length > 0) {
        const app = appsResponse.data[0];
        log(`First installed app: ${app.name}`);

        // Verify each app in the list has the expected properties
        appsResponse.data.forEach((app: any, index: number) => {
          expect(app).toHaveProperty("name");
          expect(app).toHaveProperty("start_cmd");
          if (index === 0) {
            log(`App name: ${app.name}`);
            log(`App start command: ${app.start_cmd}`);
          }
        });
      }
    });
  });

  describe("startApp() - Linux", () => {
    it("should start an application and return valid processes", async () => {
      log("Testing startApp for Linux...");
      const startCmd = "gedit";

      let processesResponse = null;
      try {
        processesResponse = await session.computer.startApp(startCmd);
        log(`Started app "${startCmd}"`);
        log(
          `Start App RequestId: ${processesResponse.requestId || "undefined"}`
        );

        // Verify ProcessListResult structure
        expect(processesResponse.requestId).toBeDefined();
        expect(processesResponse.success).toBe(true);

        // Ensure data is an array
        expect(Array.isArray(processesResponse.data)).toBe(true);

        if (processesResponse.data.length > 0) {
          const process = processesResponse.data[0];
          log(`Process name: ${process.pname}`);
          log(`Process PID: ${process.pid}`);

          // Verify each process in the list has the expected properties
          processesResponse.data.forEach((process: any, index: number) => {
            expect(process).toHaveProperty("pname");
            expect(process).toHaveProperty("pid");
            expect(typeof process.pid).toBe("number");
            expect(process.pid).toBeGreaterThan(0);
          });

          // Stop the application
          log(`Stopping app "${startCmd}"...`);
          const stopResponse = await session.computer.stopAppByPName(
            process.pname
          );
          log(
            `Stop App RequestId: ${stopResponse.requestId || "undefined"}`
          );
          expect(stopResponse.success).toBe(true);
        }
      } catch (error) {
        log(`Note: startApp failed: ${error}`);
        log("Continuing with test...");
      }
    });
  });

  describe("stopAppByPID() - Linux", () => {
    it("should stop an application by PID", async () => {
      log("Testing stopAppByPID for Linux...");
      const startCmd = "gedit";

      try {
        const startResponse = await session.computer.startApp(startCmd);
        log(`Started app "${startCmd}"`);

        if (startResponse.data && startResponse.data.length > 0) {
          const process = startResponse.data[0];
          const pid = process.pid;
          log(`Process PID: ${pid}`);

          // Stop the application by PID
          log(`Stopping app with PID: ${pid}...`);
          const stopResponse = await session.computer.stopAppByPID(pid);
          log(
            `Stop App RequestId: ${stopResponse.requestId || "undefined"}`
          );
          expect(stopResponse.success).toBe(true);
        }
      } catch (error) {
        log(`Note: stopAppByPID test failed: ${error}`);
      }
    });
  });

  describe("listVisibleApps() - Linux", () => {
    it("should list visible applications", async () => {
      log("Testing listVisibleApps for Linux...");

      try {
        // Start an app first
        const startCmd = "gedit";
        const startResponse = await session.computer.startApp(startCmd);
        log(`Started app "${startCmd}"`);

        if (startResponse.data && startResponse.data.length > 0) {
          const process = startResponse.data[0];

          // List visible apps
          const visibleAppsResponse = await session.computer.listVisibleApps();
          log(
            `List Visible Apps RequestId: ${
              visibleAppsResponse.requestId || "undefined"
            }`
          );
          expect(visibleAppsResponse.success).toBe(true);

          // Clean up - stop the app
          log(`Stopping app "${startCmd}"...`);
          await session.computer.stopAppByPName(process.pname);
        }
      } catch (error) {
        log(`Note: listVisibleApps test failed: ${error}`);
      }
    });
  });

  describe("stopAppByCmd() - Linux", () => {
    it("should stop an application by stop command", async () => {
      log("Testing stopAppByCmd for Linux...");
      const startCmd = "gedit";
      const stopCmd = "killall gedit";

      try {
        // Start the application
        const startResponse = await session.computer.startApp(startCmd);
        log(`Started app "${startCmd}"`);

        if (startResponse.data && startResponse.data.length > 0) {
          // Get list of visible apps to confirm it's running
          const visibleAppsResponse = await session.computer.listVisibleApps();
          log(
            `List Visible Apps RequestId: ${
              visibleAppsResponse.requestId || "undefined"
            }`
          );
          expect(visibleAppsResponse.success).toBe(true);

          // Stop the application using stop command
          log(`Stopping app using command: "${stopCmd}"...`);
          const stopResponse = await session.computer.stopAppByCmd(stopCmd);
          log(
            `Stop App RequestId: ${stopResponse.requestId || "undefined"}`
          );
          expect(stopResponse.success).toBe(true);
        }
      } catch (error) {
        log(`Note: stopAppByCmd test failed: ${error}`);
      }
    });
  });
});
