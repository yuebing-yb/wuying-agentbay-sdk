import {ApiResponse} from '../types/api-response';
import {log, logDebug} from '../utils/logger';

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
  stream?: Array<{content?: string; reasoning?: string; timestamp_ms?: number}>;
  error?: string;
}

/**
 * Result of agent initialization.
 */
export interface InitializationResult extends ApiResponse {
  success: boolean;
}

/**
 * Options for Agent initialization.

 */
export interface AgentOptions {
  use_vision: boolean;
  output_schema: '';
}

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
  callMcpTool(toolName: string, args: any): Promise<McpToolResult>;
}

/**
 * Base class for task execution agents.
 * Provides common functionality for ComputerUseAgent and BrowserUseAgent.
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
      execute: 'execute_task',
      get_status: 'get_task_status',
      terminate: 'terminate_task',
    };
    const baseName = toolMap[action] || action;
    if (this.toolPrefix) {
      return `${this.toolPrefix}_${baseName}`;
    }
    return baseName;
  }

  /**
   * Execute a specific task described in human language.
   */
  async executeTask(task: string, timeout?: number):
      Promise<ExecutionResult> {
    try {
      const args = {task};
      // If timeout is provided, use blocking version
      if (timeout !== undefined) {
        return this.executeTaskAndWait(task, timeout);
      }
      const result = await this.session.callMcpTool(
          this.getToolName('execute'), args);

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskStatus: 'failed',
          taskId: '',
          taskResult: 'Task Failed',
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
          taskStatus: 'failed',
          taskId: '',
          taskResult: 'Invalid execution response.',
        };
      }

      const taskId = content.task_id || '';
      if (!taskId) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: 'Task ID not found in response',
          taskStatus: 'failed',
          taskId: '',
          taskResult: 'Invalid task ID.',
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        errorMessage: '',
        taskId: taskId,
        taskStatus: 'running',
        taskResult: '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to execute: ${error}`,
        taskStatus: 'failed',
        taskId: '',
        taskResult: 'Task Failed',
      };
    }
  }

  /**
   * Execute a specific task described in human language synchronously.
   * This is a synchronous interface that blocks until the task is completed or
   * an error occurs, or timeout happens. The default polling interval is 3 seconds.
   */
  async executeTaskAndWait(task: string, timeout: number):
      Promise<ExecutionResult> {
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
            taskStatus: 'failed',
            taskId: taskId,
            taskResult: '',
          };
        }

        switch (query.taskStatus) {
          case 'finished':
            return {
              requestId: query.requestId,
              success: true,
              errorMessage: '',
              taskId: taskId,
              taskStatus: 'finished',
              taskResult: query.taskProduct,
            };
          case 'failed':
            return {
              requestId: query.requestId,
              success: false,
              errorMessage: query.errorMessage || 'Failed to execute task.',
              taskId: taskId,
              taskStatus: 'failed',
              taskResult: '',
            };
          case 'unsupported':
            return {
              requestId: query.requestId,
              success: false,
              errorMessage: query.errorMessage || 'Unsupported task.',
              taskId: taskId,
              taskStatus: 'unsupported',
              taskResult: '',
            };
        }

        logDebug(`Task ${taskId} is still running, please wait for a while.`);
      await new Promise((resolve) => setTimeout(resolve, pollInterval * 1000));
        triedTime++;
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: 'Task execution timed out',
        taskStatus: 'timeout',
        taskId: taskId,
        taskResult: 'Task Timed Out',
      };
  }

  /**
   * Get the status of the task with the given task ID.
   */
  async getTaskStatus(taskId: string): Promise<QueryResult> {
    try {
      const args = {task_id: taskId};
      const result = await this.session.callMcpTool(
          this.getToolName('get_status'), args);

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskId: taskId,
          taskAction: '',
          taskProduct: '',
          taskStatus: 'failed',
        };
      }
      let queryResult: any;
      try {
        queryResult = JSON.parse(result.data);
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: '',
          taskId: queryResult.task_id || taskId,
          taskAction: queryResult.action || '',
          taskProduct: queryResult.product || '',
          taskStatus: queryResult.status || 'finised',
        };
      } catch (error) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to get task status: ${error}`,
          taskId: taskId,
          taskAction: '',
          taskProduct: '',
          taskStatus: 'failed',
        };
      }
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to get task status: ${error}`,
        taskId: taskId,
        taskAction: '',
        taskProduct: '',
        taskStatus: 'failed',
      };
    }
  }

  /**
   * Terminate a task with a specified task ID.
   */
  async terminateTask(taskId: string): Promise<ExecutionResult> {
    logDebug('Terminating task');

    try {
      const args = {task_id: taskId};
      const result = await this.session.callMcpTool(
          this.getToolName('terminate'), args);

      let content: any;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskId,
          taskStatus: 'failed',
          taskResult: '',
        };
      }

      const terminatedTaskId = content.task_id || taskId;
      const status = content.status || 'finised';

      if (result.success) {
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: '',
          taskId: terminatedTaskId,
          taskStatus: status,
          taskResult: '',
        };
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: result.errorMessage,
        taskId: terminatedTaskId,
        taskStatus: status,
        taskResult: '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to terminate: ${error}`,
        taskId,
        taskStatus: 'failed',
        taskResult: '',
      };
    }
  }
}

/**
 * An Agent to perform tasks on the computer.
 */
export class ComputerUseAgent extends BaseTaskAgent {
  protected toolPrefix = 'flux';
}


export class BrowserUseAgent extends BaseTaskAgent {
  protected toolPrefix = 'browser_use';

  /**
   * Initialize the browser agent with specific options.
   * @param options - agent initialization options
   * @returns  InitializationResult containing success status, task output,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'linux_latest' });
   * if (result.success) {
   *   options:AgentOptions = new AgentOptions(use_vision=False,
   * output_schema=""); const initResult = await
   * result.session.agent.browser.initialize(options); console.log(`Initialize
   * success: ${initResult.success}`); await result.session.delete();
   * }
   * ```
   */
  async initialize(options: AgentOptions): Promise<InitializationResult> {
    const args = {
      use_vision: options.use_vision,
      output_schema: options.output_schema
    };
    try {
      const result =
          await this.session.callMcpTool('browser_use_initialize', args);
      if (!result.success) {
        return {
          success: false,
          errorMessage: result.errorMessage,
        };
      } else {
        return {
          success: true,
          errorMessage: '',
        };
      }
    } catch (error) {
      return {
        success: false,
        errorMessage: `Failed to initialize: ${error}`,
      };
    }
  }
}

/**
 * An Agent to perform tasks on mobile devices.
 */
export class MobileUseAgent extends BaseTaskAgent {
  protected toolPrefix = '';

  /**
   * Execute a task in human language without waiting for completion
   * (non-blocking). This is a fire-and-return interface that immediately
   * provides a task ID. Call getTaskStatus to check the task status.
   *
   * @param task - Task description in human language.
   * @param maxSteps - Maximum number of steps (clicks/swipes/etc.) allowed.
   *                   Used to prevent infinite loops or excessive resource
   *                   consumption. Default is 50.
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.mobile.executeTask(
   *     'Open WeChat app', 100
   *   );
   *   console.log(`Task ID: ${execResult.taskId}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTask(
      task: string,
      maxSteps: number = 50): Promise<ExecutionResult> {
    const args = {
      task,
      max_steps: maxSteps,
    };

      try {
        const result = await this.session.callMcpTool(
            this.getToolName('execute'), args);

      if (!result.success) {
        const errorMessage = result.errorMessage || 'Failed to execute task';
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: errorMessage,
          taskStatus: 'failed',
          taskId: '',
          taskResult: 'Task Failed',
        };
      }

          let content: any;
          try {
            content = JSON.parse(result.data);
          } catch (err) {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: `Failed to parse response: ${err}`,
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Invalid execution response.',
            };
          }

      const taskId = content.taskId || content.task_id;
          if (!taskId) {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: 'Task ID not found in response',
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Invalid task ID.',
            };
          }

          return {
            requestId: result.requestId,
            success: true,
            errorMessage: '',
            taskId: taskId,
            taskStatus: 'running',
            taskResult: '',
          };
      } catch (error) {
          return {
        requestId: '',
            success: false,
        errorMessage: `Failed to execute: ${error}`,
            taskStatus: 'failed',
            taskId: '',
            taskResult: 'Task Failed',
          };
        }
  }

  /**
   * Execute a specific task described in human language synchronously.
   * This is a synchronous interface that blocks until the task is completed or
   * an error occurs, or timeout happens. The default polling interval is
   * 3 seconds.
   *
   * @param task - Task description in human language.
   * @param timeout - Maximum time to wait for task completion (in seconds).
   *                  Used to control how long to wait for task completion.
   * @param maxSteps - Maximum number of steps (clicks/swipes/etc.) allowed.
   *                   Used to prevent infinite loops or excessive resource
   *                   consumption. Default is 50.
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.mobile.executeTaskAndWait(
   *     'Open WeChat app', 180, 100
   *   );
   *   console.log(`Task result: ${execResult.taskResult}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTaskAndWait(
      task: string,
      timeout: number,
      maxSteps: number = 50): Promise<ExecutionResult> {
    const args = {
      task,
      max_steps: maxSteps,
    };

        const result = await this.session.callMcpTool(
            this.getToolName('execute'), args);

    if (!result.success) {
      const errorMessage = result.errorMessage || 'Failed to execute task';
      return {
        requestId: result.requestId,
        success: false,
        errorMessage: errorMessage,
        taskStatus: 'failed',
        taskId: '',
        taskResult: 'Task Failed',
      };
    }

          let content: any;
          try {
            content = JSON.parse(result.data);
          } catch (err) {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: `Failed to parse response: ${err}`,
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Invalid execution response.',
            };
          }

    const taskId = content.taskId || content.task_id;
          if (!taskId) {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: 'Task ID not found in response',
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Invalid task ID.',
            };
          }

    const pollInterval = 3;
    const maxPollAttempts = Math.floor(timeout / pollInterval);
    let triedTime = 0;
    const processedTimestamps = new Set<number>(); // Track processed stream fragments by timestamp_ms
    while (triedTime < maxPollAttempts) {
      const query = await this.getTaskStatus(taskId);
      if (!query.success) {
        return {
          requestId: query.requestId,
          success: false,
          errorMessage: query.errorMessage,
          taskStatus: 'failed',
          taskId: taskId,
          taskResult: '',
        };
      }

      // Process new stream fragments for real-time output
      if (query.stream) {
        for (const streamItem of query.stream) {
          const timestamp = streamItem.timestamp_ms;
          // Use timestamp_ms to identify new fragments (handles backend returning snapshots)
          if (timestamp !== undefined && !processedTimestamps.has(timestamp)) {
            processedTimestamps.add(timestamp); // Mark as processed immediately
            
            // Output immediately for true streaming effect
            const content = streamItem.content || '';
            const reasoning = streamItem.reasoning || '';
            if (content) {
              // Use process.stdout.write for streaming output without automatic newlines
              process.stdout.write(content);
            }
            if (reasoning) {
              // Log reasoning at debug level if needed
              // logDebug(`💭 ${reasoning}`);
            }
          }
        }
      }

      // Check for error field
      if (query.error) {
        // Log error if needed
        // logWarning(`⚠️ Task error: ${query.error}`);
      }

      switch (query.taskStatus) {
        case 'completed':
          return {
            requestId: query.requestId,
            success: true,
            errorMessage: '',
            taskId: taskId,
            taskStatus: 'completed',
            taskResult: query.taskProduct,
          };
        case 'failed':
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || 'Failed to execute task.',
            taskId: taskId,
            taskStatus: 'failed',
            taskResult: '',
          };
        case 'cancelled':
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || 'Task was cancelled.',
            taskId: taskId,
            taskStatus: 'cancelled',
            taskResult: '',
          };
        case 'unsupported':
          return {
            requestId: query.requestId,
            success: false,
            errorMessage: query.errorMessage || 'Unsupported task.',
            taskId: taskId,
            taskStatus: 'unsupported',
            taskResult: '',
          };
      }

      logDebug(`⏳ Task ${taskId} running 🚀: ${query.taskAction}.`);
      await new Promise((resolve) => setTimeout(resolve, 3000));
      triedTime++;
    }

    logDebug('⚠️ task execution timeout!');
    return {
      requestId: result.requestId,
      success: false,
      errorMessage: 'Task timeout.',
      taskStatus: 'failed',
      taskId: taskId,
      taskResult: 'Task timeout.',
    };
  }

  /**
   * Get the status of the task with the given task ID.
   */
  async getTaskStatus(taskId: string): Promise<QueryResult> {
    try {
      const args = {task_id: taskId};
      const result = await this.session.callMcpTool(
          this.getToolName('get_status'), args);

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskId: taskId,
          taskAction: '',
          taskProduct: '',
          taskStatus: 'failed',
        };
      }
      let queryResult: any;
      try {
        queryResult = JSON.parse(result.data);
        const contentTaskId = queryResult.taskId || queryResult.task_id || taskId;
        const taskProduct = queryResult.result || queryResult.product || '';
        const stream = Array.isArray(queryResult.stream) ? queryResult.stream : undefined;
        const error = queryResult.error || undefined;
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: '',
          taskId: contentTaskId,
          taskAction: queryResult.action || '',
          taskProduct: taskProduct,
          taskStatus: queryResult.status || 'completed',
          stream: stream,
          error: error,
        };
      } catch (error) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to get task status: ${error}`,
          taskId: taskId,
          taskAction: '',
          taskProduct: '',
          taskStatus: 'failed',
        };
      }
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to get task status: ${error}`,
        taskId: taskId,
        taskAction: '',
        taskProduct: '',
        taskStatus: 'failed',
      };
    }
  }

  /**
   * Terminate a task with a specified task ID.
   */
  async terminateTask(taskId: string): Promise<ExecutionResult> {
    logDebug('Terminating task');

    try {
      const args = {task_id: taskId};
      const result = await this.session.callMcpTool(
          this.getToolName('terminate'), args);

      let content: any;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskId,
          taskStatus: 'failed',
          taskResult: '',
        };
      }

      const terminatedTaskId = content.taskId || content.task_id || taskId;
      const status = content.status || 'cancelling';

      if (result.success) {
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: '',
          taskId: terminatedTaskId,
          taskStatus: status,
          taskResult: '',
        };
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: result.errorMessage,
        taskId: terminatedTaskId,
        taskStatus: status,
        taskResult: '',
      };
    } catch (error) {
      return {
        requestId: '',
        success: false,
        errorMessage: `Failed to terminate: ${error}`,
        taskId,
        taskStatus: 'failed',
        taskResult: '',
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