/**
 * Unit tests for extra configurations types and validation functions.
 */

import {
  AppManagerRule,
  MobileExtraConfig,
  MobileSimulateConfig,
  MobileSimulateMode,
  ExtraConfigs,
  validateAppManagerRule,
  validateMobileExtraConfig,
  validateMobileSimulateConfig,
  validateExtraConfigs,
  extraConfigsToJSON,
  extraConfigsFromJSON,
} from '../../src/types/extra-configs';

describe('Extra Configurations Types', () => {
  describe('AppManagerRule', () => {
    it('should create valid whitelist rule', () => {
      const rule: AppManagerRule = {
        ruleType: 'White',
        appPackageNameList: ['com.example.app1', 'com.example.app2'],
      };

      expect(() => validateAppManagerRule(rule)).not.toThrow();
    });

    it('should create valid blacklist rule', () => {
      const rule: AppManagerRule = {
        ruleType: 'Black',
        appPackageNameList: ['com.malware.app', 'com.unwanted.app'],
      };

      expect(() => validateAppManagerRule(rule)).not.toThrow();
    });

    it('should validate rule type', () => {
      const rule = {
        ruleType: 'Invalid' as any,
        appPackageNameList: ['com.example.app'],
      };

      expect(() => validateAppManagerRule(rule)).toThrow(
        'Invalid ruleType: Invalid. Must be "White" or "Black"'
      );
    });

    it('should validate package name list', () => {
      const rule = {
        ruleType: 'White' as const,
        appPackageNameList: 'not-an-array' as any,
      };

      expect(() => validateAppManagerRule(rule)).toThrow(
        'AppManagerRule appPackageNameList must be an array'
      );
    });

    it('should validate package name types', () => {
      const rule: AppManagerRule = {
        ruleType: 'White',
        appPackageNameList: [123 as any, 'com.example.app'],
      };

      expect(() => validateAppManagerRule(rule)).toThrow(
        'AppManagerRule appPackageNameList items must be strings'
      );
    });
  });

  describe('MobileSimulateConfig', () => {
    it('should create valid simulate config with PropertiesOnly mode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulateMode: MobileSimulateMode.PropertiesOnly,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config with SensorsOnly mode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulateMode: MobileSimulateMode.SensorsOnly,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config with PackagesOnly mode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulateMode: MobileSimulateMode.PackagesOnly,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config with ServicesOnly mode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulateMode: MobileSimulateMode.ServicesOnly,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config with All mode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulateMode: MobileSimulateMode.All,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config without mode (defaults to PropertiesOnly)', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should create valid simulate config with simulate disabled', () => {
      const config: MobileSimulateConfig = {
        simulate: false,
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should validate simulate type', () => {
      const config = {
        simulate: 'true' as any,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).toThrow(
        'MobileSimulateConfig simulate must be a boolean'
      );
    });

    it('should validate simulateMode type', () => {
      const config = {
        simulate: true,
        simulateMode: 'InvalidMode' as any,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).toThrow(
        'Invalid simulateMode: InvalidMode'
      );
    });

    it('should validate simulatedContextId type', () => {
      const config = {
        simulate: true,
        simulateMode: MobileSimulateMode.PropertiesOnly,
        simulatedContextId: 123 as any,
      };

      expect(() => validateMobileSimulateConfig(config)).toThrow(
        'MobileSimulateConfig simulatedContextId must be a string'
      );
    });

    it('should allow undefined simulateMode', () => {
      const config: MobileSimulateConfig = {
        simulate: true,
        simulatedContextId: 'test-context-id',
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });

    it('should allow undefined simulatedContextId', () => {
      const config: MobileSimulateConfig = {
        simulate: false,
      };

      expect(() => validateMobileSimulateConfig(config)).not.toThrow();
    });
  });

  describe('MobileExtraConfig', () => {
    it('should create comprehensive mobile config', () => {
      const config: MobileExtraConfig = {
        lockResolution: true,
        hideNavigationBar: true,
        uninstallBlacklist: ['com.android.systemui', 'com.android.settings'],
        appManagerRule: {
          ruleType: 'White',
          appPackageNameList: ['com.example.app1', 'com.example.app2'],
        },
      };

      expect(() => validateMobileExtraConfig(config)).not.toThrow();
    });

    it('should create minimal mobile config', () => {
      const config: MobileExtraConfig = {
        lockResolution: false,
        hideNavigationBar: true,
        uninstallBlacklist: ['com.android.systemui'],
      };

      expect(() => validateMobileExtraConfig(config)).not.toThrow();
    });

    it('should validate lockResolution type', () => {
      const config = {
        lockResolution: 'true' as any,
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'MobileExtraConfig lockResolution must be a boolean'
      );
    });

    it('should validate hideNavigationBar type', () => {
      const config = {
        lockResolution: true,
        hideNavigationBar: 'true' as any,
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'MobileExtraConfig hideNavigationBar must be a boolean'
      );
    });

    it('should validate uninstallBlacklist type', () => {
      const config = {
        lockResolution: true,
        uninstallBlacklist: 'com.android.systemui' as any,
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'MobileExtraConfig uninstallBlacklist must be an array'
      );
    });

    it('should validate uninstallBlacklist items', () => {
      const config: MobileExtraConfig = {
        lockResolution: true,
        uninstallBlacklist: ['', 'com.android.systemui'],
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'MobileExtraConfig uninstallBlacklist items must be non-empty strings'
      );
    });

    it('should validate appManagerRule if present', () => {
      const config: MobileExtraConfig = {
        lockResolution: true,
        appManagerRule: {
          ruleType: 'Invalid' as any,
          appPackageNameList: ['com.example.app'],
        },
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'Invalid ruleType: Invalid. Must be "White" or "Black"'
      );
    });

    it('should create mobile config with simulateConfig', () => {
      const config: MobileExtraConfig = {
        lockResolution: false,
        hideNavigationBar: false,
        simulateConfig: {
          simulate: true,
          simulateMode: MobileSimulateMode.PropertiesOnly,
          simulatedContextId: 'test-context-id',
        },
      };

      expect(() => validateMobileExtraConfig(config)).not.toThrow();
    });

    it('should validate simulateConfig if present', () => {
      const config: MobileExtraConfig = {
        lockResolution: true,
        simulateConfig: {
          simulate: 'true' as any,
          simulatedContextId: 'test-context-id',
        },
      };

      expect(() => validateMobileExtraConfig(config)).toThrow(
        'MobileSimulateConfig simulate must be a boolean'
      );
    });

    it('should create comprehensive mobile config with all features', () => {
      const config: MobileExtraConfig = {
        lockResolution: true,
        hideNavigationBar: true,
        uninstallBlacklist: ['com.android.systemui'],
        appManagerRule: {
          ruleType: 'White',
          appPackageNameList: ['com.example.app'],
        },
        simulateConfig: {
          simulate: true,
          simulateMode: MobileSimulateMode.All,
          simulatedContextId: 'test-context-id',
        },
      };

      expect(() => validateMobileExtraConfig(config)).not.toThrow();
    });
  });

  describe('ExtraConfigs', () => {
    it('should validate extra configs with mobile config', () => {
      const extraConfigs: ExtraConfigs = {
        mobile: {
          lockResolution: true,
          hideNavigationBar: false,
          uninstallBlacklist: ['com.android.systemui'],
          appManagerRule: {
            ruleType: 'White',
            appPackageNameList: ['com.example.app'],
          },
        },
      };

      expect(() => validateExtraConfigs(extraConfigs)).not.toThrow();
    });

    it('should validate empty extra configs', () => {
      const extraConfigs: ExtraConfigs = {};

      expect(() => validateExtraConfigs(extraConfigs)).not.toThrow();
    });

    it('should validate extra configs with invalid mobile config', () => {
      const extraConfigs: ExtraConfigs = {
        mobile: {
          lockResolution: 'invalid' as any,
        },
      };

      expect(() => validateExtraConfigs(extraConfigs)).toThrow(
        'MobileExtraConfig lockResolution must be a boolean'
      );
    });
  });

  describe('JSON Serialization', () => {
    it('should serialize extra configs to JSON', () => {
      const extraConfigs: ExtraConfigs = {
        mobile: {
          lockResolution: true,
          hideNavigationBar: true,
          uninstallBlacklist: ['com.android.systemui', 'com.android.settings'],
          appManagerRule: {
            ruleType: 'White',
            appPackageNameList: ['com.example.app1', 'com.example.app2'],
          },
        },
      };

      const json = extraConfigsToJSON(extraConfigs);
      const parsed = JSON.parse(json);

      expect(parsed.mobile.lockResolution).toBe(true);
      expect(parsed.mobile.hideNavigationBar).toBe(true);
      expect(parsed.mobile.uninstallBlacklist).toEqual([
        'com.android.systemui',
        'com.android.settings',
      ]);
      expect(parsed.mobile.appManagerRule.ruleType).toBe('White');
      expect(parsed.mobile.appManagerRule.appPackageNameList).toEqual([
        'com.example.app1',
        'com.example.app2',
      ]);
    });

    it('should serialize empty extra configs', () => {
      const json = extraConfigsToJSON(undefined);
      expect(json).toBe('');

      const json2 = extraConfigsToJSON(null);
      expect(json2).toBe('');
    });

    it('should deserialize extra configs from JSON', () => {
      const jsonStr = JSON.stringify({
        mobile: {
          lockResolution: false,
          hideNavigationBar: false,
          uninstallBlacklist: ['com.android.systemui'],
          appManagerRule: {
            ruleType: 'Black',
            appPackageNameList: ['com.malware.app'],
          },
        },
      });

      const extraConfigs = extraConfigsFromJSON(jsonStr);

      expect(extraConfigs).toBeDefined();
      expect(extraConfigs!.mobile!.lockResolution).toBe(false);
      expect(extraConfigs!.mobile!.hideNavigationBar).toBe(false);
      expect(extraConfigs!.mobile!.uninstallBlacklist).toEqual(['com.android.systemui']);
      expect(extraConfigs!.mobile!.appManagerRule!.ruleType).toBe('Black');
      expect(extraConfigs!.mobile!.appManagerRule!.appPackageNameList).toEqual(['com.malware.app']);
    });

    it('should handle empty JSON string', () => {
      expect(extraConfigsFromJSON('')).toBeNull();
      expect(extraConfigsFromJSON('   ')).toBeNull();
    });

    it('should throw error for invalid JSON', () => {
      expect(() => extraConfigsFromJSON('invalid json')).toThrow(
        'Failed to parse ExtraConfigs JSON:'
      );
    });

    it('should handle round-trip serialization', () => {
      const originalConfig: ExtraConfigs = {
        mobile: {
          lockResolution: true,
          hideNavigationBar: true,
          uninstallBlacklist: ['com.android.systemui'],
          appManagerRule: {
            ruleType: 'White',
            appPackageNameList: ['com.example.app'],
          },
        },
      };

      const json = extraConfigsToJSON(originalConfig);
      const deserializedConfig = extraConfigsFromJSON(json);

      expect(deserializedConfig).toEqual(originalConfig);
    });

    it('should serialize mobile config with simulateConfig', () => {
      const extraConfigs: ExtraConfigs = {
        mobile: {
          lockResolution: false,
          hideNavigationBar: false,
          simulateConfig: {
            simulate: true,
            simulateMode: MobileSimulateMode.PropertiesOnly,
            simulatedContextId: 'test-context-id-123',
          },
        },
      };

      const json = extraConfigsToJSON(extraConfigs);
      const parsed = JSON.parse(json);

      expect(parsed.mobile.simulateConfig.simulate).toBe(true);
      expect(parsed.mobile.simulateConfig.simulateMode).toBe('PropertiesOnly');
      expect(parsed.mobile.simulateConfig.simulatedContextId).toBe('test-context-id-123');
    });

    it('should serialize mobile config with all simulate modes', () => {
      const modes = [
        MobileSimulateMode.PropertiesOnly,
        MobileSimulateMode.SensorsOnly,
        MobileSimulateMode.PackagesOnly,
        MobileSimulateMode.ServicesOnly,
        MobileSimulateMode.All,
      ];

      modes.forEach((mode) => {
        const extraConfigs: ExtraConfigs = {
          mobile: {
            lockResolution: false,
            simulateConfig: {
              simulate: true,
              simulateMode: mode,
              simulatedContextId: 'test-context-id',
            },
          },
        };

        const json = extraConfigsToJSON(extraConfigs);
        const parsed = JSON.parse(json);

        expect(parsed.mobile.simulateConfig.simulateMode).toBe(mode);
      });
    });

    it('should handle round-trip serialization with simulateConfig', () => {
      const originalConfig: ExtraConfigs = {
        mobile: {
          lockResolution: true,
          hideNavigationBar: true,
          uninstallBlacklist: ['com.android.systemui'],
          appManagerRule: {
            ruleType: 'White',
            appPackageNameList: ['com.example.app'],
          },
          simulateConfig: {
            simulate: true,
            simulateMode: MobileSimulateMode.All,
            simulatedContextId: 'test-context-id',
          },
        },
      };

      const json = extraConfigsToJSON(originalConfig);
      const deserializedConfig = extraConfigsFromJSON(json);

      expect(deserializedConfig).toEqual(originalConfig);
    });

    it('should deserialize mobile config with simulateConfig from JSON', () => {
      const jsonStr = JSON.stringify({
        mobile: {
          lockResolution: false,
          hideNavigationBar: false,
          simulateConfig: {
            simulate: true,
            simulateMode: 'SensorsOnly',
            simulatedContextId: 'sensor-context-id',
          },
        },
      });

      const extraConfigs = extraConfigsFromJSON(jsonStr);

      expect(extraConfigs).toBeDefined();
      expect(extraConfigs!.mobile!.simulateConfig).toBeDefined();
      expect(extraConfigs!.mobile!.simulateConfig!.simulate).toBe(true);
      expect(extraConfigs!.mobile!.simulateConfig!.simulateMode).toBe('SensorsOnly');
      expect(extraConfigs!.mobile!.simulateConfig!.simulatedContextId).toBe('sensor-context-id');
    });
  });
});
