package main

import (
	"fmt"
	"os"
	"path/filepath"
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
		ImageId: "imgc-0ab5ta4mn31wth5lh",
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

	cmds := []string{
		"wm size 720x1280",
		"wm density 160",
	}
	for _, c := range cmds {
		r, err := session.Command.ExecuteCommand(c, 10000)
		if err != nil || !r.Success {
			fmt.Printf("Command failed: %s error=%s\n", c, r.ErrorMessage)
			return
		}
	}

	start := session.Mobile.StartApp("monkey -p com.android.settings 1", "", "")
	if start.ErrorMessage != "" {
		fmt.Printf("Failed to start Settings: %s\n", start.ErrorMessage)
		return
	}
	time.Sleep(2 * time.Second)

	outDir := "./tmp"
	if err := os.MkdirAll(outDir, 0o755); err != nil {
		fmt.Printf("Failed to create output directory: %v\n", err)
		return
	}

	s1 := session.Mobile.BetaTakeScreenshot()
	if !s1.Success {
		fmt.Printf("beta_take_screenshot failed: %s\n", s1.ErrorMessage)
		return
	}
	p1 := filepath.Join(outDir, "mobile_beta_screenshot.png")
	if err := os.WriteFile(p1, s1.Data, 0o644); err != nil {
		fmt.Printf("Failed to write screenshot: %v\n", err)
		return
	}
	size1 := ""
	if s1.Width != nil && s1.Height != nil {
		size1 = fmt.Sprintf(", size=%dx%d", *s1.Width, *s1.Height)
	}
	fmt.Printf("Saved %s (%d bytes%s)\n", p1, len(s1.Data), size1)

	s2 := session.Mobile.BetaTakeLongScreenshot(2, "png")
	if !s2.Success {
		fmt.Printf("beta_take_long_screenshot failed: %s\n", s2.ErrorMessage)
		return
	}
	p2 := filepath.Join(outDir, "mobile_beta_long_screenshot.png")
	if err := os.WriteFile(p2, s2.Data, 0o644); err != nil {
		fmt.Printf("Failed to write long screenshot: %v\n", err)
		return
	}
	size2 := ""
	if s2.Width != nil && s2.Height != nil {
		size2 = fmt.Sprintf(", size=%dx%d", *s2.Width, *s2.Height)
	}
	fmt.Printf("Saved %s (%d bytes%s)\n", p2, len(s2.Data), size2)
}
