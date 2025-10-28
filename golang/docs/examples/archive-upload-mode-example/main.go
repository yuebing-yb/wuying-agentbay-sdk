package main

import (
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	fmt.Println("🚀 AgentBay Archive Upload Mode Context Sync Example")
	fmt.Println(strings.Repeat("=", 60))

	// Get API key from environment variable or use a default value for testing
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		apiKey = "your-api-key-here" // Replace with your actual API key
		fmt.Println("Warning: AGENTBAY_API_KEY environment variable not set. Using default key.")
	}

	// Initialize the AgentBay client
	ab, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("❌ Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	uniqueID := generateUniqueID()

	// Execute archive upload mode example
	if err := archiveUploadModeExample(ab, uniqueID); err != nil {
		fmt.Printf("❌ Example execution failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("✅ Archive upload mode example completed")
}

func generateUniqueID() string {
	timestamp := time.Now().UnixNano()/1000000 + int64(rand.Intn(1000))
	randomPart := rand.Intn(10000)
	return fmt.Sprintf("%d-%d", timestamp, randomPart)
}

func archiveUploadModeExample(ab *agentbay.AgentBay, uniqueID string) error {
	fmt.Println("\n📦 === Archive Upload Mode Context Sync Example ===")

	var session *agentbay.Session

	defer func() {
		// Step 8: Cleanup
		if session != nil {
			fmt.Println("\n🧹 Step 8: Cleaning up session...")
			deleteResult, err := ab.Delete(session)
			if err != nil {
				fmt.Printf("❌ Failed to delete session: %v\n", err)
			} else {
				fmt.Printf("✅ Session deleted successfully!\n")
				fmt.Printf("   Success: %t\n", deleteResult.Success)
				fmt.Printf("   Request ID: %s\n", deleteResult.RequestID)
			}
		}
	}()

	// Step 1: Create context for Archive mode
	fmt.Println("\n📦 Step 1: Creating context for Archive upload mode...")
	contextName := fmt.Sprintf("archive-mode-context-%s", uniqueID)
	contextResult, err := ab.Context.Get(contextName, true)
	if err != nil {
		return fmt.Errorf("context creation failed: %v", err)
	}

	fmt.Printf("✅ Context created successfully!\n")
	fmt.Printf("   Context ID: %s\n", contextResult.ContextID)
	fmt.Printf("   Request ID: %s\n", contextResult.RequestID)

	// Step 2: Configure sync policy with Archive upload mode
	fmt.Println("\n⚙️  Step 2: Configuring sync policy with Archive upload mode...")
	uploadPolicy := &agentbay.UploadPolicy{
		UploadMode: agentbay.UploadModeArchive, // Set to Archive mode
	}
	syncPolicy := &agentbay.SyncPolicy{
		UploadPolicy: uploadPolicy,
	}

	fmt.Printf("✅ Sync policy configured with uploadMode: %s\n", syncPolicy.UploadPolicy.UploadMode)

	// Step 3: Create context sync configuration
	fmt.Println("\n🔧 Step 3: Creating context sync configuration...")
	contextSync := &agentbay.ContextSync{
		ContextID: contextResult.ContextID,
		Path:      "/tmp/archive-mode-test",
		Policy:    syncPolicy,
	}

	fmt.Printf("✅ Context sync created:\n")
	fmt.Printf("   Context ID: %s\n", contextSync.ContextID)
	fmt.Printf("   Path: %s\n", contextSync.Path)
	fmt.Printf("   Upload Mode: %s\n", contextSync.Policy.UploadPolicy.UploadMode)

	// Step 4: Create session with Archive mode context sync
	fmt.Println("\n🏗️  Step 4: Creating session with Archive mode context sync...")
	sessionParams := agentbay.NewCreateSessionParams().
		WithLabels(map[string]string{
			"example":    fmt.Sprintf("archive-mode-%s", uniqueID),
			"type":       "archive-upload-demo",
			"uploadMode": "Archive",
		}).
		WithContextSync([]*agentbay.ContextSync{contextSync})

	sessionResult, err := ab.Create(sessionParams)
	if err != nil {
		return fmt.Errorf("session creation failed: %v", err)
	}

	session = sessionResult.Session
	fmt.Printf("✅ Session created successfully!\n")
	fmt.Printf("   Session ID: %s\n", session.SessionID)
	fmt.Printf("   Request ID: %s\n", sessionResult.RequestID)

	// Get session info to verify setup
	sessionInfo, err := ab.GetSession(session.SessionID)
	if err == nil && sessionInfo.Success && sessionInfo.Data != nil {
		fmt.Printf("   App Instance ID: %s\n", sessionInfo.Data.AppInstanceID)
	}

	// Step 5: Create and write test files
	fmt.Println("\n📝 Step 5: Creating test files in Archive mode context...")

	// Generate 5KB test content
	contentSize := 5 * 1024 // 5KB
	baseContent := "Archive mode test successful! This is a test file created in the session path. "
	repeatedContent := strings.Repeat(baseContent, (contentSize/len(baseContent))+1)
	fileContent := repeatedContent[:contentSize]

	filePath := "/tmp/archive-mode-test/test-file-5kb.txt"

	fmt.Printf("📄 Creating file: %s\n", filePath)
	fmt.Printf("📊 File content size: %d bytes\n", len(fileContent))

	writeResult, err := session.FileSystem.WriteFile(filePath, fileContent, "overwrite")
	if err != nil {
		return fmt.Errorf("file write failed: %v", err)
	}

	fmt.Printf("✅ File write successful!\n")
	fmt.Printf("   Request ID: %s\n", writeResult.RequestID)

	// Step 6: Test context info functionality
	fmt.Println("\n📊 Step 6: Testing context info functionality...")
	infoResult, err := session.Context.Info()
	if err != nil {
		return fmt.Errorf("context info failed: %v", err)
	}

	fmt.Printf("✅ Context info retrieved successfully!\n")
	fmt.Printf("   Request ID: %s\n", infoResult.RequestID)
	fmt.Printf("   Context status data count: %d\n", len(infoResult.ContextStatusData))

	// Display context status details
	if len(infoResult.ContextStatusData) > 0 {
		fmt.Println("\n📋 Context status details:")
		for index, status := range infoResult.ContextStatusData {
			fmt.Printf("   [%d] Context ID: %s\n", index, status.ContextId)
			fmt.Printf("       Path: %s\n", status.Path)
			fmt.Printf("       Status: %s\n", status.Status)
			fmt.Printf("       Task Type: %s\n", status.TaskType)
			if status.ErrorMessage != "" {
				fmt.Printf("       Error: %s\n", status.ErrorMessage)
			}
		}
	}

	// Step 7: Verify file information
	fmt.Println("\n🔍 Step 7: Verifying file information...")
	fileInfoResult, err := session.FileSystem.GetFileInfo(filePath)
	if err != nil {
		return fmt.Errorf("get file info failed: %v", err)
	}

	fmt.Printf("✅ File info retrieved successfully!\n")
	fmt.Printf("   Request ID: %s\n", fileInfoResult.RequestID)

	if fileInfoResult.FileInfo != nil {
		fmt.Printf("📄 File details:\n")
		fmt.Printf("   Size: %d bytes\n", fileInfoResult.FileInfo.Size)
		fmt.Printf("   Is Directory: %t\n", fileInfoResult.FileInfo.IsDirectory)
		fmt.Printf("   Modified Time: %s\n", fileInfoResult.FileInfo.ModTime)
		fmt.Printf("   Mode: %s\n", fileInfoResult.FileInfo.Mode)
	}

	fmt.Println("\n🎉 Archive upload mode example completed successfully!")
	fmt.Println("✅ All operations completed without errors.")

	return nil
}