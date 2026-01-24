/**
 * Unit tests for Computer module.
 * Following TDD principles - tests first, then implementation.
 */

import { Computer, MouseButton, ScrollDirection } from '../../src/computer/computer';
import { Session } from '../../src/session';

// Mock Session interface
interface MockSession {
  callMcpTool: jest.Mock;
  getAPIKey: () => string;
  sessionId: string;
}

describe('Computer', () => {
  let mockSession: MockSession;
  let computer: Computer;

  beforeEach(() => {
    mockSession = {
      callMcpTool: jest.fn(),
      getAPIKey: () => 'test-api-key',
      sessionId: 'test-session-id'
    };
    computer = new Computer(mockSession as any);
  });

  describe('Mouse Operations', () => {
    test('clickMouse should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        errorMessage: ''
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.clickMouse(100, 200, 'left');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('click_mouse', {
        x: 100,
        y: 200,
        button: 'left'
      }, false);
      expect(result.success).toBe(true);
      expect(result.requestId).toBe('test-123');
    });

    test('clickMouse should validate button parameter', async () => {
      // Act & Assert
      await expect(computer.clickMouse(100, 200, 'invalid' as any))
        .rejects.toThrow('Invalid button');
    });

    test('moveMouse should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.moveMouse(150, 250);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('move_mouse', {
        x: 150,
        y: 250
      }, false);
      expect(result.success).toBe(true);
    });

    test('dragMouse should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.dragMouse(100, 100, 200, 200, 'left');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('drag_mouse', {
        from_x: 100,
        from_y: 100,
        to_x: 200,
        to_y: 200,
        button: 'left'
      }, false);
      expect(result.success).toBe(true);
    });

    test('scroll should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.scroll(100, 200, 'up', 3);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('scroll', {
        x: 100,
        y: 200,
        direction: 'up',
        amount: 3
      }, false);
      expect(result.success).toBe(true);
    });

    test('scroll should validate direction parameter', async () => {
      // Act & Assert
      await expect(computer.scroll(100, 200, 'invalid' as any, 1))
        .rejects.toThrow('Invalid direction');
    });

    test('clickMouse should accept MouseButton enum', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.clickMouse(100, 200, MouseButton.RIGHT);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('click_mouse', {
        x: 100,
        y: 200,
        button: 'right'
      }, false);
      expect(result.success).toBe(true);
    });

    test('clickMouse should accept MouseButton.DOUBLE_LEFT enum', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.clickMouse(100, 200, MouseButton.DOUBLE_LEFT);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('click_mouse', {
        x: 100,
        y: 200,
        button: 'double_left'
      }, false);
      expect(result.success).toBe(true);
    });

    test('dragMouse should accept MouseButton enum', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.dragMouse(100, 100, 200, 200, MouseButton.MIDDLE);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('drag_mouse', {
        from_x: 100,
        from_y: 100,
        to_x: 200,
        to_y: 200,
        button: 'middle'
      }, false);
      expect(result.success).toBe(true);
    });

    test('scroll should accept ScrollDirection enum', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.scroll(100, 200, ScrollDirection.DOWN, 5);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('scroll', {
        x: 100,
        y: 200,
        direction: 'down',
        amount: 5
      }, false);
      expect(result.success).toBe(true);
    });
  });

  describe('Keyboard Operations', () => {
    test('inputText should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.inputText('Hello World');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('input_text', {
        text: 'Hello World'
      }, false);
      expect(result.success).toBe(true);
    });

    test('pressKeys should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.pressKeys(['Ctrl', 'C'], false);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('press_keys', {
        keys: ['Ctrl', 'C'],
        hold: false
      }, false);
      expect(result.success).toBe(true);
    });

    test('releaseKeys should call MCP tool with correct parameters', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.releaseKeys(['Ctrl', 'C']);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('release_keys', {
        keys: ['Ctrl', 'C']
      }, false);
      expect(result.success).toBe(true);
    });
  });

  describe('Screen Operations', () => {
    test('betaTakeScreenshot should call MCP tool and return JPEG bytes', async () => {
      // Arrange
      const jpgHeader = Buffer.from([0xff, 0xd8, 0xff]);
      const payload = Buffer.concat([jpgHeader, Buffer.from('jpegpayload')]).toString('base64');
      const mockResult = {
        success: true,
        requestId: 'test-beta-jpg-123',
        data: JSON.stringify({
          type: "image",
          mime_type: "image/jpeg",
          width: 1280,
          height: 720,
          data: payload,
        }),
        errorMessage: '',
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.betaTakeScreenshot('jpg');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('screenshot', { format: 'jpeg' }, false);
      expect(result.success).toBe(true);
      expect(result.requestId).toBe('test-beta-jpg-123');
      expect(result.format).toBe('jpeg');
      expect(result.width).toBe(1280);
      expect(result.height).toBe(720);
      expect(Buffer.from(result.data).slice(0, 3).equals(jpgHeader)).toBe(true);
    });

    test('betaTakeScreenshot should reject non-JSON payloads', async () => {
      // Arrange
      const jpgHeader = Buffer.from([0xff, 0xd8, 0xff]);
      const payload = Buffer.concat([jpgHeader, Buffer.from('jpegpayload')]).toString('base64');
      const mockResult = {
        success: true,
        requestId: 'test-beta-non-json-123',
        data: payload,
        errorMessage: '',
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.betaTakeScreenshot('jpeg');

      // Assert
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain('non-JSON');
      expect(result.data.length).toBe(0);
    });
  });

  describe('Screen Operations', () => {
    test('getCursorPosition should call MCP tool and return position', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: '{"x":100,"y":200}'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.getCursorPosition();

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('get_cursor_position', {}, false);
      expect(result.x).toBe(100);
      expect(result.y).toBe(200);
    });

    test('getScreenSize should call MCP tool and return screen info', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: '{"width":1920,"height":1080,"dpiScalingFactor":1.0}'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.getScreenSize();

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('get_screen_size', {}, false);
      expect(result.width).toBe(1920);
      expect(result.height).toBe(1080);
      expect(result.dpiScalingFactor).toBe(1.0);
    });

    test('screenshot should call MCP tool and return URL', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: 'https://example.com/screenshot.png'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.screenshot();

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('system_screenshot', {}, false);
      expect(result.data).toBe('https://example.com/screenshot.png');
    });
  });

  describe('Error Handling', () => {
    test('should handle MCP tool errors gracefully', async () => {
      // Arrange
      const mockError = new Error('MCP tool failed');
      mockSession.callMcpTool.mockRejectedValue(mockError);

      // Act
      const result = await computer.clickMouse(100, 200);

      // Assert
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain('MCP tool failed');
    });

    test('should handle invalid JSON response', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: 'invalid json'
      };
      mockSession.callMcpTool.mockResolvedValue(mockResult);

      // Act
      const result = await computer.getCursorPosition();

      // Assert
      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain('Failed to parse');
    });
  });

  describe('Application Management Operations', () => {
    test('getInstalledApps should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify([
          { name: 'App1', start_cmd: 'app1.exe' },
          { name: 'App2', start_cmd: 'app2.exe' }
        ])
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.getInstalledApps();

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('get_installed_apps', {
        start_menu: true,
        desktop: false,
        ignore_system_apps: true
      }, false);
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(2);
      expect(result.data[0].name).toBe('App1');
    });

    test('startApp should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify([{ pname: 'app1', pid: 1234 }])
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.startApp('app1.exe');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('start_app', {
        start_cmd: 'app1.exe'
      }, false);
      expect(result.success).toBe(true);
    });

    test('stopAppByPName should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify({ success: true })
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.stopAppByPName('app1');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('stop_app_by_pname', {
        pname: 'app1'
      }, false);
      expect(result.success).toBe(true);
    });

    test('stopAppByPID should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify({ success: true })
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.stopAppByPID(1234);

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('stop_app_by_pid', {
        pid: 1234
      }, false);
      expect(result.success).toBe(true);
    });

    test('stopAppByCmd should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify({ success: true })
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.stopAppByCmd('app1.exe');

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('stop_app_by_cmd', {
        stop_cmd: 'app1.exe'
      }, false);
      expect(result.success).toBe(true);
    });

    test('listVisibleApps should call MCP tool', async () => {
      // Arrange
      const mockResult = {
        success: true,
        requestId: 'test-123',
        data: JSON.stringify([{ pname: 'app1', pid: 1234 }])
      };

      mockSession.callMcpTool = jest.fn().mockResolvedValue(mockResult);

      // Act
      const result = await computer.listVisibleApps();

      // Assert
      expect(mockSession.callMcpTool).toHaveBeenCalledWith('list_visible_apps', {}, false);
      expect(result.success).toBe(true);
      expect(result.data).toHaveLength(1);
    });

    test('application management methods should have correct signatures', async () => {
      // Verify all application management methods exist with correct signatures
      const methods = [
        'getInstalledApps',
        'startApp',
        'stopAppByPName',
        'stopAppByPID',
        'stopAppByCmd',
        'listVisibleApps'
      ];

      methods.forEach(method => {
        expect(computer).toHaveProperty(method);
        expect(typeof (computer as any)[method]).toBe('function');
      });
    });
  });
}); 