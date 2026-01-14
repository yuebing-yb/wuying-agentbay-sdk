package integration

import (
	"bytes"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/require"
)

func TestComputerBetaScreenshotJPEG(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)

	sessionResult, err := agentBay.Create(&agentbay.CreateSessionParams{ImageId: "linux_latest"})
	require.NoError(t, err)
	require.NotNil(t, sessionResult.Session)
	session := sessionResult.Session
	defer func() { _, _ = session.Delete() }()

	time.Sleep(10 * time.Second)

	s := session.Computer.BetaTakeScreenshot("jpg")
	require.True(t, s.Success, "beta screenshot failed: %s", s.ErrorMessage)
	require.Equal(t, "jpeg", s.Format)
	require.Greater(t, len(s.Data), 3)
	require.True(t, bytes.HasPrefix(s.Data, []byte{0xff, 0xd8, 0xff}))
}
