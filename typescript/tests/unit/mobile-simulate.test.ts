/**
 * Unit tests for MobileSimulateService module.
 * 
 * This test suite covers all functionality of the MobileSimulateService class,
 * including initialization, configuration management, mobile info operations,
 * and context management.
 */

import { MobileSimulateService, type MobileSimulateUploadResult } from '../../src/mobile-simulate';
import { ContextSync } from '../../src/context-sync';
import { Context, ContextService } from '../../src/context';
import { MobileSimulateMode } from '../../src/types/extra-configs';

// Mock AgentBay
interface MockAgentBay {
  context: ContextService;
}

// Mock ContextService
class MockContextService {
  get = jest.fn();
  listFiles = jest.fn();
  getFileUploadUrl = jest.fn();
}

// Mock node-fetch
jest.mock('node-fetch', () => jest.fn());

import fetch from 'node-fetch';

describe('MobileSimulateService', () => {
  let mockAgentBay: MockAgentBay;
  let mockContextService: MockContextService;
  let mobileSimulateService: MobileSimulateService;

  beforeEach(() => {
    mockContextService = new MockContextService();
    mockAgentBay = {
      context: mockContextService as any
    };
    mobileSimulateService = new MobileSimulateService(mockAgentBay as any);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    test('should throw error if agentBay is not provided', () => {
      expect(() => new MobileSimulateService(null as any)).toThrow('agentBay is required');
    });

    test('should throw error if agentBay.context is not provided', () => {
      expect(() => new MobileSimulateService({} as any)).toThrow('agentBay.context is required');
    });

    test('should create instance successfully with valid agentBay', () => {
      expect(mobileSimulateService).toBeInstanceOf(MobileSimulateService);
    });

    test('should initialize with default values', () => {
      expect(mobileSimulateService.getSimulateEnable()).toBe(false);
      expect(mobileSimulateService.getSimulateMode()).toBe(MobileSimulateMode.PropertiesOnly);
      expect(mobileSimulateService.getSimulateContextId()).toBeUndefined();
    });
  });

  describe('setSimulateEnable and getSimulateEnable', () => {
    test('should set and get simulate enable flag', () => {
      mobileSimulateService.setSimulateEnable(true);
      expect(mobileSimulateService.getSimulateEnable()).toBe(true);

      mobileSimulateService.setSimulateEnable(false);
      expect(mobileSimulateService.getSimulateEnable()).toBe(false);
    });

    test('should default to false', () => {
      expect(mobileSimulateService.getSimulateEnable()).toBe(false);
    });
  });

  describe('setSimulateMode and getSimulateMode', () => {
    test('should set and get simulate mode', () => {
      mobileSimulateService.setSimulateMode(MobileSimulateMode.All);
      expect(mobileSimulateService.getSimulateMode()).toBe(MobileSimulateMode.All);

      mobileSimulateService.setSimulateMode(MobileSimulateMode.SensorsOnly);
      expect(mobileSimulateService.getSimulateMode()).toBe(MobileSimulateMode.SensorsOnly);
    });

    test('should default to PropertiesOnly', () => {
      expect(mobileSimulateService.getSimulateMode()).toBe(MobileSimulateMode.PropertiesOnly);
    });

    test('should support all simulate modes', () => {
      const modes = [
        MobileSimulateMode.PropertiesOnly,
        MobileSimulateMode.SensorsOnly,
        MobileSimulateMode.PackagesOnly,
        MobileSimulateMode.ServicesOnly,
        MobileSimulateMode.All
      ];

      modes.forEach(mode => {
        mobileSimulateService.setSimulateMode(mode);
        expect(mobileSimulateService.getSimulateMode()).toBe(mode);
      });
    });
  });

  describe('setSimulateContextId and getSimulateContextId', () => {
    test('should set and get simulate context id', () => {
      const contextId = 'test-context-123';
      mobileSimulateService.setSimulateContextId(contextId);
      expect(mobileSimulateService.getSimulateContextId()).toBe(contextId);
    });

    test('should default to undefined', () => {
      expect(mobileSimulateService.getSimulateContextId()).toBeUndefined();
    });

    test('should handle empty string', () => {
      mobileSimulateService.setSimulateContextId('');
      expect(mobileSimulateService.getSimulateContextId()).toBe('');
    });
  });

  describe('getSimulateConfig', () => {
    test('should return default config', () => {
      const config = mobileSimulateService.getSimulateConfig();
      
      expect(config.simulate).toBe(false);
      expect(config.simulateMode).toBe(MobileSimulateMode.PropertiesOnly);
      expect(config.simulatedContextId).toBeUndefined();
      expect(config.simulatePath).toBeUndefined();
    });

    test('should return config with all settings', () => {
      mobileSimulateService.setSimulateEnable(true);
      mobileSimulateService.setSimulateMode(MobileSimulateMode.All);
      mobileSimulateService.setSimulateContextId('test-ctx-456');

      const config = mobileSimulateService.getSimulateConfig();
      
      expect(config.simulate).toBe(true);
      expect(config.simulateMode).toBe(MobileSimulateMode.All);
      expect(config.simulatedContextId).toBe('test-ctx-456');
    });

    test('should update config when settings change', () => {
      mobileSimulateService.setSimulateEnable(true);
      let config = mobileSimulateService.getSimulateConfig();
      expect(config.simulate).toBe(true);

      mobileSimulateService.setSimulateEnable(false);
      config = mobileSimulateService.getSimulateConfig();
      expect(config.simulate).toBe(false);
    });
  });

  describe('hasMobileInfo', () => {
    test('should throw error if contextSync is not provided', async () => {
      await expect(mobileSimulateService.hasMobileInfo(null as any)).rejects.toThrow('contextSync is required');
    });

    test('should throw error if contextSync.contextId is not provided', async () => {
      const contextSync = new ContextSync('', '/test/path');
      await expect(mobileSimulateService.hasMobileInfo(contextSync)).rejects.toThrow('contextSync.contextId is required');
    });

    test('should throw error if contextSync.path is not provided', async () => {
      const contextSync = new ContextSync('test-context-id', '');
      await expect(mobileSimulateService.hasMobileInfo(contextSync)).rejects.toThrow('contextSync.path is required');
    });

    test('should return true if mobile dev info file exists', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.listFiles.mockResolvedValue({
        success: true,
        entries: [
          { fileName: 'dev_info.json' }
        ]
      });

      const result = await mobileSimulateService.hasMobileInfo(contextSync);

      expect(result).toBe(true);
      expect(mockContextService.listFiles).toHaveBeenCalledWith(
        'test-context-id',
        '/test/path/agentbay_mobile_info/',
        1,
        50
      );
    });

    test('should return false if mobile dev info file does not exist', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.listFiles.mockResolvedValue({
        success: true,
        entries: [
          { fileName: 'other_file.json' }
        ]
      });

      const result = await mobileSimulateService.hasMobileInfo(contextSync);

      expect(result).toBe(false);
    });

    test('should return false if listFiles fails', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.listFiles.mockResolvedValue({
        success: false,
        errorMessage: 'Failed to list files'
      });

      const result = await mobileSimulateService.hasMobileInfo(contextSync);

      expect(result).toBe(false);
    });

    test('should return false if entries is empty', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.listFiles.mockResolvedValue({
        success: true,
        entries: []
      });

      const result = await mobileSimulateService.hasMobileInfo(contextSync);

      expect(result).toBe(false);
    });
  });

  describe('uploadMobileInfo', () => {
    const validMobileInfo = JSON.stringify({ model: 'SM-A505F', brand: 'Samsung' });

    test('should throw error if mobileDevInfoContent is not provided', async () => {
      await expect(mobileSimulateService.uploadMobileInfo('')).rejects.toThrow('mobileDevInfoContent is required');
    });

    test('should throw error if mobileDevInfoContent is not valid JSON', async () => {
      await expect(mobileSimulateService.uploadMobileInfo('invalid json')).rejects.toThrow('mobileDevInfoContent is not a valid JSON string');
    });

    test('should throw error if mobileDevInfoContent is malformed JSON', async () => {
      await expect(mobileSimulateService.uploadMobileInfo('{"incomplete":')).rejects.toThrow('mobileDevInfoContent is not a valid JSON string');
    });

    test('should create new context if not provided', async () => {
      mockContextService.get.mockResolvedValue({
        success: true,
        context: new Context('new-context-id', 'mobile_sim_test_123')
      });
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo);

      expect(result.success).toBe(true);
      expect(result.mobileSimulateContextId).toBe('new-context-id');
      expect(mockContextService.get).toHaveBeenCalled();
      const callArgs = mockContextService.get.mock.calls[0];
      expect(callArgs[0]).toContain('mobile_sim_');
      expect(callArgs[1]).toBe(true);
    });

    test('should use provided context sync', async () => {
      const contextSync = new ContextSync('existing-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(result.success).toBe(true);
      expect(result.mobileSimulateContextId).toBe('existing-context-id');
      expect(mockContextService.get).not.toHaveBeenCalled();
    });

    test('should throw error if contextSync is provided without contextId', async () => {
      const contextSync = new ContextSync('', '/test/path');

      await expect(mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync)).rejects.toThrow('contextSync.contextId is required');
    });

    test('should return error if failed to create context', async () => {
      mockContextService.get.mockResolvedValue({
        success: false,
        errorMessage: 'Failed to create context'
      });

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo);

      expect(result.success).toBe(false);
      expect(result.errorMessage).toBe('Failed to create context for simulate');
    });

    test('should return error if failed to get upload URL', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: false,
        errorMessage: 'Failed to get upload URL'
      });

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(result.success).toBe(false);
      expect(result.errorMessage).toBe('Failed to get upload URL');
    });

    test('should return error if upload fails', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockRejectedValue(new Error('Network error'));

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain('Network error');
    });

    test('should return error if upload response is not ok', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      } as any);

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain('Upload failed with status 500');
    });

    test('should upload successfully with valid data', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      const result = await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(result.success).toBe(true);
      expect(result.mobileSimulateContextId).toBe('test-context-id');
      const fetchCall = (fetch as jest.MockedFunction<typeof fetch>).mock.calls[0];
      expect(fetchCall[0]).toBe('https://test-upload-url.com');
      expect(fetchCall[1]).toHaveProperty('method', 'PUT');
      expect(fetchCall[1]).toHaveProperty('body');
      if (fetchCall[1]) {
        expect(fetchCall[1].body).toBeInstanceOf(Uint8Array);
      }
    });

    test('should upload with correct file path', async () => {
      const contextSync = new ContextSync('test-context-id', '/test/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      await mobileSimulateService.uploadMobileInfo(validMobileInfo, contextSync);

      expect(mockContextService.getFileUploadUrl).toHaveBeenCalledWith(
        'test-context-id',
        '/test/path/agentbay_mobile_info/dev_info.json'
      );
    });
  });

  describe('integration scenarios', () => {
    test('should handle complete workflow: configure -> upload -> get config', async () => {
      // Configure
      mobileSimulateService.setSimulateEnable(true);
      mobileSimulateService.setSimulateMode(MobileSimulateMode.All);

      // Upload
      const contextSync = new ContextSync('workflow-context-id', '/workflow/path');
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      const uploadResult = await mobileSimulateService.uploadMobileInfo(
        JSON.stringify({ model: 'TestDevice' }),
        contextSync
      );

      expect(uploadResult.success).toBe(true);

      // Get config
      const config = mobileSimulateService.getSimulateConfig();
      expect(config.simulate).toBe(true);
      expect(config.simulateMode).toBe(MobileSimulateMode.All);
      expect(config.simulatedContextId).toBeUndefined(); // External context
    });

    test('should handle workflow with internal context', async () => {
      mobileSimulateService.setSimulateEnable(true);
      mobileSimulateService.setSimulateMode(MobileSimulateMode.PropertiesOnly);

      mockContextService.get.mockResolvedValue({
        success: true,
        context: new Context('internal-context-id', 'mobile_sim_internal')
      });
      mockContextService.getFileUploadUrl.mockResolvedValue({
        success: true,
        url: 'https://test-upload-url.com'
      });
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        status: 200
      } as any);

      const uploadResult = await mobileSimulateService.uploadMobileInfo(
        JSON.stringify({ model: 'InternalDevice' })
      );

      expect(uploadResult.success).toBe(true);
      expect(uploadResult.mobileSimulateContextId).toBe('internal-context-id');

      const config = mobileSimulateService.getSimulateConfig();
      expect(config.simulatedContextId).toBe('internal-context-id'); // Internal context
    });
  });
});
