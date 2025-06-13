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

	// Check if there's an error in the response
	isError, ok := data["isError"].(bool)
	if ok && isError {
		// Try to extract the error message from the content field
		contentArray, ok := data["content"].([]interface{})
		if ok && len(contentArray) > 0 {
			contentItem, ok := contentArray[0].(map[string]interface{})
			if ok {
				text, ok := contentItem["text"].(string)
				if ok && strings.Contains(text, "No such file or directory") {
					return nil, fmt.Errorf("file not found: %s", path)
				} else if ok {
					return nil, fmt.Errorf("%s", text)
				}
			}
		}
		return nil, fmt.Errorf("error getting file info")
	}

	// Try to parse file info from the content field
	contentArray, ok := data["content"].([]interface{})
	if ok && len(contentArray) > 0 {
		contentItem, ok := contentArray[0].(map[string]interface{})
		if ok {
			text, ok := contentItem["text"].(string)
			if ok {
				// Parse the text to extract file info
				// Format is expected to be:
				// size: 36
				// modified: 2025-06-10 20:56:39
				// created: N/A
				// accessed: N/A
				// isDirectory: false
				// isFile: true
				// permissions: rw-r--r--
				result := make(map[string]interface{})

				// Extract the file name from the path
				parts := strings.Split(path, "/")
				if len(parts) > 0 {
					result["name"] = parts[len(parts)-1]
				}

				lines := strings.Split(text, "\n")
				for _, line := range lines {
					line = strings.TrimSpace(line)
					if line == "" {
						continue
					}

					parts := strings.SplitN(line, ":", 2)
					if len(parts) != 2 {
						continue
					}

					key := strings.TrimSpace(parts[0])
					value := strings.TrimSpace(parts[1])

					switch key {
					case "size":
						// Try to parse size as a number
						var size float64
						fmt.Sscanf(value, "%f", &size)
						result["size"] = size
					case "isDirectory":
						result["isDirectory"] = value == "true"
					case "isFile":
						result["isFile"] = value == "true"
					case "modified":
						result["modifiedTime"] = value
					case "created":
						if value != "N/A" {
							result["createdTime"] = value
						}
					case "accessed":
						if value != "N/A" {
							result["accessedTime"] = value
						}
					case "permissions":
						result["permissions"] = value
					}
				}

				return result, nil
			}
		}
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

	// First try to get the entries field
	entries, ok := data["entries"].([]interface{})
	if ok {
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

	// If entries field is not found, try to parse from content field
	contentArray, ok := data["content"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("neither entries nor content field found in response")
	}

	// Parse the content from the text chunks
	result := make([]map[string]interface{}, 0)
	for _, item := range contentArray {
		contentItem, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		text, ok := contentItem["text"].(string)
		if !ok {
			continue
		}

		// Parse the text to extract directory entries
		// Format is expected to be:
		// [DIR] directory_name
		// [FILE] file_name
		lines := strings.Split(text, "\n")
		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}

			entryMap := make(map[string]interface{})
			if strings.HasPrefix(line, "[DIR]") {
				entryMap["isDirectory"] = true
				entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[DIR]"))
			} else if strings.HasPrefix(line, "[FILE]") {
				entryMap["isDirectory"] = false
				entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[FILE]"))
			} else {
				// Skip lines that don't match the expected format
				continue
			}

			result = append(result, entryMap)
		}
	}

	// If we couldn't parse any entries, return an error
	if len(result) == 0 {
		return nil, fmt.Errorf("could not parse directory entries from response")
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
		for i, item := range contentArray {
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

			fullText += text
			// Only add newline if not the last item
			if i < len(contentArray)-1 {
				fullText += "\n"
			}
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

	// First try to get the files field
	filesData, ok := data["files"].(map[string]interface{})
	if ok {
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

	// If files field is not found, try to parse from content field
	contentArray, ok := data["content"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("neither files nor content field found in response")
	}

	// Parse the content from the text chunks
	result := make(map[string]string)
	for _, item := range contentArray {
		contentItem, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		text, ok := contentItem["text"].(string)
		if !ok {
			continue
		}

		// Parse the text to extract file contents
		// Format is expected to be:
		// /path/to/file1:
		// content1
		//
		// ---
		// /path/to/file2:
		// content2
		//
		lines := strings.Split(text, "\n")
		var currentPath string
		var currentContent strings.Builder
		inContent := false

		for _, line := range lines {
			if strings.HasSuffix(line, ":") {
				// This is a file path line
				if currentPath != "" && currentContent.Len() > 0 {
					// Save the previous file content
					result[currentPath] = strings.TrimSpace(currentContent.String())
					currentContent.Reset()
				}
				currentPath = strings.TrimSuffix(line, ":")
				inContent = true
			} else if line == "---" {
				// This is a separator line
				if currentPath != "" && currentContent.Len() > 0 {
					// Save the previous file content
					result[currentPath] = strings.TrimSpace(currentContent.String())
					currentContent.Reset()
				}
				inContent = false
			} else if inContent {
				// This is a content line
				if currentContent.Len() > 0 {
					currentContent.WriteString("\n")
				}
				currentContent.WriteString(line)
			}
		}

		// Save the last file content
		if currentPath != "" && currentContent.Len() > 0 {
			result[currentPath] = strings.TrimSpace(currentContent.String())
		}
	}

	// If we couldn't parse any files, return an error
	if len(result) == 0 {
		return nil, fmt.Errorf("could not parse file contents from response")
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

	// First try to get the results field
	results, ok := data["results"].([]interface{})
	if ok {
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

	// If results field is not found, try to parse from content field
	contentArray, ok := data["content"].([]interface{})
	if !ok {
		return nil, fmt.Errorf("neither results nor content field found in response")
	}

	// Parse the content from the text chunks
	searchResults := make([]map[string]interface{}, 0)
	for _, item := range contentArray {
		contentItem, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		text, ok := contentItem["text"].(string)
		if !ok {
			continue
		}

		// Check if no matches were found
		if strings.Contains(text, "No matches found") {
			// Return an empty array for no matches
			return searchResults, nil
		}

		// First, try to parse as a simple list of file paths
		// This format is just a list of file paths separated by newlines
		if !strings.Contains(text, "File:") && !strings.Contains(text, "Line") {
			lines := strings.Split(text, "\n")
			for _, line := range lines {
				line = strings.TrimSpace(line)
				if line == "" {
					continue
				}

				// Create a result entry for each file path
				resultMap := map[string]interface{}{
					"path": line,
				}
				searchResults = append(searchResults, resultMap)
			}

			// If we found any results in this format, return them
			if len(searchResults) > 0 {
				return searchResults, nil
			}
		}

		// If not a simple list of paths, try the more complex format
		// Format is expected to be:
		// File: /path/to/file1.txt
		// Line 5: This is a line with the search pattern
		// Line 10: This is another line with the search pattern
		//
		// File: /path/to/file2.txt
		// Line 3: This is a line with the search pattern
		lines := strings.Split(text, "\n")
		var currentFile string
		var matches []map[string]interface{}

		for _, line := range lines {
			line = strings.TrimSpace(line)
			if line == "" {
				continue
			}

			if strings.HasPrefix(line, "File:") {
				// This is a file path line
				if currentFile != "" && len(matches) > 0 {
					// Save the previous file's matches
					resultMap := map[string]interface{}{
						"path":    currentFile,
						"matches": matches,
					}
					searchResults = append(searchResults, resultMap)
					matches = nil
				}
				currentFile = strings.TrimSpace(strings.TrimPrefix(line, "File:"))
				matches = make([]map[string]interface{}, 0)
			} else if strings.HasPrefix(line, "Line") && currentFile != "" {
				// This is a match line
				parts := strings.SplitN(line, ":", 2)
				if len(parts) == 2 {
					lineNum := strings.TrimSpace(strings.TrimPrefix(parts[0], "Line"))
					lineContent := strings.TrimSpace(parts[1])

					// Try to parse line number
					var lineNumber int
					fmt.Sscanf(lineNum, "%d", &lineNumber)

					match := map[string]interface{}{
						"line":    lineNumber,
						"content": lineContent,
					}
					matches = append(matches, match)
				}
			}
		}

		// Save the last file's matches
		if currentFile != "" && len(matches) > 0 {
			resultMap := map[string]interface{}{
				"path":    currentFile,
				"matches": matches,
			}
			searchResults = append(searchResults, resultMap)
		}
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
