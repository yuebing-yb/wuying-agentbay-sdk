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
  taskStatus: string;
  taskAction: string;
  taskProduct: string;
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
  async executeTask(task: string, maxTryTimes: number):
      Promise<ExecutionResult> {
    try {
      const args = {task, max_try_times: maxTryTimes};
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

      const taskId = content.task_id;
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

      // Poll for task completion
      let triedTime = 0;
      while (triedTime < maxTryTimes) {
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
        await new Promise((resolve) => setTimeout(resolve, 3000));
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
          taskAction: queryResult.action || '',
          taskProduct: queryResult.product || '',
          taskStatus: queryResult.status || 'failed',
        };
      } catch (error) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to get task status: ${error}`,
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
      const status = content.status || 'unknown';

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
   * @param maxStepRetries - Maximum retry times for MCP tool call failures
   *                         at SDK level. Used to retry when callMcpTool fails
   *                         (e.g., network errors, timeouts). Default is 3.
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.mobile.executeTask(
   *     'Open WeChat app', 100, 5
   *   );
   *   console.log(`Task ID: ${execResult.taskId}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTask(
      task: string,
      maxSteps: number = 50,
      maxStepRetries: number = 3): Promise<ExecutionResult> {
    const args = {
      task,
      max_steps: maxSteps,
    };

    let lastError: string | undefined;
    let lastRequestId = '';

    for (let attempt = 0; attempt < maxStepRetries; attempt++) {
      try {
        const result = await this.session.callMcpTool(
            this.getToolName('execute'), args);

        lastRequestId = result.requestId;

        if (result.success) {
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

          const taskId = content.task_id;
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
        } else {
          lastError = result.errorMessage || 'Failed to execute task';
          if (attempt < maxStepRetries - 1) {
            logDebug(
                `Attempt ${attempt + 1}/${maxStepRetries} failed, retrying...`);
            await new Promise((resolve) => setTimeout(resolve, 1000));
            continue;
          } else {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: lastError,
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Task Failed',
            };
          }
        }
      } catch (error) {
        lastError = `Failed to execute: ${error}`;
        if (attempt < maxStepRetries - 1) {
          logDebug(
              `Attempt ${attempt + 1}/${maxStepRetries} raised exception, ` +
              'retrying...');
          await new Promise((resolve) => setTimeout(resolve, 1000));
          continue;
        } else {
          return {
            requestId: lastRequestId,
            success: false,
            errorMessage: lastError,
            taskStatus: 'failed',
            taskId: '',
            taskResult: 'Task Failed',
          };
        }
      }
    }

    return {
      requestId: lastRequestId,
      success: false,
      errorMessage: `Failed after ${maxStepRetries} attempts: ${
          lastError || 'Unknown error'}`,
      taskStatus: 'failed',
      taskId: '',
      taskResult: 'Task Failed',
    };
  }

  /**
   * Execute a specific task described in human language synchronously.
   * This is a synchronous interface that blocks until the task is completed or
   * an error occurs, or timeout happens. The default polling interval is
   * 3 seconds.
   *
   * @param task - Task description in human language.
   * @param maxSteps - Maximum number of steps (clicks/swipes/etc.) allowed.
   *                   Used to prevent infinite loops or excessive resource
   *                   consumption. Default is 50.
   * @param maxStepRetries - Maximum retry times for MCP tool call failures
   *                         at SDK level. Used to retry when callMcpTool fails
   *                         (e.g., network errors, timeouts). Default is 3.
   * @param maxTryTimes - Maximum number of polling attempts (each 3 seconds).
   *                      Used to control how long to wait for task completion.
   *                      Default is 300 (about 15 minutes).
   * @returns ExecutionResult containing success status, task ID, task status,
   *     and error message if any.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: 'mobile_latest' });
   * if (result.success) {
   *   const execResult = await result.session.agent.mobile.executeTaskAndWait(
   *     'Open WeChat app', 100, 3, 200
   *   );
   *   console.log(`Task result: ${execResult.taskResult}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeTaskAndWait(
      task: string,
      maxSteps: number = 50,
      maxStepRetries: number = 3,
      maxTryTimes: number = 300): Promise<ExecutionResult> {
    const args = {
      task,
      max_steps: maxSteps,
    };

    let taskId: string | undefined;
    let lastError: string | undefined;
    let lastRequestId = '';

    for (let attempt = 0; attempt < maxStepRetries; attempt++) {
      try {
        const result = await this.session.callMcpTool(
            this.getToolName('execute'), args);

        lastRequestId = result.requestId;

        if (result.success) {
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

          taskId = content.task_id;
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
          break;
        } else {
          lastError = result.errorMessage || 'Failed to execute task';
          if (attempt < maxStepRetries - 1) {
            logDebug(
                `Attempt ${attempt + 1}/${maxStepRetries} failed, retrying...`);
            await new Promise((resolve) => setTimeout(resolve, 1000));
            continue;
          } else {
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: lastError,
              taskStatus: 'failed',
              taskId: '',
              taskResult: 'Task Failed',
            };
          }
        }
      } catch (error) {
        lastError = `Failed to execute: ${error}`;
        if (attempt < maxStepRetries - 1) {
          logDebug(
              `Attempt ${attempt + 1}/${maxStepRetries} raised exception, ` +
              'retrying...');
          await new Promise((resolve) => setTimeout(resolve, 1000));
          continue;
        } else {
          return {
            requestId: lastRequestId,
            success: false,
            errorMessage: lastError,
            taskStatus: 'failed',
            taskId: '',
            taskResult: 'Task Failed',
          };
        }
      }
    }

    if (!taskId) {
      return {
        requestId: lastRequestId,
        success: false,
        errorMessage: `Failed to get task_id after ${maxStepRetries} ` +
            `attempts: ${lastError || 'Unknown error'}`,
        taskStatus: 'failed',
        taskId: '',
        taskResult: 'Task Failed',
      };
    }

    let triedTime = 0;
    while (triedTime < maxTryTimes) {
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

      logDebug(`⏳ Task ${taskId} running 🚀: ${query.taskAction}.`);
      await new Promise((resolve) => setTimeout(resolve, 3000));
      triedTime++;
    }

    logDebug('⚠️ task execution timeout!');
    return {
      requestId: lastRequestId,
      success: false,
      errorMessage: 'Task timeout.',
      taskStatus: 'failed',
      taskId: taskId,
      taskResult: 'Task timeout.',
    };
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