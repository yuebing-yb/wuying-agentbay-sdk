import { AgentBay } from './agent-bay';
import { APIError } from './exceptions';
import { FileSystem } from './filesystem';
import { Command } from './command';
import { Adb } from './adb';
import Client from './api/client';
import { ReleaseMcpSessionRequest } from './api/models/model';
import * as $_client from './api';

/**
 * Represents a session in the AgentBay cloud environment.
 */
export class Session {
  private agentBay: AgentBay;
  public client:  $_client.Client;
  public sessionId: string;
  
  // File, command, and adb handlers
  public filesystem: FileSystem;
  public command: Command;
  public adb: Adb;

  /**
   * Initialize a Session object.
   * 
   * @param agentBay - The AgentBay instance that created this session.
   * @param sessionId - The ID of this session.
   */
  constructor(agentBay: AgentBay, sessionId: string) {
    this.agentBay = agentBay;
    this.sessionId = sessionId;
    this.client = agentBay.getClient();
    console.log(`Session created with ID: ${sessionId}`);
    
    // Initialize filesystem, command, and adb handlers
    this.filesystem = new FileSystem(this);
    this.command = new Command(this);
    this.adb = new Adb(this);
  }

  /**
   * Get information about this session.
   * 
   * @returns Session information.
   */
  // async get_info(): Promise<Record<string, any>> {
  //   // TODO: Implement the API call to get session info
  //   try {
  //     const response = await this.client.get(this.baseUrl);
  //     return response.data;
  //   } catch (error) {
  //     throw new APIError(`Failed to get session info: ${error}`);
  //   }
  // }

  /**
   * Delete this session.
   * 
   * @returns True if the session was successfully deleted.
   */
  async delete(): Promise<boolean> {
    try {
      const releaseSessionRequest = new ReleaseMcpSessionRequest({
        authorization: `Bearer ${this.getAPIKey()}`,
        sessionId: this.sessionId
      });
      
      await this.client.releaseMcpSession(releaseSessionRequest);
      return true;
    } catch (error) {
      throw new APIError(`Failed to delete session: ${error}`);
    }
  }
  
  /**
   * Get the API key.
   * 
   * @returns The API key.
   */
  getAPIKey(): string {
    return this.agentBay.getAPIKey();
  }
  
  /**
   * Get the client.
   * 
   * @returns The client.
   */
  getClient(): Client {
    return this.client;
  }
  
  /**
   * Get the session ID.
   * 
   * @returns The session ID.
   */
  getSessionId(): string {
    return this.sessionId;
  }
}
