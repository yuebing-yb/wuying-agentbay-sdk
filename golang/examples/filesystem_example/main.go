package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	// Get API key from environment variable or use a default value for testing
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "akm-xxx" // Replace with your actual API key for testing
		fmt.Println("Warning: Using default API key. Set AGENTBAY_API_KEY environment variable for production use.")
	}

	// Initialize the AgentBay client
	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// Create a new session
	fmt.Println("\nCreating a new session...")
	session, err := agentBay.Create(nil)
	if err != nil {
		fmt.Printf("\nError creating session: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("\nSession created with ID: %s\n", session.SessionID)
	defer func() {
		// Clean up by deleting the session when we're done
		fmt.Println("\nDeleting the session...")
		err = agentBay.Delete(session)
		if err != nil {
			fmt.Printf("Error deleting session: %v\n", err)
		} else {
			fmt.Println("Session deleted successfully")
		}
	}()

	// 1. Create a directory
	testDirPath := "/tmp/test_directory"
	fmt.Printf("\nCreating directory: %s\n", testDirPath)
	success, err := session.FileSystem.CreateDirectory(testDirPath)
	if err != nil {
		fmt.Printf("Error creating directory: %v\n", err)
	} else {
		fmt.Printf("Directory created: %t\n", success)
	}

	// 2. Write a file
	testFilePath := "/tmp/test_directory/sample.txt"
	testContent := "This is a sample file content.\nThis is the second line.\nThis is the third line."
	fmt.Printf("\nWriting file: %s\n", testFilePath)
	success, err = session.FileSystem.WriteFile(testFilePath, testContent, "overwrite")
	if err != nil {
		fmt.Printf("Error writing file: %v\n", err)
	} else {
		fmt.Printf("File written successfully: %t\n", success)
	}

	// 3. Read the file we just created
	fmt.Printf("\nReading file: %s\n", testFilePath)
	content, err := session.FileSystem.ReadFile(testFilePath)
	if err != nil {
		fmt.Printf("Error reading file: %v\n", err)
	} else {
		fmt.Printf("File content:\n%s\n", content)

		// Verify content matches what we wrote
		if content == testContent {
			fmt.Println("Content verification successful!")
		} else {
			fmt.Println("Content verification failed!")
		}
	}

	// 4. Get file info
	fmt.Printf("\nGetting file info for: %s\n", testFilePath)
	fileInfo, err := session.FileSystem.GetFileInfo(testFilePath)
	if err != nil {
		fmt.Printf("Error getting file info: %v\n", err)
	} else {
		fmt.Printf("File info: Name=%s, Path=%s, Size=%d, IsDirectory=%t\n",
			fileInfo.Name, fileInfo.Path, fileInfo.Size, fileInfo.IsDirectory)
	}

	// 5. List directory
	fmt.Printf("\nListing directory: %s\n", "/tmp/test_directory")
	entries, err := session.FileSystem.ListDirectory("/tmp/test_directory")
	if err != nil {
		fmt.Printf("Error listing directory: %v\n", err)
	} else {
		fmt.Println("Directory entries:")
		for _, entry := range entries {
			entryType := "FILE"
			if entry.IsDirectory {
				entryType = "DIR"
			}
			fmt.Printf("  [%s] %s\n", entryType, entry.Name)
		}
	}

	// 6. Edit file
	fmt.Printf("\nEditing file: %s\n", testFilePath)
	edits := []map[string]string{
		{
			"oldText": "second line",
			"newText": "MODIFIED second line",
		},
	}
	success, err = session.FileSystem.EditFile(testFilePath, edits, false)
	if err != nil {
		fmt.Printf("Error editing file: %v\n", err)
	} else {
		fmt.Printf("File edited successfully: %t\n", success)

		// Read the file again to verify the edit
		content, err := session.FileSystem.ReadFile(testFilePath)
		if err != nil {
			fmt.Printf("Error reading edited file: %v\n", err)
		} else {
			fmt.Printf("Edited file content:\n%s\n", content)
		}
	}

	// 7. Search files
	fmt.Printf("\nSearching for files in /tmp containing 'sample'\n")
	searchResults, err := session.FileSystem.SearchFiles("/tmp", "sample", nil)
	if err != nil {
		fmt.Printf("Error searching files: %v\n", err)
	} else {
		fmt.Println("Search results:")
		for _, result := range searchResults {
			fmt.Printf("  %s\n", result)
		}
	}

	// 8. Move/Rename file
	newFilePath := "/tmp/test_directory/renamed.txt"
	fmt.Printf("\nMoving file from %s to %s\n", testFilePath, newFilePath)
	success, err = session.FileSystem.MoveFile(testFilePath, newFilePath)
	if err != nil {
		fmt.Printf("Error moving file: %v\n", err)
	} else {
		fmt.Printf("File moved successfully: %t\n", success)

		// List directory again to verify the move
		entries, err := session.FileSystem.ListDirectory("/tmp/test_directory")
		if err != nil {
			fmt.Printf("Error listing directory after move: %v\n", err)
		} else {
			fmt.Println("Directory entries after move:")
			for _, entry := range entries {
				entryType := "FILE"
				if entry.IsDirectory {
					entryType = "DIR"
				}
				fmt.Printf("  [%s] %s\n", entryType, entry.Name)
			}
		}
	}
}
