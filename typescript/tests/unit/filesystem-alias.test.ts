import { FileSystem } from '../../src/filesystem/filesystem';

class MockSession {
  public callMcpTool = jest.fn();
  public sessionId = 'mock-session-id';
}

describe('FileSystem aliases', () => {
  let fs: FileSystem;
  let mockSession: MockSession;

  beforeEach(() => {
    mockSession = new MockSession() as any;
    fs = new FileSystem(mockSession as any);
  });

  it('read() should call readFile()', async () => {
    const expected = {
      requestId: 'request-123',
      success: true,
      content: 'content',
      errorMessage: undefined,
    };
    const spy = jest.spyOn(fs as any, 'readFile').mockResolvedValue(expected);

    const result = await (fs as any).read('/tmp/a.txt');

    expect(spy).toHaveBeenCalledWith('/tmp/a.txt');
    expect(result).toBe(expected);
  });

  it('write() should call writeFile()', async () => {
    const expected = {
      requestId: 'request-123',
      success: true,
      data: true,
      errorMessage: undefined,
    };
    const spy = jest.spyOn(fs as any, 'writeFile').mockResolvedValue(expected);

    const result = await (fs as any).write('/tmp/a.txt', 'hello', 'overwrite');

    expect(spy).toHaveBeenCalledWith('/tmp/a.txt', 'hello', 'overwrite');
    expect(result).toBe(expected);
  });

  it('list() should call listDirectory()', async () => {
    const expected = {
      requestId: 'request-123',
      success: true,
      entries: [{ name: 'a.txt', isDirectory: false }],
      errorMessage: undefined,
    };
    const spy = jest.spyOn(fs as any, 'listDirectory').mockResolvedValue(expected);

    const result = await (fs as any).list('/tmp');

    expect(spy).toHaveBeenCalledWith('/tmp');
    expect(result).toBe(expected);
  });

  it('delete() should call deleteFile()', async () => {
    const expected = {
      requestId: 'request-123',
      success: true,
      data: true,
      errorMessage: undefined,
    };
    const spy = jest.spyOn(fs as any, 'deleteFile').mockResolvedValue(expected);

    const result = await (fs as any).delete('/tmp/a.txt');

    expect(spy).toHaveBeenCalledWith('/tmp/a.txt');
    expect(result).toBe(expected);
  });
});


