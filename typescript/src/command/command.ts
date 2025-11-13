import { Session } from "../session";
import {
  CommandResult,
} from "../types/api-response";


/**
 * Handles command execution operations in the AgentBay cloud environment.
 */
export class Command {
  private session: Session;

  /**
   * Initialize a Command object.
   *
   * @param session - The Session instance that this Command belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Sanitizes error messages to remove sensitive information like API keys.
   *
   * @param error - The error to sanitize
   * @returns The sanitized error
   */
  private sanitizeError(error: any): any {
    if (!error) {
      return error;
    }

    const errorString = String(error);
    return errorString.replace(/Bearer\s+[^\s]+/g, "Bearer [REDACTED]");
  }

  /**
   * Executes a shell command in the session environment.
   *
   * @param command - The shell command to execute.
   * @param timeoutMs - Timeout in milliseconds. Defaults to 1000ms.
   *
   * @returns Promise resolving to CommandResult containing:
   *          - success: Whether the command executed successfully
   *          - output: Combined stdout and stderr output
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if execution failed
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const cmdResult = await result.session.command.executeCommand('echo "Hello"', 3000);
   *   console.log('Command output:', cmdResult.output);
   *   await result.session.delete();
   * }
   * ```
   *
   * @remarks
   * **Behavior:**
   * - Executes in a Linux shell environment
   * - Combines stdout and stderr in the output
   * - Default timeout is 1000ms (1 second)
   * - Command runs with session user permissions
   *
   * @see {@link FileSystem.readFile}, {@link FileSystem.writeFile}
   */
  async executeCommand(
    command: string,
    timeoutMs = 1000
  ): Promise<CommandResult> {
    try {
      const args = {
        command,
        timeout_ms: timeoutMs,
      };
      const result = await this.session.callMcpTool("shell", args);

      return {
        requestId: result.requestId,
        success: result.success,
        output: result.data,
        errorMessage: result.errorMessage,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        output: "",
        errorMessage: `Failed to execute command: ${error}`,
      };
    }
  }
}
