package integration

import (
	"fmt"
	"os"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func isNotFoundStatusResult(r *agentbay.SessionStatusResult) bool {
	if r == nil {
		return false
	}
	if r.Success {
		return false
	}
	return r.Code == "InvalidMcpSession.NotFound"
}

// TestSessionIdleReleaseTimeoutIntegration verifies session is released between timeout and timeout+60s.
func TestSessionIdleReleaseTimeoutIntegration(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Fatal("AGENTBAY_API_KEY environment variable is not set")
	}

	client, err := agentbay.NewAgentBay(apiKey, nil)
	if err != nil {
		t.Fatalf("Failed to initialize AgentBay client: %v", err)
	}

	idleReleaseTimeoutSeconds := int32(60)
	maxOverSeconds := int32(60)
	imageID := "linux_latest"

	params := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithIdleReleaseTimeout(idleReleaseTimeoutSeconds).
		WithLabels(map[string]string{
			"test": "idle-release-timeout",
			"sdk":  "golang",
		})

	start := time.Now()
	createResult, err := client.Create(params)
	if err != nil {
		t.Fatalf("Failed to create session: %v", err)
	}
	if createResult == nil || createResult.Session == nil {
		t.Fatalf("Create returned nil session")
	}
	session := createResult.Session
	t.Logf("Session created: %s", session.SessionID)

	defer func() {
		// Best-effort cleanup: if still running, delete it.
		status, e := session.GetStatus()
		if e == nil && status != nil && status.Success && status.Status != "" &&
			status.Status != "FINISH" && status.Status != "DELETING" && status.Status != "DELETED" {
			_, _ = session.Delete()
		}
	}()

	timeoutDeadline := start.Add(time.Duration(idleReleaseTimeoutSeconds) * time.Second)
	for time.Now().Before(timeoutDeadline) {
		status, e := session.GetStatus()
		if e != nil {
			t.Fatalf("GetStatus failed: %v", e)
		}
		if isNotFoundStatusResult(status) {
			t.Fatalf("Session released too early: NotFound before %ds", idleReleaseTimeoutSeconds)
		}
		if status.Success && (status.Status == "FINISH" || status.Status == "DELETING" || status.Status == "DELETED") {
			t.Fatalf("Session released too early: status=%s before %ds", status.Status, idleReleaseTimeoutSeconds)
		}
		remaining := time.Until(timeoutDeadline)
		sleep := 2 * time.Second
		if remaining < sleep {
			sleep = remaining
		}
		time.Sleep(sleep)
	}

	deadline := timeoutDeadline.Add(time.Duration(maxOverSeconds) * time.Second)
	for time.Now().Before(deadline) {
		status, e := session.GetStatus()
		if e != nil {
			t.Fatalf("GetStatus failed: %v", e)
		}

		if isNotFoundStatusResult(status) {
			elapsed := time.Since(start).Seconds()
			if elapsed < float64(idleReleaseTimeoutSeconds) {
				t.Fatalf("Session released too early: elapsed=%.2fs", elapsed)
			}
			if elapsed > float64(idleReleaseTimeoutSeconds+maxOverSeconds) {
				t.Fatalf("Session released too late: elapsed=%.2fs", elapsed)
			}
			fmt.Printf("✅ Session released: NotFound, elapsed=%.2fs\n", elapsed)
			return
		}

		if status.Success && (status.Status == "FINISH" || status.Status == "DELETING" || status.Status == "DELETED") {
			elapsed := time.Since(start).Seconds()
			if elapsed < float64(idleReleaseTimeoutSeconds) {
				t.Fatalf("Session released too early: elapsed=%.2fs", elapsed)
			}
			if elapsed > float64(idleReleaseTimeoutSeconds+maxOverSeconds) {
				t.Fatalf("Session released too late: elapsed=%.2fs", elapsed)
			}
			fmt.Printf("✅ Session released: status=%s, elapsed=%.2fs\n", status.Status, elapsed)
			return
		}

		time.Sleep(2 * time.Second)
	}

	t.Fatalf("Session was not released within %ds~%ds", idleReleaseTimeoutSeconds, idleReleaseTimeoutSeconds+maxOverSeconds)
}
