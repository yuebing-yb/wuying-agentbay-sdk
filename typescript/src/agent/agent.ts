import { ApiResponse } from "../types/api-response";
import { logDebug } from "../utils/logger";

/**
 * Result of task execution.
 */
export interface ExecutionResult extends ApiResponse {
  success: boolean;
  errorMessage: string;
  taskId: string;
  taskStatus: string;
}

/**
 * Result of query operations.
 */
export interface QueryResult extends ApiResponse {
  success: boolean;
  output: string;
  errorMessage: string;
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
 * An Agent to manipulate applications to complete specific tasks.
 */
export class Agent {
  private session: McpSession;

  /**
   * Initialize an Agent object.
   *
   * @param session - The Session instance that this Agent belongs to.
   */
  constructor(session: McpSession) {
    this.session = session;
  }

  /**
   * Execute a specific task described in human language.
   *
   * @param task - Task description in human language.
   * @param maxTryTimes - Maximum number of retry attempts.
   * @returns ExecutionResult containing success status, task output, and error message if any.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateAgentTask() {
   *   try {
   *     const result = await agentBay.create({ imageId: 'windows_latest' });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Execute a task with the agent
   *       const taskResult = await session.agent.executeTask(
   *         'Open notepad and type Hello World',
   *         10
   *       );
   *
   *       if (taskResult.success) {
   *         console.log('Task completed successfully');
   *         // Output: Task completed successfully
   *         console.log(`Task ID: ${taskResult.taskId}`);
   *         console.log(`Task Status: ${taskResult.taskStatus}`);
   *         // Output: Task Status: finished
   *       } else {
   *         console.error(`Task failed: ${taskResult.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateAgentTask().catch(console.error);
   * ```
   */
  async executeTask(task: string, maxTryTimes: number): Promise<ExecutionResult> {
    try {
      const args = { task, max_try_times: maxTryTimes };
      const result = await this.session.callMcpTool("flux_execute_task", args);
      
      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          taskStatus: "failed",
          taskId: "",
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
        };
      }

      const taskId = content.task_id;
      if (!taskId) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: "Task ID not found in response",
          taskStatus: "failed",
          taskId: "",
        };
      }

      // Poll for task completion
      let triedTime = 0;
      while (triedTime < maxTryTimes) {
        const query = await this.getTaskStatus(taskId);
        if (!query.success) {
          return {
            requestId: result.requestId,
            success: false,
            errorMessage: query.errorMessage,
            taskStatus: "failed",
            taskId,
          };
        }

        let statusContent: any;
        try {
          statusContent = JSON.parse(query.output);
        } catch (err) {
          return {
            requestId: result.requestId,
            success: false,
            errorMessage: `Failed to parse status response: ${err}`,
            taskStatus: "failed",
            taskId,
          };
        }

        const taskStatus = statusContent.status;
        if (!taskStatus) {
          return {
            requestId: result.requestId,
            success: false,
            errorMessage: "Task status not found in response",
            taskStatus: "failed",
            taskId,
          };
        }

        switch (taskStatus) {
          case "finished":
            return {
              requestId: result.requestId,
              success: true,
              errorMessage: "",
              taskId,
              taskStatus,
            };
          case "failed":
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: "Failed to execute task.",
              taskId,
              taskStatus,
            };
          case "unsupported":
            return {
              requestId: result.requestId,
              success: false,
              errorMessage: "Unsupported task.",
              taskId,
              taskStatus,
            };
        }

        logDebug(`Task ${taskId} is still running, please wait for a while.`);
        await new Promise(resolve => setTimeout(resolve, 3000));
        triedTime++;
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: "Task execution timed out",
        taskStatus: "timeout",
        taskId,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to execute: ${error}`,
        taskStatus: "failed",
        taskId: "",
      };
    }
  }

  /**
   * Get the status of the task with the given task ID.
   *
   * @param taskId - Task ID
   * @returns QueryResult containing the task status
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateGetTaskStatus() {
   *   try {
   *     const result = await agentBay.create({ imageId: 'windows_latest' });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start a task
   *       const taskResult = await session.agent.executeTask(
   *         'Open calculator',
   *         10
   *       );
   *
   *       if (taskResult.taskId) {
   *         // Query the task status
   *         const statusResult = await session.agent.getTaskStatus(taskResult.taskId);
   *
   *         if (statusResult.success) {
   *           console.log('Task status retrieved successfully');
   *           // Output: Task status retrieved successfully
   *           console.log(`Status output: ${statusResult.output}`);
   *           // Parse the output to get detailed status information
   *           const status = JSON.parse(statusResult.output);
   *           console.log(`Task status: ${status.status}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateGetTaskStatus().catch(console.error);
   * ```
   */
  async getTaskStatus(taskId: string): Promise<QueryResult> {
    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool("flux_get_task_status", args);
      
      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: result.errorMessage,
          output: "",
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        output: result.data,
        errorMessage: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to get task status: ${error}`,
        output: "",
      };
    }
  }

  /**
   * Terminate a task with a specified task ID.
   *
   * @param taskId - The ID of the running task.
   * @returns ExecutionResult containing success status, task output, and error message if any.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function demonstrateTerminateTask() {
   *   try {
   *     const result = await agentBay.create({ imageId: 'windows_latest' });
   *     if (result.success) {
   *       const session = result.session;
   *
   *       // Start a long-running task
   *       const taskResult = await session.agent.executeTask(
   *         'Open notepad and wait for 10 minutes',
   *         5
   *       );
   *
   *       if (taskResult.taskId) {
   *         // Terminate the task after some time
   *         const terminateResult = await session.agent.terminateTask(taskResult.taskId);
   *
   *         if (terminateResult.success) {
   *           console.log('Task terminated successfully');
   *           // Output: Task terminated successfully
   *           console.log(`Task ID: ${terminateResult.taskId}`);
   *           console.log(`Task Status: ${terminateResult.taskStatus}`);
   *           // Output: Task Status: terminated
   *         } else {
   *           console.error(`Failed to terminate task: ${terminateResult.errorMessage}`);
   *         }
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * demonstrateTerminateTask().catch(console.error);
   * ```
   */
  async terminateTask(taskId: string): Promise<ExecutionResult> {
            logDebug("Terminating task");
    
    try {
      const args = { task_id: taskId };
      const result = await this.session.callMcpTool("flux_terminate_task", args);

      let content: any;
      try {
        content = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          errorMessage: `Failed to parse response: ${err}`,
          taskId,
          taskStatus: "failed",
        };
      }

      const terminatedTaskId = content.task_id || taskId;
      const status = content.status || "unknown";

      if (result.success) {
        return {
          requestId: result.requestId,
          success: true,
          errorMessage: "",
          taskId: terminatedTaskId,
          taskStatus: status,
        };
      }

      return {
        requestId: result.requestId,
        success: false,
        errorMessage: result.errorMessage,
        taskId: terminatedTaskId,
        taskStatus: status,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to terminate: ${error}`,
        taskId,
        taskStatus: "failed",
      };
    }
  }
} 