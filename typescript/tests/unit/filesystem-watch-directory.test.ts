import { FileSystem, FileChangeEvent } from "../../src/filesystem/filesystem";
import * as sinon from "sinon";

describe("FileSystem Watch Directory Tests", () => {
  let mockFileSystem: FileSystem;
  let mockSession: any;
  let sandbox: sinon.SinonSandbox;
  let callMcpToolStub: sinon.SinonStub;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockSession = {
      getAPIKey: sandbox.stub().returns("dummy_key"),
      getSessionId: sandbox.stub().returns("dummy_session"),
      callMcpTool: sandbox.stub(),
    };

    mockFileSystem = new FileSystem(mockSession);
    callMcpToolStub = mockSession.callMcpTool;
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe("getFileChange", () => {
    it("should get file changes successfully", async () => {
      const mockResponse = {
        success: true,
        requestId: "test-123",
        data: JSON.stringify([
          { eventType: "create", path: "/tmp/file1.txt", pathType: "file" },
          { eventType: "modify", path: "/tmp/file2.txt", pathType: "file" },
        ]),
        errorMessage: "",
      };

      callMcpToolStub.resolves(mockResponse);

      const result = await mockFileSystem.getFileChange("/tmp/test_dir");

      expect(callMcpToolStub.calledWith("get_file_change", { path: "/tmp/test_dir" })).toBe(true);
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-123");
      expect(result.events).toHaveLength(2);
      expect(result.events[0].eventType).toBe("create");
      expect(result.events[0].path).toBe("/tmp/file1.txt");
      expect(result.events[1].eventType).toBe("modify");
      expect(result.events[1].path).toBe("/tmp/file2.txt");
    });

    it("should handle get file change failure", async () => {
      const mockResponse = {
        success: false,
        requestId: "test-456",
        data: "",
        errorMessage: "Directory not found",
      };

      callMcpToolStub.resolves(mockResponse);

      const result = await mockFileSystem.getFileChange("/tmp/nonexistent");

      expect(result.success).toBe(false);
      expect(result.requestId).toBe("test-456");
      expect(result.errorMessage).toBe("Directory not found");
      expect(result.events).toHaveLength(0);
    });
  });

  describe("watchDirectory event validation", () => {
    it("should validate writeFile operations produce expected 3 events from 2 polling cycles", async () => {
      // watchDirectory establishes a baseline first (first get_file_change does NOT trigger callback).
      // Only subsequent polling cycles pass events to the callback.
      // Mock: baseline (empty) -> poll1: modify test1.txt (1 event) -> poll2: create+modify test2.txt (2 events)
      // Expected: 1 + 2 = 3 events in callback

      const callbackEvents: FileChangeEvent[] = [];
      const callback = (events: FileChangeEvent[]) => {
        callbackEvents.push(...events);
      };

      const mockResponses = [
        // First call: baseline - consumed but NOT passed to callback
        {
          success: true,
          requestId: "baseline",
          data: JSON.stringify([]),
          errorMessage: "",
        },
        // Second call: modify test1.txt
        {
          success: true,
          requestId: "test-2",
          data: JSON.stringify([
            { eventType: "modify", path: "/tmp/test_dir/test1.txt", pathType: "file" },
          ]),
          errorMessage: "",
        },
        // Third call: create + modify test2.txt
        {
          success: true,
          requestId: "test-3",
          data: JSON.stringify([
            { eventType: "create", path: "/tmp/test_dir/test2.txt", pathType: "file" },
            { eventType: "modify", path: "/tmp/test_dir/test2.txt", pathType: "file" },
          ]),
          errorMessage: "",
        },
      ];

      let responseIndex = 0;
      callMcpToolStub.callsFake(() => {
        if (responseIndex < mockResponses.length) {
          const response = mockResponses[responseIndex];
          responseIndex++;
          return Promise.resolve(response);
        } else {
          // Return empty response after all expected responses
          return Promise.resolve({
            success: true,
            requestId: "empty",
            data: JSON.stringify([]),
            errorMessage: "",
          });
        }
      });

      // Create a mock AbortController for testing
      const mockController = {
        signal: {
          aborted: false,
          addEventListener: jest.fn(),
          removeEventListener: jest.fn(),
          dispatchEvent: jest.fn(),
          onabort: null,
        } as any,
        abort: jest.fn(() => {
          mockController.signal.aborted = true;
        }),
      };

      // Start watching
      const { monitoring, ready } = mockFileSystem.watchDirectory(
        "/tmp/test_dir",
        callback,
        50, // Fast polling for testing
        mockController.signal
      );

      // Wait for baseline to be established before running the test
      await ready;

      // Let it run to capture all events - need enough time for 3 polling cycles
      // Each cycle takes 50ms + processing time, so 300ms should be sufficient
      await new Promise((resolve) => setTimeout(resolve, 300));

      // Stop watching
      mockController.abort();
      await monitoring;

      // Verify exact number of events - 3 (baseline not passed to callback)
      const expectedEvents = 3;
      expect(callbackEvents.length).toBe(expectedEvents);

      // Verify event types and counts
      const createEvents = callbackEvents.filter(event => event.eventType === "create").length;
      const modifyEvents = callbackEvents.filter(event => event.eventType === "modify").length;

      const expectedCreateEvents = 1;
      const expectedModifyEvents = 2;

      expect(createEvents).toBe(expectedCreateEvents);
      expect(modifyEvents).toBe(expectedModifyEvents);

      // Verify specific event sequence (poll1: modify test1, poll2: create+modify test2)
      expect(callbackEvents[0].eventType).toBe("modify");
      expect(callbackEvents[0].path).toBe("/tmp/test_dir/test1.txt");
      expect(callbackEvents[1].eventType).toBe("create");
      expect(callbackEvents[1].path).toBe("/tmp/test_dir/test2.txt");
      expect(callbackEvents[2].eventType).toBe("modify");
      expect(callbackEvents[2].path).toBe("/tmp/test_dir/test2.txt");
    });
  });
}); 