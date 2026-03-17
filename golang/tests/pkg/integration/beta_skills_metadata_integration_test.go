package integration

import (
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/require"
)

func TestBetaSkillsListMetadata(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("Skipping integration test: AGENTBAY_API_KEY not set")
	}

	ab, err := agentbay.NewAgentBay(apiKey)
	require.NoError(t, err)

	items, err := ab.BetaSkills.ListMetadata()
	require.NoError(t, err)
	require.Greater(t, len(items), 0)
	require.NotEmpty(t, items[0].Name)
}
