import { AgentBay, Session } from '../../src';
import { getTestApiKey, containsToolNotFound } from '../utils/test-helpers';
import { log } from '../../src/utils/logger';

// Helper function to get OSS credentials from environment variables or use defaults
function getOssCredentials(): {
  accessKeyId: string;
  accessKeySecret: string;
  securityToken: string;
  endpoint: string;
  region: string;
} {
  const accessKeyId = process.env.OSS_ACCESS_KEY_ID || 'test-access-key-id';
  const accessKeySecret = process.env.OSS_ACCESS_KEY_SECRET || 'test-access-key-secret';
  const securityToken = process.env.OSS_SECURITY_TOKEN || 'test-security-token';
  const endpoint = process.env.OSS_ENDPOINT || 'https://oss-cn-hangzhou.aliyuncs.com';
  const region = process.env.OSS_REGION || 'cn-hangzhou';

  if (!process.env.OSS_ACCESS_KEY_ID) {
    log('OSS_ACCESS_KEY_ID environment variable not set, using default value');
  }
  if (!process.env.OSS_ACCESS_KEY_SECRET) {
    log('OSS_ACCESS_KEY_SECRET environment variable not set, using default value');
  }
  if (!process.env.OSS_SECURITY_TOKEN) {
    log('OSS_SECURITY_TOKEN environment variable not set, using default value');
  }
  if (!process.env.OSS_ENDPOINT) {
    log('OSS_ENDPOINT environment variable not set, using default value');
  }
  if (!process.env.OSS_REGION) {
    log('OSS_REGION environment variable not set, using default value');
  }

  return {
    accessKeyId,
    accessKeySecret,
    securityToken,
    endpoint,
    region
  };
}

// Helper function to check if content has error
function hasErrorInContent(content: any[]): boolean {
  if (!Array.isArray(content)) {
    return true;
  }
  
  if (content.length === 0) {
    return true;
  }
  
  // Check if first content item has error text
  return content.some(item => 
    item && typeof item === 'object' && 
    item.text && typeof item.text === 'string' && 
    (item.text.includes('error') || item.text.includes('Error'))
  );
}

describe('OSS', () => {
  let agentBay: AgentBay;
  let session: Session;
  
  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    
    // Create a session
    log('Creating a new session for OSS testing...');
    session = await agentBay.create({ imageId: 'code_latest' });
    log(`Session created with ID: ${session.sessionId}`);
  });
  
  afterEach(async () => {
    // Clean up the session
    log('Cleaning up: Deleting the session...');
    try {
      if(session)
        await agentBay.delete(session);
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });
  
  describe('envInit', () => {
    it.only('should initialize OSS environment', async () => {
      if (session.oss) {
        // Get OSS credentials from environment variables
        const { accessKeyId, accessKeySecret, securityToken, endpoint, region } = getOssCredentials();
        
        log('Initializing OSS environment...');
        try {
          const content = await session.oss.envInit(accessKeyId, accessKeySecret, securityToken, endpoint, region);
          log(`EnvInit content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS environment initialization successful');
        } catch (error) {
          log(`OSS environment initialization failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS interface is nil, skipping OSS test');
      }
    });
  });
  
  describe('upload', () => {
    it.only('should upload a file to OSS', async () => {
      if (session.oss && session.filesystem) {
        // First initialize the OSS environment
        const { accessKeyId, accessKeySecret, securityToken, endpoint, region } = getOssCredentials();
        await session.oss.envInit(accessKeyId, accessKeySecret, securityToken, endpoint, region);
        
        // Create a test file to upload
        const testContent = "This is a test file for OSS upload.";
        const testFilePath = "/tmp/test_oss_upload.txt";
        await session.filesystem.writeFile(testFilePath, testContent);
        
        log('Uploading file to OSS...');
        const bucket = process.env.OSS_TEST_BUCKET || 'test-bucket';
        const objectKey = 'test-object.txt';
        
        try {
          const content = await session.oss.upload(bucket, objectKey, testFilePath);
          log(`Upload content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS upload successful');
        } catch (error) {
          log(`OSS upload failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS or FileSystem interface is nil, skipping OSS test');
      }
    });
  });
  
  describe('uploadAnonymous', () => {
    it.only('should upload a file anonymously', async () => {
      if (session.oss && session.filesystem) {
        // Create a test file to upload
        const testContent = "This is a test file for OSS anonymous upload.";
        const testFilePath = "/tmp/test_oss_upload_anon.txt";
        await session.filesystem.writeFile(testFilePath, testContent);
        
        log('Uploading file anonymously...');
        const uploadUrl = process.env.OSS_TEST_UPLOAD_URL || 'https://example.com/upload/test-file.txt';
        
        try {
          const content = await session.oss.uploadAnonymous(uploadUrl, testFilePath);
          log(`UploadAnonymous content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS anonymous upload successful');
        } catch (error) {
          log(`OSS anonymous upload failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS or FileSystem interface is nil, skipping OSS test');
      }
    });
  });
  
  describe('download', () => {
    it.only('should download a file from OSS', async () => {
      if (session.oss && session.filesystem) {
        // First initialize the OSS environment
        const { accessKeyId, accessKeySecret, securityToken, endpoint, region } = getOssCredentials();
        await session.oss.envInit(accessKeyId, accessKeySecret, securityToken, endpoint, region);
        
        log('Downloading file from OSS...');
        const bucket = process.env.OSS_TEST_BUCKET || 'test-bucket';
        const objectKey = 'test-object.txt';
        const downloadPath = "/tmp/test_oss_download.txt";
        
        try {
          const content = await session.oss.download(bucket, objectKey, downloadPath);
          log(`Download content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS download successful');
          
          // Verify the downloaded file exists
          const fileInfo = await session.filesystem.getFileInfo(downloadPath);
          log(`Downloaded file info:`, fileInfo);
          expect(fileInfo).toBeDefined();
        } catch (error) {
          log(`OSS download failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS or FileSystem interface is nil, skipping OSS test');
      }
    });
  });
  
  describe('downloadAnonymous', () => {
    it.only('should download a file anonymously', async () => {
      if (session.oss && session.filesystem) {
        log('Downloading file anonymously...');
        const downloadUrl = process.env.OSS_TEST_DOWNLOAD_URL || 'https://example.com/download/test-file.txt';
        const downloadPath = "/tmp/test_oss_download_anon.txt";
        
        try {
          const content = await session.oss.downloadAnonymous(downloadUrl, downloadPath);
          log(`DownloadAnonymous content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS anonymous download successful');
          
          // Verify the downloaded file exists
          const fileInfo = await session.filesystem.getFileInfo(downloadPath);
          log(`Downloaded file info:`, fileInfo);
          expect(fileInfo).toBeDefined();
        } catch (error) {
          log(`OSS anonymous download failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS or FileSystem interface is nil, skipping OSS test');
      }
    });
  });
  
  describe('createClient', () => {
    it.only('should create an OSS client', async () => {
      if (session.oss) {
        // Get OSS credentials from environment variables
        const { accessKeyId, accessKeySecret, endpoint, region } = getOssCredentials();
        
        log('Creating OSS client...');
        try {
          const content = await session.oss.createClient(accessKeyId, accessKeySecret, endpoint, region);
          log(`CreateClient content:`, content);
          
          // Check if content has errors
          expect(content).toBeDefined();
          expect(Array.isArray(content)).toBe(true);
          expect(hasErrorInContent(content)).toBe(false);
          
          log('OSS client creation successful');
        } catch (error) {
          log(`OSS client creation failed: ${error}`);
          throw error;
        }
      } else {
        log('Note: OSS interface is nil, skipping OSS test');
      }
    });
  });
});
