package agentbay_test

import (
	"encoding/base64"
	"testing"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/filesystem"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/stretchr/testify/assert"
)

// MockSessionForBinaryTest is a mock session for testing binary file operations
type MockSessionForBinaryTest struct {
	CallMcpToolFunc func(toolName string, args interface{}) (*models.McpToolResult, error)
}

func (m *MockSessionForBinaryTest) GetAPIKey() string {
	return "dummy_key"
}

func (m *MockSessionForBinaryTest) GetClient() *mcp.Client {
	return nil
}

func (m *MockSessionForBinaryTest) GetSessionId() string {
	return "dummy_session"
}

func (m *MockSessionForBinaryTest) IsVpc() bool {
	return false
}

func (m *MockSessionForBinaryTest) NetworkInterfaceIp() string {
	return ""
}

func (m *MockSessionForBinaryTest) HttpPort() string {
	return ""
}

func (m *MockSessionForBinaryTest) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error) {
	if m.CallMcpToolFunc != nil {
		return m.CallMcpToolFunc(toolName, args)
	}
	return nil, nil
}

func TestFileSystem_ReadFileBinaryFormatSuccess(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo call
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: image.jpeg\npath: /path/to/image.jpeg\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		// Mock read_file call with binary format
		if toolName == "read_file" {
			// Create binary data (JPEG header)
			binaryData := []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46}
			base64Data := base64.StdEncoding.EncodeToString(binaryData)

			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         base64Data,
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileBinary
	result, err := fs.ReadFileBinary("/path/to/image.jpeg")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.NotNil(t, result.Content)
	assert.Equal(t, 10, len(result.Content)) // JPEG header is 10 bytes
	assert.Equal(t, []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46}, result.Content)
}

func TestFileSystem_ReadFileBinaryFormatLargeFile(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}
	chunkCount := 0

	// Mock GetFileInfo call
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: large_binary.bin\npath: /path/to/large_binary.bin\nsize: 150000\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		// Mock read_file call with binary format (chunked)
		if toolName == "read_file" {
			chunkCount++
			var chunkData []byte
			if chunkCount == 1 {
				chunkData = make([]byte, 50*1024) // 50KB chunk
				for i := range chunkData {
					chunkData[i] = 0x00
				}
			} else if chunkCount == 2 {
				chunkData = make([]byte, 50*1024) // 50KB chunk
				for i := range chunkData {
					chunkData[i] = 0x01
				}
			} else if chunkCount == 3 {
				chunkData = make([]byte, 50*1024) // 50KB chunk
				for i := range chunkData {
					chunkData[i] = 0x02
				}
			}

			base64Data := base64.StdEncoding.EncodeToString(chunkData)
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         base64Data,
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with binary format
	_, result, err := fs.ReadFileWithFormat("/path/to/large_binary.bin", "binary")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, 150*1024, len(result.Content))
	assert.Equal(t, int64(150*1024), result.Size)
	assert.Equal(t, 3, chunkCount) // Should have read 3 chunks
}

func TestFileSystem_ReadFileBinaryFormatGetInfoError(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo call to fail
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      false,
				Data:         "",
				ErrorMessage: "File not found",
			}, nil
		}
		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with binary format
	_, result, err := fs.ReadFileWithFormat("/path/to/image.jpeg", "binary")
	assert.Error(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.Equal(t, 0, len(result.Content))
	assert.Contains(t, err.Error(), "File not found")
}

func TestFileSystem_ReadFileBinaryFormatChunkError(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo call
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: image.jpeg\npath: /path/to/image.jpeg\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		// Mock read_file call with invalid base64
		if toolName == "read_file" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "invalid-base64!!!", // Invalid base64
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with binary format
	_, result, err := fs.ReadFileWithFormat("/path/to/image.jpeg", "binary")
	assert.Error(t, err)
	assert.NotNil(t, result)
	assert.False(t, result.Success)
	assert.Equal(t, 0, len(result.Content))
	assert.Contains(t, err.Error(), "failed to decode base64")
}

func TestFileSystem_ReadFileBinaryFormatEmptyFile(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo call for empty file
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: empty.bin\npath: /path/to/empty.bin\nsize: 0\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}
		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with binary format
	_, result, err := fs.ReadFileWithFormat("/path/to/empty.bin", "binary")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.Equal(t, 0, len(result.Content))
	assert.Equal(t, int64(0), result.Size)
}

func TestFileSystem_ReadFileTextFormatExplicit(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo call
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: file.txt\npath: /path/to/file.txt\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		// Mock read_file call with text format
		if toolName == "read_file" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "file content",
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with text format
	result, _, err := fs.ReadFileWithFormat("/path/to/file.txt", "text")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.Equal(t, "file content", result.Content)
}

func TestFileSystem_ReadFileChunkBinaryFormat(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock read_file call with binary format
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "read_file" {
			// Verify format parameter is set to "binary"
			argsMap := args.(map[string]interface{})
			if format, ok := argsMap["format"]; ok {
				assert.Equal(t, "binary", format)
			} else {
				t.Error("format parameter not found in read_file call")
			}

			// Create binary data (JPEG header)
			binaryData := []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46}
			base64Data := base64.StdEncoding.EncodeToString(binaryData)

			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         base64Data,
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Mock GetFileInfo as well
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: image.jpeg\npath: /path/to/image.jpeg\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		if toolName == "read_file" {
			// Verify format parameter is set to "binary"
			argsMap := args.(map[string]interface{})
			if format, ok := argsMap["format"]; ok {
				assert.Equal(t, "binary", format)
			} else {
				t.Error("format parameter not found in read_file call")
			}

			// Create binary data (JPEG header)
			binaryData := []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46}
			base64Data := base64.StdEncoding.EncodeToString(binaryData)

			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         base64Data,
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	// Test ReadFileBinary which internally calls readFileChunk
	result, err := fs.ReadFileBinary("/path/to/image.jpeg")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.Equal(t, 10, len(result.Content))
	assert.Equal(t, []byte{0xff, 0xd8, 0xff, 0xe0, 0x00, 0x10, 0x4a, 0x46, 0x49, 0x46}, result.Content)
}

func TestFileSystem_ReadFileChunkBinaryFormatBase64DecodeError(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo and read_file calls
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: image.jpeg\npath: /path/to/image.jpeg\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		if toolName == "read_file" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "invalid-base64!!!", // Invalid base64
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileBinary which will trigger base64 decode error
	_, err := fs.ReadFileBinary("/path/to/image.jpeg")
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "failed to decode base64")
}

func TestFileSystem_ReadFileChunkTextFormatNoFormatParam(t *testing.T) {
	// Create mock session
	mockSession := &MockSessionForBinaryTest{}

	// Mock GetFileInfo and read_file calls
	mockSession.CallMcpToolFunc = func(toolName string, args interface{}) (*models.McpToolResult, error) {
		if toolName == "get_file_info" {
			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "name: file.txt\npath: /path/to/file.txt\nsize: 1024\nisDirectory: false",
				ErrorMessage: "",
			}, nil
		}

		if toolName == "read_file" {
			// Verify format parameter is NOT set for text format
			argsMap := args.(map[string]interface{})
			if _, ok := argsMap["format"]; ok {
				t.Error("format parameter should not be present for text format")
			}

			return &models.McpToolResult{
				RequestID:    "test-request-id",
				Success:      true,
				Data:         "file content",
				ErrorMessage: "",
			}, nil
		}

		return nil, nil
	}

	fs := filesystem.NewFileSystem(mockSession)

	// Test ReadFileWithFormat with text format
	result, _, err := fs.ReadFileWithFormat("/path/to/file.txt", "text")
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "test-request-id", result.RequestID)
	assert.Equal(t, "file content", result.Content)
}
