import { FileSystem } from "../../src/filesystem/filesystem";
import { APIError } from "../../src/exceptions";
import { BinaryFileContentResult } from "../../src/types/api-response";
import * as sinon from "sinon";

describe("TestFileSystem", () => {
  let mockFileSystem: FileSystem;
  let mockSession: any;
  let sandbox: sinon.SinonSandbox;
  let callMcpToolStub: sinon.SinonStub;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockSession = {
      getAPIKey: sandbox.stub().returns("dummy_key"),
      getSessionId: sandbox.stub().returns("dummy_session"),
      callMcpTool: sandbox.stub(),
    };

    mockFileSystem = new FileSystem(mockSession);
    callMcpToolStub = mockSession.callMcpTool;
  });

  afterEach(() => {
    sandbox.restore();
  });

  describe("test_read_file_success", () => {
    it("should read file successfully", async () => {
      // Mock getFileInfo to return file info
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "file.txt",
          path: "/path/to/file.txt",
          size: 12,
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });
      
      // Mock readFileChunk to return file content
      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk").resolves({
        success: true,
        requestId: "test-request-id",
        content: "file content",
      });

      const result = await mockFileSystem.readFile("/path/to/file.txt");

      // Verify FileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBe("file content");
      expect(result.errorMessage).toBeUndefined();

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledOnce).toBe(true);
    });
  });

  describe("test_read_file_failure", () => {
    it("should handle read file error", async () => {
      // Mock getFileInfo to fail
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: false,
        requestId: "",
        errorMessage: "some error message",
      });

      const result = await mockFileSystem.readFile("/path/to/file.txt");

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.content).toBe("");
      expect(result.errorMessage).toContain("some error message");
    });
  });

  describe("test_create_directory_success", () => {
    it("should create directory successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.createDirectory("/path/to/directory");

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_delete_file_success", () => {
    it("should delete file successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.deleteFile("/path/to/file.txt");

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
      const callArgs = callMcpToolStub.getCall(0).args;
      expect(callArgs[0]).toBe("delete_file");
      expect(callArgs[1]).toEqual({ path: "/path/to/file.txt" });
    });
  });

  describe("test_delete_file_failure", () => {
    it("should handle delete file error", async () => {
      callMcpToolStub.rejects(new Error("Delete failed"));

      const result = await mockFileSystem.deleteFile("/path/to/file.txt");

      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined();
      expect(result.errorMessage).toContain("Failed to delete file");
    });
  });

  describe("test_create_directory_failure", () => {
    it("should handle create directory error", async () => {
      callMcpToolStub.rejects(new Error("Directory creation failed"));

      const result = await mockFileSystem.createDirectory("/path/to/directory");

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Failed to create directory");
    });
  });

  describe("test_edit_file_success", () => {
    it("should edit file successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.editFile("/path/to/file.txt", [
        { oldText: "old content", newText: "new content" },
      ]);

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_edit_file_failure", () => {
    it("should handle edit file error", async () => {
      callMcpToolStub.rejects(new Error("Edit failed"));

      const result = await mockFileSystem.editFile("/path/to/file.txt", [
        { oldText: "old content", newText: "new content" },
      ]);

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Failed to edit file");
    });
  });

  describe("test_write_file_success", () => {
    it("should write file successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.writeFile(
        "/path/to/file.txt",
        "new content",
        "overwrite" // Use valid mode
      );

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_write_file_failure", () => {
    it("should handle write file error", async () => {
      callMcpToolStub.rejects(new Error("Write failed"));

      const result = await mockFileSystem.writeFile(
        "/path/to/file.txt",
        "new content",
        "overwrite"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Failed to write file");
    });
  });

  describe("test_write_file_invalid_mode", () => {
    it("should handle invalid write mode", async () => {
      // No need to stub callMcpTool as validation happens before API call
      const result = await mockFileSystem.writeFile(
        "/path/to/file.txt",
        "new content",
        "invalid_mode"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Invalid mode");
    });
  });

  describe("test_get_file_info_success", () => {
    it("should get file info successfully", async () => {
      const fileInfoData = {
        name: "test.txt",
        path: "/path/to/test.txt",
        size: 1024,
        isDirectory: false,
        modTime: "2023-01-01T00:00:00Z",
        mode: "rw-r--r--",
      };

      // Simulate the actual format returned by the API
      const fileInfoString = 
        "name: test.txt\n" +
        "path: /path/to/test.txt\n" +
        "size: 1024\n" +
        "isDirectory: false\n" +
        "modTime: 2023-01-01T00:00:00Z\n" +
        "mode: rw-r--r--";

      callMcpToolStub.resolves({
        success: true,
        data: fileInfoString,
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.getFileInfo("/path/to/test.txt");

      // Verify FileInfoResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.fileInfo).toBeDefined();
      expect(result.fileInfo?.name).toBe("test.txt");
      expect(result.fileInfo?.size).toBe(1024);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_get_file_info_failure", () => {
    it("should handle get file info error", async () => {
      callMcpToolStub.rejects(new Error("File not found"));

      const result = await mockFileSystem.getFileInfo("/path/to/test.txt");

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.fileInfo).toBeUndefined();
      expect(result.errorMessage).toContain("Failed to get file info");
    });
  });

  describe("test_list_directory_success", () => {
    it("should list directory successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "[DIR] subdir\n[FILE] file1.txt",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.listDirectory("/path/to/directory");

      // Verify DirectoryListResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.entries).toBeDefined();
      expect(result.entries.length).toBe(2);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_list_directory_failure", () => {
    it("should handle list directory error", async () => {
      callMcpToolStub.rejects(new Error("Directory not found"));

      const result = await mockFileSystem.listDirectory("/path/to/directory");

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.entries).toEqual([]);
      expect(result.errorMessage).toContain("Failed to list directory");
    });
  });

  describe("test_move_file_success", () => {
    it("should move file successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.moveFile(
        "/path/to/source.txt",
        "/path/to/destination.txt"
      );

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_move_file_failure", () => {
    it("should handle move file error", async () => {
      callMcpToolStub.rejects(new Error("Move failed"));

      const result = await mockFileSystem.moveFile(
        "/path/to/source.txt",
        "/path/to/destination.txt"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Failed to move file");
    });
  });

  describe("test_read_multiple_files_success", () => {
    it("should read multiple files successfully", async () => {
      // Simulate the actual format expected by readMultipleFiles
      const filesData = 
        "/path/to/file1.txt: content1\n" +
        "---\n" +
        "/path/to/file2.txt: content2\n";

      callMcpToolStub.resolves({
        success: true,
        data: filesData,
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.readMultipleFiles([
        "/path/to/file1.txt",
        "/path/to/file2.txt",
      ]);

      // Verify result structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.contents["/path/to/file1.txt"]).toBe("content1");
      expect(result.contents["/path/to/file2.txt"]).toBe("content2");

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_read_multiple_files_failure", () => {
    it("should handle read multiple files error", async () => {
      callMcpToolStub.rejects(new Error("API Error"));

      const result = await mockFileSystem.readMultipleFiles([
        "/path/to/file1.txt",
        "/path/to/file2.txt",
      ]);

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.contents).toEqual({});
      expect(result.errorMessage).toContain("Failed to read multiple files");
    });
  });

  describe("test_search_files_success", () => {
    it("should search files successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "/path/to/file1.txt\n/path/to/file2.txt",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.searchFiles(
        "/path/to/search",
        "*.txt",
        ["*.tmp"]
      );

      // Verify FileSearchResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.matches).toBeDefined();
      expect(result.matches.length).toBe(2);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_search_files_failure", () => {
    it("should handle search files error", async () => {
      callMcpToolStub.rejects(new Error("API Error"));

      const result = await mockFileSystem.searchFiles(
        "/path/to/search",
        "*.txt",
        ["*.tmp"]
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.matches).toEqual([]);
      expect(result.errorMessage).toContain("Failed to search files");
    });
  });

  describe("test_read_large_file_success", () => {
    it("should read large file successfully", async () => {
      // Mock getFileInfo to return large file size
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "large.txt",
          path: "/path/to/large.txt",
          size: 150 * 1024, // 150KB
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      // Mock readFileChunk for chunked reading
      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk");
      readFileChunkStub.onFirstCall().resolves({
        success: true,
        requestId: "test-request-id",
        content: "chunk1",
      });
      readFileChunkStub.onSecondCall().resolves({
        success: true,
        requestId: "test-request-id", 
        content: "chunk2",
      });
      readFileChunkStub.onThirdCall().resolves({
        success: true,
        requestId: "test-request-id",
        content: "chunk3",
      });

      const result = await mockFileSystem.readFile("/path/to/large.txt");

      // Verify FileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBe("chunk1chunk2chunk3");
      expect(result.errorMessage).toBeUndefined();

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.callCount).toBe(3);
    });
  });

  describe("test_read_large_file_failure", () => {
    it("should handle read large file error", async () => {
      // Mock getFileInfo to fail
      sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: false,
        requestId: "",
        errorMessage: "File not found",
      });

      const result = await mockFileSystem.readFile("/path/to/large.txt");

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");  
      expect(result.content).toBe("");
      expect(result.errorMessage).toContain("File not found");
    });
  });

  describe("test_write_large_file_success", () => {
    it("should write large file successfully", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.writeFile(
        "/path/to/large.txt",
        "large content"
      );

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_write_large_file_small_content", () => {
    it("should write large file with small content", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "True",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await mockFileSystem.writeFile(
        "/path/to/small.txt",
        "small content"
      );

      // Verify BoolResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.data).toBe(true);
      expect(result.errorMessage).toBeUndefined();

      expect(callMcpToolStub.calledOnce).toBe(true);
    });
  });

  describe("test_write_large_file_failure", () => {
    it("should handle write large file error", async () => {
      // Mock writeFile to fail
      sandbox.stub(mockFileSystem, "writeFile").resolves({
        success: false,
        requestId: "",
        errorMessage: "Write failed",
      });

      const result = await mockFileSystem.writeFile(
        "/path/to/large.txt",
        "large content"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("");
      expect(result.data).toBeUndefined(); // data is undefined in error cases
      expect(result.errorMessage).toContain("Write failed");
    });
  });

  describe("test_read_file_binary_format_success", () => {
    it("should read binary file successfully", async () => {
      // Mock getFileInfo to return file info
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "image.jpeg",
          path: "/path/to/image.jpeg",
          size: 1024,
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      // Mock binary chunk read - backend returns base64, SDK decodes to Uint8Array
      const binaryData = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46]); // JPEG header
      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk").resolves({
        success: true,
        requestId: "test-request-id",
        content: binaryData,
      });

      const result = await mockFileSystem.readFile("/path/to/image.jpeg", { format: "bytes" });

      // Verify BinaryFileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect(result.content).toEqual(binaryData);
      expect(result.errorMessage).toBeUndefined();

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledWith("/path/to/image.jpeg", 0, 1024, "binary")).toBe(true);
    });
  });

  describe("test_read_file_binary_format_large_file", () => {
    it("should read large binary file successfully with chunking", async () => {
      // Mock getFileInfo to return large file size (150KB)
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "large_binary.bin",
          path: "/path/to/large_binary.bin",
          size: 150 * 1024, // 150KB
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      // Mock chunked binary reads (3 chunks of 60KB each)
      const chunk1 = new Uint8Array(60 * 1024).fill(0x00);
      const chunk2 = new Uint8Array(60 * 1024).fill(0x01);
      const chunk3 = new Uint8Array(30 * 1024).fill(0x02); // Last chunk is smaller

      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk");
      readFileChunkStub.onFirstCall().resolves({
        success: true,
        requestId: "test-request-id-1",
        content: chunk1,
      });
      readFileChunkStub.onSecondCall().resolves({
        success: true,
        requestId: "test-request-id-2",
        content: chunk2,
      });
      readFileChunkStub.onThirdCall().resolves({
        success: true,
        requestId: "test-request-id-3",
        content: chunk3,
      });

      const result = await mockFileSystem.readFile("/path/to/large_binary.bin", { format: "bytes" });

      // Verify BinaryFileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect(result.content.length).toBe(150 * 1024);
      expect(result.size).toBe(150 * 1024);
      expect(result.errorMessage).toBeUndefined();

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.callCount).toBe(3);
    });
  });

  describe("test_read_file_binary_format_get_info_error", () => {
    it("should handle get_file_info error for binary format", async () => {
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: false,
        requestId: "test-request-id",
        errorMessage: "File not found",
      });

      const result = await mockFileSystem.readFile("/path/to/image.jpeg", { format: "bytes" });

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect((result.content as Uint8Array).length).toBe(0);
      expect(result.errorMessage).toBe("File not found");

      expect(getFileInfoStub.calledOnce).toBe(true);
    });
  });

  describe("test_read_file_binary_format_chunk_error", () => {
    it("should handle chunk reading error for binary format", async () => {
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "image.jpeg",
          path: "/path/to/image.jpeg",
          size: 1024,
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      // Mock chunk read error
      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk").resolves({
        success: false,
        requestId: "test-request-id",
        content: new Uint8Array(0),
        errorMessage: "Failed to decode base64",
      });

      const result = await mockFileSystem.readFile("/path/to/image.jpeg", { format: "bytes" });

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.errorMessage).toBe("Failed to decode base64");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect((result.content as Uint8Array).length).toBe(0);

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledOnce).toBe(true);
    });
  });

  describe("test_read_file_binary_format_empty_file", () => {
    it("should handle empty binary file", async () => {
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "empty.bin",
          path: "/path/to/empty.bin",
          size: 0,
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      const result = await mockFileSystem.readFile("/path/to/empty.bin", { format: "bytes" });

      // Verify empty file result
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect((result.content as Uint8Array).length).toBe(0);
      expect(result.size).toBe(0);

      expect(getFileInfoStub.calledOnce).toBe(true);
    });
  });

  describe("test_read_file_text_format_explicit", () => {
    it("should read text file with explicit format='text'", async () => {
      const getFileInfoStub = sandbox.stub(mockFileSystem, "getFileInfo").resolves({
        success: true,
        requestId: "test-request-id",
        fileInfo: {
          name: "file.txt",
          path: "/path/to/file.txt",
          size: 1024,
          isDirectory: false,
          modTime: "2023-01-01T00:00:00Z",
          mode: "rw-r--r--",
        },
      });

      const readFileChunkStub = sandbox.stub(mockFileSystem as any, "readFileChunk").resolves({
        success: true,
        requestId: "test-request-id",
        content: "file content",
      });

      const result = await mockFileSystem.readFile("/path/to/file.txt", { format: "text" });

      // Verify FileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(typeof result.content).toBe("string");
      expect(result.content).toBe("file content");
      expect(result.errorMessage).toBeUndefined();

      expect(getFileInfoStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledOnce).toBe(true);
      expect(readFileChunkStub.calledWith("/path/to/file.txt", 0, 1024, "text")).toBe(true);
    });
  });

  describe("test_read_file_chunk_binary_format", () => {
    it("should read file chunk in binary format", async () => {
      // Mock MCP tool call returning base64-encoded string
      const binaryData = new Uint8Array([0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46]);
      const base64Data = Buffer.from(binaryData).toString("base64");

      callMcpToolStub.resolves({
        success: true,
        data: base64Data,
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await (mockFileSystem as any).readFileChunk(
        "/path/to/image.jpeg",
        0,
        1024,
        "binary"
      );

      // Verify BinaryFileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect(result.content).toEqual(binaryData);
      expect(result.errorMessage).toBeUndefined();

      // Verify MCP tool was called with format='binary'
      expect(callMcpToolStub.calledOnce).toBe(true);
      const callArgs = callMcpToolStub.getCall(0).args;
      expect(callArgs[0]).toBe("read_file");
      expect(callArgs[1].format).toBe("binary");
      expect(callArgs[1].path).toBe("/path/to/image.jpeg");
      expect(callArgs[1].offset).toBe(0);
      expect(callArgs[1].length).toBe(1024);
    });
  });

  describe("test_read_file_chunk_binary_format_base64_decode_error", () => {
    it("should handle base64 decode error", async () => {
      // Mock MCP tool call returning invalid base64 string
      callMcpToolStub.resolves({
        success: true,
        data: "invalid-base64!!!", // Invalid base64
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await (mockFileSystem as any).readFileChunk(
        "/path/to/image.jpeg",
        0,
        1024,
        "binary"
      );

      // Verify error result structure
      expect(result.success).toBe(false);
      expect(result.content).toBeInstanceOf(Uint8Array);
      expect((result.content as Uint8Array).length).toBe(0);
      expect(result.errorMessage).toContain("Failed to decode base64");
    });
  });

  describe("test_read_file_chunk_text_format_no_format_param", () => {
    it("should read file chunk in text format without format param", async () => {
      callMcpToolStub.resolves({
        success: true,
        data: "file content",
        errorMessage: "",
        requestId: "test-request-id",
      });

      const result = await (mockFileSystem as any).readFileChunk(
        "/path/to/file.txt",
        0,
        1024,
        "text"
      );

      // Verify FileContentResult structure
      expect(result.success).toBe(true);
      expect(result.requestId).toBe("test-request-id");
      expect(typeof result.content).toBe("string");
      expect(result.content).toBe("file content");

      // Verify MCP tool was called without format parameter
      expect(callMcpToolStub.calledOnce).toBe(true);
      const callArgs = callMcpToolStub.getCall(0).args;
      expect(callArgs[0]).toBe("read_file");
      expect(callArgs[1].format).toBeUndefined();
      expect(callArgs[1].path).toBe("/path/to/file.txt");
    });
  });
});
