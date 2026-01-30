package integration

import (
	"bytes"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMobileBetaScreenshotPNG(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	sessionParams := &agentbay.CreateSessionParams{
		ImageId: "imgc-0ab5ta4mn31wth5lh",
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
	assert.True(t, s.Success, "beta screenshot failed: %s", s.ErrorMessage)
	assert.Equal(t, "png", s.Format)
	assert.NotNil(t, s.Width)
	assert.NotNil(t, s.Height)
	assert.Greater(t, *s.Width, 0)
	assert.Greater(t, *s.Height, 0)
	assert.True(t, bytes.HasPrefix(s.Data, []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}))
	assert.Greater(t, len(s.Data), 8)

	ls := session.Mobile.BetaTakeLongScreenshot(2, "png")
	assert.NotEmpty(t, ls.RequestID)
	assert.True(t, ls.Success, "beta long screenshot failed: %s", ls.ErrorMessage)
	assert.Equal(t, "png", ls.Format)
	assert.NotNil(t, ls.Width)
	assert.NotNil(t, ls.Height)
	assert.Greater(t, *ls.Width, 0)
	assert.Greater(t, *ls.Height, 0)
	assert.True(t, bytes.HasPrefix(ls.Data, []byte{0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a}))
	assert.Greater(t, len(ls.Data), 8)
}

func TestMobileBetaLongScreenshotJPEGQuality(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err, "Failed to create AgentBay client")

	sessionParams := &agentbay.CreateSessionParams{
		ImageId: "imgc-0ab5ta4mn31wth5lh",
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

	invalid := session.Mobile.BetaTakeLongScreenshot(2, "jpeg", 0)
	assert.False(t, invalid.Success)
	assert.Contains(t, invalid.ErrorMessage, "invalid quality")
	assert.Equal(t, "jpeg", invalid.Format)

	high := session.Mobile.BetaTakeLongScreenshot(2, "jpeg", 95)
	low := session.Mobile.BetaTakeLongScreenshot(2, "jpeg", 10)

	assert.NotEmpty(t, high.RequestID)
	assert.True(t, high.Success, "beta long screenshot (jpeg, q=95) failed: %s", high.ErrorMessage)
	assert.Equal(t, "jpeg", high.Format)
	assert.NotNil(t, high.Width)
	assert.NotNil(t, high.Height)
	assert.Greater(t, *high.Width, 0)
	assert.Greater(t, *high.Height, 0)
	assert.True(t, bytes.HasPrefix(high.Data, []byte{0xff, 0xd8, 0xff}))
	assert.Greater(t, len(high.Data), 3)

	assert.NotEmpty(t, low.RequestID)
	assert.True(t, low.Success, "beta long screenshot (jpeg, q=10) failed: %s", low.ErrorMessage)
	assert.Equal(t, "jpeg", low.Format)
	assert.NotNil(t, low.Width)
	assert.NotNil(t, low.Height)
	assert.Greater(t, *low.Width, 0)
	assert.Greater(t, *low.Height, 0)
	assert.True(t, bytes.HasPrefix(low.Data, []byte{0xff, 0xd8, 0xff}))
	assert.Greater(t, len(low.Data), 3)

	assert.Greater(t, len(high.Data), len(low.Data))
}
