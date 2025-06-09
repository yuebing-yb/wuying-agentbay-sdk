package agentbay_test

import (
	"fmt"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestFileSystem_ReadFile(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem read operations
	if session.FileSystem != nil {
		fmt.Println("Reading file...")
		content, err := session.FileSystem.ReadFile("/etc/hosts")
		t.Logf("ReadFile result: content='%s', err=%v", content, err)
		if err != nil {
			t.Logf("Note: File read failed: %v", err)
		} else {
			t.Logf("File read successful, content length: %d bytes", len(content))
			// Check if response contains "tool not found"
			if containsToolNotFound(content) {
				t.Errorf("FileSystem.ReadFile returned 'tool not found'")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file test")
	}
}

func TestFileSystem_WriteFile(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem write operations
	if session.FileSystem != nil {
		fmt.Println("Writing file...")
		testContent := "This is a test file content for WriteFile test."
		success, err := session.FileSystem.WriteFile("/tmp/test_write.txt", testContent, "overwrite")
		t.Logf("WriteFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File write failed: %v", err)
		} else {
			t.Log("File write successful")

			// Verify the file was written correctly by reading it back
			content, err := session.FileSystem.ReadFile("/tmp/test_write.txt")
			if err != nil {
				t.Errorf("Failed to read back written file: %v", err)
			} else if content != testContent {
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
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem directory creation
	if session.FileSystem != nil {
		fmt.Println("Creating directory...")
		success, err := session.FileSystem.CreateDirectory("/tmp/test_directory")
		t.Logf("CreateDirectory result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("Directory creation failed: %v", err)
		} else {
			t.Log("Directory creation successful")

			// Verify the directory was created by listing its parent directory
			entries, err := session.FileSystem.ListDirectory("/tmp")
			if err != nil {
				t.Errorf("Failed to list directory: %v", err)
			} else {
				directoryFound := false
				for _, entry := range entries {
					name, ok := entry["name"].(string)
					if ok && name == "test_directory" {
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
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem edit operations
	if session.FileSystem != nil {
		// First create a file to edit
		initialContent := "This is the original content.\nLine to be replaced.\nThis is the final line."
		_, err := session.FileSystem.WriteFile("/tmp/test_edit.txt", initialContent, "overwrite")
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
		success, err := session.FileSystem.EditFile("/tmp/test_edit.txt", edits, false)
		t.Logf("EditFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File edit failed: %v", err)
		} else {
			t.Log("File edit successful")

			// Verify the file was edited correctly by reading it back
			content, err := session.FileSystem.ReadFile("/tmp/test_edit.txt")
			if err != nil {
				t.Errorf("Failed to read back edited file: %v", err)
			} else {
				expectedContent := "This is the original content.\nThis line has been edited.\nThis is the final line."
				if content != expectedContent {
					t.Errorf("File content mismatch after edit. Expected: %s, Got: %s", expectedContent, content)
				} else {
					t.Log("File edit verified successfully")
				}
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file edit test")
	}
}

func TestFileSystem_GetFileInfo(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem get file info
	if session.FileSystem != nil {
		// First create a file to get info for
		testContent := "This is a test file for GetFileInfo."
		_, err := session.FileSystem.WriteFile("/tmp/test_info.txt", testContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create file for info test: %v", err)
		}

		fmt.Println("Getting file info...")
		fileInfo, err := session.FileSystem.GetFileInfo("/tmp/test_info.txt")
		t.Logf("GetFileInfo result: fileInfo=%v, err=%v", fileInfo, err)
		if err != nil {
			t.Errorf("Get file info failed: %v", err)
		} else {
			t.Log("Get file info successful")

			// Verify the file info contains expected fields
			if name, ok := fileInfo["name"].(string); !ok || name != "test_info.txt" {
				t.Errorf("File info missing or incorrect name field")
			}
			if _, ok := fileInfo["size"].(float64); !ok {
				t.Errorf("File info missing size field")
			}
			if isDir, ok := fileInfo["isDirectory"].(bool); !ok || isDir {
				t.Errorf("File info missing or incorrect isDirectory field")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file info test")
	}
}

func TestFileSystem_ListDirectory(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem list directory
	if session.FileSystem != nil {
		fmt.Println("Listing directory...")
		entries, err := session.FileSystem.ListDirectory("/tmp")
		t.Logf("ListDirectory result: entries count=%d, err=%v", len(entries), err)
		if err != nil {
			t.Errorf("List directory failed: %v", err)
		} else {
			t.Log("List directory successful")

			// Verify the entries contain expected fields
			if len(entries) > 0 {
				firstEntry := entries[0]
				if _, ok := firstEntry["name"].(string); !ok {
					t.Errorf("Directory entry missing name field")
				}
				if _, ok := firstEntry["isDirectory"].(bool); !ok {
					t.Errorf("Directory entry missing isDirectory field")
				}
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping directory listing test")
	}
}

func TestFileSystem_MoveFile(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem move file
	if session.FileSystem != nil {
		// First create a file to move
		testContent := "This is a test file for MoveFile."
		_, err := session.FileSystem.WriteFile("/tmp/test_source.txt", testContent, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create file for move test: %v", err)
		}

		fmt.Println("Moving file...")
		success, err := session.FileSystem.MoveFile("/tmp/test_source.txt", "/tmp/test_destination.txt")
		t.Logf("MoveFile result: success=%v, err=%v", success, err)
		if err != nil {
			t.Errorf("File move failed: %v", err)
		} else {
			t.Log("File move successful")

			// Verify the file was moved correctly by reading it back
			content, err := session.FileSystem.ReadFile("/tmp/test_destination.txt")
			if err != nil {
				t.Errorf("Failed to read back moved file: %v", err)
			} else if content != testContent {
				t.Errorf("File content mismatch after move. Expected: %s, Got: %s", testContent, content)
			} else {
				t.Log("File move verified successfully")
			}

			// Verify the source file no longer exists
			_, err = session.FileSystem.GetFileInfo("/tmp/test_source.txt")
			if err == nil {
				t.Errorf("Source file still exists after move")
			} else {
				t.Log("Source file correctly no longer exists")
			}
		}
	} else {
		t.Logf("Note: FileSystem interface is nil, skipping file move test")
	}
}

func TestFileSystem_ReadMultipleFiles(t *testing.T) {
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem read multiple files
	if session.FileSystem != nil {
		// First create some test files
		file1Content := "This is test file 1 content."
		file2Content := "This is test file 2 content."
		_, err := session.FileSystem.WriteFile("/tmp/test_file1.txt", file1Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create test file 1: %v", err)
		}
		_, err = session.FileSystem.WriteFile("/tmp/test_file2.txt", file2Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create test file 2: %v", err)
		}

		fmt.Println("Reading multiple files...")
		paths := []string{"/tmp/test_file1.txt", "/tmp/test_file2.txt"}
		contents, err := session.FileSystem.ReadMultipleFiles(paths)
		t.Logf("ReadMultipleFiles result: contents count=%d, err=%v", len(contents), err)
		if err != nil {
			t.Errorf("Read multiple files failed: %v", err)
		} else {
			t.Log("Read multiple files successful")

			// Verify the contents of each file
			if content, ok := contents["/tmp/test_file1.txt"]; !ok || content != file1Content {
				t.Errorf("File 1 content mismatch or missing. Expected: %s, Got: %s", file1Content, content)
			} else {
				t.Log("File 1 content verified successfully")
			}

			if content, ok := contents["/tmp/test_file2.txt"]; !ok || content != file2Content {
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
	// Initialize AgentBay client
	apiKey := getTestAPIKey(t)
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	// Create a session
	fmt.Println("Creating a new session for filesystem testing...")
	session, err := agentBay.Create(nil)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	t.Logf("Session created with ID: %s", session.SessionID)

	// IMPORTANT: Ensure cleanup of the session after test
	defer func() {
		fmt.Println("Cleaning up: Deleting the session...")
		err := agentBay.Delete(session)
		if err != nil {
			t.Logf("Warning: Error deleting session: %v", err)
		} else {
			t.Log("Session successfully deleted")
		}
	}()

	// Test FileSystem search files
	if session.FileSystem != nil {
		// First create some test files with searchable content
		file1Content := "This is a test file with SEARCHABLE_PATTERN in it."
		file2Content := "This is another file without the pattern."
		file3Content := "This file also has the SEARCHABLE_PATTERN present."

		_, err := session.FileSystem.WriteFile("/tmp/search_test1.txt", file1Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 1: %v", err)
		}
		_, err = session.FileSystem.WriteFile("/tmp/search_test2.txt", file2Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 2: %v", err)
		}
		_, err = session.FileSystem.WriteFile("/tmp/search_test3.txt", file3Content, "overwrite")
		if err != nil {
			t.Fatalf("Failed to create search test file 3: %v", err)
		}

		fmt.Println("Searching files...")
		searchPattern := "SEARCHABLE_PATTERN"
		excludePatterns := []string{"ignored_pattern"}
		results, err := session.FileSystem.SearchFiles("/tmp", searchPattern, excludePatterns)
		t.Logf("SearchFiles result: results count=%d, err=%v", len(results), err)
		if err != nil {
			t.Errorf("Search files failed: %v", err)
		} else {
			t.Log("Search files successful")

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
				path, ok := result["path"].(string)
				if !ok {
					continue
				}

				if path == "/tmp/search_test1.txt" {
					foundFile1 = true
				} else if path == "/tmp/search_test3.txt" {
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
