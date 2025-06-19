package filesystem

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
)

// FileSystem handles file operations in the AgentBay cloud environment.
type FileSystem struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// callMcpToolResult represents the result of a CallMcpTool operation
type callMcpToolResult struct {
	Data       map[string]interface{}
	Content    []map[string]interface{}
	IsError    bool
	ErrorMsg   string
	StatusCode int32
}

// callMcpTool calls the MCP tool and checks for errors in the response
func (fs *FileSystem) callMcpTool(toolName string, args interface{}, defaultErrorMsg string) (*callMcpToolResult, error) {
	// Marshal arguments to JSON
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	// Create the request
	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String(toolName),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request with content length for file operations
	fmt.Println("API Call: CallMcpTool -", toolName)

	// Handle logging differently based on operation type
	if isFileOperation(toolName) {
		// For file operations, log content length instead of content
		truncatedArgs := truncateContentForLogging(string(argsJSON))
		fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, truncatedArgs)
	} else {
		// For non-file operations, log normally
		fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)
	}

	// Call the MCP tool
	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool -", toolName, ":", err)
		return nil, fmt.Errorf("failed to call %s: %w", toolName, err)
	}

	if response != nil && response.Body != nil {
		if isFileOperation(toolName) {
			// Log content size for file operations instead of full content
			fmt.Println("Response from CallMcpTool -", toolName, "- status:", *response.StatusCode)

			// Log only relevant response information without content
			data, ok := response.Body.Data.(map[string]interface{})
			if ok {
				isError, _ := data["isError"].(bool)
				if isError {
					fmt.Println("Response contains error:", data["isError"])
				} else {
					fmt.Println("Response successful, content length info provided separately")
				}
			}
		} else {
			// Log full response for non-file operations
			fmt.Println("Response from CallMcpTool -", toolName, ":", response.Body)
		}
	}

	// Extract data from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	// Create result object
	result := &callMcpToolResult{
		Data:       data,
		StatusCode: *response.StatusCode,
	}

	// Check if there's an error in the response
	isError, ok := data["isError"].(bool)
	if ok && isError {
		result.IsError = true

		// Try to extract the error message from the content field
		contentArray, ok := data["content"].([]interface{})
		if ok && len(contentArray) > 0 {
			// Convert content array to a more usable format
			result.Content = make([]map[string]interface{}, 0, len(contentArray))
			for _, item := range contentArray {
				contentItem, ok := item.(map[string]interface{})
				if !ok {
					continue
				}
				result.Content = append(result.Content, contentItem)
			}

			// Extract error message from the first content item
			if len(result.Content) > 0 {
				text, ok := result.Content[0]["text"].(string)
				if ok {
					result.ErrorMsg = text
					return result, fmt.Errorf("%s", text)
				}
			}
		}
		return result, fmt.Errorf("%s", defaultErrorMsg)
	}

	// Extract content array if it exists
	contentArray, ok := data["content"].([]interface{})
	if ok {
		result.Content = make([]map[string]interface{}, 0, len(contentArray))
		for _, item := range contentArray {
			contentItem, ok := item.(map[string]interface{})
			if !ok {
				continue
			}
			result.Content = append(result.Content, contentItem)
		}
	}

	return result, nil
}

// isFileOperation checks if the tool operation is file-related and might contain large content
func isFileOperation(toolName string) bool {
	fileOperations := map[string]bool{
		"read_file":           true,
		"write_file":          true,
		"read_multiple_files": true,
	}
	return fileOperations[toolName]
}

// truncateContentForLogging replaces large content with size information in JSON args
func truncateContentForLogging(jsonArgs string) string {
	var args map[string]interface{}
	if err := json.Unmarshal([]byte(jsonArgs), &args); err != nil {
		return fmt.Sprintf("[Could not parse args for logging: %s]", err)
	}

	// Check for content field and replace with length info
	if content, ok := args["content"]; ok {
		contentStr, isString := content.(string)
		if isString {
			contentLength := len(contentStr)
			args["content"] = fmt.Sprintf("[Content length: %d bytes]", contentLength)
		}
	}

	// Check for paths array and log number of paths instead of all paths
	if paths, ok := args["paths"].([]interface{}); ok && len(paths) > 3 {
		args["paths"] = fmt.Sprintf("[%d paths, first few: %v, %v, %v, ...]",
			len(paths), paths[0], paths[1], paths[2])
	}

	// Serialize back to JSON
	modifiedJSON, err := json.Marshal(args)
	if err != nil {
		return fmt.Sprintf("[Could not serialize modified args: %s]", err)
	}

	return string(modifiedJSON)
}

// NewFileSystem creates a new FileSystem object.
func NewFileSystem(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *FileSystem {
	return &FileSystem{
		Session: session,
	}
}

// CreateDirectory creates a new directory at the specified path.
// API Parameters:
//
//	{
//	  "path": "directory/path/to/create"
//	}
func (fs *FileSystem) CreateDirectory(path string) (bool, error) {
	args := map[string]string{
		"path": path,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := fs.callMcpTool("create_directory", args, "error creating directory")
	if err != nil {
		return false, err
	}

	return true, nil
}

// EditFile edits a file by replacing occurrences of oldText with newText.
// API Parameters:
//
//	{
//	  "path": "file/path/to/edit",
//	  "edits": [
//	    {
//	      "oldText": "text to search for",
//	      "newText": "text to replace with"
//	    },
//	    {
//	      "oldText": "another text to search",
//	      "newText": "another replacement"
//	    }
//	  ],
//	  "dryRun": false  // Optional: Preview changes without applying them
//	}
func (fs *FileSystem) EditFile(path string, edits []map[string]string, dryRun bool) (bool, error) {
	args := map[string]interface{}{
		"path":   path,
		"edits":  edits,
		"dryRun": dryRun,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := fs.callMcpTool("edit_file", args, "error editing file")
	if err != nil {
		return false, err
	}

	return true, nil
}

// GetFileInfo gets information about a file or directory.
// API Parameters:
//
//	{
//	  "path": "file/or/directory/path/to/inspect"
//	}
func (fs *FileSystem) GetFileInfo(path string) (interface{}, error) {
	args := map[string]string{
		"path": path,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := fs.callMcpTool("get_file_info", args, "error getting file info")
	if err != nil {
		// Check if it's a "file not found" error
		if strings.Contains(err.Error(), "No such file or directory") {
			return nil, fmt.Errorf("file not found: %s", path)
		}
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// ListDirectory lists the contents of a directory.
// API Parameters:
//
//	{
//	  "path": "directory/path/to/list"
//	}
func (fs *FileSystem) ListDirectory(path string) (interface{}, error) {
	args := map[string]string{
		"path": path,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := fs.callMcpTool("list_directory", args, "error listing directory")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// MoveFile moves a file or directory from source to destination.
// API Parameters:
//
//	{
//	  "source": "source/file/or/directory/path",
//	  "destination": "destination/file/or/directory/path"
//	}
func (fs *FileSystem) MoveFile(source, destination string) (bool, error) {
	args := map[string]string{
		"source":      source,
		"destination": destination,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := fs.callMcpTool("move_file", args, "error moving file")
	if err != nil {
		return false, err
	}

	return true, nil
}

// ReadFile reads the contents of a file in the cloud environment.
// For backward compatibility, this function can be called with just the path parameter.
// API Parameters:
//
//	{
//	  "path": "file/path/to/read",
//	  "offset": 0,  // Optional: Start reading from this byte offset
//	  "length": 0   // Optional: Number of bytes to read. If 0, read to end of file
//	}
func (fs *FileSystem) ReadFile(path string, optionalParams ...int) (interface{}, error) {
	// Handle optional parameters for backward compatibility
	offset, length := 0, 0
	if len(optionalParams) > 0 {
		offset = optionalParams[0]
	}
	if len(optionalParams) > 1 {
		length = optionalParams[1]
	}

	args := map[string]interface{}{
		"path": path,
	}

	// Only include optional parameters if they are non-default values
	if offset > 0 {
		args["offset"] = offset
	}
	if length > 0 {
		args["length"] = length
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := fs.callMcpTool("read_file", args, "error reading file")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// ReadMultipleFiles reads the contents of multiple files.
// API Parameters:
//
//	{
//	  "paths": ["file1/path", "file2/path", "file3/path"]
//	}
func (fs *FileSystem) ReadMultipleFiles(paths []string) (interface{}, error) {
	args := map[string]interface{}{
		"paths": paths,
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := fs.callMcpTool("read_multiple_files", args, "error reading multiple files")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// SearchFiles searches for files matching a pattern in a directory.
// API Parameters:
//
//	{
//	  "path": "directory/path/to/start/search",
//	  "pattern": "pattern to match",
//	  "excludePatterns": ["pattern1", "pattern2"]  // Optional: Patterns to exclude
//	}
func (fs *FileSystem) SearchFiles(path, pattern string, excludePatterns []string) (interface{}, error) {
	args := map[string]interface{}{
		"path":    path,
		"pattern": pattern,
	}

	// Only include excludePatterns if non-empty
	if len(excludePatterns) > 0 {
		args["excludePatterns"] = excludePatterns
	}

	// Use the helper method to call MCP tool and check for errors
	mcpResult, err := fs.callMcpTool("search_files", args, "error searching files")
	if err != nil {
		return nil, err
	}

	// Return the raw content field for the caller to parse
	return mcpResult.Data["content"], nil
}

// WriteFile writes content to a file.
// API Parameters:
//
//	{
//	  "path": "file/path/to/write",
//	  "content": "Content to write to the file",
//	  "mode": "overwrite"  // Optional: "overwrite" (default) or "append"
//	}
func (fs *FileSystem) WriteFile(path, content string, mode string) (bool, error) {
	if mode == "" {
		mode = "overwrite"
	}

	args := map[string]interface{}{
		"path":    path,
		"content": content,
		"mode":    mode,
	}

	// Use the helper method to call MCP tool and check for errors
	_, err := fs.callMcpTool("write_file", args, "error writing file")
	if err != nil {
		return false, err
	}

	return true, nil
}

// ChunkSize is the default size of chunks for large file operations (60KB)
const ChunkSize = 60 * 1024

// ReadLargeFile reads a large file in chunks to handle size limitations of the underlying API.
// It automatically splits the read operation into multiple requests of chunkSize bytes each.
// If chunkSize is <= 0, the default ChunkSize (60KB) will be used.
func (fs *FileSystem) ReadLargeFile(path string, chunkSize int) (string, error) {
	if chunkSize <= 0 {
		chunkSize = ChunkSize
	}

	// First get the file size
	fileInfo, err := fs.GetFileInfo(path)
	if err != nil {
		return "", fmt.Errorf("failed to get file info: %w", err)
	}

	// Extract file size from the content array
	contentArray, ok := fileInfo.([]interface{})
	if !ok || len(contentArray) == 0 {
		return "", fmt.Errorf("invalid file info format")
	}

	// Get the first content item
	contentItem, ok := contentArray[0].(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid file info content item format")
	}

	// Extract the text field which contains the file info
	text, ok := contentItem["text"].(string)
	if !ok {
		return "", fmt.Errorf("invalid file info text format")
	}

	// Parse the size from the text
	var size float64
	for _, line := range strings.Split(text, "\n") {
		if strings.HasPrefix(line, "size:") {
			sizeStr := strings.TrimSpace(strings.TrimPrefix(line, "size:"))
			if _, err := fmt.Sscanf(sizeStr, "%f", &size); err != nil {
				return "", fmt.Errorf("couldn't parse file size: %w", err)
			}
			break
		}
	}

	if size == 0 {
		return "", fmt.Errorf("couldn't determine file size")
	}

	// Prepare to read the file in chunks
	var result strings.Builder
	offset := 0
	fileSize := int(size)

	fmt.Printf("ReadLargeFile: Starting chunked read of %s (total size: %d bytes, chunk size: %d bytes)\n",
		path, fileSize, chunkSize)

	chunkCount := 0
	for offset < fileSize {
		// Calculate how much to read in this chunk
		length := chunkSize
		if offset+length > fileSize {
			length = fileSize - offset
		}

		fmt.Printf("ReadLargeFile: Reading chunk %d (%d bytes at offset %d/%d)\n",
			chunkCount+1, length, offset, fileSize)

		// Read the chunk
		chunk, err := fs.ReadFile(path, offset, length)
		if err != nil {
			return "", fmt.Errorf("error reading chunk at offset %d: %w", offset, err)
		}

		// Extract text from the content array
		contentArray, ok := chunk.([]interface{})
		if !ok || len(contentArray) == 0 {
			return "", fmt.Errorf("invalid chunk format at offset %d", offset)
		}

		// Process each content item
		for _, item := range contentArray {
			contentItem, ok := item.(map[string]interface{})
			if !ok {
				continue
			}

			text, ok := contentItem["text"].(string)
			if !ok {
				continue
			}

			result.WriteString(text)
		}

		// Move to the next chunk
		offset += length
		chunkCount++
	}

	fmt.Printf("ReadLargeFile: Successfully read %s in %d chunks (total: %d bytes)\n",
		path, chunkCount, fileSize)

	return result.String(), nil
}

// WriteLargeFile writes a large file in chunks to handle size limitations of the underlying API.
// It automatically splits the write operation into multiple requests of chunkSize bytes each.
// If chunkSize is <= 0, the default ChunkSize (60KB) will be used.
func (fs *FileSystem) WriteLargeFile(path, content string, chunkSize int) (bool, error) {
	if chunkSize <= 0 {
		chunkSize = ChunkSize
	}

	contentLen := len(content)

	fmt.Printf("WriteLargeFile: Starting chunked write to %s (total size: %d bytes, chunk size: %d bytes)\n",
		path, contentLen, chunkSize)

	// If content is small enough, use the regular WriteFile method
	if contentLen <= chunkSize {
		fmt.Printf("WriteLargeFile: Content size (%d bytes) is smaller than chunk size, using normal WriteFile\n",
			contentLen)
		return fs.WriteFile(path, content, "overwrite")
	}

	// Write the first chunk with "overwrite" mode to create/clear the file
	firstChunkEnd := chunkSize
	if firstChunkEnd > contentLen {
		firstChunkEnd = contentLen
	}

	fmt.Printf("WriteLargeFile: Writing first chunk (0-%d bytes) with overwrite mode\n", firstChunkEnd)
	_, err := fs.WriteFile(path, content[:firstChunkEnd], "overwrite")
	if err != nil {
		return false, fmt.Errorf("error writing first chunk: %w", err)
	}

	// Write the remaining chunks with "append" mode
	chunkCount := 1 // Already wrote first chunk
	for offset := firstChunkEnd; offset < contentLen; {
		end := offset + chunkSize
		if end > contentLen {
			end = contentLen
		}

		fmt.Printf("WriteLargeFile: Writing chunk %d (%d-%d bytes) with append mode\n",
			chunkCount+1, offset, end)
		_, err := fs.WriteFile(path, content[offset:end], "append")
		if err != nil {
			return false, fmt.Errorf("error writing chunk at offset %d: %w", offset, err)
		}

		offset = end
		chunkCount++
	}

	fmt.Printf("WriteLargeFile: Successfully wrote %s in %d chunks (total: %d bytes)\n",
		path, chunkCount, contentLen)

	return true, nil
}
