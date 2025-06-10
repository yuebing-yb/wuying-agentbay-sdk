import { APIError } from '../exceptions';
import { Session } from '../session';
import Client from '../api/client';
import { CallMcpToolRequest } from '../api/models/model';

import * as $_client from '../api';
/**
 * Handles command execution operations in the AgentBay cloud environment.
 */
export class Command {
  private session: Session;
  private client!: $_client.Client;
  private baseUrl!: string;

  /**
   * Initialize a Command object.
   * 
   * @param session - The Session instance that this Command belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Execute a command in the cloud environment with a specified timeout.
   * 
   * @param command - The command to execute.
   * @param timeoutMs - The timeout for the command execution in milliseconds. Default is 1000ms.
   * @returns The result of the command execution.
   */
  async executeCommand(command: string, timeoutMs: number = 1000): Promise<string> {
    try {
      const args = {
        command,
        timeout_ms: timeoutMs
      };
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'shell',
        args: JSON.stringify(args)
      })
      console.log(callToolRequest,'callToolRequest');
      
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response,'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract content from response
      const data = response.body.data as any;
      if (!data.content || !Array.isArray(data.content)) {
        throw new Error('Content field not found or not an array');
      }
      
      // Concatenate all text fields
      let fullText = '';
      for (const item of data.content) {
        if (item && typeof item === 'object' && 'text' in item) {
          fullText += item.text + '\n';
        }
      }
      
      return fullText;
    } catch (error) {
      throw new APIError(`Failed to execute command: ${error}`);
    }
  }
  
  /**
   * Execute code in the specified language with a timeout.
   * 
   * @param code - The code to execute.
   * @param language - The programming language of the code. Must be either 'python' or 'javascript'.
   * @param timeoutS - The timeout for the code execution in seconds. Default is 300s.
   * @returns The output of the code execution.
   * @throws APIError if the code execution fails or if an unsupported language is specified.
   */
  async runCode(code: string, language: string, timeoutS: number = 300): Promise<string> {
    try {
      // Validate language
      if (language !== 'python' && language !== 'javascript') {
        throw new Error(`Unsupported language: ${language}. Supported languages are 'python' and 'javascript'`);
      }
      
      const args = {
        code,
        language,
        timeout_s: timeoutS
      };
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'run_code',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract output from response
      const data = response.body.data as any;
      if (typeof data.output !== 'string') {
        throw new Error('Output field not found or not a string');
      }
      
      return data.output;
    } catch (error) {
      throw new APIError(`Failed to execute code: ${error}`);
    }
  }
}
