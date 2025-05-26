import { Session } from '../session';
import { CallMcpToolRequest } from '../api/models/model';

/**
 * Adb handles ADB operations in the AgentBay cloud environment.
 */
export class Adb {
  private session: Session;

  /**
   * Create a new Adb instance.
   * 
   * @param session - The session to use for ADB operations
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Execute an ADB shell command in the mobile environment.
   * 
   * @param command - The ADB shell command to execute
   * @returns The output of the ADB shell command
   */
  async shell(command: string): Promise<string> {
    try {
      const args = {
        command
      };
      
      const callToolRequest = new CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'shell',
        args: JSON.stringify(args)
      });
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
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
      throw new Error(`Failed to execute ADB shell command: ${error}`);
    }
  }
}
