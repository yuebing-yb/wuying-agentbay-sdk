package main

import (
	"fmt"
	"os"
	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// This example demonstrates the beta volume (data disk) flow:
// - create (via GetVolume allowCreate=true)
// - mount to session at creation time
// - cleanup session and volume
func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("AGENTBAY_API_KEY is not set")
		os.Exit(1)
	}

	client, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	imageID := "imgc-0ab5ta4mgqs15qxjf"
	volumeName := fmt.Sprintf("beta-volume-example-%d", time.Now().UnixNano())

	volRes, err := client.BetaVolume.BetaGetByName(volumeName, imageID, true)
	if err != nil {
		fmt.Printf("BetaGetByName failed: %v\n", err)
		os.Exit(1)
	}
	if !volRes.Success || volRes.Volume == nil || volRes.Volume.ID == "" {
		fmt.Printf("Create/get volume failed: %s\n", volRes.ErrorMessage)
		os.Exit(1)
	}
	volumeID := volRes.Volume.ID
	fmt.Printf("Volume ready: %s\n", volumeID)

	defer func() {
		_, _ = client.BetaVolume.BetaDelete(volumeID)
	}()

	params := agentbay.NewCreateSessionParams().
		WithImageId(imageID).
		WithVolumeId(volumeID).
		WithLabels(map[string]string{"example": "beta-volume-mount"})

	createRes, err := client.Create(params)
	if err != nil {
		fmt.Printf("Create session failed: %v\n", err)
		os.Exit(1)
	}
	session := createRes.Session
	fmt.Printf("Session created: %s\n", session.SessionID)

	_, _ = client.Delete(session)
	fmt.Println("Session deleted, volume preserved (beta).")
}
