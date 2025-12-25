package com.aliyun.agentbay.mobile;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Configuration for mobile environment settings.
 * 
 * <p>Provides comprehensive mobile environment configuration options including
 * resolution control, app management, navigation bar visibility, uninstall protection,
 * and device simulation capabilities.</p>
 * 
 * @see MobileSimulateConfig
 * @see AppManagerRule
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class MobileExtraConfig {
    
    @JsonProperty("LockResolution")
    private Boolean lockResolution;
    
    @JsonProperty("AppManagerRule")
    private AppManagerRule appManagerRule;
    
    @JsonProperty("HideNavigationBar")
    private Boolean hideNavigationBar;
    
    @JsonProperty("UninstallBlacklist")
    private List<String> uninstallBlacklist;

    @JsonProperty("SimulateConfig")
    private MobileSimulateConfig simulateConfig;

    /**
     * Default constructor.
     */
    public MobileExtraConfig() {
    }

    /**
     * Constructor with all parameters.
     *
     * @param lockResolution Whether to lock device resolution
     * @param appManagerRule App whitelist/blacklist rules
     * @param hideNavigationBar Whether to hide navigation bar
     * @param uninstallBlacklist Apps protected from uninstallation
     * @param simulateConfig Mobile device simulation configuration
     */
    public MobileExtraConfig(Boolean lockResolution, AppManagerRule appManagerRule, 
                            Boolean hideNavigationBar, List<String> uninstallBlacklist,
                            MobileSimulateConfig simulateConfig) {
        this.lockResolution = lockResolution;
        this.appManagerRule = appManagerRule;
        this.hideNavigationBar = hideNavigationBar;
        this.uninstallBlacklist = uninstallBlacklist;
        this.simulateConfig = simulateConfig;
    }

    /**
     * Constructor without simulate config (backward compatibility).
     */
    public MobileExtraConfig(Boolean lockResolution, AppManagerRule appManagerRule, 
                            Boolean hideNavigationBar, List<String> uninstallBlacklist) {
        this(lockResolution, appManagerRule, hideNavigationBar, uninstallBlacklist, null);
    }

    public Boolean getLockResolution() {
        return lockResolution;
    }

    public void setLockResolution(Boolean lockResolution) {
        this.lockResolution = lockResolution;
    }

    public AppManagerRule getAppManagerRule() {
        return appManagerRule;
    }

    public void setAppManagerRule(AppManagerRule appManagerRule) {
        this.appManagerRule = appManagerRule;
    }

    public Boolean getHideNavigationBar() {
        return hideNavigationBar;
    }

    public void setHideNavigationBar(Boolean hideNavigationBar) {
        this.hideNavigationBar = hideNavigationBar;
    }

    public List<String> getUninstallBlacklist() {
        return uninstallBlacklist;
    }

    public void setUninstallBlacklist(List<String> uninstallBlacklist) {
        this.uninstallBlacklist = uninstallBlacklist;
    }

    /**
     * Get mobile simulation configuration.
     *
     * @return Simulation configuration, or null if not set
     */
    public MobileSimulateConfig getSimulateConfig() {
        return simulateConfig;
    }

    /**
     * Set mobile simulation configuration.
     *
     * @param simulateConfig Simulation configuration
     */
    public void setSimulateConfig(MobileSimulateConfig simulateConfig) {
        this.simulateConfig = simulateConfig;
    }

    /**
     * Validate the configuration.
     * 
     * @throws IllegalArgumentException if configuration is invalid
     */
    public void validate() {
        if (appManagerRule != null) {
            appManagerRule.validate();
        }
        
        if (uninstallBlacklist != null) {
            for (String pkg : uninstallBlacklist) {
                if (pkg == null || pkg.trim().isEmpty()) {
                    throw new IllegalArgumentException("uninstall_blacklist items must be non-empty strings");
                }
            }
        }
        
        if (simulateConfig != null) {
            simulateConfig.validate();
        }
    }

    /**
     * Convert to Map for API request.
     *
     * @return Map representation
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new HashMap<>();
        
        if (lockResolution != null) {
            result.put("LockResolution", lockResolution);
        }
        
        if (appManagerRule != null) {
            result.put("AppManagerRule", appManagerRule.toMap());
        }
        
        if (hideNavigationBar != null) {
            result.put("HideNavigationBar", hideNavigationBar);
        }
        
        if (uninstallBlacklist != null) {
            result.put("UninstallBlacklist", uninstallBlacklist);
        }
        
        if (simulateConfig != null) {
            result.put("SimulateConfig", simulateConfig.toMap());
        }
        
        return result;
    }

    /**
     * Create from Map.
     *
     * @param map Map representation
     * @return MobileExtraConfig instance
     */
    public static MobileExtraConfig fromMap(Map<String, Object> map) {
        if (map == null) {
            return null;
        }
        
        MobileExtraConfig config = new MobileExtraConfig();
        
        if (map.containsKey("LockResolution")) {
            config.setLockResolution((Boolean) map.get("LockResolution"));
        }
        
        if (map.containsKey("AppManagerRule")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> ruleMap = (Map<String, Object>) map.get("AppManagerRule");
            config.setAppManagerRule(AppManagerRule.fromMap(ruleMap));
        }
        
        if (map.containsKey("HideNavigationBar")) {
            config.setHideNavigationBar((Boolean) map.get("HideNavigationBar"));
        }
        
        if (map.containsKey("UninstallBlacklist")) {
            @SuppressWarnings("unchecked")
            List<String> blacklist = (List<String>) map.get("UninstallBlacklist");
            config.setUninstallBlacklist(blacklist);
        }
        
        if (map.containsKey("SimulateConfig")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> simConfigMap = (Map<String, Object>) map.get("SimulateConfig");
            config.setSimulateConfig(MobileSimulateConfig.fromMap(simConfigMap));
        }
        
        return config;
    }

    @Override
    public String toString() {
        return "MobileExtraConfig{" +
                "lockResolution=" + lockResolution +
                ", appManagerRule=" + appManagerRule +
                ", hideNavigationBar=" + hideNavigationBar +
                ", uninstallBlacklist=" + uninstallBlacklist +
                ", simulateConfig=" + simulateConfig +
                '}';
    }
}
