package integration

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMobileGetAllUIElementsXMLFormatContract(t *testing.T) {
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

	ui := session.Mobile.GetAllUIElements(10000, "xml")
	assert.NotEmpty(t, ui.RequestID, "Should have request ID")
	assert.Empty(t, ui.ErrorMessage, "get_all_ui_elements(xml) should not return error")
	assert.Equal(t, "xml", ui.Format)
	assert.NotEmpty(t, ui.Raw)
	assert.Contains(t, ui.Raw, "<hierarchy")
	assert.Equal(t, 0, len(ui.Elements))
}
