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
		fmt.Println("AGENTBAY_API_KEY is not set")
		return
	}

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Failed to create AgentBay client: %v\n", err)
		return
	}

	sessionResult, err := client.Create(&agentbay.CreateSessionParams{
		ImageId: "imgc-0ab5takhnmlvhx9gp",
	})
	if err != nil || sessionResult == nil || sessionResult.Session == nil {
		fmt.Printf("Failed to create session: %v\n", err)
		return
	}

	session := sessionResult.Session
	defer func() {
		_, _ = session.Delete()
	}()

	time.Sleep(15 * time.Second)

	ui := session.Mobile.GetAllUIElements(10000, "xml")
	if ui.ErrorMessage != "" {
		fmt.Printf("get_all_ui_elements(xml) failed: %s\n", ui.ErrorMessage)
		return
	}

	fmt.Printf("RequestID: %s\n", ui.RequestID)
	fmt.Printf("Format: %s\n", ui.Format)
	fmt.Printf("Raw length: %d\n", len(ui.Raw))
	fmt.Printf("Elements: %d\n", len(ui.Elements))
}
