import {
  AgentEvent,
  AgentStreamingOptions,
  AgentEventCallback,
  MobileTaskOptions,
  TaskExecution,
  MobileUseAgent,
  ComputerUseAgent,
  BrowserUseAgent,
  Agent,
} from "../../src/agent";

describe("AgentEvent", () => {
  test("should create reasoning event correctly", () => {
    const event: AgentEvent = {
      type: "reasoning",
      seq: 1,
      round: 1,
      content: "thinking...",
    };
    expect(event.type).toBe("reasoning");
    expect(event.seq).toBe(1);
    expect(event.round).toBe(1);
    expect(event.content).toBe("thinking...");
  });

  test("should create tool_call event correctly", () => {
    const event: AgentEvent = {
      type: "tool_call",
      seq: 2,
      round: 1,
      toolCallId: "call_001",
      toolName: "browser_navigate",
      args: { url: "https://example.com" },
    };
    expect(event.toolName).toBe("browser_navigate");
    expect(event.args).toEqual({ url: "https://example.com" });
  });

  test("should create tool_result event correctly", () => {
    const event: AgentEvent = {
      type: "tool_result",
      seq: 3,
      round: 1,
      toolCallId: "call_001",
      toolName: "browser_navigate",
      result: { output: "success" },
    };
    expect(event.result).toEqual({ output: "success" });
  });

  test("should create error event correctly", () => {
    const event: AgentEvent = {
      type: "error",
      seq: 4,
      round: 1,
      error: { message: "something went wrong" },
    };
    expect(event.error).toEqual({ message: "something went wrong" });
  });
});

describe("AgentStreamingOptions", () => {
  test("should not have streamBeta field", () => {
    const options: AgentStreamingOptions = {
      onReasoning: (_e: AgentEvent) => {},
    };
    expect("streamBeta" in options).toBe(false);
  });

  test("should accept all callback fields", () => {
    const cb: AgentEventCallback = (_e: AgentEvent) => {};
    const options: AgentStreamingOptions = {
      onReasoning: cb,
      onContent: cb,
      onToolCall: cb,
      onToolResult: cb,
      onError: cb,
    };
    expect(options.onReasoning).toBe(cb);
    expect(options.onContent).toBe(cb);
    expect(options.onToolCall).toBe(cb);
    expect(options.onToolResult).toBe(cb);
    expect(options.onError).toBe(cb);
  });
});

describe("Agent target resolution", () => {
  const mockSession = {
    getAPIKey: () => "test_key",
    getSessionId: () => "sess_test",
    callMcpTool: async () => ({
      success: true,
      data: "{}",
      errorMessage: "",
      requestId: "",
    }),
    mcpTools: [],
  };

  test("MobileUseAgent resolves to wuying_mobile_agent", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).resolveAgentTarget()).toBe("wuying_mobile_agent");
  });

  test("ComputerUseAgent resolves to wuying_computer_agent", () => {
    const agent = new ComputerUseAgent(mockSession);
    expect((agent as any).resolveAgentTarget()).toBe("wuying_computer_agent");
  });

  test("BrowserUseAgent resolves to wuying_browseruse", () => {
    const agent = new BrowserUseAgent(mockSession);
    expect((agent as any).resolveAgentTarget()).toBe("wuying_browseruse");
  });
});

describe("hasStreamingParams", () => {
  const mockSession = {
    getAPIKey: () => "test_key",
    getSessionId: () => "sess_test",
    callMcpTool: async () => ({
      success: true,
      data: "{}",
      errorMessage: "",
      requestId: "",
    }),
  };

  test("returns false when no options provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams()).toBe(false);
    expect((agent as any).hasStreamingParams(undefined)).toBe(false);
  });

  test("returns false for empty options object", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({})).toBe(false);
  });

  test("returns true when onReasoning is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({ onReasoning: () => {} })).toBe(
      true
    );
  });

  test("returns true when onContent is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({ onContent: () => {} })).toBe(
      true
    );
  });

  test("returns true when onToolCall is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({ onToolCall: () => {} })).toBe(
      true
    );
  });

  test("returns true when onToolResult is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({ onToolResult: () => {} })).toBe(
      true
    );
  });

  test("returns true when onError is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect((agent as any).hasStreamingParams({ onError: () => {} })).toBe(true);
  });

  test("returns true when onCallForUser is provided", () => {
    const agent = new MobileUseAgent(mockSession);
    expect(
      (agent as any).hasStreamingParams({
        onCallForUser: async () => "user input",
      })
    ).toBe(true);
  });
});

describe("MobileTaskOptions", () => {
  test("should accept maxSteps and onCallForUser", () => {
    const options: MobileTaskOptions = {
      maxSteps: 100,
      onCallForUser: async () => "user input",
    };
    expect(options.maxSteps).toBe(100);
    expect(options.onCallForUser).toBeDefined();
  });
});

describe("TaskExecution", () => {
  test("wait() should resolve with result when no timeout", async () => {
    const result = {
      requestId: "r1",
      success: true,
      errorMessage: "",
      taskStatus: "completed",
      taskId: "t1",
      taskResult: "done",
    };
    const exec = new TaskExecution("t1", Promise.resolve(result));
    const got = await exec.wait();
    expect(got).toEqual(result);
    expect(exec.taskId).toBe("t1");
  });

  test("wait(timeout) should timeout when promise is slow", async () => {
    const cancelFn = jest.fn();
    const exec = new TaskExecution("t1", new Promise(() => {}), cancelFn);
    const result = await exec.wait(0.1);
    expect(result.success).toBe(false);
    expect(result.taskStatus).toBe("failed");
    expect(result.errorMessage).toContain("timed out");
    expect(cancelFn).toHaveBeenCalled();
  });

  test("wait(timeout) should resolve when promise completes before timeout", async () => {
    const result = {
      requestId: "r1",
      success: true,
      errorMessage: "",
      taskStatus: "completed",
      taskId: "t1",
      taskResult: "done",
    };
    const exec = new TaskExecution("t1", Promise.resolve(result));
    const got = await exec.wait(60);
    expect(got).toEqual(result);
  });
});

describe("MobileUseAgent executeTask and executeTaskAndWait", () => {
  test("executeTaskAndWait should route to WS when streaming options provided", async () => {
    let wsStreamCalled = false;
    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      getWsClient: async () => ({
        callStream: async (params: any) => {
          wsStreamCalled = true;
          expect(params.data.method).toBe("exec_task");
          expect(params.data.stream).toBeUndefined();
          expect(params.data.params.task).toBe("Test task");
          expect(params.data.params.max_steps).toBe(10);
          return {
            waitEnd: async () => ({ status: "finished", taskResult: "done" }),
            cancel: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      maxSteps: 10,
      onReasoning: () => {},
    });

    expect(wsStreamCalled).toBe(true);
    expect(result.success).toBe(true);
    expect(result.taskStatus).toBe("finished");
  });

  test("executeTaskAndWait should route to WS when options passed as 3rd arg", async () => {
    let wsStreamCalled = false;
    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      getWsClient: async () => ({
        callStream: async () => {
          wsStreamCalled = true;
          return {
            waitEnd: async () => ({ status: "finished", taskResult: "done" }),
            cancel: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    await agent.executeTaskAndWait("Test task", 60, { onReasoning: () => {} });

    expect(wsStreamCalled).toBe(true);
  });

  test("executeTask should return TaskExecution and use HTTP polling when no streaming options", async () => {
    let httpCalled = false;
    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => {
        httpCalled = true;
        return {
          success: true,
          data: JSON.stringify({
            task_id: "task_123",
            status: "completed",
            result: "done",
          }),
          errorMessage: "",
          requestId: "req_test",
        };
      },
    };

    const agent = new MobileUseAgent(mockSession);
    const execution = await agent.executeTask("Test task");
    expect(execution).toBeInstanceOf(TaskExecution);
    expect(execution.taskId).toBe("task_123");
    expect(httpCalled).toBe(true);
  });
});

describe("ComputerUseAgent and BrowserUseAgent do not accept streaming options", () => {
  test("ComputerUseAgent.executeTaskAndWait has no streaming option parameter", () => {
    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
    };

    const agent = new ComputerUseAgent(mockSession);
    // executeTaskAndWait only accepts (task, timeout) - no streaming options
    expect(agent.executeTaskAndWait.length).toBeLessThanOrEqual(2);
  });
});

describe("WS stream does not send stream field", () => {
  test("executeTaskStreamWs should not include stream in data payload", async () => {
    let capturedData: any = null;
    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          capturedData = params.data;
          return {
            waitEnd: async () => ({ status: "finished" }),
            cancel: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    await agent.executeTaskAndWait("Test task", 60, { onReasoning: () => {} });

    expect(capturedData).toBeDefined();
    expect(capturedData.method).toBe("exec_task");
    expect(capturedData.stream).toBeUndefined();
    expect(capturedData.params.task).toBe("Test task");
  });
});

describe("Streaming event dispatch", () => {
  test("should dispatch events to typed callbacks", async () => {
    const reasoningEvents: AgentEvent[] = [];
    const contentEvents: AgentEvent[] = [];
    const toolCallEvents: AgentEvent[] = [];
    const toolResultEvents: AgentEvent[] = [];

    let onEventHandler: ((invocationId: string, data: any) => void) | null =
      null;

    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          onEventHandler = params.onEvent;
          return {
            waitEnd: () =>
              new Promise<any>((resolve) => {
                setTimeout(() => {
                  if (onEventHandler) {
                    onEventHandler("inv_test", {
                      eventType: "reasoning",
                      seq: 1,
                      round: 1,
                      content: "thinking",
                    });
                    onEventHandler("inv_test", {
                      eventType: "content",
                      seq: 2,
                      round: 1,
                      content: "hello",
                    });
                    onEventHandler("inv_test", {
                      eventType: "tool_call",
                      seq: 3,
                      round: 1,
                      toolCallId: "tc1",
                      toolName: "click",
                      args: { x: 100 },
                    });
                    onEventHandler("inv_test", {
                      eventType: "tool_result",
                      seq: 4,
                      round: 1,
                      toolCallId: "tc1",
                      toolName: "click",
                      result: { output: "ok" },
                    });
                  }
                  resolve({ status: "finished", taskResult: "done" });
                }, 50);
              }),
            cancel: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      onReasoning: (e: AgentEvent) => reasoningEvents.push(e),
      onContent: (e: AgentEvent) => contentEvents.push(e),
      onToolCall: (e: AgentEvent) => toolCallEvents.push(e),
      onToolResult: (e: AgentEvent) => toolResultEvents.push(e),
    });

    expect(result.success).toBe(true);
    expect(result.taskResult).toBe("done");
    expect(reasoningEvents.length).toBe(1);
    expect(reasoningEvents[0].content).toBe("thinking");
    expect(contentEvents.length).toBe(1);
    expect(contentEvents[0].content).toBe("hello");
    expect(toolCallEvents.length).toBe(1);
    expect(toolCallEvents[0].toolName).toBe("click");
    expect(toolResultEvents.length).toBe(1);
    expect(toolResultEvents[0].result).toEqual({ output: "ok" });
  });

  test("should accumulate content for task result", async () => {
    let onEventHandler: ((invocationId: string, data: any) => void) | null =
      null;

    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          onEventHandler = params.onEvent;
          return {
            waitEnd: () =>
              new Promise<any>((resolve) => {
                setTimeout(() => {
                  if (onEventHandler) {
                    onEventHandler("inv_test", {
                      eventType: "content",
                      seq: 1,
                      round: 1,
                      content: "Hello",
                    });
                    onEventHandler("inv_test", {
                      eventType: "content",
                      seq: 2,
                      round: 1,
                      content: " World",
                    });
                  }
                  resolve({ status: "finished" });
                }, 50);
              }),
            cancel: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      onContent: () => {},
    });

    expect(result.success).toBe(true);
    expect(result.taskResult).toBe("Hello World");
  });
});

describe("call_for_user via tool_call", () => {
  test("onCallForUser is invoked when tool_call has toolName=call_for_user", async () => {
    const callForUserEvents: AgentEvent[] = [];
    let onEventHandler: ((invocationId: string, data: any) => void) | null =
      null;

    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          onEventHandler = params.onEvent;
          return {
            waitEnd: () =>
              new Promise<any>((resolve) => {
                setTimeout(() => {
                  if (onEventHandler) {
                    onEventHandler("inv_test", {
                      eventType: "tool_call",
                      seq: 1,
                      round: 1,
                      toolCallId: "call_003",
                      toolName: "call_for_user",
                      args: { prompt: "Please enter verification code" },
                    });
                  }
                  resolve({ status: "finished", taskResult: "done" });
                }, 50);
              }),
            cancel: async () => {},
            write: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      onCallForUser: async (e) => {
        callForUserEvents.push(e);
        return "385216";
      },
    });

    expect(result.success).toBe(true);
    expect(callForUserEvents.length).toBe(1);
    expect(callForUserEvents[0].toolName).toBe("call_for_user");
    expect(callForUserEvents[0].prompt).toBe("Please enter verification code");
  });

  test("resume_task is sent after onCallForUser returns", async () => {
    const writeCalls: Array<Record<string, any>> = [];
    let onEventHandler: ((invocationId: string, data: any) => void) | null =
      null;

    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          onEventHandler = params.onEvent;
          return {
            waitEnd: () =>
              new Promise<any>((resolve) => {
                setTimeout(() => {
                  if (onEventHandler) {
                    onEventHandler("inv_test", {
                      eventType: "tool_call",
                      seq: 1,
                      round: 1,
                      toolCallId: "call_003",
                      toolName: "call_for_user",
                      args: { prompt: "Continue?" },
                    });
                  }
                  resolve({ status: "finished", taskResult: "done" });
                }, 50);
              }),
            cancel: async () => {},
            write: async (data: Record<string, any>) => {
              writeCalls.push(data);
            },
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      onCallForUser: async () => "yes",
    });

    expect(result.success).toBe(true);
    expect(writeCalls.length).toBe(1);
    expect(writeCalls[0].method).toBe("resume_task");
    expect(writeCalls[0].params.toolCallId).toBe("call_003");
    expect(writeCalls[0].params.response).toBe("yes");
  });

  test("call_for_user tool_call also triggers onToolCall", async () => {
    const toolCallEvents: AgentEvent[] = [];
    let onEventHandler: ((invocationId: string, data: any) => void) | null =
      null;

    const mockSession = {
      getAPIKey: () => "test_key",
      getSessionId: () => "sess_test",
      callMcpTool: async () => ({
        success: true,
        data: "{}",
        errorMessage: "",
        requestId: "",
      }),
      mcpTools: [],
      getWsClient: async () => ({
        callStream: async (params: any) => {
          onEventHandler = params.onEvent;
          return {
            waitEnd: () =>
              new Promise<any>((resolve) => {
                setTimeout(() => {
                  if (onEventHandler) {
                    onEventHandler("inv_test", {
                      eventType: "tool_call",
                      seq: 1,
                      round: 1,
                      toolCallId: "call_003",
                      toolName: "call_for_user",
                      args: { prompt: "Input code" },
                    });
                  }
                  resolve({ status: "finished", taskResult: "done" });
                }, 50);
              }),
            cancel: async () => {},
            write: async () => {},
            invocationId: "inv_test",
          };
        },
      }),
    };

    const agent = new MobileUseAgent(mockSession);
    const result = await agent.executeTaskAndWait("Test task", 60, {
      onToolCall: (e) => toolCallEvents.push(e),
      onCallForUser: async () => "123456",
    });

    expect(result.success).toBe(true);
    expect(toolCallEvents.some((e) => e.toolName === "call_for_user")).toBe(
      true
    );
  });
});
