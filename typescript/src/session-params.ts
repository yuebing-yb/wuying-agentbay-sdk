import { ContextSync, SyncPolicy, newUploadPolicy, newExtractPolicy,newRecyclePolicy,Lifecycle,DownloadStrategy, WhiteList, newDeletePolicy } from "./context-sync";
import { ExtensionOption } from "./extension";
import { BrowserFingerprintContext } from "./browser";
import { ExtraConfigs, extraConfigsToJSON } from "./types/extra-configs";

// Browser fingerprint persistent path constant (moved from config.ts)
const BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";
import {
  log,
  logError,
  logInfo,
  logDebug,
  logAPICall,
  logAPIResponseWithDetails,
  maskSensitiveData,
  setRequestId,
  getRequestId,
} from "./utils/logger";

/**
 * Browser context configuration for session with optional extension support.
 * 
 * This class provides browser context configuration for cloud sessions and supports
 * automatic extension synchronization when ExtensionOption is provided.
 * 
 * Key Features:
 * - Browser context binding for sessions
 * - Automatic browser data upload on session end
 * - Optional extension integration with automatic context sync generation
 * - Clean API with ExtensionOption encapsulation
 * 
 * Extension Configuration:
 * - **ExtensionOption**: Pass an ExtensionOption object with contextId and extensionIds
 * - **No Extensions**: Don't provide extensionOption parameter (extensionContextSyncs will be undefined)
 * 
 * Usage Examples:
 * ```typescript
 * // With extensions using ExtensionOption
 * import { ExtensionOption } from "./extension";
 * 
 * const extOption = new ExtensionOption(
 *   "my_extensions",
 *   ["ext1", "ext2"]
 * );
 * 
 * const browserContext = new BrowserContext(
 *   "browser_session",
 *   true,
 *   extOption
 * );
 * 
 * // Without extensions (minimal configuration)
 * const browserContext = new BrowserContext(
 *   "browser_session",
 *   true
 * );
 * // extensionContextSyncs will be undefined
 * ```
 */
export class BrowserContext {
  /** ID of the browser context to bind to the session */
  contextId: string;
  /** Whether to automatically upload browser data when the session ends */
  autoUpload: boolean;
  /** Optional browser fingerprint context configuration object containing fingerprintContextId */
  fingerprintContext?: BrowserFingerprintContext;
  /** ID of the fingerprint context for browser fingerprint. Set automatically from fingerprint_context. */
  fingerprintContextId?: string;
  /** Auto-generated context sync for fingerprint. None if no fingerprint configuration provided. */
  fingerprintContextSync?: ContextSync;
  /** Optional extension configuration object containing context_id and extension_ids */
  extensionOption?: ExtensionOption;
  /** ID of the extension context for browser extensions. Set automatically from extension_option. */
  extensionContextId?: string;
  /** List of extension IDs to synchronize. Set automatically from extension_option. */
  extensionIds?: string[];
  /** Auto-generated context syncs for extensions. None if no extension configuration provided. */
  extensionContextSyncs?: ContextSync[];

  /**
   * Initialize BrowserContextImpl with optional extension and fingerprint support.
   *
   * @param contextId - ID of the browser context to bind to the session.
   *                   This identifies the browser instance for the session.
   * @param autoUpload - Whether to automatically upload browser data
   *                    when the session ends. Defaults to true.
   * @param extensionOption - Extension configuration object containing
   *                         contextId and extensionIds. This encapsulates
   *                         all extension-related configuration.
   *                         Defaults to undefined.
   * @param fingerprintContext - Browser fingerprint context configuration object containing
   *                            fingerprintContextId. This encapsulates
   *                            all fingerprint-related configuration.
   *                            Defaults to undefined.
   *
   * Extension Configuration:
   * - **ExtensionOption**: Use extensionOption parameter with an ExtensionOption object
   * - **No Extensions**: Don't provide extensionOption parameter
   *
   * Fingerprint Configuration:
   * - **BrowserFingerprintContext**: Use fingerprintContext parameter with a BrowserFingerprintContext object
   * - **No Fingerprint**: Don't provide fingerprintContext parameter
   *
   * Auto-generation:
   * - extensionContextSyncs is automatically generated when extensionOption is provided
   * - extensionContextSyncs will be undefined if no extensionOption is provided
   * - extensionContextSyncs will be a ContextSync[] if extensionOption is valid
   * - fingerprintContextSync is automatically generated when fingerprintContext is provided
   * - fingerprintContextSync will be undefined if no fingerprintContext is provided
   * - fingerprintContextSync will be a ContextSync if fingerprintContext is valid
   */
  constructor(
    contextId: string,
    autoUpload = true,
    extensionOption?: ExtensionOption,
    fingerprintContext?: BrowserFingerprintContext
  ) {
    this.contextId = contextId;
    this.autoUpload = autoUpload;
    this.extensionOption = extensionOption;
    this.fingerprintContext = fingerprintContext;

    // Handle fingerprint configuration from BrowserFingerprintContext
    if (fingerprintContext) {
      // Extract fingerprint information from BrowserFingerprintContext
      this.fingerprintContextId = fingerprintContext.fingerprintContextId;
      // Auto-generate fingerprint context sync
      this.fingerprintContextSync = this._createFingerprintContextSync();
    } else {
      // No fingerprint configuration provided
      this.fingerprintContextId = undefined;
      this.fingerprintContextSync = undefined;
    }

    // Handle extension configuration from ExtensionOption
    if (extensionOption) {
      // Extract extension information from ExtensionOption
      this.extensionContextId = extensionOption.contextId;
      this.extensionIds = extensionOption.extensionIds;
      // Auto-generate extension context syncs
      this.extensionContextSyncs = this._createExtensionContextSyncs();
    } else {
      // No extension configuration provided
      this.extensionContextId = undefined;
      this.extensionIds = [];
      this.extensionContextSyncs = undefined;
    }
  }

  /**
   * Create ContextSync configurations for browser extensions.
   *
   * This method is called only when extensionOption is provided and contains
   * valid extension configuration (contextId and extensionIds).
   *
   * @returns ContextSync[] - List of context sync configurations for extensions.
   *                         Returns empty list if extension configuration is invalid.
   */
  private _createExtensionContextSyncs(): ContextSync[] {
    if (!this.extensionIds || this.extensionIds.length === 0 || !this.extensionContextId) {
      return [];
    }

    // Create whitelist for each extension ID
    const whiteLists: WhiteList[] = this.extensionIds.map(extId => ({
      path: extId,
      excludePaths: []
    }));

    // Create sync policy for extensions
    const syncPolicy: SyncPolicy = {
      uploadPolicy: {
        ...newUploadPolicy(),
        autoUpload: false
      },
      extractPolicy: {
        ...newExtractPolicy(),
        extract: true,
        deleteSrcFile: true
      },
      deletePolicy: {
        ...newDeletePolicy(),
        syncLocalFile: false
      },
      recyclePolicy: newRecyclePolicy(),
      bwList: {
        whiteLists: whiteLists
      },
      downloadPolicy:{
        autoDownload:true,
        downloadStrategy: DownloadStrategy.DownloadAsync
      },
    };

    // Create context sync for extensions
    const extensionSync = new ContextSync(
      this.extensionContextId,
      "/tmp/extensions/",
      syncPolicy
    );

    return [extensionSync];
  }

  /**
   * Create ContextSync configuration for browser fingerprint.
   *
   * This method is called only when fingerprintContext is provided and contains
   * valid fingerprint configuration (fingerprintContextId).
   *
   * @returns ContextSync - Context sync configuration for fingerprint.
   *                       Returns undefined if fingerprint configuration is invalid.
   */
  private _createFingerprintContextSync(): ContextSync | undefined {
    if (!this.fingerprintContextId || !this.fingerprintContextId.trim()) {
      return undefined;
    }

    // Create sync policy for fingerprint
    const syncPolicy: SyncPolicy = {
      uploadPolicy: {
        ...newUploadPolicy(),
        autoUpload: false
      },
      extractPolicy: {
        ...newExtractPolicy(),
        extract: true,
        deleteSrcFile: true
      },
      deletePolicy: {
        ...newDeletePolicy(),
        syncLocalFile: false
      },
      recyclePolicy: newRecyclePolicy(),
      bwList: {
        whiteLists: []
      }
    };

    // Create context sync for fingerprint
    const fingerprintSync = new ContextSync(
      this.fingerprintContextId,
      BROWSER_FINGERPRINT_PERSIST_PATH,
      syncPolicy
    );

    return fingerprintSync;
  }

  /**
   * Get context syncs for extensions.
   *
   * @returns ContextSync[] - Context sync configurations for extensions. Returns empty list if no extensions configured.
   */
  getExtensionContextSyncs(): ContextSync[] {
    return this.extensionContextSyncs || [];
  }

  /**
   * Get context sync for fingerprint.
   *
   * @returns ContextSync - Context sync configuration for fingerprint.
   *                       Returns undefined if fingerprint configuration is invalid.
   */
  getFingerprintContextSync(): ContextSync | undefined {
    return this.fingerprintContextSync;
  }
  
}

/**
 * Configuration interface for CreateSessionParams
 */
export interface CreateSessionParamsConfig {
   /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
  labels?: Record<string, string>;
  /** Image ID to use for the session. */
  imageId?: string;
  /** List of context synchronization configurations. */
  contextSync?: ContextSync[];
  /** Optional configuration for browser data synchronization. */
  browserContext?: BrowserContext;
  /** Security policy ID (interface field name). */
  policyId?: string;
  /** Beta network ID to bind this session to. */
  betaNetworkId?: string;
  /** Whether to enable browser session recording. */
  enableBrowserReplay?: boolean;
  /** Additional configuration options. */
  extraConfigs?: ExtraConfigs;
  /** Framework identifier for tracking. */
  framework?: string;
  /** Whether to create a VPC-based session. Defaults to false. */
  isVpc?: boolean;
  /** MCP policy id to apply when creating the session (class field name). */
  mcpPolicyId?: string;
}

/**
 * Parameters for creating a session.
 * This interface defines all possible fields that can be used when creating a session.
 */
export interface CreateSessionParamsInterface {
  /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
  labels?: Record<string, string>;
  /** Image ID to use for the session. */
  imageId?: string;
  /** List of context synchronization configurations. */
  contextSync?: ContextSync[];
  /** Optional configuration for browser data synchronization. */
  browserContext?: BrowserContext;
  /** Security policy ID (interface field name). */
  policyId?: string;
  /** Beta network ID to bind this session to. */
  betaNetworkId?: string;
  /** Whether to enable browser session recording. */
  enableBrowserReplay?: boolean;
  /** Additional configuration options. */
  extraConfigs?: ExtraConfigs;
  /** Framework identifier for tracking. */
  framework?: string;
  /** Whether to create a VPC-based session. Defaults to false. */
  isVpc?: boolean;
  /** MCP policy id to apply when creating the session (class field name). */
  mcpPolicyId?: string;
}

/**
 * CreateSessionParams provides a way to configure the parameters for creating a new session
 * in the AgentBay cloud environment.
 */
export class CreateSessionParams implements CreateSessionParamsInterface {
  /** Custom labels for the Session. These can be used for organizing and filtering sessions. */
  public labels: Record<string, string>;

  /** Image ID to use for the session. */
  public imageId?: string;

  /**
   * List of context synchronization configurations.
   * These configurations define how contexts should be synchronized and mounted.
   */
  public contextSync: ContextSync[];

  /** Whether to create a VPC-based session. Defaults to false. */
  public isVpc?: boolean;

  /** MCP policy id to apply when creating the session. */
  public mcpPolicyId?: string;

  /** Security policy ID (interface field name). Maps to mcpPolicyId internally. */
  public policyId?: string;

  /** Beta network ID to bind this session to. */
  public betaNetworkId?: string;

  /** Whether to enable browser session recording. */
  public enableBrowserReplay: boolean;

  /** Additional configuration options. */
  public extraConfigs?: ExtraConfigs;

  /** Framework identifier for tracking. */
  public framework: string;

  public browserContext?: BrowserContext;
  

  constructor(params?: CreateSessionParamsConfig) {
    this.labels = params?.labels || {};
    this.imageId = params?.imageId;
    this.isVpc = params?.isVpc || false;
    // Handle policyId mapping - if policyId is provided, use it, otherwise use mcpPolicyId
    this.mcpPolicyId = params?.policyId || params?.mcpPolicyId;
    this.policyId = params?.policyId || params?.mcpPolicyId;
    this.betaNetworkId = params?.betaNetworkId;
    // Default to true like Python version
    this.enableBrowserReplay = params?.enableBrowserReplay ? params.enableBrowserReplay : true;
    this.extraConfigs = params?.extraConfigs;
    this.framework = params?.framework || "";
    
    // Start with provided contextSync
    let allContextSyncs = params?.contextSync ? [...params.contextSync] : [];

    // Add extension context syncs from browserContext if available
    if (params?.browserContext && params.browserContext.extensionContextSyncs) {
      allContextSyncs = [...allContextSyncs, ...params.browserContext.extensionContextSyncs];
      console.log(`Added ${params.browserContext.extensionContextSyncs.length} extension context sync(s) from BrowserContext`);
    }
    
    // Add fingerprint context sync from browserContext if available
    if (params?.browserContext && params.browserContext.fingerprintContextSync) {
      allContextSyncs = [...allContextSyncs, params.browserContext.fingerprintContextSync];
      console.log("Added fingerprint context sync from BrowserContext");
    }

    this.contextSync = allContextSyncs;
    this.browserContext = params?.browserContext;
  }
}