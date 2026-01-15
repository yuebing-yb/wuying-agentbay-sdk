import { Code } from '../../src/code/code';

class MockSession {
  public callMcpTool = jest.fn();
  public sessionId = 'mock-session-id';
}

describe('Code aliases', () => {
  let code: Code;
  let mockSession: MockSession;

  beforeEach(() => {
    mockSession = new MockSession() as any;
    code = new Code(mockSession as any);
  });

  it('run() should call runCode()', async () => {
    const mockResult = {
      requestId: 'request-123',
      success: true,
      data: { content: [{ text: 'OK\n' }] },
      errorMessage: undefined,
    };
    mockSession.callMcpTool.mockResolvedValue(mockResult);

    await (code as any).run("print('OK')", 'python', 10);

    expect(mockSession.callMcpTool).toHaveBeenCalledWith('run_code', {
      code: "print('OK')",
      language: 'python',
      timeout_s: 10,
    }, false);
  });

  it('execute() should call runCode()', async () => {
    const mockResult = {
      requestId: 'request-123',
      success: true,
      data: { content: [{ text: 'OK\n' }] },
      errorMessage: undefined,
    };
    mockSession.callMcpTool.mockResolvedValue(mockResult);

    await (code as any).execute("print('OK')", 'python');

    expect(mockSession.callMcpTool).toHaveBeenCalledWith('run_code', {
      code: "print('OK')",
      language: 'python',
      timeout_s: 60,
    }, false);
  });
});


