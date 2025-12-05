/**
 * App manager rule for mobile device configuration.
 * 
 * Defines rules for managing app access on mobile devices through whitelist or blacklist modes.
 */
export interface AppManagerRule {
  /**
   * Type of rule to apply.
   * - "White": Whitelist mode - only allow specified apps
   * - "Black": Blacklist mode - block specified apps
   */
  ruleType: "White" | "Black";
  
  /**
   * List of Android package names to apply the rule to.
   * Example: ["com.android.settings", "com.example.app"]
   */
  appPackageNameList: string[];
}

/**
 * Mobile simulate mode enum.
 */
export enum MobileSimulateMode {
  PropertiesOnly = "PropertiesOnly",
  SensorsOnly = "SensorsOnly",
  PackagesOnly = "PackagesOnly",
  ServicesOnly = "ServicesOnly",
  All = "All",
}

/**
 * Mobile simulate configuration.
 */
export interface MobileSimulateConfig {
  simulate: boolean;
  simulatePath?: string;
  simulateMode: MobileSimulateMode;
  simulatedContextId?: string;
}

/**
 * Mobile-specific configuration settings for session creation.
 * 
 * These settings allow control over mobile device behavior including
 * resolution locking, app access management, navigation bar visibility, uninstall protection,
 * and device simulation.
 */
export interface MobileExtraConfig {
  /**
   * Whether to lock the screen resolution.
   * - true: Locks resolution for consistent mobile testing environments
   * - false: Allows adaptive resolution for different device types
   */
  lockResolution: boolean;
  
  /**
   * Optional app manager rule for controlling app access.
   * Defines which apps are allowed (whitelist) or blocked (blacklist).
   */
  appManagerRule?: AppManagerRule;
  
  /**
   * Whether to hide the system navigation bar for immersive full-screen experience.
   * - true: Hide navigation bar
   * - false: Show navigation bar (default)
   */
  hideNavigationBar?: boolean;
  
  /**
   * List of package names to protect from uninstallation.
   * Prevents accidental or malicious removal of critical apps.
   * Example: ["com.android.systemui", "com.android.settings"]
   */
  uninstallBlacklist?: string[];

  /**
   * Configuration for mobile device simulation.
   * Used to simulate specific device properties, sensors, etc.
   */
  simulateConfig?: MobileSimulateConfig;
}

/**
 * Extra configuration settings for different session types.
 * 
 * This container holds specialized configurations for various
 * session environments (mobile, desktop, etc.).
 */
export interface ExtraConfigs {
  /**
   * Mobile-specific configuration settings.
   * Only applicable when creating mobile sessions.
   */
  mobile?: MobileExtraConfig;
}

/**
 * Serializes ExtraConfigs to JSON string format.
 * Returns empty string if extraConfigs is null or undefined.
 * 
 * @param extraConfigs - The extra configs to serialize
 * @returns JSON string representation
 */
export function extraConfigsToJSON(extraConfigs?: ExtraConfigs | null): string {
  if (!extraConfigs) {
    return "";
  }
  
  return JSON.stringify(extraConfigs);
}

/**
 * Deserializes ExtraConfigs from JSON string format.
 * Returns null if jsonStr is empty or invalid.
 * 
 * @param jsonStr - JSON string to deserialize
 * @returns Parsed ExtraConfigs object or null
 */
export function extraConfigsFromJSON(jsonStr: string): ExtraConfigs | null {
  if (!jsonStr || jsonStr.trim() === "") {
    return null;
  }
  
  try {
    return JSON.parse(jsonStr) as ExtraConfigs;
  } catch (error) {
    throw new Error(`Failed to parse ExtraConfigs JSON: ${error}`);
  }
}

/**
 * Validates an AppManagerRule object.
 * Throws an error if validation fails.
 * 
 * @param rule - The rule to validate
 */
export function validateAppManagerRule(rule: AppManagerRule): void {
  if (!rule.ruleType) {
    throw new Error("AppManagerRule ruleType is required");
  }
  
  if (rule.ruleType !== "White" && rule.ruleType !== "Black") {
    throw new Error(`Invalid ruleType: ${rule.ruleType}. Must be "White" or "Black"`);
  }
  
  if (!Array.isArray(rule.appPackageNameList)) {
    throw new Error("AppManagerRule appPackageNameList must be an array");
  }
  
  for (const packageName of rule.appPackageNameList) {
    if (typeof packageName !== "string") {
      throw new Error("AppManagerRule appPackageNameList items must be strings");
    }
  }
}

/**
 * Validates a MobileSimulateConfig object.
 * Throws an error if validation fails.
 * 
 * @param config - The config to validate
 */
export function validateMobileSimulateConfig(config: MobileSimulateConfig): void {
  if (typeof config.simulate !== "boolean") {
    throw new Error("MobileSimulateConfig simulate must be a boolean");
  }
  
  if (!config.simulateMode) {
    throw new Error("MobileSimulateConfig simulateMode is required");
  }
  
  if (!Object.values(MobileSimulateMode).includes(config.simulateMode)) {
    throw new Error(`Invalid simulateMode: ${config.simulateMode}`);
  }
  
  if (config.simulatePath !== undefined && typeof config.simulatePath !== "string") {
    throw new Error("MobileSimulateConfig simulatePath must be a string");
  }
  
  if (config.simulatedContextId !== undefined && typeof config.simulatedContextId !== "string") {
    throw new Error("MobileSimulateConfig simulatedContextId must be a string");
  }
}

/**
 * Validates a MobileExtraConfig object.
 * Throws an error if validation fails.
 * 
 * @param config - The config to validate
 */
export function validateMobileExtraConfig(config: MobileExtraConfig): void {
  if (typeof config.lockResolution !== "boolean") {
    throw new Error("MobileExtraConfig lockResolution must be a boolean");
  }
  
  if (config.appManagerRule) {
    validateAppManagerRule(config.appManagerRule);
  }
  
  if (config.hideNavigationBar !== undefined && typeof config.hideNavigationBar !== "boolean") {
    throw new Error("MobileExtraConfig hideNavigationBar must be a boolean");
  }
  
  if (config.uninstallBlacklist) {
    if (!Array.isArray(config.uninstallBlacklist)) {
      throw new Error("MobileExtraConfig uninstallBlacklist must be an array");
    }
    
    for (const packageName of config.uninstallBlacklist) {
      if (typeof packageName !== "string" || packageName.trim() === "") {
        throw new Error("MobileExtraConfig uninstallBlacklist items must be non-empty strings");
      }
    }
  }

  if (config.simulateConfig) {
    validateMobileSimulateConfig(config.simulateConfig);
  }
}

/**
 * Validates an ExtraConfigs object.
 * Throws an error if validation fails.
 * 
 * @param extraConfigs - The extra configs to validate
 */
export function validateExtraConfigs(extraConfigs: ExtraConfigs): void {
  if (extraConfigs.mobile) {
    validateMobileExtraConfig(extraConfigs.mobile);
  }
}
