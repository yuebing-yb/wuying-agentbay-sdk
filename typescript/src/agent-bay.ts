import axios, { AxiosInstance } from 'axios';
import { Session } from './session';
import { AuthenticationError, APIError } from './exceptions';
import * as $_client from './api';
import OpenApi from '@alicloud/openapi-core';
import { OpenApiUtil, $OpenApiUtil }from '@alicloud/openapi-core';
import Client from './api/client';
import { CreateMcpSessionRequest, CreateMcpSessionResponse } from './api/models/model';
import { loadConfig } from './config';
import 'dotenv/config';
/**
 * Main class for interacting with the AgentBay cloud runtime environment.
 */
export class AgentBay {
  private apiKey: string;
  private client!: Client;
  private regionId: string;
  private endpoint:string;
  private sessions: Map<string, Session> = new Map();
  


  /**
   * Initialize the AgentBay client.
   * 
   * @param options - Configuration options
   * @param options.apiKey - API key for authentication. If not provided, will look for AGENTBAY_API_KEY environment variable.
   */
  constructor(options: {
    apiKey?: string;
  } = {}) {
    this.apiKey = options.apiKey || process.env.AGENTBAY_API_KEY || '';
    
    if (!this.apiKey) {
      throw new AuthenticationError(
        'API key is required. Provide it as a parameter or set the AGENTBAY_API_KEY environment variable.'
      );
    }
    
    // Load configuration
    const configData = loadConfig();
    this.regionId = configData.region_id;
    this.endpoint = configData.endpoint;
    
    const config = new $OpenApiUtil.Config({
      regionId: this.regionId,
      endpoint: this.endpoint
    })
    
    config.readTimeout = configData.timeout_ms;
    try{
      this.client = new $_client.Client(config)
      
    }catch(error){
      console.log( `Failed to constructor: ${error}`)
      throw new AuthenticationError(`Failed to constructor: ${error}`);
    }
    
  }

  /**
   * Create a new session in the AgentBay cloud environment.
   * 
   * @returns A new Session object.
   */
  async create(): Promise<Session> {
    try {
      const createSessionRequest = new $_client.CreateMcpSessionRequest({
        authorization: "Bearer "+this.apiKey,
      });
      
        const response = await this.client.createMcpSession(createSessionRequest);
        console.log('agentBay create session response',response);
        const sessionId = response.body?.data?.sessionId;
        if (!sessionId) {
          throw new APIError('Invalid session ID in response')
        }else{
          const session =  new Session(this, response.body?.data?.sessionId||'');
          this.sessions.set(session.sessionId, session);
          return session;
        }
       
    } catch (error) {
      throw new APIError(`Failed to create session: ${error}`);
    }
  }

  /**
   * List all available sessions.
   * 
   * @returns A list of session objects.
   */
  list(): Session[] {
    return Array.from(this.sessions.values());
  }

  /**
   * Delete a session by ID.
   * 
   * @param sessionId - The ID of the session to delete.
   * @returns True if the session was successfully deleted.
   */
  async delete(sessionId: string): Promise<boolean> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session with ID ${sessionId} not found`);
    }
    
    try {
      await session.delete();
      this.sessions.delete(sessionId);
      return true;
    } catch (error) {
      throw new APIError(`Failed to delete session: ${error}`);
    }
  }

  // For internal use by the Session class
  getClient(): Client {
    return this.client;
  }
  
  getAPIKey(): string {
    return this.apiKey;
  }
}
