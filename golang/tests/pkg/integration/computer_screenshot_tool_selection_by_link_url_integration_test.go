package integration_test

import (
	"os"
	"strings"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

const (
	computerLinkUrlEndpoint = "agentbay-pre.cn-hangzhou.aliyuncs.com"
	computerLinkUrlImageID  = "computer-use-ubuntu-2204-regionGW"

	computerNoLinkUrlEndpoint = "wuyingai.cn-shanghai.aliyuncs.com"
	computerNoLinkUrlImageID  = "moltbot-linux-ubuntu-2204"
)

func newAgentBayWithEndpoint(t *testing.T, apiKey string, endpoint string) *agentbay.AgentBay {
	t.Helper()
	cfg := &agentbay.Config{
		Endpoint:  endpoint,
		TimeoutMs: 60000,
		RegionID:  os.Getenv("AGENTBAY_REGION_ID"),
	}
	client, err := agentbay.NewAgentBay(apiKey, agentbay.WithConfig(cfg))
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}
	return client
}

func TestComputerLinkUrlPresentRequiresBetaTakeScreenshot(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client := newAgentBayWithEndpoint(t, apiKey, computerLinkUrlEndpoint)

	params := agentbay.NewCreateSessionParams().WithImageId(computerLinkUrlImageID)
	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := createResult.Session
	defer func() {
		_, _ = client.Delete(session)
	}()

	if session.GetLinkUrl() == "" {
		t.Fatalf("Expected session.LinkUrl to be non-empty for this endpoint/image")
	}

	r := session.Computer.Screenshot()
	if r == nil {
		t.Fatalf("Computer.Screenshot returned nil")
	}
	if r.ErrorMessage == "" {
		t.Fatalf("Expected screenshot() to fail when LinkUrl is present")
	}
	if !strings.Contains(r.ErrorMessage, "does not support `screenshot()`") || !strings.Contains(r.ErrorMessage, "beta_take_screenshot") {
		t.Fatalf("Unexpected screenshot() error message: %q", r.ErrorMessage)
	}

	beta := session.Computer.BetaTakeScreenshot("png")
	if beta == nil {
		t.Fatalf("Computer.BetaTakeScreenshot returned nil")
	}
	if !beta.Success {
		t.Fatalf("beta_take_screenshot failed: %s", beta.ErrorMessage)
	}
	if beta.Format != "png" {
		t.Fatalf("Unexpected format: %q", beta.Format)
	}
	if beta.Width == nil || beta.Height == nil || *beta.Width <= 0 || *beta.Height <= 0 {
		t.Fatalf("Unexpected dimensions: width=%v height=%v", beta.Width, beta.Height)
	}
	if len(beta.Data) == 0 {
		t.Fatalf("Expected non-empty screenshot bytes")
	}
	pngMagic := []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}
	if len(beta.Data) < len(pngMagic) {
		t.Fatalf("Screenshot bytes too short: %d", len(beta.Data))
	}
	ok := true
	for i := 0; i < len(pngMagic); i++ {
		if beta.Data[i] != pngMagic[i] {
			ok = false
			break
		}
	}
	if !ok {
		t.Fatalf("Screenshot bytes do not look like PNG")
	}
}

func TestComputerLinkUrlAbsentRequiresScreenshot(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client := newAgentBayWithEndpoint(t, apiKey, computerNoLinkUrlEndpoint)

	params := agentbay.NewCreateSessionParams().WithImageId(computerNoLinkUrlImageID)
	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Error creating session: %v", err)
	}
	session := createResult.Session
	defer func() {
		_, _ = client.Delete(session)
	}()

	if session.GetLinkUrl() != "" {
		t.Fatalf("Expected session.LinkUrl to be empty for this endpoint/image, got: %q", session.GetLinkUrl())
	}

	r := session.Computer.Screenshot()
	if r == nil {
		t.Fatalf("Computer.Screenshot returned nil")
	}
	if r.ErrorMessage != "" {
		t.Fatalf("Screenshot failed: %s", r.ErrorMessage)
	}
	if strings.TrimSpace(r.Data) == "" {
		t.Fatalf("Expected non-empty screenshot URL")
	}

	beta := session.Computer.BetaTakeScreenshot("png")
	if beta == nil {
		t.Fatalf("Computer.BetaTakeScreenshot returned nil")
	}
	if beta.Success {
		t.Fatalf("Expected beta_take_screenshot to fail when LinkUrl is absent")
	}
	if !strings.Contains(beta.ErrorMessage, "does not support `beta_take_screenshot()`") {
		t.Fatalf("Unexpected beta_take_screenshot error message: %q", beta.ErrorMessage)
	}
}
