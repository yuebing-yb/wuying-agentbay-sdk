package main

import (
	"fmt"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("AGENTBAY_API_KEY environment variable is not set")
		os.Exit(1)
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Failed to initialize AgentBay client: %v\n", err)
		os.Exit(1)
	}

	params := agentbay.NewCreateSessionParams().
		WithImageId("linux_latest").
		WithIdleReleaseTimeout(30).
		WithLabels(map[string]string{
			"example": "session-keep-alive",
			"sdk":     "golang",
		})

	create, err := agentBay.Create(params)
	if err != nil || create == nil || create.Session == nil {
		fmt.Printf("Failed to create session: %v\n", err)
		os.Exit(1)
	}
	session := create.Session
	fmt.Printf("Session ID: %s\n", session.SessionID)

	defer func() {
		_, _ = session.Delete()
	}()

	fmt.Println("Sleeping for 15 seconds...")
	time.Sleep(15 * time.Second)

	fmt.Println("Calling KeepAlive() to refresh idle timer...")
	keepAliveResult, err := session.KeepAlive()
	if err != nil {
		fmt.Printf("KeepAlive failed: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("KeepAlive success: %t (RequestID: %s)\n", keepAliveResult.Success, keepAliveResult.RequestID)
	if !keepAliveResult.Success {
		fmt.Printf("Error: %s\n", keepAliveResult.ErrorMessage)
	}
}

