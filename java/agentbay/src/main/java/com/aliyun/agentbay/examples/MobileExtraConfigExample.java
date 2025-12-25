package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.mobile.AppManagerRule;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Example demonstrating how to use ExtraConfigs with MobileExtraConfig
 * to configure mobile environment settings during session creation.
 * 
 * This example shows:
 * 1. Creating an app whitelist
 * 2. Locking device resolution
 * 3. Hiding navigation bar
 * 4. Setting uninstall protection
 */
public class MobileExtraConfigExample {

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.isEmpty()) {
            System.err.println("Please set AGENTBAY_API_KEY environment variable");
            return;
        }

        try {
            // Initialize AgentBay client
            AgentBay agentBay = new AgentBay(apiKey);
            System.out.println("AgentBay client initialized successfully");

            // Example 1: Basic Mobile Configuration
            basicMobileConfiguration(agentBay);

            // Example 2: App Whitelist Configuration
            appWhitelistConfiguration(agentBay);

            // Example 3: Complete Mobile Configuration
            completeMobileConfiguration(agentBay);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 1: Basic mobile configuration with resolution lock.
     */
    private static void basicMobileConfiguration(AgentBay agentBay) {
        System.out.println("\n=== Example 1: Basic Mobile Configuration ===");
        
        try {
            // Create mobile configuration
            MobileExtraConfig mobileConfig = new MobileExtraConfig();
            mobileConfig.setLockResolution(true);  // Lock screen resolution
            mobileConfig.setHideNavigationBar(true);  // Hide navigation bar

            // Create ExtraConfigs
            ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

            // Create session with mobile configuration
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("mobile_latest");
            params.setExtraConfigs(extraConfigs);
            
            // Add labels for organization
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "basic-mobile-config");
            labels.put("environment", "development");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Mobile session created successfully!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Request ID: " + result.getRequestId());
                System.out.println("   Configuration:");
                System.out.println("   - Resolution locked: Yes");
                System.out.println("   - Navigation bar hidden: Yes");

                // Clean up
                agentBay.delete(session, false);
                System.out.println("✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error in basicMobileConfiguration: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 2: Mobile configuration with app whitelist.
     */
    private static void appWhitelistConfiguration(AgentBay agentBay) {
        System.out.println("\n=== Example 2: App Whitelist Configuration ===");
        
        try {
            // Create app whitelist rule
            List<String> allowedApps = Arrays.asList(
                "com.android.settings",
                "com.android.chrome",
                "com.example.myapp"
            );
            
            AppManagerRule appWhitelistRule = new AppManagerRule(
                "White",  // Rule type: "White" for whitelist
                allowedApps
            );

            // Create mobile configuration with whitelist
            MobileExtraConfig mobileConfig = new MobileExtraConfig(
                true,                 // lockResolution
                appWhitelistRule,     // appManagerRule
                false,                // hideNavigationBar
                null                  // uninstallBlacklist
            );

            // Create ExtraConfigs
            ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

            // Create session parameters
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("mobile_latest");
            params.setExtraConfigs(extraConfigs);
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "app-whitelist");
            labels.put("config_type", "whitelist");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Mobile session with whitelist created!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Allowed apps:");
                for (String app : allowedApps) {
                    System.out.println("   - " + app);
                }

                // Clean up
                agentBay.delete(session, false);
                System.out.println("✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error in appWhitelistConfiguration: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 3: Complete mobile configuration with all options.
     */
    private static void completeMobileConfiguration(AgentBay agentBay) {
        System.out.println("\n=== Example 3: Complete Mobile Configuration ===");
        
        try {
            // Create app blacklist rule
            AppManagerRule appBlacklistRule = new AppManagerRule(
                "Black",  // Rule type: "Black" for blacklist
                Arrays.asList(
                    "com.malicious.app",
                    "com.unwanted.service"
                )
            );

            // Create uninstall protection list
            List<String> protectedApps = Arrays.asList(
                "com.android.systemui",
                "com.android.settings",
                "com.google.android.gms"
            );

            // Create comprehensive mobile configuration
            MobileExtraConfig mobileConfig = new MobileExtraConfig();
            mobileConfig.setLockResolution(true);
            mobileConfig.setAppManagerRule(appBlacklistRule);
            mobileConfig.setHideNavigationBar(true);
            mobileConfig.setUninstallBlacklist(protectedApps);

            // Create ExtraConfigs
            ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);

            // Create session parameters with all features
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("mobile_latest");
            params.setExtraConfigs(extraConfigs);
            params.setPolicyId("my-custom-policy");  // Optional: custom policy
            params.setEnableBrowserReplay(false);     // Optional: disable browser replay
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "complete-config");
            labels.put("project", "mobile-testing");
            labels.put("environment", "development");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Mobile session with complete configuration created!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Request ID: " + result.getRequestId());
                System.out.println("\n   Mobile Configuration:");
                System.out.println("   - Resolution locked: Yes");
                System.out.println("   - Navigation bar hidden: Yes");
                System.out.println("   - App blacklist enabled (2 packages)");
                System.out.println("   - Uninstall protection enabled (3 packages)");
                System.out.println("\n   Session Configuration:");
                System.out.println("   - Policy ID: my-custom-policy");
                System.out.println("   - Browser replay: Disabled");
                
                System.out.println("\n   Protected apps:");
                for (String app : protectedApps) {
                    System.out.println("   - " + app);
                }

                // Test mobile operations
                System.out.println("\n   Testing mobile operations...");
                try {
                    com.aliyun.agentbay.model.CommandResult packageResult = 
                        session.getCommand().executeCommand("dumpsys window | grep mCurrentFocus", 5000);
                    if (packageResult.isSuccess()) {
                        System.out.println("   ✅ Command executed successfully");
                    }
                } catch (Exception e) {
                    System.out.println("   ⚠️  Mobile test skipped: " + e.getMessage());
                }

                // Clean up
                agentBay.delete(session, false);
                System.out.println("\n✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error in completeMobileConfiguration: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

