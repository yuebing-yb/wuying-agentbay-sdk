package integration

import (
	"bytes"
	"os"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func firstN(s string, n int) string {
	if n <= 0 {
		return ""
	}
	if len(s) <= n {
		return s
	}
	return s[:n]
}

func TestMobileBetaScreenshotPNG(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	sessionParams := &agentbay.CreateSessionParams{
		ImageId: "imgc-0ab5takhnlaixj11v",
	}
	sessionResult, err := agentBay.Create(sessionParams)
	require.NoError(t, err, "Failed to create session")
	require.NotNil(t, sessionResult.Session, "Session should be created")

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
		require.NoError(t, err)
		require.True(t, r.Success, "Command failed: %s error=%s", c, r.ErrorMessage)
	}

	start := session.Mobile.StartApp("monkey -p com.android.settings 1", "", "")
	require.NotEmpty(t, start.RequestID)
	require.Empty(t, start.ErrorMessage)
	time.Sleep(2 * time.Second)

	s := session.Mobile.BetaTakeScreenshot()
	assert.NotEmpty(t, s.RequestID)
	if !s.Success {
		raw, _ := session.CallMcpTool("screenshot", map[string]interface{}{"format": "png"})
		t.Fatalf("beta screenshot failed: %s raw_success=%v raw_len=%d raw_prefix=%q raw_err=%q", s.ErrorMessage, raw.Success, len(raw.Data), firstN(raw.Data, 300), raw.ErrorMessage)
	}
	assert.True(t, s.Success)
	assert.Equal(t, "png", s.Format)
	assert.True(t, bytes.HasPrefix(s.Data, []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}))
	assert.Greater(t, len(s.Data), 8)

	ls := session.Mobile.BetaTakeLongScreenshot(2, "png")
	if !ls.Success && strings.Contains(ls.ErrorMessage, "Failed to capture long screenshot") {
		t.Skip(ls.ErrorMessage)
	}
	assert.NotEmpty(t, ls.RequestID)
	assert.True(t, ls.Success)
	assert.Equal(t, "png", ls.Format)
	assert.True(t, bytes.HasPrefix(ls.Data, []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}))
	assert.Greater(t, len(ls.Data), 8)
}

