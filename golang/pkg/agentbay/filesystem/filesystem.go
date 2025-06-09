package filesystem

import (
	"encoding/json"
	"fmt"

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
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return false, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("create_directory"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - create_directory")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - create_directory:", err)
		return false, fmt.Errorf("failed to create directory: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - create_directory:", response.Body)
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
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return false, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("edit_file"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - edit_file")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - edit_file:", err)
		return false, fmt.Errorf("failed to edit file: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - edit_file:", response.Body)
	}

	return true, nil
}

// GetFileInfo gets information about a file or directory.
// API Parameters:
//
//	{
//	  "path": "file/or/directory/path/to/inspect"
//	}
func (fs *FileSystem) GetFileInfo(path string) (map[string]interface{}, error) {
	args := map[string]string{
		"path": path,
	}
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("get_file_info"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - get_file_info")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - get_file_info:", err)
		return nil, fmt.Errorf("failed to get file info: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - get_file_info:", response.Body)
	}

	// Extract file info from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	return data, nil
}

// ListDirectory lists the contents of a directory.
// API Parameters:
//
//	{
//	  "path": "directory/path/to/list"
//	}
func (fs *FileSystem) ListDirectory(path string) ([]map[string]interface{}, error) {
	args := map[string]string{
		"path": path,
	}
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("list_directory"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - list_directory")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - list_directory:", err)
		return nil, fmt.Errorf("failed to list directory: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - list_directory:", response.Body)
	}

	// Extract directory listing from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	entries, ok := data["entries"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("entries field not found or not an array")
	}

	result := make([]map[string]interface{}, 0, len(entries))
	for _, entry := range entries {
		entryMap, ok := entry.(map[string]interface{})
		if !ok {
			continue
		}
		result = append(result, entryMap)
	}

	return result, nil
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
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return false, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("move_file"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - move_file")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - move_file:", err)
		return false, fmt.Errorf("failed to move file: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - move_file:", response.Body)
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
func (fs *FileSystem) ReadFile(path string, optionalParams ...int) (string, error) {
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

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return "", fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("read_file"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - read_file")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - read_file:", err)
		return "", fmt.Errorf("failed to read file: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - read_file:", response.Body)
	}

	// Extract content from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return "", fmt.Errorf("invalid response data format")
	}

	content, ok := data["content"].(string)
	if !ok {
		// Try to handle the content as an array of text chunks
		contentArray, ok := data["content"].([]interface{})
		if !ok {
			return "", fmt.Errorf("content field not found or has unexpected format")
		}

		var fullText string
		for _, item := range contentArray {
			// Try to assert each element is a map[string]interface{}
			contentItem, ok := item.(map[string]interface{})
			if !ok {
				continue
			}

			// Extract the text field
			text, ok := contentItem["text"].(string)
			if !ok {
				continue
			}

			fullText += text + "\n" // Concatenate text content
		}

		return fullText, nil
	}

	return content, nil
}

// ReadMultipleFiles reads the contents of multiple files.
// API Parameters:
//
//	{
//	  "paths": ["file1/path", "file2/path", "file3/path"]
//	}
func (fs *FileSystem) ReadMultipleFiles(paths []string) (map[string]string, error) {
	args := map[string]interface{}{
		"paths": paths,
	}
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("read_multiple_files"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - read_multiple_files")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - read_multiple_files:", err)
		return nil, fmt.Errorf("failed to read multiple files: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - read_multiple_files:", response.Body)
	}

	// Extract file contents from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	filesData, ok := data["files"].(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("files field not found or not a map")
	}

	result := make(map[string]string)
	for path, content := range filesData {
		contentStr, ok := content.(string)
		if !ok {
			continue
		}
		result[path] = contentStr
	}

	return result, nil
}

// SearchFiles searches for files matching a pattern in a directory.
// API Parameters:
//
//	{
//	  "path": "directory/path/to/start/search",
//	  "pattern": "pattern to match",
//	  "excludePatterns": ["pattern1", "pattern2"]  // Optional: Patterns to exclude
//	}
func (fs *FileSystem) SearchFiles(path, pattern string, excludePatterns []string) ([]map[string]interface{}, error) {
	args := map[string]interface{}{
		"path":    path,
		"pattern": pattern,
	}

	// Only include excludePatterns if non-empty
	if len(excludePatterns) > 0 {
		args["excludePatterns"] = excludePatterns
	}

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("search_files"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - search_files")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - search_files:", err)
		return nil, fmt.Errorf("failed to search files: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - search_files:", response.Body)
	}

	// Extract search results from response
	data, ok := response.Body.Data.(map[string]interface{})
	if !ok {
		return nil, fmt.Errorf("invalid response data format")
	}

	results, ok := data["results"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("results field not found or not an array")
	}

	searchResults := make([]map[string]interface{}, 0, len(results))
	for _, result := range results {
		resultMap, ok := result.(map[string]interface{})
		if !ok {
			continue
		}
		searchResults = append(searchResults, resultMap)
	}

	return searchResults, nil
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

	argsJSON, err := json.Marshal(args)
	if err != nil {
		return false, fmt.Errorf("failed to marshal args: %w", err)
	}

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization: tea.String("Bearer " + fs.Session.GetAPIKey()),
		SessionId:     tea.String(fs.Session.GetSessionId()),
		Name:          tea.String("write_file"),
		Args:          tea.String(string(argsJSON)),
	}

	// Log API request
	fmt.Println("API Call: CallMcpTool - write_file")
	fmt.Printf("Request: SessionId=%s, Args=%s\n", *callToolRequest.SessionId, *callToolRequest.Args)

	response, err := fs.Session.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		fmt.Println("Error calling CallMcpTool - write_file:", err)
		return false, fmt.Errorf("failed to write file: %w", err)
	}
	if response != nil && response.Body != nil {
		fmt.Println("Response from CallMcpTool - write_file:", response.Body)
	}

	return true, nil
}
