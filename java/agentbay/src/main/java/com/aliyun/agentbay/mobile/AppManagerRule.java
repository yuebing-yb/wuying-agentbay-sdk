package com.aliyun.agentbay.mobile;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * App manager rule for whitelist/blacklist configuration.
 * 
 * <p>Controls which apps can be launched on the mobile device.</p>
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class AppManagerRule {
    
    @JsonProperty("RuleType")
    private String ruleType; // "White" or "Black"
    
    @JsonProperty("AppPackageNameList")
    private List<String> appPackageNameList;

    /**
     * Default constructor.
     */
    public AppManagerRule() {
    }

    /**
     * Constructor with parameters.
     *
     * @param ruleType Rule type: "White" for whitelist, "Black" for blacklist
     * @param appPackageNameList List of app package names
     */
    public AppManagerRule(String ruleType, List<String> appPackageNameList) {
        this.ruleType = ruleType;
        this.appPackageNameList = appPackageNameList;
    }

    public String getRuleType() {
        return ruleType;
    }

    public void setRuleType(String ruleType) {
        this.ruleType = ruleType;
    }

    public List<String> getAppPackageNameList() {
        return appPackageNameList;
    }

    public void setAppPackageNameList(List<String> appPackageNameList) {
        this.appPackageNameList = appPackageNameList;
    }

    /**
     * Validate the configuration.
     * 
     * @throws IllegalArgumentException if configuration is invalid
     */
    public void validate() {
        if (appPackageNameList != null) {
            for (String pkg : appPackageNameList) {
                if (pkg == null || pkg.trim().isEmpty()) {
                    throw new IllegalArgumentException("app_package_name_list items must be non-empty strings");
                }
            }
        }
    }

    /**
     * Convert to Map for API request.
     *
     * @return Map representation
     */
    public Map<String, Object> toMap() {
        Map<String, Object> result = new HashMap<>();
        
        if (ruleType != null) {
            result.put("RuleType", ruleType);
        }
        
        if (appPackageNameList != null) {
            result.put("AppPackageNameList", appPackageNameList);
        }
        
        return result;
    }

    /**
     * Create from Map.
     *
     * @param map Map representation
     * @return AppManagerRule instance
     */
    public static AppManagerRule fromMap(Map<String, Object> map) {
        if (map == null) {
            return null;
        }
        
        AppManagerRule rule = new AppManagerRule();
        
        if (map.containsKey("RuleType")) {
            rule.setRuleType((String) map.get("RuleType"));
        }
        
        if (map.containsKey("AppPackageNameList")) {
            @SuppressWarnings("unchecked")
            List<String> packageList = (List<String>) map.get("AppPackageNameList");
            rule.setAppPackageNameList(packageList);
        }
        
        return rule;
    }

    @Override
    public String toString() {
        return "AppManagerRule{" +
                "ruleType='" + ruleType + '\'' +
                ", appPackageNameList=" + appPackageNameList +
                '}';
    }
}
