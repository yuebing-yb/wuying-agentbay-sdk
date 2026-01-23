package com.aliyun.agentbay.session;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import com.aliyun.agentbay.browser.BrowserContext;
import com.aliyun.agentbay.context.ContextSync;
import com.aliyun.agentbay.model.ExtraConfigs;

/**
 * Parameters for creating a new session in the AgentBay cloud environment.
 * 
 * <p>Supports various configuration options including labels, context synchronization,
 * browser context, policy management, browser replay, and mobile extra configurations.</p>
 * 
 * @see BrowserContext
 * @see ContextSync
 * @see ExtraConfigs
 */
public class CreateSessionParams {
    
    private String appId;
    private String browserType;
    private boolean autoUpload;
    private String imageId;
    private Map<String, String> labels;
    private Map<String, String> metadata;
    private List<ContextSync> contextSyncs;
    private BrowserContext browserContext;
    private String framework;
    private String policyId;
    private Boolean enableBrowserReplay;
    private ExtraConfigs extraConfigs;
    // Beta: network binding during session creation
    private String betaNetworkId;

    public CreateSessionParams() {
        this.contextSyncs = new ArrayList<>();
    }

    public CreateSessionParams(String appId) {
        this.appId = appId;
        this.browserType = "chrome";
        this.autoUpload = true;
        this.contextSyncs = new ArrayList<>();
    }
    
    /**
     * Set the browser context and automatically merge extension and fingerprint context syncs.
     * 
     * @param browserContext Browser context configuration
     */
    public void setBrowserContext(BrowserContext browserContext) {
        this.browserContext = browserContext;
        
        if (browserContext != null) {
            // Initialize contextSyncs if null
            if (this.contextSyncs == null) {
                this.contextSyncs = new ArrayList<>();
            }
            
            // Add extension context syncs from browser_context if available
            List<ContextSync> extensionSyncs = browserContext.getExtensionContextSyncs();
            if (extensionSyncs != null && !extensionSyncs.isEmpty()) {
                this.contextSyncs.addAll(extensionSyncs);
            }
            
            // Add fingerprint context sync from browser_context if available
            ContextSync fingerprintSync = browserContext.getFingerprintContextSync();
            if (fingerprintSync != null) {
                this.contextSyncs.add(fingerprintSync);
            }
        }
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getBrowserType() {
        return browserType;
    }

    public void setBrowserType(String browserType) {
        this.browserType = browserType;
    }

    public boolean isAutoUpload() {
        return autoUpload;
    }

    public void setAutoUpload(boolean autoUpload) {
        this.autoUpload = autoUpload;
    }

    public Map<String, String> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, String> metadata) {
        this.metadata = metadata;
    }

    public String getImageId() {
        return imageId;
    }

    public void setImageId(String imageId) {
        this.imageId = imageId;
    }

    public Map<String, String> getLabels() {
        return labels;
    }

    public void setLabels(Map<String, String> labels) {
        this.labels = labels;
    }

    public List<ContextSync> getContextSyncs() {
        return contextSyncs;
    }

    public void setContextSyncs(List<ContextSync> contextSyncs) {
        this.contextSyncs = contextSyncs;
    }
    
    public BrowserContext getBrowserContext() {
        return browserContext;
    }
    
    /**
     * Get the framework name (e.g., "spring-ai", "langchain4j").
     * This is used for SDK statistics tracking.
     * 
     * @return framework name, or null if not set
     */
    public String getFramework() {
        return framework;
    }
    
    /**
     * Set the framework name (e.g., "spring-ai", "langchain4j").
     * This is used for SDK statistics tracking.
     * 
     * @param framework framework name
     */
    public void setFramework(String framework) {
        this.framework = framework;
    }

    /**
     * Get the policy ID to apply when creating the session.
     * 
     * @return Policy ID, or null if not set
     */
    public String getPolicyId() {
        return policyId;
    }

    /**
     * Set the policy ID to apply when creating the session.
     * 
     * @param policyId Policy ID
     */
    public void setPolicyId(String policyId) {
        this.policyId = policyId;
    }

    /**
     * Get whether browser replay recording is enabled.
     * 
     * @return true if enabled, false if disabled, null if not set (defaults to true)
     */
    public Boolean getEnableBrowserReplay() {
        return enableBrowserReplay;
    }

    /**
     * Set whether to enable browser replay recording for the session.
     * 
     * <p>Browser replay is enabled by default. Set to false to disable recording.</p>
     * 
     * @param enableBrowserReplay true to enable, false to disable
     */
    public void setEnableBrowserReplay(Boolean enableBrowserReplay) {
        this.enableBrowserReplay = enableBrowserReplay;
    }

    /**
     * Get advanced configuration parameters.
     * 
     * @return ExtraConfigs instance, or null if not set
     */
    public ExtraConfigs getExtraConfigs() {
        return extraConfigs;
    }

    /**
     * Set advanced configuration parameters for specialized environments.
     *
     * <p>Currently supports mobile environment configurations including
     * device simulation, app management rules, and more.</p>
     *
     * @param extraConfigs Advanced configuration parameters
     * @see ExtraConfigs
     */
    public void setExtraConfigs(ExtraConfigs extraConfigs) {
        this.extraConfigs = extraConfigs;
    }

    public String getBetaNetworkId() {
        return betaNetworkId;
    }

    public void setBetaNetworkId(String betaNetworkId) {
        this.betaNetworkId = betaNetworkId;
    }

}