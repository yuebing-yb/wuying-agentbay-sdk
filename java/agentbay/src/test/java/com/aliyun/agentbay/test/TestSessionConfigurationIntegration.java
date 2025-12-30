package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.mobile.AppManagerRule;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

import static org.junit.Assert.*;

/**
 * Integration tests for session configuration parameters including
 * policy_id, enable_browser_replay, and extra_configs.
 */
public class TestSessionConfigurationIntegration {

    private AgentBay agentBay;
    private Session session;

    @Before
    public void setUp() throws Exception {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        assertNotNull(apiKey, "AGENTBAY_API_KEY must be set");
        agentBay = new AgentBay();
    }

    @After
    public void tearDown() {
        if (session != null) {
            try {
                agentBay.delete(session, false);
                System.out.println("✅ Test session cleaned up: " + session.getSessionId());
            } catch (Exception e) {
                System.err.println("⚠️  Failed to clean up session: " + e.getMessage());
            }
            session = null;
        }
    }

    @Test
    public void testCreateSessionWithPolicyId() throws Exception {
        System.out.println("\n=== Test: Create Session with Policy ID ===");
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("linux_latest");
        params.setPolicyId("test-policy-123");
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "policy-id");
        params.setLabels(labels);

        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());
        assertNotNull(result.getRequestId());
        
        session = result.getSession();
        System.out.println("✅ Session created with policy ID");
        System.out.println("   Session ID: " + session.getSessionId());
        System.out.println("   Request ID: " + result.getRequestId());
    }

    @Test
    public void testCreateSessionWithBrowserReplayDisabled() throws Exception {
        System.out.println("\n=== Test: Create Session with Browser Replay Disabled ===");
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        params.setEnableBrowserReplay(false);
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "no-replay");
        params.setLabels(labels);

        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());
        
        session = result.getSession();
        System.out.println("✅ Session created without browser replay");
        System.out.println("   Session ID: " + session.getSessionId());
        
        // Verify browser replay is disabled
        assertNotNull(session.getEnableBrowserReplay());
        // Note: The actual verification would require checking the session state
    }

    @Test
    public void testCreateSessionWithMobileExtraConfig() throws Exception {
        System.out.println("\n=== Test: Create Session with Mobile Extra Config ===");
        
        // Create mobile configuration
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setHideNavigationBar(false);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile_latest");
        params.setExtraConfigs(extraConfigs);
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "mobile-config");
        params.setLabels(labels);

        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());
        
        session = result.getSession();
        System.out.println("✅ Session created with mobile config");
        System.out.println("   Session ID: " + session.getSessionId());
        
        // Verify mobile module is available
        assertNotNull(session.mobile);
    }

    @Test
    public void testCreateSessionWithAppWhitelist() throws Exception {
        System.out.println("\n=== Test: Create Session with App Whitelist ===");
        
        // Create app whitelist rule
        AppManagerRule appRule = new AppManagerRule(
            "White",
            Arrays.asList("com.android.settings", "com.android.chrome")
        );
        
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setAppManagerRule(appRule);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile_latest");
        params.setExtraConfigs(extraConfigs);
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "app-whitelist");
        params.setLabels(labels);

        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());
        
        session = result.getSession();
        System.out.println("✅ Session created with app whitelist");
        System.out.println("   Whitelisted apps: com.android.settings, com.android.chrome");
    }

    @Test
    public void testCreateSessionWithCombinedConfiguration() throws Exception {
        System.out.println("\n=== Test: Create Session with Combined Configuration ===");
        
        // Create comprehensive mobile config
        AppManagerRule appRule = new AppManagerRule(
            "Black",
            Arrays.asList("com.malicious.app")
        );
        
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setAppManagerRule(appRule);
        mobileConfig.setHideNavigationBar(true);
        mobileConfig.setUninstallBlacklist(Arrays.asList("com.android.systemui"));
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        // Create session with all configuration options
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile_latest");
        params.setPolicyId("comprehensive-policy");
        params.setEnableBrowserReplay(false);
        params.setExtraConfigs(extraConfigs);
        params.setFramework("junit-test");
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "combined-config");
        labels.put("environment", "integration-test");
        params.setLabels(labels);

        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        assertNotNull(result.getSession());
        assertNotNull(result.getRequestId());
        
        session = result.getSession();
        System.out.println("✅ Session created with combined configuration");
        System.out.println("   Session ID: " + session.getSessionId());
        System.out.println("   Policy ID: comprehensive-policy");
        System.out.println("   Browser replay: Disabled");
        System.out.println("   Framework: junit-test");
        
        // Labels are set via params but not directly retrievable from session object
    }

    @Test
    public void testPolicyIdNullOrEmpty() throws Exception {
        System.out.println("\n=== Test: Policy ID Null or Empty ===");
        
        // Test with null policy_id (should work)
        CreateSessionParams params1 = new CreateSessionParams();
        params1.setImageId("linux_latest");
        params1.setPolicyId(null);
        
        SessionResult result1 = agentBay.create(params1);
        assertTrue(result1.isSuccess());
        session = result1.getSession();
        agentBay.delete(session, false);
        session = null;
        
        // Test with empty policy_id (should work)
        CreateSessionParams params2 = new CreateSessionParams();
        params2.setImageId("linux_latest");
        params2.setPolicyId("");
        
        SessionResult result2 = agentBay.create(params2);
        assertTrue(result2.isSuccess());
        session = result2.getSession();
        
        System.out.println("✅ Null and empty policy_id handled correctly");
    }

    @Test
    public void testEnableBrowserReplayDefault() throws Exception {
        System.out.println("\n=== Test: Enable Browser Replay Default Behavior ===");
        
        // When enable_browser_replay is null, browser replay should be enabled by default
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("browser_latest");
        // Don't set enableBrowserReplay (null by default)
        
        SessionResult result = agentBay.create(params);

        assertNotNull(result);
        assertTrue(result.isSuccess());
        session = result.getSession();
        
        System.out.println("✅ Session created with default browser replay (enabled)");
        System.out.println("   Note: Browser replay is enabled by default when not specified");
    }
}

