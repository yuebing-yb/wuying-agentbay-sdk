import { spawn, ChildProcess } from 'child_process';
import { readFile, writeFile, mkdir } from 'fs/promises';
import { join } from 'path';
import { randomUUID } from 'crypto';
import { chromium, Browser as PlaywrightBrowser, BrowserContext } from 'playwright';
import { Session } from '../../session';
import { Browser } from '../browser';
import { BrowserAgent } from '../browser_agent';
import { OperationResult, DeleteResult } from '../../types/api-response';
import { McpToolResult } from '../../agent/agent';
import { logInfo, logDebug, logWarn, logError } from '../../utils/logger';

/**
 * Local MCP Client for communicating with MCP servers via stdio
 */
class LocalMCPClient {
  private server: string;
  private command: string;
  private args: string[];
  private session: any | null = null;
  private workerThread: ChildProcess | null = null;
  private toolCallQueue: Array<{
    toolName: string;
    arguments: Record<string, any>;
    resolve: (result: OperationResult) => void;
    reject: (error: Error) => void;
  }> = [];
  private isConnected: boolean = false;
  private connectPromise: Promise<void> | null = null;

  /**
   * Check if the MCP client is connected
   */
  get connected(): boolean {
    return this.isConnected && this.workerThread !== null;
  }

  constructor(server: string, command: string, args: string[]) {
    this.server = server;
    this.command = command;
    this.args = args;
  }

  /**
   * Connect to the MCP server
   * If already connected, returns immediately
   * If connection is in progress, waits for it to complete
   */
  async connect(): Promise<void> {
    // If already connected, return immediately
    if (this.connected) {
      return;
    }

    // If connection is in progress, wait for it
    if (this.connectPromise) {
      return this.connectPromise;
    }

    // Start a new connection
    this.connectPromise = this._doConnect();
    return this.connectPromise;
  }

  /**
   * Internal method to perform the actual connection
   */
  private async _doConnect(): Promise<void> {
    return new Promise((resolve, reject) => {
      logInfo('[LocalMCPClient] Starting connection to MCP server');
      logInfo(`[LocalMCPClient] command = ${this.command}, args = ${this.args.join(' ')}`);

      // Spawn the MCP server process
      const childProcess = spawn(this.command, this.args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: process.env,
      });

      this.workerThread = childProcess;

      let initResolved = false;
      const initTimeout = setTimeout(() => {
        if (!initResolved) {
          initResolved = true;
          this.isConnected = true;
          this.connectPromise = null;
          logInfo('[LocalMCPClient] MCP client connection timeout - marking as connected (server may still be initializing)');
          resolve();
        }
      }, 15000); // 15 second timeout as fallback

      // Handle stdout (MCP server responses)
      let buffer = '';
      childProcess.stdout?.on('data', (data: Buffer) => {
        buffer += data.toString();
        // Try to parse JSON messages (simplified - real MCP protocol is more complex)
        try {
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          for (const line of lines) {
            if (line.trim()) {
              const parsed = JSON.parse(line.trim());
              // Check for initialization response or any response that indicates server is ready
              if (parsed.result || parsed.method === 'notifications/initialized' || (parsed.id && parsed.id === 'init')) {
                if (!initResolved) {
                  clearTimeout(initTimeout);
                  initResolved = true;
                  this.isConnected = true;
                  this.connectPromise = null;
                  logInfo('[LocalMCPClient] MCP client session initialized (received response from server)');
                  resolve();
                }
              }
              this.handleMessage(line.trim());
            }
          }
        } catch (e) {
          // Not JSON or parse error, continue
        }
      });

      // Handle stderr
      childProcess.stderr?.on('data', (data: Buffer) => {
        const stderrText = data.toString();
        logDebug(`[LocalMCPClient] stderr: ${stderrText}`);
        // Check for initialization complete indicators in stderr logs
        if (stderrText.includes('started') || stderrText.includes('initialized') || stderrText.includes('ready')) {
          // Give it a moment after seeing these messages
          setTimeout(() => {
            if (!initResolved) {
              clearTimeout(initTimeout);
              initResolved = true;
              this.isConnected = true;
              this.connectPromise = null;
              logInfo('[LocalMCPClient] MCP client session initialized (detected from stderr logs)');
              resolve();
            }
          }, 2000); // Wait 2 seconds after seeing ready message
        }
      });

      // Handle process exit
      childProcess.on('exit', (code: number | null) => {
        logInfo(`[LocalMCPClient] Process exited with code ${code}`);
        clearTimeout(initTimeout);
        this.isConnected = false;
        this.workerThread = null;
        this.connectPromise = null; // Clear the promise on exit
        if (!initResolved) {
          initResolved = true;
          reject(new Error(`MCP server process exited with code ${code} before initialization completed`));
        }
      });

      childProcess.on('error', (error: Error) => {
        clearTimeout(initTimeout);
        this.connectPromise = null; // Clear the promise on error
        logError(`[LocalMCPClient] Failed to spawn MCP server: ${error}`);
        if (!initResolved) {
          initResolved = true;
          reject(error);
        }
      });

      // Send initialization request (MCP protocol)
      const initRequest = {
        jsonrpc: '2.0',
        id: 'init',
        method: 'initialize',
        params: {
          protocolVersion: '2024-11-05',
          capabilities: {},
          clientInfo: {
            name: 'LocalPageAgent',
            version: '1.0.0',
          },
        },
      };

      // Wait a moment for the process to start, then send init request
      setTimeout(() => {
        if (childProcess.stdin && !childProcess.stdin.destroyed) {
          childProcess.stdin.write(JSON.stringify(initRequest) + '\n');
          logInfo('[LocalMCPClient] Sent initialization request to MCP server');
        }
      }, 1000);
    });
  }

  /**
   * Handle incoming messages from MCP server
   */
  private handleMessage(message: string): void {
    // Simplified message handling - real MCP protocol requires proper JSON-RPC parsing
    try {
      const parsed = JSON.parse(message);
      // Process tool call responses
      if (parsed.result && this.toolCallQueue.length > 0) {
        const queued = this.toolCallQueue.shift();
        if (queued) {
          // Extract the actual data from MCP response format
          // MCP responses have format: { jsonrpc: "2.0", id: "...", result: { content: [{ type: "text", text: "..." }] } }
          let responseData: any = parsed.result;

          //logInfo(`[LocalMCPClient] Tool call response raw data: ${JSON.stringify(responseData, null, 2)}`);
          // If result has content array, extract text from the first content item
          if (parsed.result && parsed.result.content && Array.isArray(parsed.result.content) && parsed.result.content.length > 0) {
            const contentItem = parsed.result.content[0];
            if (contentItem && contentItem.text !== undefined) {
              // Extract the text field which contains the actual data
              responseData = contentItem.text;
            }
          } else if (typeof parsed.result === 'string') {
            // If result is already a string, use it directly
            responseData = parsed.result;
          } else {
            // For other formats, stringify the result
            responseData = typeof parsed.result === 'string' ? parsed.result : JSON.stringify(parsed.result);
          }

          const response: OperationResult = {
            requestId: parsed.id || `local_request_${randomUUID()}`,
            success: !parsed.error,
            data: typeof responseData === 'string' ? responseData : JSON.stringify(responseData),
            errorMessage: parsed.error?.message,
          };
          //logInfo(`[LocalMCPClient] Tool call response: ${JSON.stringify(response, null, 2)}`);
          queued.resolve(response);
        }
      }
    } catch (e) {
      // Not JSON, continue
      logDebug(`[LocalMCPClient] Failed to parse message: ${e}, message: ${message.substring(0, 200)}`);
    }
  }

  /**
   * Call an MCP tool
   */
  async callTool(toolName: string, arguments_: Record<string, any>): Promise<OperationResult> {
    if (!this.connected) {
      throw new RuntimeError(
        'MCP client is not connected. Call connect() and ensure it completes before calling callTool.'
      );
    }

    return new Promise((resolve, reject) => {
      logInfo(`[LocalMCPClient] Call tool ${toolName} with arguments ${JSON.stringify(arguments_)}`);

      // Queue the tool call
      this.toolCallQueue.push({
        toolName,
        arguments: arguments_,
        resolve,
        reject,
      });

      // Send tool call request (simplified JSON-RPC format)
      const request = {
        jsonrpc: '2.0',
        id: randomUUID(),
        method: 'tools/call',
        params: {
          name: toolName,
          arguments: arguments_,
        },
      };

      this.workerThread?.stdin?.write(JSON.stringify(request) + '\n');

      // Timeout after 180 seconds
      const TOOL_CALL_TIMEOUT = 180000;
      setTimeout(() => {
        reject(new Error(`Tool call timeout: ${toolName}`));
      }, TOOL_CALL_TIMEOUT);
    });
  }
}

class RuntimeError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RuntimeError';
  }
}

/**
 * Local Page Agent that extends BrowserAgent for local execution
 * 
 * Note: Since BrowserAgent._callMcpTool is private, we route through the session instead.
 * The LocalSession.callMcpTool method routes to this agent's MCP client.
 */
export class LocalPageAgent extends BrowserAgent {
  private mcpClient: LocalMCPClient | null = null;

  constructor(session: Session, browser: Browser) {
    super(session, browser);

    const mcpScript = process.env.PAGE_TASK_MCP_SERVER_SCRIPT || '';

    if (mcpScript) {
      this.mcpClient = new LocalMCPClient('PageUseAgent', "python", [mcpScript]);
    } else {
      this.mcpClient = null;
      logWarn(
        'PAGE_TASK_MCP_SERVER_SCRIPT not set. MCP client will not be initialized.'
      );
    }
  }

  /**
   * Initialize the MCP client connection
   */
  async initialize(): Promise<void> {
    if (this.mcpClient) {
      await this.mcpClient.connect();
    }
  }

  /**
   * Call MCP tool asynchronously (used by LocalSession)
   * Public to allow LocalSession to route tool calls through the MCP client
   * Automatically ensures the MCP client is connected before calling
   */
  async _callMcpToolAsync(name: string, args: Record<string, any>): Promise<OperationResult> {
    if (!this.mcpClient) {
      throw new RuntimeError('mcp_client is not set on LocalPageAgent.');
    }
    // Ensure connection is established before calling tool
    if (!this.mcpClient.connected) {
      await this.mcpClient.connect();
    }
    return await this.mcpClient.callTool(name, args);
  }
}

/**
 * Local Browser implementation that uses Playwright directly
 */
export class LocalBrowser extends Browser {
  private _cdpPort: number = 9222;
  private _browser: PlaywrightBrowser | BrowserContext | null = null;
  private _workerThread: ChildProcess | null = null;
  private _playwrightInteractiveLoopAbortSignal: AbortSignal | null = null;
  private _playwrightInteractiveLoopAbortController: AbortController | null = null;
  public agent: LocalPageAgent;

  constructor(session?: Session) {
    // Create a minimal mock session if none provided (static method to avoid using 'this')
    const tempSession = session || LocalBrowser._createMinimalMockSession();
    super(tempSession);
    // @ts-ignore - Access protected member
    this.contexts = [];
    // @ts-expect-error - LocalBrowser uses async initialize, incompatible with base Browser type
    this.agent = new LocalPageAgent(tempSession, this);

    // Create an abort signal for the playwright interactive loop
    this._playwrightInteractiveLoopAbortController = new AbortController();
    this._playwrightInteractiveLoopAbortSignal = this._playwrightInteractiveLoopAbortController.signal;

    // Update the mock session's callMcpTool to use the agent now that it's created
    if (!session && (tempSession as any).__isMock) {
      (tempSession as any).callMcpTool = async (name: string, args: Record<string, any>) => {
        return await this.agent._callMcpToolAsync(name, args);
      };
    }
  }

  /**
   * Create a minimal mock session for local mode (static to avoid using 'this' before super())
   */
  private static _createMinimalMockSession(): Session {
    // Create a minimal session-like object that will be updated after agent creation
    const mockSession = {
      sessionId: 'local_session',
      __isMock: true,
      callMcpTool: async (_name: string, _args: Record<string, any>) => {
        throw new Error('Mock session not yet initialized - this should not be called');
      },
    } as any as Session;

    return mockSession;
  }

  /**
   * Initialize the local browser
   * Note: This overrides the base class sync initialize method with async implementation
   */
  // @ts-expect-error - LocalBrowser uses async initialization, incompatible with base class sync signature
  async initialize(options: any): Promise<boolean> {
    if (this._workerThread) {
      return true;
    }

    return new Promise(async (resolve) => {
      logInfo('[LocalBrowser] Start launching local browser');

      try {
        // Create CDP ports file
        const tmpDir = process.platform === 'win32' ? process.env.TEMP || '/tmp' : '/tmp';
        const chromeCdpPortsPath = join(tmpDir, 'chrome_cdp_ports.json');
        const cdpPortsData = {
          chrome: String(this._cdpPort),
          router: String(this._cdpPort),
          local: String(this._cdpPort),
        };

        await writeFile(chromeCdpPortsPath, JSON.stringify(cdpPortsData, null, 2));

        const cwd = process.cwd();
        const userDataDir = join(
          cwd,
          'tmp',
          `browser_user_data_${process.pid}_${randomUUID()}`
        );

        // Read env variable HEADLESS_MODE
        const headlessMode = process.env.HEADLESS || 'false';
        const headless = headlessMode.toLowerCase() === 'true';

        // Launch Playwright browser with persistent context
        const playwright = await import('playwright');
        const browser = await playwright.chromium.launchPersistentContext(userDataDir, {
          headless: headless,
          viewport: { width: 1280, height: 1200 },
          args: [`--remote-debugging-port=${this._cdpPort}`],
        });

        this._browser = browser;

        logInfo('[LocalBrowser] Local browser launched successfully');
        // Initialize MCP agent connection (don't block on it, but start it)
        this.agent.initialize().catch((err) => {
          logWarn(`[LocalBrowser] Failed to initialize agent: ${err}`);
        });
        resolve(true);

        // Keep the process alive
        await this._playwrightInteractiveLoop(this._playwrightInteractiveLoopAbortSignal ?? undefined);
        logInfo('[LocalBrowser] Local browser interactive loop completed');
      } catch (error: any) {
        logError(`[LocalBrowser] Failed to connect to browser: ${error}`);
        resolve(false);
      }
    });
  }

  /**
   * Check if browser is initialized
   */
  isInitialized(): boolean {
    return this._browser !== null;
  }

  /**
   * Get the endpoint URL for CDP connection
   */
  async getEndpointUrl(): Promise<string> {
    return `http://localhost:${this._cdpPort}`;
  }

  /**
   * Playwright interactive loop to keep the browser alive
   */
  private async _playwrightInteractiveLoop(shutdownSignal?: AbortSignal): Promise<void> {
    while (!shutdownSignal?.aborted) {
      await new Promise((resolve) => setTimeout(resolve, 3000));
    }
  }

  /**
   * Abort the playwright interactive loop
   */
  abortPlaywrightInteractiveLoop(): void {
    this._playwrightInteractiveLoopAbortController?.abort();
  }
}

/**
 * Local Session implementation for local mode execution
 */
export class LocalSession extends Session {
  // @ts-expect-error - LocalBrowser uses async initialize, incompatible with base Browser type
  public browser: LocalBrowser;

  constructor() {
    // Create a mock agent_bay with the required attributes
    const mockAgentBay = {
      apiKey: process.env.AGENTBAY_API_KEY || '',
      apiKeyConfigured: !!process.env.AGENTBAY_API_KEY,
      client: {
        apiBaseUrl: '',
        getSessionStatus: (request: any) => ({
          toMap: () => ({
            success: true,
            data: { status: 'running' },
          }),
        }),
        callMcpTool: (name: string, args: Record<string, any>, kwargs?: any) => ({
          requestId: 'mock_request_id',
          success: false,
          data: null,
          errorMessage: 'Mock mode: Cannot execute tool calls without proper API connection',
        }),
      },
    } as any;

    super(mockAgentBay, 'local_session');
    // @ts-expect-error - LocalBrowser uses async initialize, incompatible with base Browser type
    this.browser = new LocalBrowser(this);
  }

  /**
   * Call MCP tool asynchronously
   */
  async callMcpTool(
    toolName: string,
    args: any,
    autoGenSession = false
  ): Promise<McpToolResult> {
    /**
     * Async stub for local mode. Keeps call signature compatible with the base
     * Session.callMcpTool signature. Routes through LocalPageAgent's MCP client.
     */
    const localAgent = this.browser.agent as LocalPageAgent;
    const result = await localAgent._callMcpToolAsync(toolName, args);
    // Convert OperationResult to McpToolResult format
    return {
      success: result.success,
      data: result.data as string,
      errorMessage: result.errorMessage || '',
      requestId: result.requestId,
    };
  }

  /**
   * Delete the session (no-op for local mode)
   */
  async delete(syncContext: boolean = false): Promise<DeleteResult> {
    this.browser.abortPlaywrightInteractiveLoop();
    
    // No-op for local session
    return {
      success: true,
      requestId: `local_delete_${this.sessionId}`,
      errorMessage: undefined,
    };
  }
}

