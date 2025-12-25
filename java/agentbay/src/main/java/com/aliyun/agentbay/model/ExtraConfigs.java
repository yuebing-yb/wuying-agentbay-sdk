package com.aliyun.agentbay.model;

import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.HashMap;
import java.util.Map;

/**
 * Advanced configuration parameters for session creation.
 * Currently supports mobile environment configurations.
 * 
 * <p>This class matches the Python SDK's ExtraConfigs and provides
 * additional configuration options for specialized environments.</p>
 * 
 * @see MobileExtraConfig
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ExtraConfigs {
    
    @JsonProperty("Mobile")
    private MobileExtraConfig mobile;

    /**
     * Default constructor.
     */
    public ExtraConfigs() {
    }

    /**
     * Constructor with mobile configuration.
     *
     * @param mobile Mobile environment configuration
     */
    public ExtraConfigs(MobileExtraConfig mobile) {
        this.mobile = mobile;
    }

    /**
     * Get mobile configuration.
     *
     * @return Mobile configuration, or null if not set
     */
    public MobileExtraConfig getMobile() {
        return mobile;
    }

    /**
     * Set mobile configuration.
     *
     * @param mobile Mobile configuration
     */
    public void setMobile(MobileExtraConfig mobile) {
        this.mobile = mobile;
    }

    /**
     * Validate the configuration.
     * 
     * @throws IllegalArgumentException if configuration is invalid
     */
    public void validate() {
        if (mobile != null) {
            mobile.validate();
        }
    }

    /**
     * Convert to Map for API request.
     *
     * @return Map representation
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new HashMap<>();
        if (mobile != null) {
            result.put("Mobile", mobile.toMap());
        }
        return result;
    }

    /**
     * Create from Map.
     *
     * @param map Map representation
     * @return ExtraConfigs instance
     */
    public static ExtraConfigs fromMap(Map<String, Object> map) {
        if (map == null) {
            return null;
        }
        
        ExtraConfigs config = new ExtraConfigs();
        
        if (map.containsKey("Mobile")) {
            @SuppressWarnings("unchecked")
            Map<String, Object> mobileMap = (Map<String, Object>) map.get("Mobile");
            config.setMobile(MobileExtraConfig.fromMap(mobileMap));
        }
        
        return config;
    }

    @Override
    public String toString() {
        return "ExtraConfigs{" +
                "mobile=" + mobile +
                '}';
    }
}

