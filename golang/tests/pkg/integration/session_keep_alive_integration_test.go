package integration

import (
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func isReleasedStatusResult(r *agentbay.SessionStatusResult) bool {
	if r == nil {
		return false
	}
	if r.Success {
		return r.Status == "FINISH" || r.Status == "DELETING" || r.Status == "DELETED"
	}
	return r.Code == "InvalidMcpSession.NotFound"
}

// TestSessionKeepAliveIntegration verifies that keep-alive refreshes idle timer:
// after calling KeepAlive on one session, it should remain alive when the control session is released.
func TestSessionKeepAliveIntegration(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	idleReleaseTimeoutSeconds := int32(30)
	maxOverSeconds := int32(60)
	pollInterval := 15 * time.Second
	imageID := "linux_latest"

	commonLabels := map[string]string{
		"test": "session-keep-alive",
		"sdk":  "golang",
	}

	controlParams := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithIdleReleaseTimeout(idleReleaseTimeoutSeconds).
		WithLabels(map[string]string{
			"test": commonLabels["test"],
			"sdk":  commonLabels["sdk"],
			"role": "control",
		})
	refreshedParams := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithIdleReleaseTimeout(idleReleaseTimeoutSeconds).
		WithLabels(map[string]string{
			"test": commonLabels["test"],
			"sdk":  commonLabels["sdk"],
			"role": "refreshed",
		})

	start := time.Now()

	controlCreate, err := client.Create(controlParams)
	if err != nil {
		t.Fatalf("Failed to create control session: %v", err)
	}
	if controlCreate == nil || controlCreate.Session == nil {
		t.Fatalf("Create returned nil control session")
	}
	control := controlCreate.Session

	refreshedCreate, err := client.Create(refreshedParams)
	if err != nil {
		t.Fatalf("Failed to create refreshed session: %v", err)
	}
	if refreshedCreate == nil || refreshedCreate.Session == nil {
		t.Fatalf("Create returned nil refreshed session")
	}
	refreshed := refreshedCreate.Session

	defer func() {
		for _, s := range []*agentbay.Session{refreshed, control} {
			if s == nil {
				continue
			}
			status, e := s.GetStatus()
			if e == nil && status != nil && !isReleasedStatusResult(status) {
				_, _ = s.Delete()
			}
		}
	}()

	time.Sleep(time.Duration(idleReleaseTimeoutSeconds) * time.Second / 2)
	keepAliveResult, err := refreshed.KeepAlive()
	if err != nil {
		t.Fatalf("KeepAlive failed: %v", err)
	}
	if keepAliveResult == nil || !keepAliveResult.Success {
		t.Fatalf("KeepAlive returned success=false: %v", keepAliveResult)
	}

	deadline := start.Add(time.Duration(idleReleaseTimeoutSeconds+maxOverSeconds) * time.Second)
	for time.Now().Before(deadline) {
		controlStatus, e1 := control.GetStatus()
		if e1 != nil {
			t.Fatalf("Control GetStatus failed: %v", e1)
		}
		refreshedStatus, e2 := refreshed.GetStatus()
		if e2 != nil {
			t.Fatalf("Refreshed GetStatus failed: %v", e2)
		}

		if isReleasedStatusResult(controlStatus) {
			if isReleasedStatusResult(refreshedStatus) {
				t.Fatalf("Refreshed session released no later than control session; keep-alive did not extend idle timer")
			}
			return
		}

		time.Sleep(pollInterval)
	}
}
