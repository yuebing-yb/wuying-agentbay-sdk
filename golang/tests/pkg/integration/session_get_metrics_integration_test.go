package integration

import (
	"os"
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestSessionGetMetrics(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	result, err := client.Create(agentbay.NewCreateSessionParams().WithImageId("linux_latest"))
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	session := result.Session

	defer func() {
		_, _ = session.Delete()
	}()

	metricsResult, err := session.GetMetrics()
	if err != nil {
		t.Fatalf("GetMetrics failed: %v", err)
	}
	if !metricsResult.Success {
		t.Fatalf("GetMetrics returned failure: %s", metricsResult.ErrorMessage)
	}
	if metricsResult.Metrics == nil {
		t.Fatalf("GetMetrics returned nil metrics")
	}

	m := metricsResult.Metrics
	if m.CpuCount < 1 {
		t.Fatalf("unexpected cpu_count: %d", m.CpuCount)
	}
	if m.MemTotal <= 0 {
		t.Fatalf("unexpected mem_total: %d", m.MemTotal)
	}
	if m.DiskTotal <= 0 {
		t.Fatalf("unexpected disk_total: %d", m.DiskTotal)
	}
	if m.CpuUsedPct < 0 || m.CpuUsedPct > 100 {
		t.Fatalf("unexpected cpu_used_pct: %f", m.CpuUsedPct)
	}
	if m.Timestamp == "" {
		t.Fatalf("unexpected timestamp: empty")
	}
}


