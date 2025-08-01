import {
  InstalledApp,
  Process,
  Application,
} from "../../src/application/application";
import { APIError } from "../../src/exceptions";
import * as sinon from "sinon";

const mockInstalledAppsData: InstalledApp[] = [
  {
    name: "美团",
    start_cmd:
      "monkey -p com.sankuai.meituan -c android.intent.category.LAUNCHER 1",
    stop_cmd: "am force-stop com.sankuai.meituan",
    work_directory: "",
  },
  {
    name: "小红书",
    start_cmd: "monkey -p com.xingin.xhs -c android.intent.category.LAUNCHER 1",
    stop_cmd: "am force-stop com.xingin.xhs",
    work_directory: "",
  },
  {
    name: "高德地图",
    start_cmd:
      "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1",
    stop_cmd: "am force-stop com.autonavi.minimap",
    work_directory: "",
  },
];

const mockProcessData: Process[] = [
  {
    pname: "com.autonavi.minimap",
    pid: 12345,
    cmdline:
      "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1",
  },
];

const mockVisibleAppsData: Process[] = [
  {
    pname: "com.autonavi.minimap",
    pid: 12345,
    cmdline: "cmd1",
  },
  {
    pname: "com.xingin.xhs",
    pid: 23456,
    cmdline: "cmd2",
  },
];

describe("ApplicationApi", () => {
  let mockApplication: Application;
  let mockSession: any;
  let sandbox: sinon.SinonSandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockSession = {
      getAPIKey: sandbox.stub().returns("test-api-key"),
      getClient: sandbox.stub(),
      getSessionId: sandbox.stub().returns("test-session-id"),
    };

    mockApplication = new Application(mockSession);
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe("test_get_installed_apps_success", () => {
    it("should get installed apps successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          textContent: JSON.stringify(mockInstalledAppsData),
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.getInstalledApps();

      // Verify InstalledAppListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toHaveLength(3);
      expect(result.errorMessage).toBeUndefined();

      expect(result.data[0]).toBeInstanceOf(Object);
      expect(result.data[0].name).toBe("美团");
      expect(result.data[1].name).toBe("小红书");
      expect(result.data[2].name).toBe("高德地图");

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_get_installed_apps_failure", () => {
    it("should handle get installed apps failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to get installed apps"));

      const result = await mockApplication.getInstalledApps();

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toEqual([]);
      expect(result.errorMessage).toContain("Failed to get installed apps");
    });
  });

  describe("test_start_app_success", () => {
    it("should start app successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          textContent: JSON.stringify(mockProcessData),
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.startApp(
        "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1"
      );

      // Verify ProcessListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toHaveLength(1);
      expect(result.errorMessage).toBeUndefined();

      expect(result.data[0].pname).toBe("com.autonavi.minimap");
      expect(result.data[0].pid).toBe(12345);
      expect(result.data[0].cmdline).toBe(
        "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1"
      );

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_start_app_failure", () => {
    it("should handle start app failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to start app"));

      const result = await mockApplication.startApp(
        "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toEqual([]);
      expect(result.errorMessage).toContain("Failed to start app");
    });
  });

  describe("test_start_app_with_activity_success", () => {
    it("should start app with activity successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          textContent: JSON.stringify(mockProcessData),
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.startApp(
        "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1",
        "",
        ".SettingsActivity"
      );

      // Verify ProcessListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toHaveLength(1);
      expect(result.errorMessage).toBeUndefined();

      expect(result.data[0].pname).toBe("com.autonavi.minimap");
      expect(result.data[0].pid).toBe(12345);
      expect(result.data[0].cmdline).toBe(
        "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1"
      );

      // Verify that activity was passed correctly
      expect(callMcpToolStub.calledOnce).toBe(true);
      const callArgs = callMcpToolStub.getCall(0).args;
      expect(callArgs[0]).toBe("start_app");
      expect(callArgs[1]).toEqual({
        start_cmd:
          "monkey -p com.autonavi.minimap -c android.intent.category.LAUNCHER 1",
        activity: ".SettingsActivity",
      });
    });
  });

  describe("test_start_app_with_activity_and_work_directory", () => {
    it("should start app with activity and work directory successfully", async () => {
      const mockXhsProcessData: Process[] = [
        {
          pname: "com.xingin.xhs",
          pid: 23456,
          cmdline:
            "monkey -p com.xingin.xhs -c android.intent.category.LAUNCHER 1",
        },
      ];

      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          textContent: JSON.stringify(mockXhsProcessData),
          isError: false,
          statusCode: 200,
          requestId: "test-request-456",
        });

      const result = await mockApplication.startApp(
        "monkey -p com.xingin.xhs -c android.intent.category.LAUNCHER 1",
        "/storage/emulated/0",
        "com.xingin.xhs/.MainActivity"
      );

      // Verify ProcessListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-456");
      expect(result.data).toHaveLength(1);
      expect(result.errorMessage).toBeUndefined();

      expect(result.data[0].pname).toBe("com.xingin.xhs");
      expect(result.data[0].pid).toBe(23456);

      // Verify all parameters were passed correctly
      expect(callMcpToolStub.calledOnce).toBe(true);
      const callArgs = callMcpToolStub.getCall(0).args;
      expect(callArgs[0]).toBe("start_app");
      expect(callArgs[1]).toEqual({
        start_cmd:
          "monkey -p com.xingin.xhs -c android.intent.category.LAUNCHER 1",
        work_directory: "/storage/emulated/0",
        activity: "com.xingin.xhs/.MainActivity",
      });
    });
  });

  describe("test_stop_app_by_cmd_success", () => {
    it("should stop app by command successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.stopAppByCmd(
        "am force-stop com.autonavi.minimap"
      );

      // Verify AppOperationResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_stop_app_by_cmd_failure", () => {
    it("should handle stop app by command failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to stop app"));

      const result = await mockApplication.stopAppByCmd(
        "am force-stop com.autonavi.minimap"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.errorMessage).toContain("Failed to stop app by command");
    });
  });

  describe("test_stop_app_by_pname_success", () => {
    it("should stop app by package name successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.stopAppByPName(
        "com.autonavi.minimap"
      );

      // Verify AppOperationResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_stop_app_by_pname_failure", () => {
    it("should handle stop app by package name failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to stop app by pname"));

      const result = await mockApplication.stopAppByPName(
        "com.autonavi.minimap"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.errorMessage).toContain("Failed to stop app by pname");
    });
  });

  describe("test_stop_app_by_pid_success", () => {
    it("should stop app by PID successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.stopAppByPID(12345);

      // Verify AppOperationResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_stop_app_by_pid_failure", () => {
    it("should handle stop app by PID failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to stop app by pid"));

      const result = await mockApplication.stopAppByPID(12345);

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.errorMessage).toContain("Failed to stop app by pid");
    });
  });

  describe("test_list_visible_apps_success", () => {
    it("should list visible apps successfully", async () => {
      const callMcpToolStub = sandbox
        .stub(mockApplication as any, "callMcpTool")
        .resolves({
          data: {},
          textContent: JSON.stringify(mockVisibleAppsData),
          isError: false,
          statusCode: 200,
          requestId: "test-request-id",
        });

      const result = await mockApplication.listVisibleApps();

      // Verify ProcessListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toHaveLength(2);
      expect(result.errorMessage).toBeUndefined();

      expect(result.data[0]).toBeInstanceOf(Object);
      expect(result.data[0].pname).toBe("com.autonavi.minimap");
      expect(result.data[1].pname).toBe("com.xingin.xhs");

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_list_visible_apps_failure", () => {
    it("should handle list visible apps failure", async () => {
      sandbox
        .stub(mockApplication as any, "callMcpTool")
        .rejects(new APIError("Failed to list visible apps"));

      const result = await mockApplication.listVisibleApps();

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toEqual([]);
      expect(result.errorMessage).toContain("Failed to list visible apps");
    });
  });
});
