import axios, { AxiosInstance } from 'axios';
import { Session } from './session';
import { ContextService } from './context';
import { AuthenticationError, APIError } from './exceptions';
import * as $_client from './api';
import OpenApi from '@alicloud/openapi-core';
import { OpenApiUtil, $OpenApiUtil }from '@alicloud/openapi-core';
import { Client } from './api/client';
import { CreateMcpSessionRequest, CreateMcpSessionResponse, ListSessionRequest } from './api/models/model';
import { loadConfig } from './config';
import 'dotenv/config';
import { log, logError } from './utils/logger';
/**
 * Main class for interacting with the AgentBay cloud runtime environment.
 */
export class AgentBay {
  private apiKey: string;
  private client: Client;
  private regionId: string;
  private endpoint:string;
  private sessions: Map<string, Session> = new Map();
  
  /**
   * Context service for managing persistent contexts.
   */
  context: ContextService;


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
    config.connectTimeout = configData.timeout_ms;
    try{
      this.client = new Client(config)
      
      // Initialize context service
      this.context = new ContextService(this);
    }catch(error){
      logError(`Failed to constructor:`, error);
      throw new AuthenticationError(`Failed to constructor: ${error}`);
    }
    
  }

  /**
   * Create a new session in the AgentBay cloud environment.
   * 
   * @param options - Optional parameters for creating the session
   * @param options.contextId - ID of the context to bind to the session
   * @param options.labels - Custom labels for the session
   * @returns A new Session object.
   */
  async create(options: {
    contextId?: string;
    labels?: Record<string, string>;
    imageId?: string;
  } = {}): Promise<Session> {
    try {
      const createSessionRequest = new $_client.CreateMcpSessionRequest({
        authorization: "Bearer "+this.apiKey,
        imageId: options.imageId
      });
      
      // Add context_id if provided
      if (options.contextId) {
        createSessionRequest.contextId = options.contextId;
      }
      
      // Add labels if provided
      if (options.labels) {
        createSessionRequest.labels = JSON.stringify(options.labels);
      }
      
      // Log API request
      log("API Call: CreateMcpSession");
      log(`Request: ${options.contextId ? `ContextId=${options.contextId}, ` : ''}${options.labels ? `Labels=${JSON.stringify(options.labels)}, ` : ''}${options.imageId ? `ImageId=${options.imageId}` : ''}`);
      
      const response = await this.client.createMcpSession(createSessionRequest);
      
      // Log API response
      log(`Response from CreateMcpSession:`, response.body);
      
      const sessionId = response.body?.data?.sessionId;
      if (!sessionId) {
        throw new APIError('Invalid session ID in response');
      }
      
      // ResourceUrl is optional in CreateMcpSession response
      const resourceUrl = response.body?.data?.resourceUrl;
      
      const session = new Session(this, sessionId);
      if (resourceUrl) {
        session.resourceUrl = resourceUrl;
      }
      
      this.sessions.set(session.sessionId, session);
      return session;
       
    } catch (error) {
      logError("Error calling CreateMcpSession:", error);
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
   * List sessions filtered by the provided labels.
   * It returns sessions that match all the specified labels.
   * 
   * @param labels - The labels to filter by.
   * @returns A list of session objects that match the labels.
   */
  async listByLabels(labels: Record<string, string>): Promise<Session[]> {
    try {
      // Convert labels to JSON
      const labelsJSON = JSON.stringify(labels);
      
      const listSessionRequest = new ListSessionRequest({
        authorization: `Bearer ${this.apiKey}`,
        labels: labelsJSON
      });
      
      // Log API request
      log("API Call: ListSession");
      log(`Request: Labels=${labelsJSON}`);
      
      const response = await this.client.listSession(listSessionRequest);
      
      // Log API response
      log(`Response from ListSession:`, response.body);
      
      const sessions: Session[] = [];
      if (response.body?.data) {
        for (const sessionData of response.body.data) {
          if (sessionData.sessionId) {
            const session = new Session(this, sessionData.sessionId);
            sessions.push(session);
            // Also store in the local cache
            this.sessions.set(sessionData.sessionId, session);
          }
        }
      }
      
      return sessions;
    } catch (error) {
      logError("Error calling ListSession:", error);
      throw new APIError(`Failed to list sessions by labels: ${error}`);
    }
  }

  /**
   * Delete a session by ID.
   * 
   * @param sessionId - The ID of the session to delete.
   * @returns True if the session was successfully deleted.
   */
  async delete(session: Session): Promise<boolean> {
    const getSession = this.sessions.get(session.sessionId);
    if (!getSession) {
      throw new Error(`Session with ID ${session.sessionId} not found`);
    }
    
    try {
      await session.delete();
      return true;
    } catch (error) {
      throw new APIError(`Failed to delete session: ${error}`);
    }
  }
/**
 * 
 * @param sessionId - The ID of the session to remove.
 */
  public removeSession(sessionId: string): void {
    this.sessions.delete(sessionId);
  }
  // For internal use by the Session class
  getClient(): Client {
    return this.client;
  }
  
  getAPIKey(): string {
    return this.apiKey;
  }
}
