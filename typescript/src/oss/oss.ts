import { Session } from "../session";
import {
  OSSClientResult,
  OSSUploadResult,
  OSSDownloadResult,
} from "../types/api-response";


/**
 * Handles OSS operations in the AgentBay cloud environment.
 */
export class Oss {
  private session: Session;

  /**
   * Initialize an Oss object.
   *
   * @param session - The Session instance that this Oss belongs to.
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
   * Initialize OSS environment variables with the specified STS temporary credentials.
   * Corresponds to Python's env_init() method
   *
   * @param accessKeyId - The access key ID from STS temporary credentials
   * @param accessKeySecret - The access key secret from STS temporary credentials
   * @param securityToken - The security token from STS temporary credentials (required)
   * @param endpoint - The OSS endpoint (optional)
   * @param region - The OSS region (optional)
   * @returns OSSClientResult with client configuration and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   const result = await createResult.session.oss.envInit('sts_key_id', 'sts_key_secret', 'sts_token', 'oss-cn-hangzhou.aliyuncs.com', 'cn-hangzhou');
   *   console.log('OSS initialized:', result.success);
   *   await createResult.session.delete();
   * }
   * ```
   */
  async envInit(
    accessKeyId: string,
    accessKeySecret: string,
    securityToken: string,
    endpoint?: string,
    region?: string
  ): Promise<OSSClientResult> {
    try {
      const args = {
        access_key_id: accessKeyId,
        access_key_secret: accessKeySecret,
        security_token: securityToken,
        endpoint: endpoint || "",
        region: region || "",
      };
      const result = await this.session.callMcpTool(
        "oss_env_init",
        args,
        false
      );
      
      if (result.success) {
        if (result.data) {
          const clientConfigRaw = result.data;
          // Check if data contains "failed" field
          if (typeof clientConfigRaw === 'string' && clientConfigRaw.toLowerCase().includes('failed')) {
            return {
              requestId: result.requestId,
              success: false,
              clientConfig: "",
              errorMessage: `OSS environment initialization failed: ${clientConfigRaw}`,
            };
          }
          return {
            requestId: result.requestId,
            success: true,
            clientConfig: clientConfigRaw,
            errorMessage: "",
          };
        } else {
          return {
            requestId: result.requestId,
            success: false,
            clientConfig: "",
            errorMessage: "Failed to initialize OSS environment",
          };
        }
      } else {
        return {
          requestId: result.requestId,
          success: false,
          clientConfig: "",
          errorMessage: result.errorMessage || "Failed to initialize OSS environment",
        };
      }
    } catch (error) {
      return {
        requestId: "",
        success: false,
        clientConfig: "",
        errorMessage: `Failed to initialize OSS environment: ${error}`,
      };
    }
  }

  /**
   * Upload a file to OSS.
   * Corresponds to Python's upload() method
   *
   * @param bucket - The OSS bucket name
   * @param object - The OSS object key
   * @param path - The local file path to upload
   * @returns OSSUploadResult with upload result and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   await createResult.session.oss.envInit('key_id', 'key_secret', 'token', 'oss-cn-hangzhou.aliyuncs.com', 'cn-hangzhou');
   *   const result = await createResult.session.oss.upload('my-bucket', 'my-folder/file.txt', '/path/to/local/file.txt');
   *   console.log('Upload success:', result.success);
   *   await createResult.session.delete();
   * }
   * ```
   */
  async upload(
    bucket: string,
    object: string,
    path: string
  ): Promise<OSSUploadResult> {
    try {
      const args = {
        bucket,
        object,
        path,
      };
      const result = await this.session.callMcpTool(
        "oss_upload",
        args,
        false
      );

      return {
        requestId: result.requestId,
        success: result.success,
        content: result.data,
        errorMessage: result.errorMessage,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to upload file: ${error}`,
      };
    }
  }

  /**
   * Upload a file to OSS using an anonymous URL.
   * Corresponds to Python's upload_anonymous() method
   *
   * @param url - The anonymous upload URL
   * @param path - The local file path to upload
   * @returns OSSUploadResult with upload result and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   const result = await createResult.session.oss.uploadAnonymous('https://example.com/upload', '/path/to/local/file.txt');
   *   console.log('Anonymous upload success:', result.success);
   *   await createResult.session.delete();
   * }
   * ```
   */
  async uploadAnonymous(url: string, path: string): Promise<OSSUploadResult> {
    try {
      const args = {
        url,
        path,
      };
      const result = await this.session.callMcpTool(
        "oss_upload_annon",
        args,
        false
      );

      return {
        requestId: result.requestId,
        success: result.success,
        content: result.data,
        errorMessage: result.errorMessage,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to upload file anonymously: ${error}`,
      };
    }
  }

  /**
   * Download a file from OSS.
   * Corresponds to Python's download() method
   *
   * @param bucket - The OSS bucket name
   * @param object - The OSS object key
   * @param path - The local file path to save the downloaded file
   * @returns OSSDownloadResult with download result and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   await createResult.session.oss.envInit('key_id', 'key_secret', 'token', 'oss-cn-hangzhou.aliyuncs.com', 'cn-hangzhou');
   *   const result = await createResult.session.oss.download('my-bucket', 'my-folder/file.txt', '/path/to/save/file.txt');
   *   console.log('Download success:', result.success);
   *   await createResult.session.delete();
   * }
   * ```
   */
  async download(
    bucket: string,
    object: string,
    path: string
  ): Promise<OSSDownloadResult> {
    try {
      const args = {
        bucket,
        object,
        path,
      };
      const result = await this.session.callMcpTool(
        "oss_download",
        args,
        false
      );

      return {
        requestId: result.requestId,
        success: result.success,
        content: result.data,
        errorMessage: result.errorMessage,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to download file: ${error}`,
      };
    }
  }

  /**
   * Download a file from OSS using an anonymous URL.
   * Corresponds to Python's download_anonymous() method
   *
   * @param url - The anonymous download URL
   * @param path - The local file path to save the downloaded file
   * @returns OSSDownloadResult with download result and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const createResult = await agentBay.create();
   * if (createResult.success) {
   *   const result = await createResult.session.oss.downloadAnonymous('https://example.com/file.txt', '/path/to/save/file.txt');
   *   console.log('Anonymous download success:', result.success);
   *   await createResult.session.delete();
   * }
   * ```
   */
  async downloadAnonymous(
    url: string,
    path: string
  ): Promise<OSSDownloadResult> {
    try {
      const args = {
        url,
        path,
      };
      const result = await this.session.callMcpTool(
        "oss_download_annon",
        args,
        false
      );

      return {
        requestId: result.requestId,
        success: result.success,
        content: result.data,
        errorMessage: result.errorMessage,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        content: "",
        errorMessage: `Failed to download file anonymously: ${error}`,
      };
    }
  }
}
