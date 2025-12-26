package com.aliyun.agentbay.test;

import com.aliyun.agentbay.mobile.AppManagerRule;
import com.aliyun.agentbay.mobile.MobileExtraConfig;
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;
import com.aliyun.agentbay.model.ExtraConfigs;
import org.junit.Test;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

public class ExtraConfigsTest {

    @Test
    public void testExtraConfigsCreation() {
        // Test creating ExtraConfigs with mobile config
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        assertNotNull(extraConfigs);
        assertNotNull(extraConfigs.getMobile());
        assertEquals(true, extraConfigs.getMobile().getLockResolution());
    }

    @Test
    public void testExtraConfigsToMap() {
        // Create mobile config
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setHideNavigationBar(false);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        
        // Convert to map
        Map<String, Object> map = extraConfigs.toMap();
        
        assertNotNull(map);
        assertTrue(map.containsKey("Mobile"));
        
        @SuppressWarnings("unchecked")
        Map<String, Object> mobileMap = (Map<String, Object>) map.get("Mobile");
        assertEquals(true, mobileMap.get("LockResolution"));
        assertEquals(false, mobileMap.get("HideNavigationBar"));
    }

    @Test
    public void testExtraConfigsValidation() {
        // Test valid configuration
        MobileExtraConfig validConfig = new MobileExtraConfig();
        validConfig.setLockResolution(true);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(validConfig);

        try {
            extraConfigs.validate();
        } catch (Exception e) {
            fail("Validation should not throw exception: " + e.getMessage());
        }
    }

    @Test
    public void testMobileExtraConfigWithAllFields() {
        // Create app whitelist rule
        AppManagerRule appRule = new AppManagerRule(
            "White",
            Arrays.asList("com.android.settings", "com.android.chrome")
        );
        
        // Create simulate config
        MobileSimulateConfig simulateConfig = new MobileSimulateConfig(
            true,
            "/tmp/mobile_dev_info",
            MobileSimulateMode.ALL,
            "device-context-id"
        );
        
        // Create mobile config with all fields
        MobileExtraConfig mobileConfig = new MobileExtraConfig(
            true,                           // lockResolution
            appRule,                        // appManagerRule
            true,                           // hideNavigationBar
            Arrays.asList("com.android.systemui"),  // uninstallBlacklist
            simulateConfig                  // simulateConfig
        );
        
        assertNotNull(mobileConfig);
        assertTrue(mobileConfig.getLockResolution());
        assertTrue(mobileConfig.getHideNavigationBar());
        assertNotNull(mobileConfig.getAppManagerRule());
        assertNotNull(mobileConfig.getUninstallBlacklist());
        assertEquals(1, mobileConfig.getUninstallBlacklist().size());
        assertNotNull(mobileConfig.getSimulateConfig());
        assertTrue(mobileConfig.getSimulateConfig().isSimulate());
    }

    @Test
    public void testMobileExtraConfigToMap() {
        AppManagerRule appRule = new AppManagerRule("White", Arrays.asList("com.test.app"));
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        mobileConfig.setAppManagerRule(appRule);
        mobileConfig.setHideNavigationBar(false);
        mobileConfig.setUninstallBlacklist(Arrays.asList("com.protected.app"));
        
        Map<String, Object> map = mobileConfig.toMap();
        
        assertNotNull(map);
        assertEquals(true, map.get("LockResolution"));
        assertEquals(false, map.get("HideNavigationBar"));
        assertTrue(map.containsKey("AppManagerRule"));
        assertTrue(map.containsKey("UninstallBlacklist"));
    }

    @Test
    public void testMobileExtraConfigValidation() {
        // Valid configuration
        MobileExtraConfig validConfig = new MobileExtraConfig();
        validConfig.setLockResolution(true);
        try {
            validConfig.validate();
        } catch (Exception e) {
            fail("Validation should not throw exception: " + e.getMessage());
        }
        
        // Invalid configuration - empty package name in blacklist
        MobileExtraConfig invalidConfig = new MobileExtraConfig();
        invalidConfig.setUninstallBlacklist(Arrays.asList("com.valid.app", ""));
        try {
            invalidConfig.validate();
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
        }
    }

    @Test
    public void testAppManagerRuleValidation() {
        // Valid rule
        AppManagerRule validRule = new AppManagerRule("White", Arrays.asList("com.test.app"));
        try {
            validRule.validate();
        } catch (Exception e) {
            fail("Validation should not throw exception: " + e.getMessage());
        }
        
        // Invalid rule - empty package name
        AppManagerRule invalidRule = new AppManagerRule("White", Arrays.asList("com.valid.app", ""));
        try {
            invalidRule.validate();
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
        }
    }

    @Test
    public void testAppManagerRuleToMap() {
        AppManagerRule rule = new AppManagerRule(
            "Black",
            Arrays.asList("com.malicious.app", "com.unwanted.app")
        );
        
        Map<String, Object> map = rule.toMap();
        
        assertNotNull(map);
        assertEquals("Black", map.get("RuleType"));
        assertTrue(map.containsKey("AppPackageNameList"));
        
        @SuppressWarnings("unchecked")
        List<String> packageList = (List<String>) map.get("AppPackageNameList");
        assertEquals(2, packageList.size());
        assertTrue(packageList.contains("com.malicious.app"));
    }

    @Test
    public void testMobileSimulateConfigValidation() {
        // Valid configuration
        MobileSimulateConfig validConfig = new MobileSimulateConfig(
            true,
            "/tmp/device_info",
            MobileSimulateMode.PROPERTIES_ONLY,
            "ctx-123"
        );
        try {
            validConfig.validate();
        } catch (Exception e) {
            fail("Validation should not throw exception: " + e.getMessage());
        }
        
        // Invalid configuration - simulate enabled but no path
        MobileSimulateConfig invalidConfig = new MobileSimulateConfig();
        invalidConfig.setSimulate(true);
        invalidConfig.setSimulatePath(null);
        try {
            invalidConfig.validate();
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
        }
    }

    @Test
    public void testMobileSimulateConfigToMap() {
        MobileSimulateConfig config = new MobileSimulateConfig(
            true,
            "/tmp/mobile_info",
            MobileSimulateMode.ALL,
            "device-ctx-456"
        );
        
        Map<String, Object> map = config.toMap();
        
        assertNotNull(map);
        assertEquals(true, map.get("Simulate"));
        assertEquals("/tmp/mobile_info", map.get("SimulatePath"));
        assertEquals("All", map.get("SimulateMode"));
        assertEquals("device-ctx-456", map.get("SimulatedContextId"));
    }

    @Test
    public void testMobileSimulateModeEnum() {
        assertEquals("PropertiesOnly", MobileSimulateMode.PROPERTIES_ONLY.getValue());
        assertEquals("SensorsOnly", MobileSimulateMode.SENSORS_ONLY.getValue());
        assertEquals("PackagesOnly", MobileSimulateMode.PACKAGES_ONLY.getValue());
        assertEquals("ServicesOnly", MobileSimulateMode.SERVICES_ONLY.getValue());
        assertEquals("All", MobileSimulateMode.ALL.getValue());
        
        // Test fromValue
        assertEquals(MobileSimulateMode.ALL, MobileSimulateMode.fromValue("All"));
        assertEquals(MobileSimulateMode.PROPERTIES_ONLY, MobileSimulateMode.fromValue("PropertiesOnly"));

        try {
            MobileSimulateMode.fromValue("InvalidMode");
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
        }
    }

    @Test
    public void testExtraConfigsFromMap() {
        // Create original config
        MobileExtraConfig originalMobile = new MobileExtraConfig();
        originalMobile.setLockResolution(true);
        originalMobile.setHideNavigationBar(false);
        
        ExtraConfigs original = new ExtraConfigs(originalMobile);
        
        // Convert to map and back
        Map<String, Object> map = original.toMap();
        ExtraConfigs restored = ExtraConfigs.fromMap(map);
        
        assertNotNull(restored);
        assertNotNull(restored.getMobile());
        assertEquals(true, restored.getMobile().getLockResolution());
        assertEquals(false, restored.getMobile().getHideNavigationBar());
    }

    @Test
    public void testMobileExtraConfigFromMap() {
        // Create original config with all fields
        AppManagerRule appRule = new AppManagerRule("White", Arrays.asList("com.test.app"));
        MobileSimulateConfig simConfig = new MobileSimulateConfig(
            true, "/tmp/info", MobileSimulateMode.ALL, "ctx-789"
        );
        
        MobileExtraConfig original = new MobileExtraConfig();
        original.setLockResolution(true);
        original.setAppManagerRule(appRule);
        original.setHideNavigationBar(true);
        original.setUninstallBlacklist(Arrays.asList("com.protected.app"));
        original.setSimulateConfig(simConfig);
        
        // Convert to map and back
        Map<String, Object> map = original.toMap();
        MobileExtraConfig restored = MobileExtraConfig.fromMap(map);
        
        assertNotNull(restored);
        assertTrue(restored.getLockResolution());
        assertTrue(restored.getHideNavigationBar());
        assertNotNull(restored.getAppManagerRule());
        assertEquals("White", restored.getAppManagerRule().getRuleType());
        assertNotNull(restored.getUninstallBlacklist());
        assertEquals(1, restored.getUninstallBlacklist().size());
        assertNotNull(restored.getSimulateConfig());
        assertTrue(restored.getSimulateConfig().isSimulate());
        assertEquals("/tmp/info", restored.getSimulateConfig().getSimulatePath());
    }

    @Test
    public void testToStringMethods() {
        // Test ExtraConfigs toString
        MobileExtraConfig mobileConfig = new MobileExtraConfig();
        mobileConfig.setLockResolution(true);
        
        ExtraConfigs extraConfigs = new ExtraConfigs(mobileConfig);
        String str = extraConfigs.toString();
        assertNotNull(str);
        assertTrue(str.contains("ExtraConfigs"));
        
        // Test MobileExtraConfig toString
        String mobileStr = mobileConfig.toString();
        assertNotNull(mobileStr);
        assertTrue(mobileStr.contains("MobileExtraConfig"));
        assertTrue(mobileStr.contains("lockResolution=true"));
        
        // Test AppManagerRule toString
        AppManagerRule rule = new AppManagerRule("White", Arrays.asList("com.test.app"));
        String ruleStr = rule.toString();
        assertNotNull(ruleStr);
        assertTrue(ruleStr.contains("AppManagerRule"));
        assertTrue(ruleStr.contains("White"));
        
        // Test MobileSimulateConfig toString
        MobileSimulateConfig simConfig = new MobileSimulateConfig(
            true, "/tmp/info", MobileSimulateMode.ALL, "ctx-123"
        );
        String simStr = simConfig.toString();
        assertNotNull(simStr);
        assertTrue(simStr.contains("MobileSimulateConfig"));
        assertTrue(simStr.contains("simulate=true"));
    }
}

