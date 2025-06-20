package agentbay_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

// TestPathPrefix is the prefix for all test file paths
// Change this to "C:" for Windows or "/tmp" for Linux
const TestPathPrefix = "/tmp"

func TestFileSystem_ReadFile(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem read operations
	if session.FileSystem != nil {
		// Create a test file with known content
		fmt.Println("Creating a test file for reading...")
		testContent := "This is a test file content for ReadFile test."
		testFilePath := TestPathPrefix + "/test_read.txt"
		_, err := session.FileSystem.WriteFile(testFilePath, testContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create test file for reading: %v", err)
		}
		t.Log("Test file created successfully")

		// Now read the file
		fmt.Println("Reading file...")
		content, err := session.FileSystem.ReadFile(testFilePath)
		t.Logf("ReadFile result: content length=%d, err=%v", len(content), err)
		if err != nil {
			t.Errorf("File read failed: %v", err)
		} else {
			if content == "" {
				t.Errorf("Failed to read file content")
				return
			}

			t.Logf("File read successful, content length: %d bytes", len(content))

			// Verify the content matches what was written
			if content != testContent {
				t.Errorf("File content mismatch. Expected: %s, Got: %s", testContent, content)
			} else {
				t.Log("File content verified successfully")
			}

			// Check if response contains "tool not found"
			if testutil.ContainsToolNotFound(content) {
				t.Errorf("FileSystem.ReadFile returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file test")
	}
}

func TestFileSystem_WriteFile(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem write operations
	if session.FileSystem != nil {
		fmt.Println("Writing file...")
		testContent := "This is a test file content for WriteFile test."
		testFilePath := TestPathPrefix + "/test_write.txt"
		success, err := session.FileSystem.WriteFile(testFilePath, testContent, "overwrite")
		t.Logf("WriteFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File write failed: %v", err)
		} else {
			t.Log("File write successful")

			// Verify the file was written correctly by reading it back
			content, err := session.FileSystem.ReadFile(testFilePath)
			if err != nil {
				t.Errorf("Failed to read back written file: %v", err)
				return
			}

			if content == "" {
				t.Errorf("Failed to read file content")
				return
			}

			if content != testContent {
				t.Errorf("File content mismatch. Expected: %s, Got: %s", testContent, content)
			} else {
				t.Log("File content verified successfully")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file test")
	}
}

func TestFileSystem_CreateDirectory(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem create directory
	if session.FileSystem != nil {
		fmt.Println("Creating directory...")
		dirPath := TestPathPrefix + "/test_directory"
		success, err := session.FileSystem.CreateDirectory(dirPath)
		t.Logf("CreateDirectory result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("Directory creation failed: %v", err)
		} else if !success {
			t.Errorf("Directory creation returned false")
		} else {
			t.Log("Directory creation successful")

			// Verify the directory was created by listing the parent directory
			dirContent, err := session.FileSystem.ListDirectory(TestPathPrefix + "/")
			if err != nil {
				t.Errorf("Failed to list directory: %v", err)
			} else {
				// Process the directory content
				var entries []map[string]string

				// Parse the text to extract directory entries
				lines := strings.Split(dirContent, "\n")
				for _, line := range lines {
					line = strings.TrimSpace(line)
					if line == "" {
						continue
					}

					entryMap := make(map[string]string)
					if strings.HasPrefix(line, "[DIR]") {
						entryMap["type"] = "directory"
						entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[DIR]"))
						entries = append(entries, entryMap)
					} else if strings.HasPrefix(line, "[FILE]") {
						entryMap["type"] = "file"
						entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[FILE]"))
						entries = append(entries, entryMap)
					}
				}

				directoryFound := false
				for _, entry := range entries {
					if entry["type"] == "directory" && entry["name"] == "test_directory" {
						directoryFound = true
						break
					}
				}
				if !directoryFound {
					t.Errorf("Created directory not found in listing")
				} else {
					t.Log("Directory verified in listing")
				}
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping directory test")
	}
}

func TestFileSystem_EditFile(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem edit operations
	if session.FileSystem != nil {
		// First create a file to edit
		initialContent := "This is the original content.\nLine to be replaced.\nThis is the final line."
		testFilePath := TestPathPrefix + "/test_edit.txt"
		_, err := session.FileSystem.WriteFile(testFilePath, initialContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create file for editing: %v", err)
		}

		// Now edit the file
		fmt.Println("Editing file...")
		edits := []map[string]string{
			{
				"oldText": "Line to be replaced.",
				"newText": "This line has been edited.",
			},
		}
		success, err := session.FileSystem.EditFile(testFilePath, edits, false)
		t.Logf("EditFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File edit failed: %v", err)
		} else {
			t.Log("File edit successful")

			// Verify the file was edited correctly by reading it back
			content, err := session.FileSystem.ReadFile(testFilePath)
			if err != nil {
				t.Errorf("Failed to read back edited file: %v", err)
				return
			}

			if content == "" {
				t.Errorf("Failed to read file content")
				return
			}

			expectedContent := "This is the original content.\nThis line has been edited.\nThis is the final line."
			if content != expectedContent {
				t.Errorf("File content mismatch after edit. Expected: %s, Got: %s", expectedContent, content)
			} else {
				t.Log("File edit verified successfully")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file edit test")
	}
}

func TestFileSystem_GetFileInfo(t *testing.T) {
	// Setup session with cleanup
	params := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, params)
	defer cleanup()

	// Test FileSystem get file info
	if session.FileSystem != nil {
		// First create a file to get info for
		testContent := "This is a test file for GetFileInfo."
		testFilePath := TestPathPrefix + "/test_info.txt"
		_, err := session.FileSystem.WriteFile(testFilePath, testContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create file for info test: %v", err)
		}

		fmt.Println("Getting file info...")
		fileInfoText, err := session.FileSystem.GetFileInfo(testFilePath)
		t.Logf("GetFileInfo result: fileInfoText length=%d, err=%v", len(fileInfoText), err)
		if err != nil {
			t.Errorf("Get file info failed: %v", err)
		} else {
			t.Log("Get file info successful")

			// Check that the text contains expected information
			if !strings.Contains(fileInfoText, "size:") {
				t.Errorf("Text does not contain size information")
			}
			if !strings.Contains(fileInfoText, "isDirectory: false") {
				t.Errorf("Text does not contain directory information")
			}
			if !strings.Contains(fileInfoText, "isFile: true") {
				t.Errorf("Text does not contain file information")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file info test")
	}
}

func TestFileSystem_ListDirectory(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem list directory
	if session.FileSystem != nil {
		fmt.Println("Listing directory...")
		dirContent, err := session.FileSystem.ListDirectory(TestPathPrefix + "/")
		if err != nil {
			t.Errorf("List directory failed: %v", err)
		} else {
			t.Log("List directory successful")

			// Process the directory content
			var entries []map[string]string

			// Parse the text to extract directory entries
			lines := strings.Split(dirContent, "\n")
			for _, line := range lines {
				line = strings.TrimSpace(line)
				if line == "" {
					continue
				}

				entryMap := make(map[string]string)
				if strings.HasPrefix(line, "[DIR]") {
					entryMap["type"] = "directory"
					entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[DIR]"))
					entries = append(entries, entryMap)
				} else if strings.HasPrefix(line, "[FILE]") {
					entryMap["type"] = "file"
					entryMap["name"] = strings.TrimSpace(strings.TrimPrefix(line, "[FILE]"))
					entries = append(entries, entryMap)
				}
			}

			// Print the count of entries for debugging
			t.Logf("ListDirectory result: entries count=%d, err=%v", len(entries), err)

			// Verify the entries contain expected fields
			if len(entries) > 0 {
				firstEntry := entries[0]
				if _, ok := firstEntry["name"]; !ok {
					t.Errorf("Directory entry missing name field")
				}
				if _, ok := firstEntry["type"]; !ok {
					t.Errorf("Directory entry missing type field")
				}
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping directory listing test")
	}
}

func TestFileSystem_MoveFile(t *testing.T) {
	// Setup session with cleanup
	params := agentbay.NewCreateSessionParams().WithImageId("linux_latest")
	session, cleanup := testutil.SetupAndCleanup(t, params)
	defer cleanup()

	// Test FileSystem move file
	if session.FileSystem != nil {
		// First create a file to move
		testContent := "This is a test file for MoveFile."
		sourceFilePath := TestPathPrefix + "/test_source.txt"
		_, err := session.FileSystem.WriteFile(sourceFilePath, testContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create file for move test: %v", err)
		}

		fmt.Println("Moving file...")
		destFilePath := TestPathPrefix + "/test_destination.txt"
		success, err := session.FileSystem.MoveFile(sourceFilePath, destFilePath)
		t.Logf("MoveFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File move failed: %v", err)
		} else {
			t.Log("File move successful")

			// Verify the file was moved correctly by reading it back
			content, err := session.FileSystem.ReadFile(destFilePath)
			if err != nil {
				t.Errorf("Failed to read back moved file: %v", err)
				return
			}

			if content == "" {
				t.Errorf("Failed to read file content")
				return
			}

			if content != testContent {
				t.Errorf("File content mismatch after move. Expected: %s, Got: %s", testContent, content)
			} else {
				t.Log("File move verified successfully")
			}

			// Verify the source file no longer exists
			_, err = session.FileSystem.GetFileInfo(sourceFilePath)
			if err == nil {
				t.Errorf("Source file still exists after move")
			} else {
				// The file should not exist, so any error here is acceptable
				// The exact error message may vary depending on the system language
				t.Logf("Source file correctly no longer exists (error: %v)", err)
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file move test")
	}
}

func TestFileSystem_ReadMultipleFiles(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem read multiple files
	if session.FileSystem != nil {
		// First create some test files
		file1Content := "This is test file 1 content."
		file2Content := "This is test file 2 content."
		testFile1Path := TestPathPrefix + "/test_file1.txt"
		_, err := session.FileSystem.WriteFile(testFile1Path, file1Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create test file 1: %v", err)
		}
		testFile2Path := TestPathPrefix + "/test_file2.txt"
		_, err = session.FileSystem.WriteFile(testFile2Path, file2Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create test file 2: %v", err)
		}

		fmt.Println("Reading multiple files...")
		paths := []string{testFile1Path, testFile2Path}
		multiFileContent, err := session.FileSystem.ReadMultipleFiles(paths)
		if err != nil {
			t.Errorf("Read multiple files failed: %v", err)
		} else {
			t.Log("Read multiple files successful")
			t.Logf("ReadMultipleFiles result: content length=%d, err=%v", len(multiFileContent), err)

			// Extract file contents from the text content
			contents := make(map[string]string)

			// Parse the text to extract file contents
			// Format is expected to be:
			// /path/to/file1:
			// content1
			//
			// ---
			// /path/to/file2:
			// content2
			//
			lines := strings.Split(multiFileContent, "\n")
			var currentPath string
			var currentContent strings.Builder
			inContent := false

			for _, line := range lines {
				if strings.HasSuffix(line, ":") {
					// This is a file path line
					if currentPath != "" && currentContent.Len() > 0 {
						// Save the previous file content
						contents[currentPath] = strings.TrimSpace(currentContent.String())
						currentContent.Reset()
					}
					currentPath = strings.TrimSuffix(line, ":")
					inContent = true
				} else if line == "---" {
					// This is a separator line
					if currentPath != "" && currentContent.Len() > 0 {
						// Save the previous file content
						contents[currentPath] = strings.TrimSpace(currentContent.String())
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
				contents[currentPath] = strings.TrimSpace(currentContent.String())
			}

			// Verify the contents of each file
			if content, ok := contents[testFile1Path]; !ok || content != file1Content {
				t.Errorf("File 1 content mismatch or missing. Expected: %s, Got: %s", file1Content, content)
			} else {
				t.Log("File 1 content verified successfully")
			}

			if content, ok := contents[testFile2Path]; !ok || content != file2Content {
				t.Errorf("File 2 content mismatch or missing. Expected: %s, Got: %s", file2Content, content)
			} else {
				t.Log("File 2 content verified successfully")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping read multiple files test")
	}
}

func TestFileSystem_SearchFiles(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem search files
	if session.FileSystem != nil {
		// First create a subdirectory for testing
		testSubdirPath := TestPathPrefix + "/search_test_dir"
		fmt.Println("Creating a subdirectory for search testing...")
		success, err := session.FileSystem.CreateDirectory(testSubdirPath)
		if err != nil {
			t.Fatalf("Failed to create test subdirectory: %v", err)
		}
		if !success {
			t.Fatalf("Failed to create test subdirectory: operation returned false")
		}
		t.Log("Test subdirectory created successfully")

		// Create test files with specific naming patterns
		file1Content := "This is test file 1 content."
		file2Content := "This is test file 2 content."
		file3Content := "This is test file 3 content."

		// Note: The pattern to search for is in the file names, not the content
		searchFile1Path := testSubdirPath + "/SEARCHABLE_PATTERN_file1.txt"
		_, err = session.FileSystem.WriteFile(searchFile1Path, file1Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 1: %v", err)
		}
		searchFile2Path := testSubdirPath + "/regular_file2.txt"
		_, err = session.FileSystem.WriteFile(searchFile2Path, file2Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 2: %v", err)
		}
		searchFile3Path := testSubdirPath + "/SEARCHABLE_PATTERN_file3.txt"
		_, err = session.FileSystem.WriteFile(searchFile3Path, file3Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 3: %v", err)
		}

		fmt.Println("Searching files in subdirectory...")
		// Search for files with names containing the pattern
		searchPattern := "SEARCHABLE_PATTERN"
		excludePatterns := []string{"ignored_pattern"}
		searchResults, err := session.FileSystem.SearchFiles(testSubdirPath, searchPattern, excludePatterns)
		if err != nil {
			t.Errorf("Search files failed: %v", err)
		} else {
			t.Log("Search files successful")
			t.Logf("SearchFiles result: content length=%d, err=%v", len(searchResults), err)

			// Extract search results from content
			var results []map[string]string

			// Check if no matches were found
			if strings.Contains(searchResults, "No matches found") {
				t.Logf("No matches found in search results")
			} else {
				// Parse as a simple list of file paths
				lines := strings.Split(searchResults, "\n")
				for _, line := range lines {
					line = strings.TrimSpace(line)
					if line == "" {
						continue
					}

					// Create a result entry for each file path
					resultMap := map[string]string{
						"path": line,
					}
					results = append(results, resultMap)
				}
			}

			// Verify we found the expected number of results (should be 2 files)
			if len(results) != 2 {
				t.Errorf("Unexpected number of search results. Expected: 2, Got: %d", len(results))
			} else {
				t.Log("Search found the expected number of results")
			}

			// Verify the search results contain the expected files
			foundFile1 := false
			foundFile3 := false

			for _, result := range results {
				path := result["path"]

				// Normalize paths for comparison (replace backslashes with forward slashes)
				normalizedPath := path
				normalizedPath = strings.ReplaceAll(normalizedPath, "\\", "/")

				// Log the paths for debugging
				t.Logf("Comparing result path: %s with expected paths: %s and %s",
					normalizedPath, searchFile1Path, searchFile3Path)

				if normalizedPath == searchFile1Path {
					foundFile1 = true
				} else if normalizedPath == searchFile3Path {
					foundFile3 = true
				}
			}

			if !foundFile1 {
				t.Errorf("Search results missing file 1")
			}
			if !foundFile3 {
				t.Errorf("Search results missing file 3")
			}

			if foundFile1 && foundFile3 {
				t.Log("Search results contain the expected files")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping search files test")
	}
}

func TestFileSystem_LargeFileOperations(t *testing.T) {
	// Setup session with cleanup
	session, cleanup := testutil.SetupAndCleanup(t, nil)
	defer cleanup()

	// Test FileSystem large file operations
	if session.FileSystem != nil {
		// Generate a large string (approximately 150KB)
		var largeContent strings.Builder
		lineContent := "This is a line of test content for large file testing. It contains enough characters to test the chunking functionality.\n"

		// Generate about 150KB of data (60KB is the default chunk size)
		targetSize := 150 * 1024 // 150KB
		for largeContent.Len() < targetSize {
			largeContent.WriteString(lineContent)
		}

		testContent := largeContent.String()
		t.Logf("Generated test content of size: %d bytes", len(testContent))

		// Test 1: Write large file using default chunk size
		testFilePath1 := TestPathPrefix + "/test_large_default.txt"
		fmt.Println("Test 1: Writing large file with default chunk size...")
		success, err := session.FileSystem.WriteLargeFile(testFilePath1, testContent, 0)
		if err != nil {
			t.Fatalf("WriteLargeFile failed with default chunk size: %v", err)
		}
		if !success {
			t.Errorf("WriteLargeFile returned false with default chunk size")
		} else {
			t.Log("Test 1: Large file write successful with default chunk size")
		}

		// Test 2: Read the file using default chunk size
		fmt.Println("Test 2: Reading large file with default chunk size...")
		readContent1, err := session.FileSystem.ReadLargeFile(testFilePath1, 0)
		if err != nil {
			t.Fatalf("ReadLargeFile failed with default chunk size: %v", err)
		}

		// Verify content
		t.Logf("Test 2: File read successful, content length: %d bytes", len(readContent1))
		if readContent1 != testContent {
			t.Errorf("File content mismatch with default chunk size. Expected length: %d, Got length: %d",
				len(testContent), len(readContent1))

			// Find first mismatch position
			minLen := len(testContent)
			if len(readContent1) < minLen {
				minLen = len(readContent1)
			}

			for i := 0; i < minLen; i++ {
				if testContent[i] != readContent1[i] {
					t.Errorf("First mismatch at position %d: expected '%c', got '%c'",
						i, testContent[i], readContent1[i])
					break
				}
			}
		} else {
			t.Log("Test 2: File content verified successfully with default chunk size")
		}

		// Test 3: Write large file using custom chunk size
		customChunkSize := 30 * 1024 // 30KB
		testFilePath2 := TestPathPrefix + "/test_large_custom.txt"
		fmt.Printf("Test 3: Writing large file with custom chunk size: %d bytes\n", customChunkSize)

		success, err = session.FileSystem.WriteLargeFile(testFilePath2, testContent, customChunkSize)
		if err != nil {
			t.Fatalf("WriteLargeFile failed with custom chunk size: %v", err)
		}
		if !success {
			t.Errorf("WriteLargeFile returned false with custom chunk size")
		} else {
			t.Log("Test 3: Large file write successful with custom chunk size")
		}

		// Test 4: Read the file using custom chunk size
		fmt.Printf("Test 4: Reading large file with custom chunk size: %d bytes\n", customChunkSize)
		readContent2, err := session.FileSystem.ReadLargeFile(testFilePath2, customChunkSize)
		if err != nil {
			t.Fatalf("ReadLargeFile failed with custom chunk size: %v", err)
		}

		// Verify content
		t.Logf("Test 4: File read successful, content length: %d bytes", len(readContent2))
		if readContent2 != testContent {
			t.Errorf("File content mismatch with custom chunk size. Expected length: %d, Got length: %d",
				len(testContent), len(readContent2))
		} else {
			t.Log("Test 4: File content verified successfully with custom chunk size")
		}

		// Test 5: Cross-test - Write with default chunk size, read with custom chunk size
		fmt.Println("Test 5: Cross-test - Reading with custom chunk size a file written with default chunk size...")
		crossTestContent, err := session.FileSystem.ReadLargeFile(testFilePath1, customChunkSize)
		if err != nil {
			t.Fatalf("ReadLargeFile cross-test failed: %v", err)
		}

		// Verify content
		t.Logf("Test 5: Cross-test read successful, content length: %d bytes", len(crossTestContent))
		if crossTestContent != testContent {
			t.Errorf("File content mismatch in cross-test. Expected length: %d, Got length: %d",
				len(testContent), len(crossTestContent))
		} else {
			t.Log("Test 5: Cross-test content verified successfully")
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping large file operations test")
	}
}
