import { APIError } from '../exceptions';
import { Session } from '../session';
import Client from '../api/client';
import { CallMcpToolRequest } from '../api/models/model';
import { log, logError } from '../utils/logger';

import * as $_client from '../api';

/**
 * Result object for a CallMcpTool operation
 */
interface CallMcpToolResult {
  data: Record<string, any>;
  content?: any[];
  isError: boolean;
  errorMsg?: string;
  statusCode: number;
}

/**
 * Handles Object Storage Service operations in the AgentBay cloud environment.
 */
export class Oss {
  private session: Session;
  private client!: $_client.Client;
  private baseUrl!: string;

  /**
   * Initialize an Oss object.
   * 
   * @param session - The Session instance that this Oss belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Helper method to call MCP tools and handle common response processing
   * 
   * @param toolName - Name of the MCP tool to call
   * @param args - Arguments to pass to the tool
   * @param defaultErrorMsg - Default error message if specific error details are not available
   * @returns A CallMcpToolResult with the response data
   * @throws APIError if the call fails
   */
  private async callMcpTool(
    toolName: string, 
    args: Record<string, any>,
    defaultErrorMsg: string
  ): Promise<CallMcpToolResult> {
    try {
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: toolName,
        args: JSON.stringify(args)
      });
      
      // Log API request
      log(`API Call: CallMcpTool - ${toolName}`);
      log(`Request: SessionId=${this.session.getSessionId()}, Args=${JSON.stringify(args)}`);
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      
      // Log API response
      log(`Response from CallMcpTool - ${toolName}:`, response.body);
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }

      // Extract data from response
      const data = response.body.data as Record<string, any>;
      
      // Create result object
      const result: CallMcpToolResult = {
        data,
        statusCode: response.statusCode || 0,
        isError: false
      };

      // Check if there's an error in the response
      if (data.isError === true) {
        result.isError = true;
        
        // Try to extract the error message from the content field
        const contentArray = data.content as any[] | undefined;
        if (contentArray && contentArray.length > 0) {
          result.content = contentArray;
          
          // Extract error message from the first content item
          if (contentArray[0]?.text) {
            result.errorMsg = contentArray[0].text;
            throw new Error(contentArray[0].text);
          }
        }
        throw new Error(defaultErrorMsg);
      }
      
      // Extract content array if it exists
      if (Array.isArray(data.content)) {
        result.content = data.content;
      }
      
      return result;
    } catch (error) {
      logError(`Error calling CallMcpTool - ${toolName}:`, error);
      throw new APIError(`Failed to call ${toolName}: ${error}`);
    }
  }

  /**
   * Initialize OSS environment variables with the specified credentials.
   * 
   * @param accessKeyId - The Access Key ID for OSS authentication.
   * @param accessKeySecret - The Access Key Secret for OSS authentication.
   * @param securityToken - The security token for OSS authentication.
   * @param endpoint - The OSS service endpoint. If not specified, the default is used.
   * @param region - The OSS region. If not specified, the default is used.
   * @returns The content field from the API response
   */
  async envInit(
    accessKeyId: string, 
    accessKeySecret: string,
    securityToken: string,
    endpoint?: string, 
    region?: string
  ): Promise<any> {
    const args: Record<string, any> = {
      access_key_id: accessKeyId,
      access_key_secret: accessKeySecret,
      security_token: securityToken
    };
    
    // Add optional parameters if provided
    if (endpoint) {
      args.endpoint = endpoint;
    }
    if (region) {
      args.region = region;
    }
    
    const result = await this.callMcpTool('oss_env_init', args, 'error initializing OSS environment');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Create an OSS client with the provided credentials.
   * 
   * @param accessKeyId - The Access Key ID for OSS authentication.
   * @param accessKeySecret - The Access Key Secret for OSS authentication.
   * @param endpoint - The OSS service endpoint. If not specified, the default is used.
   * @param region - The OSS region. If not specified, the default is used.
   * @returns The content field from the API response
   */
  async createClient(
    accessKeyId: string, 
    accessKeySecret: string, 
    endpoint?: string, 
    region?: string
  ): Promise<any> {
    const args: Record<string, any> = {
      access_key_id: accessKeyId,
      access_key_secret: accessKeySecret
    };
    
    // Add optional parameters if provided
    if (endpoint) {
      args.endpoint = endpoint;
    }
    if (region) {
      args.region = region;
    }
    
    const result = await this.callMcpTool('oss_client_create', args, 'error creating OSS client');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Upload a local file or directory to OSS.
   * 
   * @param bucket - OSS bucket name.
   * @param object - Object key in OSS.
   * @param path - Local file or directory path to upload.
   * @returns The content field from the API response
   */
  async upload(bucket: string, object: string, path: string): Promise<any> {
    const args = {
      bucket,
      object,
      path
    };
    
    const result = await this.callMcpTool('oss_upload', args, 'error uploading to OSS');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Upload a local file or directory to a URL anonymously.
   * 
   * @param url - The HTTP/HTTPS URL to upload the file to.
   * @param path - Local file or directory path to upload.
   * @returns The content field from the API response
   */
  async uploadAnonymous(url: string, path: string): Promise<any> {
    const args = {
      url,
      path
    };
    
    const result = await this.callMcpTool('oss_upload_annon', args, 'error uploading anonymously');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Download an object from OSS to a local file.
   * 
   * @param bucket - OSS bucket name.
   * @param object - Object key in OSS.
   * @param path - Local path to save the downloaded file.
   * @returns The content field from the API response
   */
  async download(bucket: string, object: string, path: string): Promise<any> {
    const args = {
      bucket,
      object,
      path
    };
    
    const result = await this.callMcpTool('oss_download', args, 'error downloading from OSS');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }

  /**
   * Download a file from a URL anonymously to a local file.
   * 
   * @param url - The HTTP/HTTPS URL to download the file from.
   * @param path - The full local file path to save the downloaded file.
   * @returns The content field from the API response
   */
  async downloadAnonymous(url: string, path: string): Promise<any> {
    const args = {
      url,
      path
    };
    
    const result = await this.callMcpTool('oss_download_annon', args, 'error downloading anonymously');
    
    // Return the raw content field for the caller to parse
    return result.data.content;
  }
}
