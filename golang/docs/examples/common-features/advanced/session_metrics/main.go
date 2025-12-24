package main

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("AGENTBAY_API_KEY environment variable is not set")
		return
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		fmt.Printf("Failed to initialize AgentBay client: %v\n", err)
		return
	}

	result, err := client.Create(agentbay.NewCreateSessionParams().WithImageId("linux_latest"))
	if err != nil {
		fmt.Printf("Failed to create session: %v\n", err)
		return
	}
	session := result.Session
	defer func() {
		_, _ = session.Delete()
	}()

	metricsResult, err := session.GetMetrics()
	if err != nil {
		fmt.Printf("GetMetrics failed: %v\n", err)
		return
	}
	if !metricsResult.Success {
		fmt.Printf("GetMetrics returned failure: %s\n", metricsResult.ErrorMessage)
		return
	}

	out, _ := json.MarshalIndent(metricsResult.Raw, "", "  ")
	fmt.Println(string(out))
}


