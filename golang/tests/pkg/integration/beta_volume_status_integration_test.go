package integration_test

import (
	"fmt"
	"testing"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

func TestBetaVolumeCreateGetListIncludesStatus(t *testing.T) {
	apiKey := testutil.GetTestAPIKey(t)
	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		t.Fatalf("Error initializing AgentBay client: %v", err)
	}

	imageID := "imgc-0ab5ta4mgqs15qxjf"
	volumeName := fmt.Sprintf("beta-volume-status-it-%d", time.Now().UnixNano())

	created, err := client.BetaVolume.BetaGetByName(volumeName, imageID, true)
	if err != nil {
		t.Fatalf("BetaGetByName failed: %v", err)
	}
	if !created.Success || created.Volume == nil || created.Volume.ID == "" {
		t.Fatalf("expected created volume, got success=%v volume=%+v err=%s", created.Success, created.Volume, created.ErrorMessage)
	}
	if created.Volume.Status == "" {
		t.Fatalf("expected non-empty status from create/get response, got empty")
	}
	volumeID := created.Volume.ID

	defer func() {
		_, _ = client.BetaVolume.BetaDelete(volumeID)
	}()

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

	var listed *agentbay.Volume
	for _, v := range listResult.Volumes {
		if v != nil && v.ID == volumeID {
			listed = v
			break
		}
	}
	if listed == nil {
		t.Fatalf("expected volume %s to appear in list by name %q", volumeID, volumeName)
	}
	if listed.Status == "" {
		t.Fatalf("expected non-empty status from list response, got empty")
	}

	got, err := client.BetaVolume.BetaGetByID(volumeID, imageID)
	if err != nil {
		t.Fatalf("BetaGetByID failed: %v", err)
	}
	if !got.Success || got.Volume == nil {
		t.Fatalf("expected get by id success, got success=%v volume=%+v err=%s", got.Success, got.Volume, got.ErrorMessage)
	}
	if got.Volume.Status == "" {
		t.Fatalf("expected non-empty status from get by id response, got empty")
	}
}
