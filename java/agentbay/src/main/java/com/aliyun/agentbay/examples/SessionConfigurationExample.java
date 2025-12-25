package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.HashMap;
import java.util.Map;

/**
 * Example demonstrating various session configuration options including
 * policy_id and enable_browser_replay parameters.
 * 
 * This example shows:
 * 1. Creating a session with custom policy
 * 2. Creating a session with browser replay disabled
 * 3. Creating a session with both options
 */
public class SessionConfigurationExample {

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

            // Example 1: Session with custom policy
            sessionWithCustomPolicy(agentBay);

            // Example 2: Session with browser replay disabled
            sessionWithoutBrowserReplay(agentBay);

            // Example 3: Session with combined configuration
            sessionWithCombinedConfig(agentBay);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 1: Create session with custom policy ID.
     */
    private static void sessionWithCustomPolicy(AgentBay agentBay) {
        System.out.println("\n=== Example 1: Session with Custom Policy ===");
        
        try {
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");
            params.setPolicyId("my-custom-policy-id");  // Set custom policy
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "custom-policy");
            labels.put("policy", "applied");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Session created with custom policy!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Policy ID: my-custom-policy-id");
                System.out.println("   Request ID: " + result.getRequestId());

                // Clean up
                agentBay.delete(session, false);
                System.out.println("✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 2: Create session with browser replay disabled.
     */
    private static void sessionWithoutBrowserReplay(AgentBay agentBay) {
        System.out.println("\n=== Example 2: Session without Browser Replay ===");
        
        try {
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("browser_latest");
            params.setEnableBrowserReplay(false);  // Disable browser recording
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "no-replay");
            labels.put("recording", "disabled");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Session created without browser replay!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Browser replay: Disabled");
                System.out.println("   Request ID: " + result.getRequestId());
                
                System.out.println("\n   Note: Browser actions will NOT be recorded.");
                System.out.println("   This can improve performance if replay is not needed.");

                // Clean up
                agentBay.delete(session, false);
                System.out.println("\n✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Example 3: Create session with combined configuration.
     */
    private static void sessionWithCombinedConfig(AgentBay agentBay) {
        System.out.println("\n=== Example 3: Session with Combined Configuration ===");
        
        try {
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");
            params.setPolicyId("production-policy");      // Custom policy
            params.setEnableBrowserReplay(false);         // Disable recording
            params.setFramework("langchain4j");           // Track framework usage
            
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "combined-config");
            labels.put("environment", "production");
            labels.put("framework", "langchain4j");
            params.setLabels(labels);

            SessionResult result = agentBay.create(params);

            if (result.isSuccess() && result.getSession() != null) {
                Session session = result.getSession();
                System.out.println("✅ Session created with combined configuration!");
                System.out.println("   Session ID: " + session.getSessionId());
                System.out.println("   Request ID: " + result.getRequestId());
                System.out.println("\n   Configuration:");
                System.out.println("   - Policy ID: production-policy");
                System.out.println("   - Browser replay: Disabled");
                System.out.println("   - Framework: langchain4j");
                System.out.println("   - Labels: 3 labels attached");

                // Labels have been set and will be stored with the session
                System.out.println("\n   Labels configured:");
                params.getLabels().forEach((key, value) -> 
                    System.out.println("   - " + key + ": " + value)
                );

                // Clean up
                agentBay.delete(session, false);
                System.out.println("\n✅ Session deleted");
            } else {
                System.err.println("❌ Failed to create session: " + result.getErrorMessage());
            }

        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

