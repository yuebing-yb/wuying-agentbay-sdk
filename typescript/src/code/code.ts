import {
  CodeExecutionResult,
  CodeExecutionResultItem,
  CodeExecutionLogs,
  CodeExecutionError,
} from "../types/api-response";

/**
 * Handles code execution operations in the AgentBay cloud environment.
 */
export class Code {
  private session: {
    getAPIKey(): string;
    getSessionId(): string;
    getWsClient?: () => Promise<any>;
    mcpTools?: Array<{ name?: string; server?: string }>;
    callMcpTool(
      toolName: string,
      args: any,
      autoGenSession?: boolean
    ): Promise<{
      success: boolean;
      data: string;
      errorMessage: string;
      requestId: string;
    }>;
  };

  /**
   * Initialize a Code object.
   *
   * @param session - The Session instance that this Code belongs to.
   */
  constructor(session: {
    getAPIKey(): string;
    getSessionId(): string;
    getWsClient?: () => Promise<any>;
    mcpTools?: Array<{ name?: string; server?: string }>;
    callMcpTool(
      toolName: string,
      args: any,
      autoGenSession?: boolean
    ): Promise<{
      success: boolean;
      data: string;
      errorMessage: string;
      requestId: string;
    }>;
  }) {
    this.session = session;
  }

  /**
   * Parses the backend JSON response into a structured CodeExecutionResult
   * @param data Raw JSON string from backend
   */
  private parseBackendResponse(data: string): CodeExecutionResult {
    let raw: any;
    try {
      raw = JSON.parse(data);
      // Handle double-encoded JSON if necessary
      if (typeof raw === 'string') {
        try {
          raw = JSON.parse(raw);
        } catch (e) {
          // If second parse fails, keep as string (legacy output)
        }
      }
    } catch (e) {
      // Not JSON, assume legacy plain string result or simple error message
      return {
        requestId: "", // Will be filled later
        success: true,
        result: data,
        logs: { stdout: [data], stderr: [] },
        results: [{ text: data, isMainResult: true }],
      };
    }

    // Check if it's the expected structure (has result array or logs)
    // If parsed but not the structure we want, treat as plain object result?
    // But usually if it parses as object, it's likely our structure or empty object.
    
    const logs: CodeExecutionLogs = {
      stdout: raw.stdout || [],
      stderr: raw.stderr || [],
    };

    const results: CodeExecutionResultItem[] = [];
    if (Array.isArray(raw.result)) {
      for (const itemStr of raw.result) {
        try {
          // Items in 'result' are JSON strings themselves
          const itemMap = typeof itemStr === 'string' ? JSON.parse(itemStr) : itemStr;
          const item: CodeExecutionResultItem = {};

          if (itemMap.isMainResult) item.isMainResult = true;
          if (itemMap.is_main_result) item.isMainResult = true;

          // Map MIME types to fields
          if (itemMap["text/plain"]) item.text = itemMap["text/plain"];
          if (itemMap["text/html"]) item.html = itemMap["text/html"];
          if (itemMap["text/markdown"]) item.markdown = itemMap["text/markdown"];
          if (itemMap["image/png"]) item.png = itemMap["image/png"];
          if (itemMap["image/jpeg"]) item.jpeg = itemMap["image/jpeg"];
          if (itemMap["image/svg+xml"]) item.svg = itemMap["image/svg+xml"];
          if (itemMap["text/latex"]) item.latex = itemMap["text/latex"];
          if (itemMap["application/json"]) item.json = itemMap["application/json"];

          // Chart support (Vega/Vega-Lite)
          if (itemMap["application/vnd.vegalite.v4+json"]) {
            item.chart = itemMap["application/vnd.vegalite.v4+json"];
          } else if (itemMap["application/vnd.vegalite.v5+json"]) {
            item.chart = itemMap["application/vnd.vegalite.v5+json"];
          } else if (itemMap["application/vnd.vega.v5+json"]) {
            item.chart = itemMap["application/vnd.vega.v5+json"];
          }

          results.push(item);
        } catch (e) {
          // Ignore parse errors for individual items
        }
      }
    }

    let error: CodeExecutionError | undefined;
    if (raw.executionError) {
      error = {
        name: "ExecutionError",
        value: raw.executionError,
        traceback: "",
      };
    }

    // Determine legacy result string for backward compatibility
    let resultText = "";
    const mainRes = results.find((r) => r.isMainResult && r.text);
    if (mainRes && mainRes.text) {
      resultText = mainRes.text;
    } else if (results.length > 0 && results[0].text) {
      resultText = results[0].text;
    } else if (logs.stdout.length > 0) {
      resultText = logs.stdout.join("");
    }

    return {
      requestId: "", // Will be filled by caller
      success: !raw.executionError,
      result: resultText,
      errorMessage: raw.executionError,
      logs,
      results,
      error,
      executionTime: raw.executionTime || raw.execution_time,
      executionCount: raw.executionCount || raw.execution_count,
    };
  }

  private safeToString(v: any): string {
    try {
      if (typeof v === "string") return v;
      return JSON.stringify(v);
    } catch (_e) {
      return String(v);
    }
  }

  private toResultItem(payload: any): CodeExecutionResultItem {
    const item: CodeExecutionResultItem = {};
    if (!payload || typeof payload !== "object") {
      item.text = String(payload);
      return item;
    }

    if (payload.isMainResult) item.isMainResult = true;
    if (payload.is_main_result) item.isMainResult = true;

    if (payload["text/plain"]) item.text = payload["text/plain"];
    if (payload["text/html"]) item.html = payload["text/html"];
    if (payload["text/markdown"]) item.markdown = payload["text/markdown"];
    if (payload["image/png"]) item.png = payload["image/png"];
    if (payload["image/jpeg"]) item.jpeg = payload["image/jpeg"];
    if (payload["image/svg+xml"]) item.svg = payload["image/svg+xml"];
    if (payload["text/latex"]) item.latex = payload["text/latex"];
    if (payload["application/json"]) item.json = payload["application/json"];

    if (payload["application/vnd.vegalite.v4+json"]) {
      item.chart = payload["application/vnd.vegalite.v4+json"];
    } else if (payload["application/vnd.vegalite.v5+json"]) {
      item.chart = payload["application/vnd.vegalite.v5+json"];
    } else if (payload["application/vnd.vega.v5+json"]) {
      item.chart = payload["application/vnd.vega.v5+json"];
    }

    if (payload.text && !item.text) item.text = payload.text;
    return item;
  }

  private async runCodeStreamWs(params: {
    code: string;
    language: string;
    timeoutS: number;
    onStdout?: (chunk: string) => void;
    onStderr?: (chunk: string) => void;
    onError?: (err: any) => void;
  }): Promise<CodeExecutionResult> {
    const stdoutChunks: string[] = [];
    const stderrChunks: string[] = [];
    const results: CodeExecutionResultItem[] = [];
    let errorObj: CodeExecutionError | undefined;
    let errorMessage = "";

    // Determine target from MCP tool list if available.
    let target = "wuying_codespace";
    for (const tool of this.session.mcpTools || []) {
      if (tool && tool.name === "run_code" && tool.server) {
        target = tool.server;
        break;
      }
    }

    if (!this.session.getWsClient) {
      return {
        requestId: "",
        success: false,
        result: "",
        errorMessage: "WS streaming is not available in this session",
      };
    }

    const wsClient = await this.session.getWsClient();

    const handle = await wsClient.callStream({
      target,
      data: {
        method: "run_code",
        mode: "stream",
        params: {
          language: params.language,
          timeoutS: params.timeoutS,
          code: params.code,
        },
      },
      onEvent: (_invocationId: string, data: any) => {
        const eventType = data?.eventType;
        if (eventType === "stdout") {
          const chunk = String(data?.chunk ?? "");
          stdoutChunks.push(chunk);
          if (params.onStdout) params.onStdout(chunk);
          return;
        }
        if (eventType === "stderr") {
          const chunk = String(data?.chunk ?? "");
          stderrChunks.push(chunk);
          if (params.onStderr) params.onStderr(chunk);
          return;
        }
        if (eventType === "result") {
          const r = this.toResultItem(data?.result);
          results.push(r);
          return;
        }
        if (eventType === "error") {
          const msg =
            typeof data?.error === "string" ? data.error : this.safeToString(data);
          errorMessage = msg;
          errorObj = {
            name: "ExecutionError",
            value: msg,
            traceback: "",
          };
          if (params.onError) params.onError(data);
          return;
        }
      },
      onEnd: (_invocationId: string, data: any) => {
        const executionError = data?.executionError;
        if (executionError && !errorObj) {
          const msg = String(executionError);
          errorMessage = msg;
          errorObj = { name: "ExecutionError", value: msg, traceback: "" };
        }
      },
      onError: (_invocationId: string, err: any) => {
        const msg = err instanceof Error ? err.message : String(err);
        errorMessage = msg;
        if (!errorObj) {
          errorObj = { name: "ExecutionError", value: msg, traceback: "" };
        }
        if (params.onError) params.onError(err);
      },
    });

    let endData: any = {};
    try {
      endData = await handle.waitEnd();
    } catch (e: any) {
      const msg = e instanceof Error ? e.message : String(e);
      return {
        requestId: handle.invocationId,
        success: false,
        result: "",
        errorMessage: msg,
        logs: { stdout: stdoutChunks, stderr: stderrChunks },
        results,
        error: errorObj,
      };
    }

    const ok = !errorObj && !endData?.executionError && endData?.status !== "failed";

    const logs: CodeExecutionLogs = {
      stdout: stdoutChunks,
      stderr: stderrChunks,
    };

    // Determine legacy result string for backward compatibility
    let resultText = "";
    const mainRes = results.find((r) => r.isMainResult && r.text);
    if (mainRes && mainRes.text) {
      resultText = mainRes.text;
    } else if (results.length > 0 && results[0].text) {
      resultText = results[0].text;
    } else if (logs.stdout.length > 0) {
      resultText = logs.stdout.join("");
    }

    return {
      requestId: handle.invocationId,
      success: ok,
      result: resultText,
      errorMessage: ok ? "" : errorMessage || String(endData?.executionError || ""),
      logs,
      results,
      error: errorObj,
      executionTime: endData?.executionTime,
      executionCount: endData?.executionCount,
    };
  }

  /**
   * Execute code in the specified language with a timeout.
   * Corresponds to Python's run_code() method
   *
   * @param code - The code to execute.
   * @param language - The programming language of the code. Case-insensitive.
   *                  Supported values: 'python', 'javascript', 'r', 'java'.
   * @param timeoutS - The timeout for the code execution in seconds. Default is 60s.
   *                   Note: Due to gateway limitations, each request cannot exceed 60 seconds.
   * @returns CodeExecutionResult with code execution output and requestId
   * @throws Error if an unsupported language is specified.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create({ imageId: "code_latest" });
   * if (result.success) {
   *   const codeResult = await result.session.code.runCode('print("Hello")', "python");
   *   console.log(codeResult.result);
   *   if (codeResult.results) {
   *      // Access rich output like images or charts
   *   }
   *   await result.session.delete();
   * }
   * ```
   */
  async runCode(
    code: string,
    language: string,
    timeoutS = 60
  ): Promise<CodeExecutionResult> {
    try {
      // Normalize and validate language (case-insensitive)
      const rawLanguage = language ?? "";
      const normalizedLanguage = String(rawLanguage).trim().toLowerCase();
      const aliases: Record<string, string> = {
        py: "python",
        python3: "python",
        js: "javascript",
        node: "javascript",
        nodejs: "javascript",
      };
      const canonicalLanguage = aliases[normalizedLanguage] || normalizedLanguage;
      const supported = new Set(["python", "javascript", "r", "java"]);

      if (!supported.has(canonicalLanguage)) {
        return {
          requestId: "",
          success: false,
          result: "",
          errorMessage: `Unsupported language: ${rawLanguage}. Supported languages are 'python', 'javascript', 'r', and 'java'`,
        };
      }

      // Streaming is temporarily disabled in this version.
      // The streaming implementation is preserved in runCodeStreamWs()
      // and will be re-enabled in a future release.

      const args = {
        code,
        language: canonicalLanguage,
        timeout_s: timeoutS,
      };

      const response = await this.session.callMcpTool("run_code", args, false);

      let codeResult: CodeExecutionResult;
      
      // Even if response.success is false, data might contain structured error info
      if (response.success) {
        codeResult = this.parseBackendResponse(response.data);
      } else {
        // Check if errorMessage is JSON
        try {
            if (response.errorMessage && response.errorMessage.trim().startsWith('{')) {
                codeResult = this.parseBackendResponse(response.errorMessage);
                codeResult.success = false;
            } else {
                 // Real failure not from code execution but tool failure
                 return {
                    requestId: response.requestId,
                    success: false,
                    result: "",
                    errorMessage: response.errorMessage,
                  };
            }
        } catch {
             return {
                requestId: response.requestId,
                success: false,
                result: "",
                errorMessage: response.errorMessage,
              };
        }
      }

      codeResult.requestId = response.requestId;
      return codeResult;

    } catch (error) {
      return {
        requestId: "",
        success: false,
        result: "",
        errorMessage: `Failed to run code: ${error}`,
      };
    }
  }

  /**
   * Alias of runCode().
   */
  async run(
    code: string,
    language: string,
    timeoutS = 60
  ): Promise<CodeExecutionResult> {
    return await this.runCode(code, language, timeoutS);
  }

  /**
   * Alias of runCode().
   */
  async execute(
    code: string,
    language: string,
    timeoutS = 60
  ): Promise<CodeExecutionResult> {
    return await this.runCode(code, language, timeoutS);
  }
}
