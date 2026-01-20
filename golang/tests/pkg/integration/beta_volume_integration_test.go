package integration_test

import (
	"fmt"
	"strings"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestBetaVolumeCreateListMountAndDelete(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	imageID := "imgc-0ab5ta4mgqs15qxjf"
	volumeName := fmt.Sprintf("beta-volume-it-%d", time.Now().UnixNano())
	testFilePath := fmt.Sprintf("/data/local/tmp/agentbay-volume-%d.txt", time.Now().UnixNano())
	testContent := fmt.Sprintf("agentbay-beta-volume-persist-%d", time.Now().UnixNano())

	// 1) Create (via GetVolume allowCreate=true)
	volResult, err := client.BetaVolume.BetaGetByName(volumeName, imageID, true)
	if err != nil {
		t.Fatalf("BetaGetByName failed: %v", err)
	}
	if !volResult.Success || volResult.Volume == nil || volResult.Volume.ID == "" {
		t.Fatalf("expected created volume, got success=%v volume=%+v err=%s", volResult.Success, volResult.Volume, volResult.ErrorMessage)
	}
	volumeID := volResult.Volume.ID

	// Best-effort cleanup: delete the volume at the end.
	defer func() {
		_, _ = client.BetaVolume.BetaDelete(volumeID)
	}()

	// 2) List and ensure the volume can be discovered by name
	listResult, err := client.BetaVolume.BetaList(&agentbay.BetaListVolumesParams{
		ImageID:    imageID,
		MaxResults: 10,
		VolumeName: volumeName,
	})
	if err != nil {
		t.Fatalf("BetaList failed: %v", err)
	}
	if !listResult.Success {
		t.Fatalf("BetaList returned success=false: %s", listResult.ErrorMessage)
	}
	found := false
	for _, v := range listResult.Volumes {
		if v != nil && v.ID == volumeID {
			found = true
			break
		}
	}
	if !found {
		t.Fatalf("expected volume %s to appear in list by name %q", volumeID, volumeName)
	}

	// 3) Create a session mounted with this volume
	params := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithBetaVolumeId(volumeID).
		WithLabels(map[string]string{
			"test-type": "beta-volume-integration",
		})

	createResult, err := createSessionWithRetry(t, client, params, 6, 10*time.Second)
	if err != nil {
		t.Fatalf("Create session failed: %v", err)
	}
	session := createResult.Session
	if session == nil {
		t.Fatalf("expected non-nil session")
	}
	defer func() { _, _ = client.Delete(session) }()

	if session.GetToken() == "" {
		t.Fatalf("expected non-empty token from create session response")
	}

	// 4) Write a file via filesystem tools and verify it exists (this should land on the mounted volume)
	if session.FileSystem == nil {
		t.Skip("Skipping test: session.FileSystem is nil")
	}
	toolsRes, err := session.ListMcpTools()
	if err != nil {
		t.Skipf("Skipping test: ListMcpTools failed: %v", err)
	}
	hasWriteFile := false
	if toolsRes != nil {
		for _, tool := range toolsRes.Tools {
			if tool.Name == "write_file" {
				hasWriteFile = true
				break
			}
		}
	}
	if !hasWriteFile {
		t.Skip("Skipping test: write_file tool is not available for this image/session (cannot write data to validate volume persistence)")
	}
	_, err = session.FileSystem.WriteFile(testFilePath, testContent, "overwrite")
	if err != nil {
		t.Fatalf("WriteFile failed: %v", err)
	}
	read1, err := session.FileSystem.ReadFile(testFilePath)
	if err != nil {
		t.Fatalf("ReadFile failed: %v", err)
	}
	if read1 == nil || !strings.Contains(read1.Content, testContent) {
		got := ""
		if read1 != nil {
			got = read1.Content
		}
		t.Fatalf("expected ReadFile content to contain %q, got: %q", testContent, got)
	}

	// 5) Delete session1, then mount the same volume in session2 and verify the file is still there
	_, _ = client.Delete(session)
	time.Sleep(20 * time.Second)

	params2 := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithBetaVolumeId(volumeID).
		WithLabels(map[string]string{
			"test-type": "beta-volume-integration-2",
		})
	createResult2, err := createSessionWithRetry(t, client, params2, 6, 10*time.Second)
	if err != nil {
		t.Fatalf("Create session2 failed: %v", err)
	}
	session2 := createResult2.Session
	if session2 == nil {
		t.Fatalf("expected non-nil session2")
	}
	defer func() { _, _ = client.Delete(session2) }()
	if session2.FileSystem == nil {
		t.Skip("Skipping test: session2.FileSystem is nil")
	}
	read2, err := session2.FileSystem.ReadFile(testFilePath)
	if err != nil {
		t.Fatalf("ReadFile(session2) failed: %v", err)
	}
	if read2 == nil || !strings.Contains(read2.Content, testContent) {
		got := ""
		if read2 != nil {
			got = read2.Content
		}
		t.Fatalf("expected ReadFile(session2) content to contain %q, got: %q", testContent, got)
	}
}

func createSessionWithRetry(
	t *testing.T,
	client *agentbay.AgentBay,
	params *agentbay.CreateSessionParams,
	maxAttempts int,
	sleep time.Duration,
) (*agentbay.SessionResult, error) {
	t.Helper()
	if maxAttempts <= 0 {
		maxAttempts = 1
	}
	var lastErr error
	for attempt := 1; attempt <= maxAttempts; attempt++ {
		res, err := client.Create(params)
		if err == nil {
			return res, nil
		}
		lastErr = err
		msg := strings.ToLower(err.Error())
		// Backend capacity transient: retry.
		if strings.Contains(msg, "no idle appinstances") || strings.Contains(msg, "please retry later") {
			time.Sleep(sleep)
			continue
		}
		return nil, err
	}
	return nil, lastErr
}
