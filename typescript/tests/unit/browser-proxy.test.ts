import { BrowserOption, BrowserOptionClass, BrowserProxyClass } from '../../src/browser/browser';

describe('BrowserProxy Unit Tests', () => {
  describe('BrowserProxyClass', () => {
    test('should create custom proxy with all parameters', () => {
      const proxy = new BrowserProxyClass(
        'custom',
        'http://proxy.example.com:8080',
        'testuser',
        'testpass'
      );

      expect(proxy.type).toBe('custom');
      expect(proxy.server).toBe('http://proxy.example.com:8080');
      expect(proxy.username).toBe('testuser');
      expect(proxy.password).toBe('testpass');
      expect(proxy.strategy).toBeUndefined();
      expect(proxy.pollsize).toBeUndefined();
    });

    test('should create wuying restricted proxy', () => {
      const proxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'restricted');

      expect(proxy.type).toBe('wuying');
      expect(proxy.server).toBeUndefined();
      expect(proxy.username).toBeUndefined();
      expect(proxy.password).toBeUndefined();
      expect(proxy.strategy).toBe('restricted');
      expect(proxy.pollsize).toBeUndefined();
    });

    test('should create wuying polling proxy with custom pollsize', () => {
      const proxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling', 15);

      expect(proxy.type).toBe('wuying');
      expect(proxy.strategy).toBe('polling');
      expect(proxy.pollsize).toBe(15);
    });

    test('should use default pollsize for polling strategy', () => {
      const proxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling');

      expect(proxy.pollsize).toBeUndefined();
    });

    test('should throw error for invalid proxy type', () => {
      expect(() => {
        new BrowserProxyClass('invalid' as any);
      }).toThrow('proxy_type must be custom or wuying');
    });

    test('should throw error for custom proxy without server', () => {
      expect(() => {
        new BrowserProxyClass('custom');
      }).toThrow('server is required for custom proxy type');
    });

    test('should throw error for wuying proxy without strategy', () => {
      expect(() => {
        new BrowserProxyClass('wuying');
      }).toThrow('strategy is required for wuying proxy type');
    });

    test('should throw error for wuying proxy with invalid strategy', () => {
      expect(() => {
        new BrowserProxyClass('wuying', undefined, undefined, undefined, 'invalid' as any);
      }).toThrow('strategy must be restricted or polling for wuying proxy type');
    });

    test('should throw error for polling strategy with zero pollsize', () => {
      expect(() => {
        new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling', 0);
      }).toThrow('pollsize must be greater than 0 for polling strategy');
    });

    test('should throw error for polling strategy with negative pollsize', () => {
      expect(() => {
        new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling', -1);
      }).toThrow('pollsize must be greater than 0 for polling strategy');
    });
  });

  describe('BrowserProxyClass.toMap', () => {
    test('should serialize custom proxy correctly', () => {
      const proxy = new BrowserProxyClass(
        'custom',
        'http://proxy.example.com:8080',
        'testuser',
        'testpass'
      );

      const proxyMap = proxy.toMap();

      expect(proxyMap.type).toBe('custom');
      expect(proxyMap.server).toBe('http://proxy.example.com:8080');
      expect(proxyMap.username).toBe('testuser');
      expect(proxyMap.password).toBe('testpass');
      expect(proxyMap.strategy).toBeUndefined();
      expect(proxyMap.pollsize).toBeUndefined();
    });

    test('should serialize custom proxy without credentials', () => {
      const proxy = new BrowserProxyClass('custom', 'http://proxy.example.com:8080');

      const proxyMap = proxy.toMap();

      expect(proxyMap.type).toBe('custom');
      expect(proxyMap.server).toBe('http://proxy.example.com:8080');
      expect(proxyMap.username).toBeUndefined();
      expect(proxyMap.password).toBeUndefined();
    });

    test('should serialize wuying restricted proxy correctly', () => {
      const proxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'restricted');

      const proxyMap = proxy.toMap();

      expect(proxyMap.type).toBe('wuying');
      expect(proxyMap.strategy).toBe('restricted');
      expect(proxyMap.server).toBeUndefined();
      expect(proxyMap.username).toBeUndefined();
      expect(proxyMap.password).toBeUndefined();
      expect(proxyMap.pollsize).toBeUndefined();
    });

    test('should serialize wuying polling proxy correctly', () => {
      const proxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling', 15);

      const proxyMap = proxy.toMap();

      expect(proxyMap.type).toBe('wuying');
      expect(proxyMap.strategy).toBe('polling');
      expect(proxyMap.pollsize).toBe(15);
    });
  });

  describe('BrowserProxyClass.fromMap', () => {
    test('should deserialize custom proxy correctly', () => {
      const proxyMap = {
        type: 'custom',
        server: 'http://proxy.example.com:8080',
        username: 'testuser',
        password: 'testpass'
      };

      const proxy = BrowserProxyClass.fromMap(proxyMap);

      expect(proxy).not.toBeNull();
      expect(proxy?.type).toBe('custom');
      expect(proxy?.server).toBe('http://proxy.example.com:8080');
      expect(proxy?.username).toBe('testuser');
      expect(proxy?.password).toBe('testpass');
    });

    test('should deserialize wuying restricted proxy correctly', () => {
      const proxyMap = {
        type: 'wuying',
        strategy: 'restricted'
      };

      const proxy = BrowserProxyClass.fromMap(proxyMap);

      expect(proxy).not.toBeNull();
      expect(proxy?.type).toBe('wuying');
      expect(proxy?.strategy).toBe('restricted');
      expect(proxy?.pollsize).toBe(10); // default value
    });

    test('should deserialize wuying polling proxy correctly', () => {
      const proxyMap = {
        type: 'wuying',
        strategy: 'polling',
        pollsize: 20
      };

      const proxy = BrowserProxyClass.fromMap(proxyMap);

      expect(proxy).not.toBeNull();
      expect(proxy?.type).toBe('wuying');
      expect(proxy?.strategy).toBe('polling');
      expect(proxy?.pollsize).toBe(20);
    });

    test('should return null for empty map', () => {
      const proxy = BrowserProxyClass.fromMap(null);
      expect(proxy).toBeNull();

      const proxy2 = BrowserProxyClass.fromMap(undefined);
      expect(proxy2).toBeNull();

      const proxy3 = BrowserProxyClass.fromMap({});
      expect(proxy3).toBeNull();
    });

    test('should return null for missing type', () => {
      const proxyMap = {
        server: 'http://proxy.example.com:8080'
      };

      const proxy = BrowserProxyClass.fromMap(proxyMap);
      expect(proxy).toBeNull();
    });

    test('should throw error for unsupported proxy type', () => {
      const proxyMap = {
        type: 'unsupported'
      };

      expect(() => {
        BrowserProxyClass.fromMap(proxyMap);
      }).toThrow('Unsupported proxy type: unsupported');
    });
  });
});

describe('BrowserOption with Proxies', () => {
  test('should create BrowserOption with custom proxy', () => {
    const customProxy = new BrowserProxyClass(
      'custom',
      'http://proxy.example.com:8080',
      'testuser',
      'testpass'
    );
    const browserOption: BrowserOption = {
      useStealth: true,
      userAgent: 'Custom User Agent',
      viewport: { width: 1920, height: 1080 },
      screen: { width: 1920, height: 1080 },
      fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['en-US'] },
      proxies: [customProxy]
    };
    const option = new BrowserOptionClass();
    option.fromMap(browserOption as Record<string, any>);

    expect(option.useStealth).toBe(true);
    expect(option.userAgent).toBe('Custom User Agent');
    expect(option.proxies).toHaveLength(1);
    expect(option.proxies?.[0].type).toBe('custom');
    expect(option.proxies?.[0].server).toBe('http://proxy.example.com:8080');
  });

  test('should create BrowserOption with wuying proxy', () => {
    const wuyingProxy = new BrowserProxyClass('wuying', undefined, undefined, undefined, 'polling', 15);
    const browserOption: BrowserOption = {
      useStealth: false,
      userAgent: 'Wuying User Agent',
      viewport: { width: 1366, height: 768 },
      screen: { width: 1366, height: 768 },
      fingerprint: { devices: ['mobile'], operatingSystems: ['linux'], locales: ['zh-CN'] },
      proxies: [wuyingProxy]
    };
    const option = new BrowserOptionClass();
    option.fromMap(browserOption as Record<string, any>);

    expect(option.useStealth).toBe(false);
    expect(option.userAgent).toBe('Wuying User Agent');
    expect(option.proxies).toHaveLength(1);
    expect(option.proxies?.[0].type).toBe('wuying');
    expect(option.proxies?.[0].strategy).toBe('polling');
    expect(option.proxies?.[0].pollsize).toBe(15);
  });

  test('should throw error for multiple proxies', () => {
    const proxy1 = new BrowserProxyClass('custom', 'http://proxy1.com');
    const proxy2 = new BrowserProxyClass('custom', 'http://proxy2.com');

    expect(() => {
      new BrowserOptionClass(false, undefined, undefined, undefined, undefined, undefined, false, false, [proxy1, proxy2]);
    }).toThrow('proxies list length must be limited to 1');
  });

  test('should throw error for non-array proxies', () => {
    const proxy = new BrowserProxyClass('custom', 'http://proxy.com');

    expect(() => {
      new BrowserOptionClass(false, undefined, undefined, undefined, undefined, undefined, false, false, proxy as any);
    }).toThrow('proxies must be a list');
  });

  test('should serialize BrowserOption with proxies correctly', () => {
    const customProxy = new BrowserProxyClass('custom', 'http://proxy.example.com:8080');
    const browserOption: BrowserOption = {
      useStealth: true,
      userAgent: 'Serialization Test Agent',
      viewport: { width: 1280, height: 720 },
      screen: { width: 1280, height: 720 },
      fingerprint: { devices: ['desktop'], operatingSystems: ['macos'], locales: ['fr-FR'] },
      proxies: [customProxy]
    };
    const option = new BrowserOptionClass();
    option.fromMap(browserOption as Record<string, any>);

    const optionMap = option.toMap();

    expect(optionMap.useStealth).toBe(true);
    expect(optionMap.userAgent).toBe('Serialization Test Agent');
    expect(optionMap.proxies).toBeDefined();
    expect(optionMap.proxies).toHaveLength(1);
    expect(optionMap.proxies[0].type).toBe('custom');
    expect(optionMap.proxies[0].server).toBe('http://proxy.example.com:8080');
  });

  test('should deserialize BrowserOption with proxies correctly', () => {
    const browserOption: BrowserOption = {
      useStealth: true,
      userAgent: 'Deserialization Test Agent',
      viewport: { width: 1600, height: 900 },
      screen: { width: 1600, height: 900 },
      fingerprint: { devices: ['desktop'], operatingSystems: ['windows'], locales: ['de-DE'] },
      proxies: [
        new BrowserProxyClass('wuying', undefined, undefined, undefined, 'restricted')
      ]
    };

    const option = new BrowserOptionClass();
    option.fromMap(browserOption as Record<string, any>);

    expect(option.useStealth).toBe(true);
    expect(option.userAgent).toBe('Deserialization Test Agent');
    expect(option.viewport?.width).toBe(1600);
    expect(option.viewport?.height).toBe(900);
    expect(option.proxies).toHaveLength(1);
    expect(option.proxies?.[0].type).toBe('wuying');
    expect(option.proxies?.[0].strategy).toBe('restricted');
  });

  test('should throw error for multiple proxies during deserialization', () => {
    const browserOption: BrowserOption = {
      useStealth: false,
      userAgent: 'Multiple Proxies Test Agent',
      viewport: { width: 800, height: 600 },
      screen: { width: 800, height: 600 },
      fingerprint: { devices: ['mobile'], operatingSystems: ['android'], locales: ['ja-JP'] },
      proxies: [
        new BrowserProxyClass('custom', 'http://proxy1.com'),
        new BrowserProxyClass('custom', 'http://proxy2.com')
      ]
    };

    const option = new BrowserOptionClass();
    expect(() => {
      option.fromMap(browserOption as Record<string, any>);
    }).toThrow('proxies list length must be limited to 1');
  });
}); 