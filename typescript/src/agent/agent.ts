import { BrowserOption } from "src/browser";
import { ApiResponse } from "../types/api-response";
import { logWarn, logDebug, logInfo } from "../utils/logger";
import { z, ZodTypeAny } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";

const DefaultSchema = z.object({});

/**
 * Result of task execution.
 */
export interface ExecutionResult extends ApiResponse {
  taskId: string;
  taskStatus: string;
  taskResult: string;
}

/**
 * Result of query operations.
 */
export interface QueryResult extends ApiResponse {
  taskId: string;
  taskStatus: string;
  taskAction: string;
  taskProduct: string;
  stream?: Array<{
    content?: string;
    reasoning?: string;
    timestamp_ms?: number;
  }>;
  error?: string;
}

/**
 * Represents a streaming event from an Agent execution.
 *
 * Event types map directly to LLM output field names:
 * - "reasoning": from LLM reasoning_content (model's internal reasoning/thinking)
 * - "content": from LLM content (model's text output, intermediate analysis or final answer)
 * - "tool_call": from LLM tool_calls (tool invocation request)
 * - "tool_result": tool execution result
 * - "error": execution error
 *
 * The `result` field in tool_result events carries an agent-defined structure
 * that the SDK passes through without parsing. Typical fields include
 * `isError` (boolean), `output` (string), and optionally `screenshot`
 * (base64 string). The final task outcome is delivered via the
 * `ExecutionResult` return value of `executeTaskAndWait`.
 */
export interface AgentEvent {
  type: string;
  seq: number;
  round: number;
  content?: string;
  toolCallId?: string;
  toolName?: string;
  args?: Record<string, any>;
  /** Prompt text for call_for_user tool_call events. */
  prompt?: string;
  /** Agent-defined tool execution result (e.g. {isError, output, screenshot}). Not parsed by SDK. */
  result?: Record<string, any>;
  error?: Record<string, any>;
}

export type AgentEventCallback = (event: AgentEvent) => void;

/**
 * Result of an MCP tool call.
 */
export interface McpToolResult {
  success: boolean;
  data: string;
  errorMessage: string;
  requestId: string;
}

/**
 * Interface defining the methods needed by Agent from Session.
 */
export interface McpSession {
  getAPIKey(): string;
  getSessionId(): string;
  callMcpTool(
    toolName: string,
    args: Record<string, any>,
    autoGenSession?: boolean
  ): Promise<McpToolResult>;
}

/**
 * Options for executeTaskAndWait when using WebSocket streaming.
 */
export interface AgentStreamingOptions {
  onReasoning?: AgentEventCallback;
  onContent?: AgentEventCallback;
  onToolCall?: AgentEventCallback;
  /** The `result` field is agent-defined; the SDK does not parse it. */
  onToolResult?: AgentEventCallback;
  onError?: AgentEventCallback;
}

/**
 * Options for MobileUseAgent executeTask/executeTaskAndWait.
 */
export interface MobileTaskOptions extends AgentStreamingOptions {
  maxSteps?: number;
  onCallForUser?: (event: AgentEvent) => Promise<string>;
}

/**
 * Handle for a task started via executeTask. Call wait() to block until completion.
 */
export class TaskExecution {
  readonly taskId: string;
  private _resultPromise: Promise<ExecutionResult>;
  private _cancelFn?: () => void;

  constructor(
    taskId: string,
    resultPromise: Promise<ExecutionResult>,
    cancelFn?: () => void
  ) {
    this.taskId = taskId;
    this._resultPromise = resultPromise;
    this._cancelFn = cancelFn;
  }

  async wait(timeout?: number): Promise<ExecutionResult> {
    if (timeout) {
      let timerId: ReturnType<typeof setTimeout>;
      const timer = new Promise<ExecutionResult>((resolve) => {
        timerId = setTimeout(() => {
          if (this._cancelFn) {
            try {
              this._cancelFn();
            } catch {
              /* ignore cancel errors */
            }
          }
          resolve({
            success: false,
            errorMessage: `Task execution timed out after ${timeout} seconds.`,
            taskId: this.taskId,
            taskStatus: "failed",
            taskResult: "Task execution timed out.",
          });
        }, timeout * 1000);
      });
      return Promise.race([this._resultPromise, timer]).finally(() =>
        clearTimeout(timerId)
      );
    }
    return this._resultPromise;
  }
}

/**
 * Base class for task execution agents.
 * Provides common functionality for ComputerUseAgent and BrowserUseAgent.
 *
 * > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
 */
abstract class BaseTaskAgent {
  protected session: McpSession;
  protected abstract toolPrefix: string;

  constructor(session: McpSession) {
    this.session = session;
  }

  /**
   * Get the full MCP tool name based on prefix and action.
   */
  protected getToolName(action: string): string {
    const toolMap: Record<string, string> = {
      execute: "execute_task",
      get_status: "get_task_status",
      terminate: "terminate_task",
    };
    const baseName = toolMap[action] || action;
    if (this.toolPrefix) {
      return `${this.toolPrefix}_${baseName}`;
    }
    return baseName;
  }

  /**
   * Check if any streaming option is provided.
   */
  protected hasStreamingParams(
    options?: AgentStreamingOptions | MobileTaskOptions
  ): boolean {
    if (!options) return false;
    return !!(
      options.onReasoning ||
      options.onContent ||
      options.onToolCall ||
      options.onToolResult ||
      options.onError ||
      (options as MobileTaskOptions).onCallForUser
    );
  }

  /**
   * Resolve the WS target for this agent from MCP tools list.
   */
  protected resolveAgentTarget(): string {
    const executeToolName = this.getToolName("execute");
    const sessionWithTools = this.session as McpSession & {
      mcpTools?: Array<{ name?: string; server?: string }>;
    };
    for (const tool of sessionWithTools.mcpTools || []) {
      if (tool?.name === executeToolName && tool?.server) {
        return tool.server;
      }
    }
    if (this.toolPrefix === "browser_use") {
      return "wuying_browseruse";
    }
    if (this.toolPrefix === "flux") {
      return "wuying_computer_agent";
    }
    return "wuying_mobile_agent";
  }

  /**
   * Start a task via WebSocket streaming channel. Returns handle and context
   * immediately without blocking. Use handle.waitEnd() to await completion.
   */
  protected async startTaskStreamWs(params: {
    taskParams: Record<string, any>;
    options?: AgentStreamingOptions | MobileTaskOptions;
  }): Promise<{
    handle: {
      waitEnd: () => Promise<any>;
      cancel: () => Promise<void>;
      write: (data: Record<string, any>) => Promise<void>;
      invocationId: string;
    };
    context: {
      finalContentParts: string[];
      lastError: Record<string, any> | undefined;
      errors: Error[];
    };
  }> {
    const { taskParams, options } = params;
    const sessionWithWs = this.session as McpSession & {
      getWsClient?: () => Promise<{
        callStream: (p: any) => Promise<{
          waitEnd: () => Promise<any>;
          cancel: () => Promise<void>;
          write: (data: Record<string, any>) => Promise<void>;
          invocationId: string;
        }>;
      }>;
    };
    if (!sessionWithWs.getWsClient) {
      throw new Error("WS streaming is not available in this session");
    }

    const wsClient = await sessionWithWs.getWsClient();
    const target = this.resolveAgentTarget();

    const finalContentParts: string[] = [];
    let lastError: Record<string, any> | undefined;
    const errors: Error[] = [];
    const handleRef: {
      current: { write: (data: Record<string, any>) => Promise<void> } | null;
    } = { current: null };

    const dispatchEvent = (event: AgentEvent): void => {
      const cb = {
        reasoning: options?.onReasoning,
        content: options?.onContent,
        tool_call: options?.onToolCall,
        tool_result: options?.onToolResult,
        error: options?.onError,
      }[event.type];
      if (cb) {
        try {
          cb(event);
        } catch (ex) {
          logWarn(`on_${event.type} callback error: ${ex}`);
        }
      }
    };

    const handle = await wsClient.callStream({
      target,
      data: {
        method: "exec_task",
        params: taskParams,
      },
      onEvent: (_invocationId: string, data: any) => {
        const eventType = data?.eventType ?? "";
        const seq = data?.seq ?? 0;
        const round = data?.round ?? 0;

        if (eventType === "reasoning") {
          dispatchEvent({
            type: "reasoning",
            seq,
            round,
            content: data?.content ?? "",
          });
        } else if (eventType === "content") {
          const contentText = data?.content ?? "";
          finalContentParts.push(contentText);
          dispatchEvent({ type: "content", seq, round, content: contentText });
        } else if (eventType === "tool_call") {
          const toolName = String(data?.toolName ?? "");
          const args = (data?.args as Record<string, any>) ?? {};
          const evt: AgentEvent = {
            type: "tool_call",
            seq,
            round,
            toolCallId: String(data?.toolCallId ?? ""),
            toolName,
            args,
            prompt:
              toolName === "call_for_user" ? args?.prompt ?? "" : undefined,
            content:
              toolName === "call_for_user" ? args?.prompt ?? "" : undefined,
          };
          dispatchEvent(evt);
          if (toolName === "call_for_user") {
            (async () => {
              let response = "";
              const onCb = (options as MobileTaskOptions)?.onCallForUser;
              if (onCb) {
                try {
                  response = (await onCb(evt)) ?? "";
                } catch (e) {
                  logWarn(`onCallForUser callback error: ${e}`);
                }
              } else {
                logWarn(
                  "Received call_for_user but no onCallForUser callback is set, sending empty response"
                );
              }
              if (handleRef.current) {
                try {
                  await handleRef.current.write({
                    method: "resume_task",
                    params: {
                      toolCallId: evt.toolCallId,
                      response: response || "",
                    },
                  });
                } catch (e) {
                  logWarn(`Failed to send resume_task: ${e}`);
                }
              }
            })();
          }
        } else if (eventType === "tool_result") {
          dispatchEvent({
            type: "tool_result",
            seq,
            round,
            toolCallId: data?.toolCallId ?? "",
            toolName: data?.toolName ?? "",
            result: data?.result ?? {},
          });
        } else if (eventType === "error") {
          lastError = data?.error ?? data;
          dispatchEvent({
            type: "error",
            seq,
            round,
            error: lastError,
          });
        }
      },
      onError: (_invocationId: string, err: Error) => {
        errors.push(err);
      },
    });

    handleRef.current = handle;

    return {
      handle,
      context: { finalContentParts, lastError, errors },
    };
  }

  /**
   * Execute a task via WebSocket streaming channel.
   */
  protected async executeTaskStreamWs(params: {
    taskParams: Record<string, any>;
    timeout: number;
    options?: AgentStreamingOptions | MobileTaskOptions;
  }): Promise<ExecutionResult> {
    const { taskParams, timeout, options } = params;
    const sessionWithWs = this.session as McpSession & {
      getWsClient?: () => Promise<{
        callStream: (p: any) => Promise<{
          waitEnd: () => Promise<any>;
          cancel: () => Promise<void>;
          write: (data: Record<string, any>) => Promise<void>;
          invocationId: string;
        }>;
      }>;
    };
    if (!sessionWithWs.getWsClient) {
      return {
        requestId: "",
        success: false,
        errorMessage: "WS streaming is not available in this session",
        taskStatus: "failed",
        taskId: "",
        taskResult: "WS streaming is not available.",
      };
    }

    let handle: {
      waitEnd: () => Promise<any>;
      cancel: () => Promise<void>;
      write: (data: Record<string, any>) => Promise<void>;
      invocationId: string;
    };
    let context: {
      finalContentParts: string[];
      lastError: Record<string, any> | undefined;
      errors: Error[];
    };
    try {
      const result = await this.startTaskStreamWs({ taskParams, options });
      handle = result.handle;
      context = result.context;
    } catch (e: any) {
      return {
        requestId: "",
        success: false,
        errorMessage: e instanceof Error ? e.message : String(e),
        taskStatus: "failed",
        taskId: "",
        taskResult: "WS streaming is not available.",
      };
    }

    const { finalContentParts, lastError, errors } = context;
    let endData: any = {};
    try {
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(
          () =>
            reject(
              new Error(`Task execution timed out after ${timeout} seconds.`)
            ),
          timeout * 1000
        )
      );
      endData = await Promise.race([handle.waitEnd(), timeoutPromise]);
    } catch (e: any) {
      try {
        await handle.cancel();
      } catch (_cancelErr) {
        // ignore
      }
      const msg = e instanceof Error ? e.message : String(e);
      return {
        requestId: handle.invocationId,
        success: false,
        errorMessage: msg,
        taskStatus: "timeout",
        taskId: "",
        taskResult: finalContentParts.join("") || msg,
      };
    }

    if (errors.length > 0) {
      return {
        requestId: handle.invocationId,
        success: false,
        errorMessage: String(errors[0]),
        taskStatus: "failed",
        taskId: "",
        taskResult: finalContentParts.join(""),
      };
    }

    if (lastError) {
      return {
        requestId: handle.invocationId,
        success: false,
        errorMessage: String(lastError),
        taskStatus: "failed",
        taskId: "",
        taskResult: finalContentParts.join(""),
      };
    }

    const status = endData?.status ?? "finished";
    const taskResult = endData?.taskResult ?? finalContentParts.join("");

    return {
      requestId: handle.invocationId,
      success: status === "finished",
      errorMessage:
        status === "finished" ? "" : `Task ended with status: ${status}`,
      taskStatus: status,
      taskId: "",
      taskResult,
    };
  }

  /**
   * Execute a specific task described in human language.
   * Note: MobileUseAgent overrides this to return TaskExecution instead.
   */
  async executeTask(task: string): Promise<ExecutionResult> {
    try {
      const args = { task };
      const result = await this.session.callMcpTool(
        this.getToolName("execute"),
        args,
        false
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Task Failed",
        };
      }

      // Parse task ID from response
      let content: Record<string, any>;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Invalid execution response.",
        };
      }

      const taskId = content.task_id || "";
      if (!taskId) {
        // 从后端返回的content中提取error信息
        const errorMessage = content.error || "Task ID not found in response";
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: errorMessage,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Invalid task ID.",
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        errorMessage: "",
        taskId: taskId,
        taskStatus: "running",
        taskResult: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to execute: ${error}`,
        taskStatus: "failed",
        taskId: "",
        taskResult: "Task Failed",
      };
    }
  }

  /**
   * Execute a specific task described in human language synchronously.
   * This is a synchronous interface that blocks until the task is completed or
   * an error occurs, or timeout happens. The default polling interval is 3 seconds.
   */
  async executeTaskAndWait(
    task: string,
    timeout: number
  ): Promise<ExecutionResult> {
    const result = await this.executeTask(task);
    if (!result.success) {
      return result;
    }

    const taskId = result.taskId;
    const pollInterval = 3;
    const maxPollAttempts = Math.floor(timeout / pollInterval);
    let triedTime = 0;

    while (triedTime < maxPollAttempts) {
      const query = await this.getTaskStatus(taskId);
      if (!query.success) {
        return {
          requestId: query.requestId,
          success: false,
          errorMessage: query.errorMessage,
          taskStatus: "failed",
          taskId: taskId,
          taskResult: "",
        };
      }

      switch (query.taskStatus) {
        case "finished":
          return {
            requestId: query.requestId,
            success: true,
            errorMessage: "",
            taskId: taskId,
            taskStatus: "finished",
            taskResult: query.taskProduct,
          };
        case "failed":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || "Failed to execute task.",
            taskId: taskId,
            taskStatus: "failed",
            taskResult: "",
          };
        case "unsupported":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || "Unsupported task.",
            taskId: taskId,
            taskStatus: "unsupported",
            taskResult: "",
          };
      }

      logDebug(`Task ${taskId} is still running, please wait for a while.`);
      await new Promise((resolve) => setTimeout(resolve, pollInterval * 1000));
      triedTime++;
    }

    try {
      const terminateResult = await this.terminateTask(taskId);
      if (terminateResult.success) {
        logDebug(`✅ Terminate request sent for task ${taskId} after timeout`);
      } else {
        logDebug(
          `⚠️ Failed to terminate task ${taskId} after timeout: ${terminateResult.errorMessage}`
        );
      }
    } catch (e) {
      logDebug(
        `⚠️ Exception while terminating task ${taskId} after timeout: ${e}`
      );
    }

    logDebug(`⏳ Waiting for task ${taskId} to be fully terminated...`);
    const terminatePollInterval = 1;
    const maxTerminatePollAttempts = 30;
    let terminateTriedTime = 0;
    let taskTerminatedConfirmed = false;

    while (terminateTriedTime < maxTerminatePollAttempts) {
      try {
        const statusQuery = await this.getTaskStatus(taskId);
        if (!statusQuery.success) {
          const errorMsg = statusQuery.errorMessage || "";
          if (errorMsg.startsWith("Task not found or already finished")) {
            logDebug(
              `✅ Task ${taskId} confirmed terminated (not found or finished)`
            );
            taskTerminatedConfirmed = true;
            break;
          }
        }
        await new Promise((resolve) =>
          setTimeout(resolve, terminatePollInterval * 1000)
        );
        terminateTriedTime++;
      } catch (e) {
        logDebug(
          `⚠️ Exception while polling task status during termination: ${e}`
        );
        await new Promise((resolve) =>
          setTimeout(resolve, terminatePollInterval * 1000)
        );
        terminateTriedTime++;
      }
    }

    if (!taskTerminatedConfirmed) {
      logDebug(`⚠️ Timeout waiting for task ${taskId} to be fully terminated`);
    }

    const timeoutErrorMsg = `Task execution timed out after ${timeout} seconds. Task ID: ${taskId}. Polled ${triedTime} times (max: ${maxPollAttempts}).`;
    return {
      requestId: result.requestId,
      success: false,
      errorMessage: timeoutErrorMsg,
      taskStatus: "timeout",
      taskId: taskId,
      taskResult: `Task execution timed out after ${timeout} seconds.`,
    };
  }

  /**
   * Get the status of the task with the given task ID.
   */
  async getTaskStatus(taskId: string): Promise<QueryResult> {
    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool(
        this.getToolName("get_status"),
        args,
        false
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskId: taskId,
          taskAction: "",
          taskProduct: "",
          taskStatus: "failed",
        };
      }
      let queryResult: Record<string, any>;
      try {
        queryResult = JSON.parse(result.data);
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: "",
          taskId: queryResult.task_id || taskId,
          taskAction: queryResult.action || "",
          taskProduct: queryResult.product || "",
          taskStatus: queryResult.status || "finished",
        };
      } catch (error) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to get task status: ${error}`,
          taskId: taskId,
          taskAction: "",
          taskProduct: "",
          taskStatus: "failed",
        };
      }
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to get task status: ${error}`,
        taskId: taskId,
        taskAction: "",
        taskProduct: "",
        taskStatus: "failed",
      };
    }
  }

  /**
   * Terminate a task with a specified task ID.
   */
  async terminateTask(taskId: string): Promise<ExecutionResult> {
    logDebug("Terminating task");

    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool(
        this.getToolName("terminate"),
        args,
        false
      );

      let content: Record<string, any>;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskId,
          taskStatus: "failed",
          taskResult: "",
        };
      }

      const terminatedTaskId = content.task_id || taskId;
      const status = content.status || "finished";

      if (result.success) {
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: "",
          taskId: terminatedTaskId,
          taskStatus: status,
          taskResult: "",
        };
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: result.errorMessage,
        taskId: terminatedTaskId,
        taskStatus: status,
        taskResult: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to terminate: ${error}`,
        taskId,
        taskStatus: "failed",
        taskResult: "",
      };
    }
  }
}

/**
 * An Agent to perform tasks on the computer.
 */
export class ComputerUseAgent extends BaseTaskAgent {
  protected toolPrefix = "flux";
}

export class BrowserUseAgent extends BaseTaskAgent {
  protected toolPrefix = "browser_use";
  private initialized = false;

  /**
   * Initialize the browser on which the agent performs tasks.
   * You are supposed to call this API before executeTask is called, but it's optional.
   * If you want to perform a hybrid usage of browser, you must call this API before executeTask is called.
   *
   * @param option - Browser configuration options. If not provided, default options will be used.
   * @returns Promise<boolean> - True if the browser is successfully initialized, False otherwise.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create({ imageId: 'browser_latest' });
   * if (result.success) {
   *   const success = await result.session.agent.browser.initialize();
   *   console.log('Browser initialized:', success);
   *   await result.session.delete();
   * }
   * ```
   */
  async initialize(option?: BrowserOption): Promise<boolean> {
    if (this.initialized) {
      return true;
    }

    if (!option) {
      option = {};
    }

    try {
      // Access browser through session - assuming session has a browser property
      const success = await (this.session as any).browser.initializeAsync(
        option
      );
      this.initialized = success;
      return success;
    } catch (error) {
      logWarn(`Failed to initialize browser: ${error}`);
      return false;
    }
  }

  /**
   * Execute a task described in human language on a browser without waiting for completion
   * (non-blocking). This is a fire-and-return interface that immediately
   * provides a task ID. Call getTaskStatus to check the task status.
   *
   * @param task - Task description in human language.
   * @param use_vision - Whether to use vision in the task.
   * @param output_schema - Optional Zod schema for a structured task output if you need.
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const WeatherSchema = z.object({city: z.string(), weather:z.string()});
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'linux_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.browser.executeTask(
   *     'Query the weather in Shanghai', false, WeatherSchema
   *   );
   *   console.log(`Task ID: ${execResult.taskId}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTask<TSchema extends ZodTypeAny>(
    task: string,
    use_vision = true,
    output_schema?: TSchema
  ): Promise<ExecutionResult> {
    if (!this.initialized) {
      logInfo("Browser is not initialized, initializing browser!");
      const success = await this.initialize();
      if (!success) {
        logWarn("Browser initialization failed!");
        return {
          requestId: "",
          success: false,
          errorMessage: "Browser initialization failed",
          taskStatus: "failed",
          taskId: "",
          taskResult: "Browser initialization failed",
        };
      }
    }
    try {
      let json_schema = null;
      if (output_schema !== undefined) {
        json_schema = zodToJsonSchema(output_schema, {
          $refStrategy: "none",
        });
      } else {
        json_schema = zodToJsonSchema(DefaultSchema, {
          $refStrategy: "none",
        });
      }

      const args: any = {
        task,
        use_vision: use_vision,
        output_schema: JSON.stringify(json_schema),
      };
      const result = await this.session.callMcpTool(
        this.getToolName("execute"),
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Task Failed",
        };
      }

      // Parse task ID from response
      let content: any;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Invalid execution response.",
        };
      }

      const taskId = content.task_id || "";
      if (!taskId) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: "Task ID not found in response",
          taskStatus: "failed",
          taskId: "",
          taskResult: "Invalid task ID.",
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        errorMessage: "",
        taskId: taskId,
        taskStatus: "running",
        taskResult: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to execute: ${error}`,
        taskStatus: "failed",
        taskId: "",
        taskResult: "Task Failed",
      };
    }
  }

  /**
   * Execute a task described in human language on a browser synchronously.
   * This is a synchronous interface that blocks until the task is completed or
   * an error occurs, or timeout happens. The default polling interval is 3 seconds.
   *
   * @param task - Task description in human language.
   * @param timeout - Maximum time to wait for task completion (in seconds). Used to control how long to wait for task completion.
   * @param use_vision - Whether to use vision in the task.
   * @param output_schema - Optional Zod schema for a structured task output if you need.
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const WeatherSchema = z.object({city: z.string(), weather:z.string()});
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'linux_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.browser.executeTask(
   *     'Query the weather in Shanghai', false, WeatherSchema
   *   );
   *   console.log(`Task ID: ${execResult.taskId}`);
   *   const pollInterval = 3;
   *   const timeout = 180;
   *   const maxPollAttempts = Math.floor(timeout / pollInterval);
   *   let triedTime = 0;
   *   while(triedTime < maxPollAttempts) {
   *     const queryResult = await result.session.agent.browser.getTaskStatus(execResult.taskId);
   *     if (queryResult.taskStatus === 'finished') {
   *       console.log(`Task ${execResult.taskId} finished with result: ${queryResult.taskResult}`);
   *       break;
   *     }
   *     triedTime++;
   *   }
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTaskAndWait<TSchema extends ZodTypeAny>(
    task: string,
    timeout: number,
    use_vision?: boolean,
    output_schema?: TSchema
  ): Promise<ExecutionResult> {
    const use_vision_resolved = use_vision === undefined ? true : use_vision;

    if (!this.initialized) {
      logInfo("Browser is not initialized, initializing browser!");
      const success = await this.initialize();
      if (!success) {
        logWarn("Browser initialization failed!");
        return {
          requestId: "",
          success: false,
          errorMessage: "Browser initialization failed",
          taskStatus: "failed",
          taskId: "",
          taskResult: "Browser initialization failed",
        };
      }
    }

    const result = await this.executeTask(
      task,
      use_vision_resolved,
      output_schema
    );
    if (!result.success) {
      return result;
    }

    const taskId = result.taskId;
    const pollInterval = 3;
    const maxPollAttempts = Math.floor(timeout / pollInterval);
    let triedTime = 0;

    while (triedTime < maxPollAttempts) {
      const query = await this.getTaskStatus(taskId);
      if (!query.success) {
        return {
          requestId: query.requestId,
          success: false,
          errorMessage: query.errorMessage,
          taskStatus: "failed",
          taskId: taskId,
          taskResult: "",
        };
      }

      switch (query.taskStatus) {
        case "finished":
          return {
            requestId: query.requestId,
            success: true,
            errorMessage: "",
            taskId: taskId,
            taskStatus: "finished",
            taskResult: query.taskProduct,
          };
        case "failed":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || "Failed to execute task.",
            taskId: taskId,
            taskStatus: "failed",
            taskResult: "",
          };
        case "unsupported":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || "Unsupported task.",
            taskId: taskId,
            taskStatus: "unsupported",
            taskResult: "",
          };
      }

      logDebug(`Task ${taskId} is still running, please wait for a while.`);
      await new Promise((resolve) => setTimeout(resolve, pollInterval * 1000));
      triedTime++;
    }

    // Automatically terminate the task on timeout
    try {
      const terminateResult = await this.terminateTask(taskId);
      if (terminateResult.success) {
        logDebug(`✅ Task ${taskId} terminated successfully after timeout`);
      } else {
        logDebug(
          `⚠️ Failed to terminate task ${taskId} after timeout: ${terminateResult.errorMessage}`
        );
      }
    } catch (e) {
      logDebug(
        `⚠️ Exception while terminating task ${taskId} after timeout: ${e}`
      );
    }

    const timeoutErrorMsg = `Task execution timed out after ${timeout} seconds. Task ID: ${taskId}. Polled ${triedTime} times (max: ${maxPollAttempts}).`;
    return {
      requestId: result.requestId,
      success: false,
      errorMessage: timeoutErrorMsg,
      taskStatus: "timeout",
      taskId: taskId,
      taskResult: `Task execution timed out after ${timeout} seconds.`,
    };
  }
}

/**
 * An Agent to perform tasks on mobile devices.
 */
export class MobileUseAgent extends BaseTaskAgent {
  protected toolPrefix = "";

  /**
   * Poll task status until completion or timeout.
   */
  private async _pollTaskUntilComplete(
    taskId: string,
    requestId: string,
    timeout: number
  ): Promise<ExecutionResult> {
    const pollInterval = 3;
    const maxPollAttempts = Math.floor(timeout / pollInterval);
    let triedTime = 0;
    const processedTimestamps = new Set<number>();
    let lastQuery: QueryResult | null = null;

    while (triedTime < maxPollAttempts) {
      const query = await this.getTaskStatus(taskId);
      if (!query.success) {
        return {
          requestId: query.requestId,
          success: false,
          errorMessage: query.errorMessage,
          taskStatus: "failed",
          taskId: taskId,
          taskResult: "",
        };
      }

      if (query.stream && query.stream.length > 0) {
        lastQuery = query;
      }

      if (query.stream) {
        for (const streamItem of query.stream) {
          const timestamp = streamItem.timestamp_ms;
          if (timestamp !== undefined && !processedTimestamps.has(timestamp)) {
            processedTimestamps.add(timestamp);
            const content = streamItem.content || "";
            if (content) {
              process.stdout.write(content);
            }
          }
        }
      }

      switch (query.taskStatus) {
        case "completed":
          return {
            requestId: query.requestId,
            success: true,
            errorMessage: "",
            taskId: taskId,
            taskStatus: "completed",
            taskResult: query.taskProduct,
          };
        case "failed":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage:
              query.error || query.errorMessage || "Failed to execute task.",
            taskId: taskId,
            taskStatus: "failed",
            taskResult: "",
          };
        case "cancelled":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage:
              query.error || query.errorMessage || "Task was cancelled.",
            taskId: taskId,
            taskStatus: "cancelled",
            taskResult: "",
          };
        case "unsupported":
          return {
            requestId: query.requestId,
            success: false,
            errorMessage:
              query.error || query.errorMessage || "Unsupported task.",
            taskId: taskId,
            taskStatus: "unsupported",
            taskResult: "",
          };
      }

      logDebug(`⏳ Task ${taskId} running 🚀: ${query.taskAction}.`);
      await new Promise((resolve) => setTimeout(resolve, 3000));
      triedTime++;
    }

    logDebug("⚠️ task execution timeout!");
    try {
      const terminateResult = await this.terminateTask(taskId);
      if (terminateResult.success) {
        logDebug(`✅ Terminate request sent for task ${taskId} after timeout`);
      } else {
        logDebug(
          `⚠️ Failed to terminate task ${taskId} after timeout: ${terminateResult.errorMessage}`
        );
      }
    } catch (e) {
      logDebug(
        `⚠️ Exception while terminating task ${taskId} after timeout: ${e}`
      );
    }

    logDebug(`⏳ Waiting for task ${taskId} to be fully terminated...`);
    const terminatePollInterval = 1;
    const maxTerminatePollAttempts = 30;
    let terminateTriedTime = 0;
    let taskTerminatedConfirmed = false;

    while (terminateTriedTime < maxTerminatePollAttempts) {
      try {
        const statusQuery = await this.getTaskStatus(taskId);
        if (!statusQuery.success) {
          const errorMsg = statusQuery.errorMessage || "";
          if (errorMsg.startsWith("Task not found or already finished")) {
            logDebug(
              `✅ Task ${taskId} confirmed terminated (not found or finished)`
            );
            taskTerminatedConfirmed = true;
            break;
          }
        }
        await new Promise((resolve) =>
          setTimeout(resolve, terminatePollInterval * 1000)
        );
        terminateTriedTime++;
      } catch (e) {
        logDebug(
          `⚠️ Exception while polling task status during termination: ${e}`
        );
        await new Promise((resolve) =>
          setTimeout(resolve, terminatePollInterval * 1000)
        );
        terminateTriedTime++;
      }
    }

    if (!taskTerminatedConfirmed) {
      logDebug(`⚠️ Timeout waiting for task ${taskId} to be fully terminated`);
    }

    const timeoutErrorMsg = `Task execution timed out after ${timeout} seconds. Task ID: ${taskId}. Polled ${triedTime} times (max: ${maxPollAttempts}).`;
    const taskResultParts: string[] = [
      `Task execution timed out after ${timeout} seconds.`,
    ];

    if (lastQuery) {
      if (lastQuery.stream && lastQuery.stream.length > 0) {
        const streamContentParts: string[] = [];
        for (const streamItem of lastQuery.stream) {
          if (streamItem.content) {
            streamContentParts.push(streamItem.content);
          }
        }
        if (streamContentParts.length > 0) {
          taskResultParts.push(
            `Last task status output: ${streamContentParts.join("")}`
          );
        }
      }
      if (lastQuery.taskAction) {
        taskResultParts.push(`Last action: ${lastQuery.taskAction}`);
      }
      if (lastQuery.taskProduct) {
        taskResultParts.push(`Last result: ${lastQuery.taskProduct}`);
      }
      if (lastQuery.error) {
        taskResultParts.push(`Last error: ${lastQuery.error}`);
      }
      if (lastQuery.taskStatus) {
        taskResultParts.push(`Last status: ${lastQuery.taskStatus}`);
      }
    }

    return {
      requestId,
      success: false,
      errorMessage: timeoutErrorMsg,
      taskStatus: "failed",
      taskId: taskId,
      taskResult: taskResultParts.join(" | "),
    };
  }

  /**
   * Execute a task in human language without waiting for completion
   * (non-blocking). Returns TaskExecution; call wait() to block until done.
   *
   * @param task - Task description in human language.
   * @param options - Optional MobileTaskOptions (maxSteps, streaming callbacks).
   * @returns TaskExecution with taskId and wait() method.
   */
  // @ts-expect-error MobileUseAgent returns TaskExecution; base returns ExecutionResult
  async executeTask(
    task: string,
    options?: MobileTaskOptions
  ): Promise<TaskExecution> {
    const maxSteps = options?.maxSteps ?? 50;

    if (this.hasStreamingParams(options)) {
      const sessionWithWs = this.session as McpSession & {
        getWsClient?: () => Promise<{
          callStream: (p: any) => Promise<{
            waitEnd: () => Promise<any>;
            cancel: () => Promise<void>;
            write: (data: Record<string, any>) => Promise<void>;
            invocationId: string;
          }>;
        }>;
      };
      if (!sessionWithWs.getWsClient) {
        return new TaskExecution(
          "",
          Promise.resolve({
            requestId: "",
            success: false,
            errorMessage: "WS streaming is not available in this session",
            taskStatus: "failed",
            taskId: "",
            taskResult: "WS streaming is not available.",
          })
        );
      }

      const { handle, context } = await this.startTaskStreamWs({
        taskParams: { task, max_steps: maxSteps },
        options,
      });
      const resultPromise = (async (): Promise<ExecutionResult> => {
        const { finalContentParts, lastError, errors } = context;
        let endData: any = {};
        try {
          endData = await handle.waitEnd();
        } catch (e: any) {
          try {
            await handle.cancel();
          } catch (_cancelErr) {
            // ignore
          }
          const msg = e instanceof Error ? e.message : String(e);
          return {
            requestId: handle.invocationId,
            success: false,
            errorMessage: msg,
            taskStatus: "timeout",
            taskId: "",
            taskResult: finalContentParts.join("") || msg,
          };
        }

        if (errors.length > 0) {
          return {
            requestId: handle.invocationId,
            success: false,
            errorMessage: String(errors[0]),
            taskStatus: "failed",
            taskId: "",
            taskResult: finalContentParts.join(""),
          };
        }

        if (lastError) {
          return {
            requestId: handle.invocationId,
            success: false,
            errorMessage: String(lastError),
            taskStatus: "failed",
            taskId: "",
            taskResult: finalContentParts.join(""),
          };
        }

        const status = endData?.status ?? "finished";
        const taskResult = endData?.taskResult ?? finalContentParts.join("");
        return {
          requestId: handle.invocationId,
          success: status === "finished",
          errorMessage:
            status === "finished" ? "" : `Task ended with status: ${status}`,
          taskStatus: status,
          taskId: "",
          taskResult,
        };
      })();

      return new TaskExecution(handle.invocationId, resultPromise, () =>
        handle.cancel()
      );
    }

    const args = { task, max_steps: maxSteps };
    try {
      const result = await this.session.callMcpTool(
        this.getToolName("execute"),
        args
      );

      if (!result.success) {
        return new TaskExecution(
          "",
          Promise.resolve({
            requestId: result.requestId,
            success: false,
            errorMessage: result.errorMessage || "Failed to execute task",
            taskStatus: "failed",
            taskId: "",
            taskResult: "Task Failed",
          })
        );
      }

      let content: Record<string, any>;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return new TaskExecution(
          "",
          Promise.resolve({
            requestId: result.requestId,
            success: false,
            errorMessage: `Failed to parse response: ${err}`,
            taskStatus: "failed",
            taskId: "",
            taskResult: "Invalid execution response.",
          })
        );
      }

      const taskId = content.taskId || content.task_id;
      if (!taskId) {
        const errorMessage = content.error || "Task ID not found in response";
        return new TaskExecution(
          "",
          Promise.resolve({
            requestId: result.requestId,
            success: false,
            errorMessage: errorMessage,
            taskStatus: "failed",
            taskId: "",
            taskResult: "Invalid task ID.",
          })
        );
      }

      const resultPromise = this._pollTaskUntilComplete(
        taskId,
        result.requestId,
        86400
      );
      return new TaskExecution(taskId, resultPromise);
    } catch (error) {
      return new TaskExecution(
        "",
        Promise.resolve({
          requestId: "",
          success: false,
          errorMessage: `Failed to execute: ${error}`,
          taskStatus: "failed",
          taskId: "",
          taskResult: "Task Failed",
        })
      );
    }
  }

  /**
   * Execute a task described in human language synchronously.
   * Blocks until the task is completed, an error occurs, or timeout.
   *
   * @param task - Task description in human language.
   * @param timeout - Maximum time to wait for task completion (in seconds).
   * @param options - Optional MobileTaskOptions (maxSteps, streaming callbacks).
   * @returns ExecutionResult containing success status, task ID, task status.
   */
  async executeTaskAndWait(
    task: string,
    timeout: number,
    options?: MobileTaskOptions
  ): Promise<ExecutionResult> {
    try {
      const execution = await this.executeTask(task, options);
      return await execution.wait(timeout);
    } catch (e: any) {
      return {
        requestId: "",
        success: false,
        errorMessage: e instanceof Error ? e.message : String(e),
        taskStatus: "failed",
        taskId: "",
        taskResult: "Task Failed",
      };
    }
  }

  /**
   * Get the status of the task with the given task ID.
   */
  async getTaskStatus(taskId: string): Promise<QueryResult> {
    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool(
        this.getToolName("get_status"),
        args
      );

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskId: taskId,
          taskAction: "",
          taskProduct: "",
          taskStatus: "failed",
        };
      }
      let queryResult: Record<string, any>;
      try {
        queryResult = JSON.parse(result.data);
        const contentTaskId =
          queryResult.taskId || queryResult.task_id || taskId;
        const taskProduct = queryResult.result || queryResult.product || "";
        const stream = Array.isArray(queryResult.stream)
          ? queryResult.stream
          : undefined;
        const error = queryResult.error || undefined;
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: "",
          taskId: contentTaskId,
          taskAction: queryResult.action || "",
          taskProduct: taskProduct,
          taskStatus: queryResult.status || "completed",
          stream: stream,
          error: error,
        };
      } catch (error) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to get task status: ${error}`,
          taskId: taskId,
          taskAction: "",
          taskProduct: "",
          taskStatus: "failed",
        };
      }
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to get task status: ${error}`,
        taskId: taskId,
        taskAction: "",
        taskProduct: "",
        taskStatus: "failed",
      };
    }
  }

  /**
   * Terminate a task with a specified task ID.
   */
  async terminateTask(taskId: string): Promise<ExecutionResult> {
    logDebug("Terminating task");

    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool(
        this.getToolName("terminate"),
        args
      );

      let content: Record<string, any>;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskId,
          taskStatus: "failed",
          taskResult: "",
        };
      }

      const terminatedTaskId = content.taskId || content.task_id || taskId;
      const status = content.status || "cancelling";

      if (result.success) {
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: "",
          taskId: terminatedTaskId,
          taskStatus: status,
          taskResult: "",
        };
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: result.errorMessage,
        taskId: terminatedTaskId,
        taskStatus: status,
        taskResult: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to terminate: ${error}`,
        taskId,
        taskStatus: "failed",
        taskResult: "",
      };
    }
  }
}

/**
 * An Agent to manipulate applications to complete specific tasks.
 * According to the use scenary, The agent can a browser use agent which is
 * specialized for browser automation tasks, The agent also can be  a computer
 * use agent which is specialized for multiple applications automation tasks.
 */
export class Agent {
  /**
   * An instance of Computer Use Agent.
   */
  public computer: ComputerUseAgent;
  /**
   * An instance of Browser Use Agent.
   */
  public browser: BrowserUseAgent;
  /**
   * An instance of Mobile Use Agent.
   */
  public mobile: MobileUseAgent;

  /**
   * Initialize an Agent object.
   *
   * @param session - The Session instance that this Agent belongs to.
   */
  constructor(session: McpSession) {
    this.computer = new ComputerUseAgent(session);
    this.browser = new BrowserUseAgent(session);
    this.mobile = new MobileUseAgent(session);
  }
}
