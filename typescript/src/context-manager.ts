import { Client } from "./api/client";
import { GetContextInfoRequest, SyncContextRequest } from "./api/models/model";
import { ApiResponse, extractRequestId } from "./types/api-response";
import {
  log,
  logError,
  logInfo,
  logDebug,
  logAPICall,
  logAPIResponseWithDetails,
  setRequestId,
  getRequestId,
} from "./utils/logger";

export interface ContextStatusData {
  contextId: string;
  path: string;
  errorMessage: string;
  status: string;
  startTime: number;
  finishTime: number;
  taskType: string;
}

export interface ContextStatusItem {
  type: string;
  data: string;
}

export interface ContextInfoResult extends ApiResponse {
  success?: boolean;
  contextStatusData: ContextStatusData[];
  errorMessage?: string;
}

export interface ContextSyncResult extends ApiResponse {
  success: boolean;
  errorMessage?: string;
}

export type SyncCallback = (success: boolean) => void;

export interface SessionInterface {
  getAPIKey(): string;
  getClient(): Client;
  getSessionId(): string;
}

export class ContextManager {
  private session: SessionInterface;

  constructor(session: SessionInterface) {
    this.session = session;
  }

  /**
   * Gets information about context synchronization status for the current session.
   *
   * @returns Promise resolving to ContextInfoResult containing context status data and request ID
   * @throws Error if the API call fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const info = await result.session.context.info();
   *   console.log(`Context count: ${info.contextStatusData.length}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async info(): Promise<ContextInfoResult> {
    return this.infoWithParams();
  }

  /**
   * Gets information about context synchronization status with optional filter parameters.
   *
   * @param contextId - Optional context ID to filter results
   * @param path - Optional path to filter results
   * @param taskType - Optional task type to filter results (e.g., "upload", "download")
   * @returns Promise resolving to ContextInfoResult containing filtered context status data and request ID
   * @throws Error if the API call fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const info = await result.session.context.infoWithParams('SdkCtx-xxx', '/mnt/persistent');
   *   console.log(`Context status: ${info.contextStatusData[0]?.status}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async infoWithParams(
    contextId?: string,
    path?: string,
    taskType?: string
  ): Promise<ContextInfoResult> {
    const request = new GetContextInfoRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
    });

    // Set optional parameters if provided
    if (contextId) {
      request.contextId = contextId;
    }
    if (path) {
      request.path = path;
    }
    if (taskType) {
      request.taskType = taskType;
    }

    // Log API request (matching Go version format)
    logAPICall("GetContextInfo");
    let requestLog = `Request: SessionId=${request.sessionId}`;
    if (request.contextId) {
      requestLog += `, ContextId=${request.contextId}`;
    }
    if (request.path) {
      requestLog += `, Path=${request.path}`;
    }
    if (request.taskType) {
      requestLog += `, TaskType=${request.taskType}`;
    }
    logDebug(requestLog);

    try {
      const response = await this.session.getClient().getContextInfo(request);

      // Extract RequestID
      const requestId = extractRequestId(response) || "";

      // Check for API-level errors
      if (response?.body?.success === false && response.body.code) {
        const errorMsg = `[${response.body.code}] ${response.body.message || 'Unknown error'}`;
        const fullResponse = response.body ? JSON.stringify(response.body, null, 2) : "";
        logAPIResponseWithDetails("GetContextInfo", requestId, false, undefined, fullResponse);
        return {
          requestId,
          success: false,
          contextStatusData: [],
          errorMessage: errorMsg,
        };
      }

      // Parse the context status data
      const contextStatusData: ContextStatusData[] = [];
      if (response?.body?.data?.contextStatus) {
        try {
          // First, parse the outer array
          const contextStatusStr = response.body.data.contextStatus;
          const statusItems: ContextStatusItem[] = JSON.parse(contextStatusStr);

          // Process each item in the array
          for (const item of statusItems) {
            if (item.type === "data") {
              // Parse the inner data string
              const dataItems: ContextStatusData[] = JSON.parse(item.data);
              contextStatusData.push(...dataItems);
            }
          }
        } catch (error) {
          logError("Error parsing context status:", error);
        }
      }

      // Log API response with key fields
      const keyFields: Record<string, any> = {
        session_id: request.sessionId,
        context_count: contextStatusData.length,
      };
      if (request.contextId) {
        keyFields.context_id = request.contextId;
      }
      if (request.path) {
        keyFields.path = request.path;
      }
      if (request.taskType) {
        keyFields.task_type = request.taskType;
      }
      const fullResponse = response.body ? JSON.stringify(response.body, null, 2) : "";
      logAPIResponseWithDetails("GetContextInfo", requestId, true, keyFields, fullResponse);

      return {
        requestId,
        success: true,
        contextStatusData,
        errorMessage: undefined,
      };
    } catch (error) {
      logError("Error calling GetContextInfo:", error);
      throw new Error(`Failed to get context info: ${error}`);
    }
  }

  /**
   * Synchronizes a context with the session. Supports both async and callback modes.
   *
   * @param contextId - Optional context ID to synchronize. If provided, `path` must also be provided.
   * @param path - Optional path where the context should be mounted. If provided, `contextId` must also be provided.
   * @param mode - Optional synchronization mode (e.g., "upload", "download")
   * @param callback - Optional callback function. If provided, runs in background and calls callback when complete
   * @param maxRetries - Maximum number of retries for polling completion status (default: 150)
   * @param retryInterval - Milliseconds to wait between retries (default: 1500)
   * @returns Promise resolving to ContextSyncResult with success status and request ID
   * @throws Error if the API call fails
   * @throws Error if `contextId` or `path` is provided without the other parameter.
   *               Both must be provided together, or both must be omitted.
   *
   * @example
   * Sync all contexts (no parameters):
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const syncResult = await result.session.context.sync();
   *   console.log(`Sync: ${syncResult.success}`);
   *   await result.session.delete();
   * }
   * ```
   *
   * @example
   * Sync specific context with path:
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const ctxResult = await agentBay.context.get('my-context', true);
   *   const syncResult = await result.session.context.sync(ctxResult.context!.id, '/mnt/persistent', 'upload');
   *   console.log(`Sync: ${syncResult.success}`);
   *   await result.session.delete();
   * }
   * ```
   */
  async sync(
    contextId?: string,
    path?: string,
    mode?: string,
    callback?: SyncCallback,
    maxRetries = 150,
    retryInterval = 1500
  ): Promise<ContextSyncResult> {
    // Validate that contextId and path are provided together or both omitted
    const hasContextId = contextId !== undefined && contextId.trim() !== "";
    const hasPath = path !== undefined && path.trim() !== "";

    if (hasContextId !== hasPath) {
      throw new Error(
        "contextId and path must be provided together or both omitted. " +
        "If you want to sync a specific context, both contextId and path are required. " +
        "If you want to sync all contexts, omit both parameters."
      );
    }

    const request = new SyncContextRequest({
      authorization: `Bearer ${this.session.getAPIKey()}`,
      sessionId: this.session.getSessionId(),
    });

    // Set optional parameters if provided
    if (contextId) {
      request.contextId = contextId;
    }
    if (path) {
      request.path = path;
    }
    if (mode) {
      request.mode = mode;
    }

    // Log API request (matching Go version format)
    logAPICall("SyncContext");
    let requestLog = `Request: SessionId=${request.sessionId}`;
    if (request.contextId) {
      requestLog += `, ContextId=${request.contextId}`;
    }
    if (request.path) {
      requestLog += `, Path=${request.path}`;
    }
    if (request.mode) {
      requestLog += `, Mode=${request.mode}`;
    }
    logDebug(requestLog);

    try {
      const response = await this.session.getClient().syncContext(request);

      // Extract RequestID
      const requestId = extractRequestId(response) || "";

      // Check for API-level errors
      if (response?.body?.success === false && response.body.code) {
        const errorMsg = `[${response.body.code}] ${response.body.message || 'Unknown error'}`;
        const fullResponse = response.body ? JSON.stringify(response.body, null, 2) : "";
        logAPIResponseWithDetails("SyncContext", requestId, false, undefined, fullResponse);
        return {
          requestId,
          success: false,
          errorMessage: errorMsg,
        };
      }

      let success = false;
      if (response?.body?.success !== undefined) {
        success = response.body.success;
      }

      // Log API response with key fields
      const keyFields: Record<string, any> = {
        session_id: request.sessionId,
        success: success,
      };
      if (request.contextId) {
        keyFields.context_id = request.contextId;
      }
      if (request.path) {
        keyFields.path = request.path;
      }
      if (request.mode) {
        keyFields.mode = request.mode;
      }
      const fullResponse = response.body ? JSON.stringify(response.body, null, 2) : "";
      logAPIResponseWithDetails("SyncContext", requestId, success, keyFields, fullResponse);

      // If callback is provided, start polling in background (async mode)
      if (callback && success) {
        // Start polling in background without blocking
        this.pollForCompletion(callback, contextId, path, maxRetries, retryInterval)
          .catch((error) => {
            logError("Error in background polling:", error);
            callback(false);
          });
        return {
          requestId,
          success,
        };
      }

      // If no callback, wait for completion (sync mode)
      if (success) {
        const finalSuccess = await this.pollForCompletionAsync(
          contextId,
          path,
          maxRetries,
          retryInterval
        );
        return {
          requestId,
          success: finalSuccess,
        };
      }

      return {
        requestId,
        success,
      };
    } catch (error) {
      logError("Error calling SyncContext:", error);
      throw new Error(`Failed to sync context: ${error}`);
    }
  }

  /**
   * Polls the info interface to check if sync is completed and calls callback.
   */
  private async pollForCompletion(
    callback: SyncCallback,
    contextId?: string,
    path?: string,
    maxRetries = 150,
    retryInterval = 1500
  ): Promise<void> {
    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        // Get context status data
        const infoResult = await this.infoWithParams(contextId, path);

        // Check if all sync tasks are completed
        let allCompleted = true;
        let hasFailure = false;
        let hasSyncTasks = false;

        for (const item of infoResult.contextStatusData) {
          // We only care about sync tasks (upload/download)
          if (item.taskType !== "upload" && item.taskType !== "download") {
            continue;
          }

          hasSyncTasks = true;
          logDebug(`Sync task ${item.contextId} status: ${item.status}, path: ${item.path}`);

          if (item.status !== "Success" && item.status !== "Failed") {
            allCompleted = false;
            break;
          }

          if (item.status === "Failed") {
            hasFailure = true;
            logError(`Sync failed for context ${item.contextId}: ${item.errorMessage}`);
          }
        }

        if (allCompleted || !hasSyncTasks) {
          // All tasks completed or no sync tasks found
          if (hasFailure) {
            logInfo("Context sync completed with failures");
            callback(false);
          } else if (hasSyncTasks) {
            logInfo("Context sync completed successfully");
            callback(true);
          } else {
            logDebug("No sync tasks found");
            callback(true);
          }
          return; // Exit the function immediately after calling callback
        }

        logDebug(`Waiting for context sync to complete, attempt ${retry + 1}/${maxRetries}`);
        await this.sleep(retryInterval);
      } catch (error) {
        logError(`Error checking context status on attempt ${retry + 1}:`, error);
        await this.sleep(retryInterval);
      }
    }

    // If we've exhausted all retries, call callback with failure
    logError(`Context sync polling timed out after ${maxRetries} attempts`);
    callback(false);
  }

  /**
   * Async version of polling for sync completion.
   */
  private async pollForCompletionAsync(
    contextId?: string,
    path?: string,
    maxRetries = 150,
    retryInterval = 1500
  ): Promise<boolean> {
    for (let retry = 0; retry < maxRetries; retry++) {
      try {
        // Get context status data
        const infoResult = await this.infoWithParams(contextId, path);

        // Check if all sync tasks are completed
        let allCompleted = true;
        let hasFailure = false;
        let hasSyncTasks = false;

        for (const item of infoResult.contextStatusData) {
          // We only care about sync tasks (upload/download)
          if (item.taskType !== "upload" && item.taskType !== "download") {
            continue;
          }

          hasSyncTasks = true;
          logDebug(`Sync task ${item.contextId} status: ${item.status}, path: ${item.path}`);

          if (item.status !== "Success" && item.status !== "Failed") {
            allCompleted = false;
            break;
          }

          if (item.status === "Failed") {
            hasFailure = true;
            logError(`Sync failed for context ${item.contextId}: ${item.errorMessage}`);
          }
        }

        if (allCompleted || !hasSyncTasks) {
          // All tasks completed or no sync tasks found
          if (hasFailure) {
            logInfo("Context sync completed with failures");
            return false;
          } else if (hasSyncTasks) {
            logInfo("Context sync completed successfully");
            return true;
          } else {
            logDebug("No sync tasks found");
            return true;
          }
        }

        logDebug(`Waiting for context sync to complete, attempt ${retry + 1}/${maxRetries}`);
        await this.sleep(retryInterval);
      } catch (error) {
        logError(`Error checking context status on attempt ${retry + 1}:`, error);
        await this.sleep(retryInterval);
      }
    }

    // If we've exhausted all retries, return failure
    logError(`Context sync polling timed out after ${maxRetries} attempts`);
    return false;
  }

  /**
   * Sleep utility function for TypeScript
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

export function newContextManager(session: SessionInterface): ContextManager {
  return new ContextManager(session);
}
