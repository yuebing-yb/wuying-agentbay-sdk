import { AgentBay } from "./agent-bay";
import { Context, ContextService } from "./context";
import { ContextSync, newSyncPolicy } from "./context-sync";
import {
  logError,
  logInfo,
  logDebug,
} from "./utils/logger";
import fetch from "node-fetch";
import { MobileSimulateMode, MobileSimulateConfig } from "./types/extra-configs";

// Mobile info path constants
const MOBILE_INFO_DEFAULT_PATH = "/data/agentbay_mobile_info";
const MOBILE_INFO_SUB_PATH = "/agentbay_mobile_info";
const MOBILE_INFO_FILE_NAME = "dev_info.json";

/**
 * Result of the upload mobile info for mobile simulate.
 */
export interface MobileSimulateUploadResult {
  /**
   * Whether the operation was successful.
   */
  success: boolean;
  
  /**
   * The context ID of the mobile info.
   */
  mobileSimulateContextId?: string;
  
  /**
   * The error message if the operation failed.
   */
  errorMessage?: string;
}

/**
 * Provides methods to manage persistent mobile dev info and sync to the mobile device.
 */
export class MobileSimulateService {
  private agentBay: AgentBay;
  private contextService: ContextService;
  private simulateEnable: boolean = false;
  private simulateMode: MobileSimulateMode = MobileSimulateMode.PropertiesOnly;
  private contextId?: string;
  private contextSync?: ContextSync;
  private mobileDevInfoPath?: string;
  private useInternalContext: boolean = true;

  /**
   * Initialize the MobileSimulateService.
   * 
   * @param agentBay - The AgentBay instance.
   */
  constructor(agentBay: AgentBay) {
    if (!agentBay) {
      throw new Error("agentBay is required");
    }
    if (!agentBay.context) {
      throw new Error("agentBay.context is required");
    }

    this.agentBay = agentBay;
    this.contextService = agentBay.context;
  }

  /**
   * Set the simulate enable flag.
   * 
   * @param enable - The simulate feature enable flag.
   */
  setSimulateEnable(enable: boolean): void {
    this.simulateEnable = enable;
  }

  /**
   * Get the simulate enable flag.
   * 
   * @returns The simulate feature enable flag.
   */
  getSimulateEnable(): boolean {
    return this.simulateEnable;
  }

  /**
   * Set the simulate mode.
   * 
   * @param mode - The simulate mode.
   *   - PropertiesOnly: Simulate only device properties.
   *   - SensorsOnly: Simulate only device sensors.
   *   - PackagesOnly: Simulate only installed packages.
   *   - ServicesOnly: Simulate only system services.
   *   - All: Simulate all aspects of the device.
   */
  setSimulateMode(mode: MobileSimulateMode): void {
    this.simulateMode = mode;
  }

  /**
   * Get the simulate mode.
   * 
   * @returns The simulate mode.
   */
  getSimulateMode(): MobileSimulateMode {
    return this.simulateMode;
  }

  /**
   * Set a previously saved simulate context id. Please make sure the context id is provided by MobileSimulateService
   * but not user side created context.
   * 
   * @param contextId - The context ID of the previously saved mobile simulate context.
   */
  setSimulateContextId(contextId: string): void {
    this.contextId = contextId;
    logInfo(`set simulate context id = ${contextId}`);
    this.updateContext(true, contextId, undefined);
  }

  /**
   * Get the simulate context id.
   * 
   * @returns The context ID of the mobile simulate context.
   */
  getSimulateContextId(): string | undefined {
    return this.contextId;
  }

  /**
   * Get the simulate config.
   * 
   * @returns The simulate config.
   *   - simulate: The simulate feature enable flag.
   *   - simulatePath: The path of the mobile dev info file.
   *   - simulateMode: The simulate mode.
   *   - simulatedContextId: The context ID of the mobile info.
   */
  getSimulateConfig(): MobileSimulateConfig {
    const simulatedContextId = this.useInternalContext ? this.contextId : undefined;

    return {
      simulate: this.simulateEnable,
      simulatePath: this.mobileDevInfoPath,
      simulateMode: this.simulateMode,
      simulatedContextId: simulatedContextId
    };
  }

  /**
   * Check if the mobile dev info file exists in one context sync. (Only for user provided context sync)
   * 
   * @param contextSync - The context sync to check.
   * @returns True if the mobile dev info file exists, False otherwise.
   * @throws Error if context_sync is not provided or context_sync.context_id or context_sync.path is not provided.
   * 
   * @remarks
   * This method can only be used when mobile simulate context sync is managed by user side. For internal mobile simulate
   * context sync, this method will not work.
   */
  async hasMobileInfo(contextSync: ContextSync): Promise<boolean> {
    if (!contextSync) {
      throw new Error("contextSync is required");
    }
    if (!contextSync.contextId) {
      throw new Error("contextSync.contextId is required");
    }
    if (!contextSync.path) {
      throw new Error("contextSync.path is required");
    }

    const mobileDevInfoPath = contextSync.path + MOBILE_INFO_SUB_PATH + "/";
    logDebug(`hasMobileInfo: context_id = ${contextSync.contextId}, mobile_dev_info_path = ${mobileDevInfoPath}`);
    
    const res = await this.contextService.listFiles(contextSync.contextId, mobileDevInfoPath, 1, 50);
    
    let foundDevInfo = false;
    if (res.success) {
      for (const entry of res.entries) {
        if (entry.fileName === MOBILE_INFO_FILE_NAME) {
          foundDevInfo = true;
          break;
        }
      }
    } else {
      logError(`failed to list files: ${res.errorMessage}`);
      return false;
    }

    if (foundDevInfo) {
      logInfo("mobile dev info already exists");
      // update and save context sync if check success
      this.updateContext(false, contextSync.contextId, contextSync);
      return true;
    } else {
      logInfo("mobile dev info does not exist");
      return false;
    }
  }

  /**
   * Upload the mobile simulate dev info.
   * 
   * @param mobileDevInfoContent - The mobile simulate dev info content to upload.
   * @param contextSync - Optional
   *   - If not provided, a new context sync will be created for the mobile simulate service and this context id will
   *     be returned by the MobileSimulateUploadResult. User can use this context id to do persistent mobile simulate across sessions.
   *   - If provided, the mobile simulate dev info will be uploaded to the context sync in a specific path.
   * 
   * @returns The result of the upload operation.
   * 
   * @throws Error if mobile_dev_info_content is not provided or not a valid JSON string.
   * @throws Error if context_sync is provided but context_sync.context_id is not provided.
   * 
   * @remarks
   * If context_sync is not provided, a new context sync will be created for the mobile simulate.
   * If context_sync is provided, the mobile simulate dev info will be uploaded to the context sync.
   * If the mobile simulate dev info already exists in the context sync, the context sync will be updated.
   * If the mobile simulate dev info does not exist in the context sync, the context sync will be created.
   * If the upload operation fails, the error message will be returned.
   */
  async uploadMobileInfo(
    mobileDevInfoContent: string,
    contextSync?: ContextSync
  ): Promise<MobileSimulateUploadResult> {
    // validate parameters
    if (!mobileDevInfoContent) {
      throw new Error("mobileDevInfoContent is required");
    }
    
    try {
      JSON.parse(mobileDevInfoContent);
    } catch (error) {
      throw new Error("mobileDevInfoContent is not a valid JSON string");
    }

    // Create context for simulate if not provided
    if (!contextSync) {
      const createdContext = await this.createContextForSimulate();
      if (!createdContext) {
        logError("Failed to create context for simulate");
        return {
          success: false,
          errorMessage: "Failed to create context for simulate"
        };
      }
      this.updateContext(true, createdContext.id, undefined);
    } else {
      if (!contextSync.contextId) {
        throw new Error("contextSync.contextId is required");
      }
      this.updateContext(false, contextSync.contextId, contextSync);
    }

    const uploadPath = `${this.mobileDevInfoPath}/${MOBILE_INFO_FILE_NAME}`;
    const uploadUrlResult = await this.contextService.getFileUploadUrl(this.contextId!, uploadPath);
    
    if (!uploadUrlResult.success) {
      logError(`Failed to get file upload URL: ${uploadUrlResult.errorMessage}`);
      return {
        success: false,
        errorMessage: uploadUrlResult.errorMessage
      };
    }

    logDebug(`upload_url = ${uploadUrlResult.url}`);
    
    try {
      // Convert JSON string to Uint8Array
      const encoder = new TextEncoder();
      const uint8Array = encoder.encode(mobileDevInfoContent);
      const response = await fetch(uploadUrlResult.url, {
        method: 'PUT',
        body: uint8Array
      });
      
      if (!response.ok) {
        throw new Error(`Upload failed with status ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      const errorMsg = `An error occurred while uploading the file: ${error instanceof Error ? error.message : String(error)}`;
      logError(errorMsg);
      return {
        success: false,
        errorMessage: errorMsg
      };
    }

    logInfo("mobile dev info uploaded successfully");
    return {
      success: true,
      mobileSimulateContextId: this.contextId
    };
  }

  /**
   * Update the context information.
   * 
   * @param isInternal - Whether this is an internal context.
   * @param contextId - The context ID.
   * @param contextSync - The context sync (required for external context).
   */
  private updateContext(isInternal: boolean, contextId: string, contextSync?: ContextSync): void {
    if (!isInternal) {
      if (!contextSync) {
        throw new Error("contextSync is required for external context");
      }
      // add mobile info path to context sync bw list
      if (contextSync.policy?.bwList?.whiteLists) {
        const exists = contextSync.policy.bwList.whiteLists.some(
          whiteList => whiteList.path === MOBILE_INFO_SUB_PATH
        );
        
        if (!exists) {
          contextSync.policy.bwList.whiteLists.push({
            path: MOBILE_INFO_SUB_PATH,
            excludePaths: []
          });
          logInfo(`added mobile_dev_info_path to context_sync.policy.bw_list.white_lists: ${MOBILE_INFO_SUB_PATH}`);
        }
      }
    }

    this.useInternalContext = isInternal;
    this.contextId = contextId;
    this.contextSync = contextSync;
    if (isInternal) {
      this.mobileDevInfoPath = MOBILE_INFO_DEFAULT_PATH;
    } else {
      this.mobileDevInfoPath = contextSync!.path + MOBILE_INFO_SUB_PATH;
    }
    logInfo(`updated context, is_internal = ${isInternal}, context_id = ${this.contextId}, mobile_dev_info_path = ${this.mobileDevInfoPath}`);
  }

  /**
   * Create a context for simulate.
   * 
   * @returns The created context or null if failed.
   */
  private async createContextForSimulate(): Promise<Context | null> {
    const randomHex = Array.from({ length: 16 }, () => 
      Math.floor(Math.random() * 256).toString(16).padStart(2, '0')
    ).join('');
    const contextName = `mobile_sim_${randomHex}_${Math.floor(Date.now() / 1000)}`;
    
    const contextResult = await this.contextService.get(contextName, true);
    if (!contextResult.success || !contextResult.context) {
      logError(`Failed to create mobile simulate context: ${contextResult.errorMessage}`);
      return null;
    }

    const context = contextResult.context;
    logInfo(`created mobile simulate context, context_id = ${context.id}, context_name = ${context.name}`);
    return context;
  }
}
