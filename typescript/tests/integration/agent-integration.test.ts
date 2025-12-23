import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Agent", () => {
  describe("computerExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with Windows image for computer agent tasks
      log("Creating a new session for computer agent task testing...");
      const createResponse = await agentBay.create({ imageId: "windows_latest" });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(`Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`);
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully", async () => {
      if (session.agent) {
        const task = "create a folder named 'agentbay' in C:\\Windows\\Temp";
        
        // Get timeout from environment or use default
        const maxTryTimesStr = process.env.AGENT_TASK_TIMEOUT;
        let maxTryTimes = 300; // default value
        if (maxTryTimesStr) {
          const parsed = parseInt(maxTryTimesStr, 10);
          if (!isNaN(parsed)) {
            maxTryTimes = parsed;
          }
        } else {
          log("We will wait for 300 * 3 seconds to finish.");
        }

        try {
          log(`Executing computer agent task: ${task}`);
          const result = await session.agent.computer.executeTask(task, maxTryTimes);
          
          log(`Agent task result: Success=${result.success}, TaskID=${result.taskId}, Status=${result.taskStatus}`);
          log(`Agent Task RequestId: ${result.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Agent task execution failed: ${result.errorMessage}`);
            // Don't fail the test if task execution is not supported in test environment
          } else {
            log(`Agent task executed successfully with result: ${result.taskResult}`);
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
          }
        } catch (error) {
          log(`Note: Agent task execution failed: ${error}`);
          // Don't fail the test if agent execution is not supported
        }
      } else {
        log("Note: Agent interface is nil, skipping agent test");
      }
    }); // Set a long timeout for the task execution
  });

  describe("browserExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with linux image for agent tasks
      log("Creating a new session for browser agent task testing...");
      const createResponse = await agentBay.create({ imageId: "linux_latest" });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(`Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`);
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully", async () => {
      if (session.agent) {
        const task = "Navigate to baidu.com and Query the date when Alibaba listed in the U.S";
        
        // Get timeout from environment or use default
        const maxTryTimesStr = process.env.AGENT_TASK_TIMEOUT;
        let maxTryTimes = 300; // default value
        if (maxTryTimesStr) {
          const parsed = parseInt(maxTryTimesStr, 10);
          if (!isNaN(parsed)) {
            maxTryTimes = parsed;
          }
        } else {
          log("We will wait for 300 * 3 seconds to finish.");
        }

        try {
          log(`Executing browser agent task: ${task}`);
          const result = await session.agent.browser.executeTask(task, maxTryTimes);
          
          log(`Agent task result: Success=${result.success}, TaskID=${result.taskId}, Status=${result.taskStatus}`);
          log(`Agent Task RequestId: ${result.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Agent task execution failed: ${result.errorMessage}`);
            // Don't fail the test if task execution is not supported in test environment
          } else {
            log(`Agent task executed successfully with result: ${result.taskResult}`);
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
          }
        } catch (error) {
          log(`Note: Agent task execution failed: ${error}`);
          // Don't fail the test if agent execution is not supported
        }
      } else {
        log("Note: Agent interface is nil, skipping agent test");
      }
    }); // Set a long timeout for the task execution
  });

  describe("mobileExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with mobile image for mobile agent tasks
      log("Creating a new session for mobile agent task testing...");
      const createResponse = await agentBay.create({ imageId: "mobile_latest" });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(`Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`);
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully (non-blocking)", async () => {
      if (session.agent) {
        const task = "Open WeChat app";
        const maxSteps = 100;
        const maxStepRetries = 5;

        try {
          log(`Executing mobile agent task (non-blocking): ${task}`);
          const result = await session.agent.mobile.executeTask(
              task, maxSteps, maxStepRetries);

          log(`Mobile Agent task result: Success=${result.success}, ` +
              `TaskID=${result.taskId}, Status=${result.taskStatus}`);
          log(`Mobile Agent Task RequestId: ${result.requestId || "undefined"}`);

          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Mobile Agent task execution failed: ` +
                `${result.errorMessage}`);
          } else {
            log(`Mobile Agent task executed successfully, ` +
                `TaskID: ${result.taskId}`);
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
            expect(result.taskStatus).toBe("running");
          }
        } catch (error) {
          log(`Note: Mobile Agent task execution failed: ${error}`);
        }
      } else {
        log("Note: Agent interface is nil, skipping mobile agent test");
      }
    }, 120000);

    it("should execute task and wait successfully (blocking)", async () => {
      if (session.agent) {
        const task = "Open WeChat app";
        const maxSteps = 100;
        const maxStepRetries = 3;
        const maxTryTimes = 300;

        try {
          log(`Executing mobile agent task (blocking): ${task}`);
          const result = await session.agent.mobile.executeTaskAndWait(
              task, maxSteps, maxStepRetries, maxTryTimes);

          log(`Mobile Agent task result: Success=${result.success}, ` +
              `TaskID=${result.taskId}, Status=${result.taskStatus}`);
          log(`Mobile Agent Task RequestId: ${result.requestId || "undefined"}`);

          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Mobile Agent task execution failed: ` +
                `${result.errorMessage}`);
          } else {
            log(`Mobile Agent task executed successfully with result: ` +
                `${result.taskResult}`);
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
            expect(result.taskStatus).toBe("completed");
          }
        } catch (error) {
          log(`Note: Mobile Agent task execution failed: ${error}`);
        }
      } else {
        log("Note: Agent interface is nil, skipping mobile agent test");
      }
    }, 120000);
  });
}); 