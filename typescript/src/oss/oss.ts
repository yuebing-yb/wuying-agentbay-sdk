import { APIError } from '../exceptions';
import { Session } from '../session';
import Client from '../api/client';
import { CallMcpToolRequest } from '../api/models/model';

import * as $_client from '../api';

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
   * Create an OSS client with the provided credentials.
   * 
   * @param accessKeyId - The Access Key ID for OSS authentication.
   * @param accessKeySecret - The Access Key Secret for OSS authentication.
   * @param endpoint - The OSS service endpoint. If not specified, the default is used.
   * @param region - The OSS region. If not specified, the default is used.
   * @returns The result of the client creation operation.
   */
  async createClient(
    accessKeyId: string, 
    accessKeySecret: string, 
    endpoint?: string, 
    region?: string
  ): Promise<string> {
    try {
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
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'oss_client_create',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract result from response
      const data = response.body.data as any;
      if (typeof data.result !== 'string') {
        throw new Error('Result field not found or not a string');
      }
      
      return data.result;
    } catch (error) {
      throw new APIError(`Failed to create OSS client: ${error}`);
    }
  }

  /**
   * Upload a local file or directory to OSS.
   * 
   * @param bucket - OSS bucket name.
   * @param object - Object key in OSS.
   * @param path - Local file or directory path to upload.
   * @returns The result of the upload operation.
   */
  async upload(bucket: string, object: string, path: string): Promise<string> {
    try {
      const args = {
        bucket,
        object,
        path
      };
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'oss_upload',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract result from response
      const data = response.body.data as any;
      if (typeof data.result !== 'string') {
        throw new Error('Result field not found or not a string');
      }
      
      return data.result;
    } catch (error) {
      throw new APIError(`Failed to upload to OSS: ${error}`);
    }
  }

  /**
   * Upload a local file or directory to a URL anonymously.
   * 
   * @param url - The HTTP/HTTPS URL to upload the file to.
   * @param path - Local file or directory path to upload.
   * @returns The result of the upload operation.
   */
  async uploadAnonymous(url: string, path: string): Promise<string> {
    try {
      const args = {
        url,
        path
      };
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'oss_upload_annon',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract result from response
      const data = response.body.data as any;
      if (typeof data.result !== 'string') {
        throw new Error('Result field not found or not a string');
      }
      
      return data.result;
    } catch (error) {
      throw new APIError(`Failed to upload anonymously: ${error}`);
    }
  }

  /**
   * Download an object from OSS to a local file.
   * 
   * @param bucket - OSS bucket name.
   * @param object - Object key in OSS.
   * @param path - Local path to save the downloaded file.
   * @returns The result of the download operation.
   */
  async download(bucket: string, object: string, path: string): Promise<string> {
    try {
      const args = {
        bucket,
        object,
        path
      };
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'oss_download',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract result from response
      const data = response.body.data as any;
      if (typeof data.result !== 'string') {
        throw new Error('Result field not found or not a string');
      }
      
      return data.result;
    } catch (error) {
      throw new APIError(`Failed to download from OSS: ${error}`);
    }
  }

  /**
   * Download a file from a URL anonymously to a local file.
   * 
   * @param url - The HTTP/HTTPS URL to download the file from.
   * @param path - The full local file path to save the downloaded file.
   * @returns The result of the download operation.
   */
  async downloadAnonymous(url: string, path: string): Promise<string> {
    try {
      const args = {
        url,
        path
      };
      
      const callToolRequest = new $_client.CallMcpToolRequest({
        authorization: `Bearer ${this.session.getAPIKey()}`,
        sessionId: this.session.getSessionId(),
        name: 'oss_download_annon',
        args: JSON.stringify(args)
      });
      console.log(callToolRequest, 'callToolRequest');
      
      const response = await this.session.getClient().callMcpTool(callToolRequest);
      console.log(response, 'response');
      
      if (!response.body?.data) {
        throw new Error('Invalid response data format');
      }
      
      // Extract result from response
      const data = response.body.data as any;
      if (typeof data.result !== 'string') {
        throw new Error('Result field not found or not a string');
      }
      
      return data.result;
    } catch (error) {
      throw new APIError(`Failed to download anonymously: ${error}`);
    }
  }
}
