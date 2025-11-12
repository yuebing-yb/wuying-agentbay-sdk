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
   * Initialize OSS environment variables with the specified credentials.
   * Corresponds to Python's env_init() method
   *
   * @param accessKeyId - The access key ID
   * @param accessKeySecret - The access key secret
   * @param securityToken - The security token (optional)
   * @param endpoint - The OSS endpoint (optional)
   * @param region - The OSS region (optional)
   * @returns OSSClientResult with client configuration and requestId
   * @throws APIError if the operation fails.
   *
   * @example
   * ```typescript
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function initializeOssEnvironment() {
   *   try {
   *     const createResult = await agentBay.create();
   *     if (createResult.success) {
   *       const session = createResult.session;
   *
   *       const result = await session.oss.envInit(
   *         'your_access_key_id',
   *         'your_access_key_secret',
   *         'your_security_token',
   *         'oss-cn-hangzhou.aliyuncs.com',
   *         'cn-hangzhou'
   *       );
   *
   *       if (result.success) {
   *         console.log('OSS environment initialized successfully');
   *         // Output: OSS environment initialized successfully
   *         console.log(`Request ID: ${result.requestId}`);
   *       } else {
   *         console.error(`Failed to initialize OSS: ${result.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * initializeOssEnvironment().catch(console.error);
   * ```
   */
  async envInit(
    accessKeyId: string,
    accessKeySecret: string,
    securityToken?: string,
    endpoint?: string,
    region?: string
  ): Promise<OSSClientResult> {
    try {
      const args = {
        access_key_id: accessKeyId,
        access_key_secret: accessKeySecret,
        security_token: securityToken || "",
        endpoint: endpoint || "",
        region: region || "",
      };
      const result = await this.session.callMcpTool("oss_env_init", args);

      if (!result.success) {
        return {
          requestId: result.requestId,
          success: false,
          clientConfig: {},
          errorMessage: result.errorMessage,
        };
      }

      let clientConfig: Record<string, any> = {};
      try {
        clientConfig = JSON.parse(result.data);
      } catch (err) {
        return {
          requestId: result.requestId,
          success: false,
          clientConfig: {},
          errorMessage: `Failed to parse client config: ${err}`,
        };
      }

      return {
        requestId: result.requestId,
        success: true,
        clientConfig,
        errorMessage: "",
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        clientConfig: {},
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
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function uploadFileToOss() {
   *   try {
   *     const createResult = await agentBay.create();
   *     if (createResult.success) {
   *       const session = createResult.session;
   *
   *       // First, initialize OSS environment
   *       await session.oss.envInit(
   *         'your_access_key_id',
   *         'your_access_key_secret',
   *         'your_security_token',
   *         'oss-cn-hangzhou.aliyuncs.com',
   *         'cn-hangzhou'
   *       );
   *
   *       // Upload a file to OSS
   *       const result = await session.oss.upload(
   *         'my-bucket',
   *         'my-folder/file.txt',
   *         '/path/to/local/file.txt'
   *       );
   *
   *       if (result.success) {
   *         console.log('File uploaded successfully');
   *         // Output: File uploaded successfully
   *         console.log(`Request ID: ${result.requestId}`);
   *       } else {
   *         console.error(`Upload failed: ${result.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * uploadFileToOss().catch(console.error);
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
      const result = await this.session.callMcpTool("oss_upload", args);

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
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function uploadFileAnonymously() {
   *   try {
   *     const createResult = await agentBay.create();
   *     if (createResult.success) {
   *       const session = createResult.session;
   *
   *       // Upload file using an anonymous URL
   *       const result = await session.oss.uploadAnonymous(
   *         'https://example.com/upload',
   *         '/path/to/local/file.txt'
   *       );
   *
   *       if (result.success) {
   *         console.log('File uploaded anonymously');
   *         // Output: File uploaded anonymously
   *         console.log(`Request ID: ${result.requestId}`);
   *       } else {
   *         console.error(`Upload failed: ${result.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * uploadFileAnonymously().catch(console.error);
   * ```
   */
  async uploadAnonymous(url: string, path: string): Promise<OSSUploadResult> {
    try {
      const args = {
        url,
        path,
      };
      const result = await this.session.callMcpTool("oss_upload_annon", args);

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
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function downloadFileFromOss() {
   *   try {
   *     const createResult = await agentBay.create();
   *     if (createResult.success) {
   *       const session = createResult.session;
   *
   *       // First, initialize OSS environment
   *       await session.oss.envInit(
   *         'your_access_key_id',
   *         'your_access_key_secret',
   *         'your_security_token',
   *         'oss-cn-hangzhou.aliyuncs.com',
   *         'cn-hangzhou'
   *       );
   *
   *       // Download a file from OSS
   *       const result = await session.oss.download(
   *         'my-bucket',
   *         'my-folder/file.txt',
   *         '/path/to/save/file.txt'
   *       );
   *
   *       if (result.success) {
   *         console.log('File downloaded successfully');
   *         // Output: File downloaded successfully
   *         console.log(`Request ID: ${result.requestId}`);
   *       } else {
   *         console.error(`Download failed: ${result.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * downloadFileFromOss().catch(console.error);
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
      const result = await this.session.callMcpTool("oss_download", args);

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
   * import { AgentBay } from 'wuying-agentbay-sdk';
   *
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   *
   * async function downloadFileAnonymously() {
   *   try {
   *     const createResult = await agentBay.create();
   *     if (createResult.success) {
   *       const session = createResult.session;
   *
   *       // Download file using an anonymous URL
   *       const result = await session.oss.downloadAnonymous(
   *         'https://example.com/file.txt',
   *         '/path/to/save/file.txt'
   *       );
   *
   *       if (result.success) {
   *         console.log('File downloaded anonymously');
   *         // Output: File downloaded anonymously
   *         console.log(`Request ID: ${result.requestId}`);
   *       } else {
   *         console.error(`Download failed: ${result.errorMessage}`);
   *       }
   *
   *       await session.delete();
   *     }
   *   } catch (error) {
   *     console.error('Error:', error);
   *   }
   * }
   *
   * downloadFileAnonymously().catch(console.error);
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
      const result = await this.session.callMcpTool("oss_download_annon", args);

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
