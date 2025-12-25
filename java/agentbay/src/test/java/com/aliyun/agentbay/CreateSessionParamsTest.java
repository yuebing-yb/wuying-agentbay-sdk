package com.aliyun.agentbay;

import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;
import com.aliyun.agentbay.model.ExtraConfigs;
import com.aliyun.agentbay.session.CreateSessionParams;
import org.junit.jupiter.api.Test;

import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for CreateSessionParams with new parameters.
 */
public class CreateSessionParamsTest {

    @Test
    public void testCreateSessionParamsWithPolicyId() {
        CreateSessionParams params = new CreateSessionParams();
        params.setPolicyId("test-policy-123");
        
        assertEquals("test-policy-123", params.getPolicyId());
    }

    @Test
    public void testCreateSessionParamsWithEnableBrowserReplay() {
        CreateSessionParams params = new CreateSessionParams();
        
        // Test setting to false
        params.setEnableBrowserReplay(false);
        assertEquals(false, params.getEnableBrowserReplay());
        
        // Test setting to true
        params.setEnableBrowserReplay(true);
        assertEquals(true, params.getEnableBrowserReplay());
        
        // Test null (default behavior)
        params.setEnableBrowserReplay(null);
        assertNull(params.getEnableBrowserReplay());
    }

    @Test
    public void testCreateSessionParamsWithExtraConfigs() {
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        CreateSessionParams params = new CreateSessionParams();
        params.setExtraConfigs(extraConfigs);
        
        assertNotNull(params.getExtraConfigs());
        assertNotNull(params.getExtraConfigs().getMobile());
        assertTrue(params.getExtraConfigs().getMobile().getLockResolution());
    }

    @Test
    public void testCreateSessionParamsWithAllNewParameters() {
        // Create mobile simulate config
        MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
            true,
            "/tmp/device_info",
            MobileSimulateMode.PROPERTIES_ONLY,
            "device-ctx-123"
        );
        
        // Create mobile config
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setHideNavigationBar(true);
        mobileConfig.setSimulateConfig(simulateConfig);
        
        // Create extra configs
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        // Create session params with all new parameters
        CreateSessionParams params = new CreateSessionParams();
        params.setImageId("mobile_latest");
        params.setPolicyId("production-policy");
        params.setEnableBrowserReplay(false);
        params.setExtraConfigs(extraConfigs);
        
        Map<String, String> labels = new HashMap<>();
        labels.put("test", "complete-config");
        params.setLabels(labels);
        
        // Verify all fields
        assertEquals("mobile_latest", params.getImageId());
        assertEquals("production-policy", params.getPolicyId());
        assertEquals(false, params.getEnableBrowserReplay());
        assertNotNull(params.getExtraConfigs());
        assertNotNull(params.getExtraConfigs().getMobile());
        assertTrue(params.getExtraConfigs().getMobile().getLockResolution());
        assertNotNull(params.getExtraConfigs().getMobile().getSimulateConfig());
        assertEquals("/tmp/device_info", 
                    params.getExtraConfigs().getMobile().getSimulateConfig().getSimulatePath());
    }

    @Test
    public void testMobileExtraConfigBackwardCompatibility() {
        // Test old constructor still works (without simulate_config)
        MobileExtraConfig oldStyleConfig = new MobileExtraConfig(
            true,    // lockResolution
            null,    // appManagerRule
            false,   // hideNavigationBar
            null     // uninstallBlacklist
        );
        
        assertNotNull(oldStyleConfig);
        assertTrue(oldStyleConfig.getLockResolution());
        assertFalse(oldStyleConfig.getHideNavigationBar());
        assertNull(oldStyleConfig.getSimulateConfig());  // Should be null
    }

    @Test
    public void testCreateSessionParamsFramework() {
        CreateSessionParams params = new CreateSessionParams();
        params.setFramework("spring-ai");
        
        assertEquals("spring-ai", params.getFramework());
    }

    @Test
    public void testCreateSessionParamsLabels() {
        CreateSessionParams params = new CreateSessionParams();
        
        Map<String, String> labels = new HashMap<>();
        labels.put("environment", "test");
        labels.put("version", "1.0");
        params.setLabels(labels);
        
        assertNotNull(params.getLabels());
        assertEquals(2, params.getLabels().size());
        assertEquals("test", params.getLabels().get("environment"));
        assertEquals("1.0", params.getLabels().get("version"));
    }

    @Test
    public void testCreateSessionParamsDefaults() {
        CreateSessionParams params = new CreateSessionParams();

        // Test default values
        assertNull(params.getPolicyId());
        assertNull(params.getEnableBrowserReplay());
        assertNull(params.getExtraConfigs());
        assertNull(params.getNetworkId());
        assertNotNull(params.getContextSyncs());  // Should be empty list, not null
        assertTrue(params.getContextSyncs().isEmpty());
    }

    @Test
    public void testCreateSessionParamsWithNetworkId() {
        CreateSessionParams params = new CreateSessionParams();
        params.setNetworkId("test-network-123");

        assertEquals("test-network-123", params.getNetworkId());
    }

    @Test
    public void testCreateSessionParamsWithNullNetworkId() {
        CreateSessionParams params = new CreateSessionParams();
        params.setNetworkId(null);

        assertNull(params.getNetworkId());
    }

    @Test
    public void testCreateSessionParamsWithEmptyNetworkId() {
        CreateSessionParams params = new CreateSessionParams();
        params.setNetworkId("");

        assertEquals("", params.getNetworkId());
    }

    @Test
    public void testCreateSessionParamsWithNetworkIdAndOtherParams() {
        CreateSessionParams params = new CreateSessionParams();
        params.setNetworkId("shared-network");
        params.setImageId("linux_latest");
        params.setPolicyId("network-policy");

        Map<String, String> labels = new HashMap<>();
        labels.put("type", "networked-session");
        params.setLabels(labels);

        assertEquals("shared-network", params.getNetworkId());
        assertEquals("linux_latest", params.getImageId());
        assertEquals("network-policy", params.getPolicyId());
        assertNotNull(params.getLabels());
        assertEquals("networked-session", params.getLabels().get("type"));
    }
}

