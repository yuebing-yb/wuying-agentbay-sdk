package main

import (
	"fmt"
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

// This example demonstrates the Skills feature:
// 1. Get skills metadata without starting a sandbox
// 2. Get metadata filtered by group IDs
// 3. Create session with skills loaded
// 4. Verify skills in sandbox
func main() {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		fmt.Println("Warning: Set AGENTBAY_API_KEY environment variable.")
		return
	}

	agentBay, err := agentbay.NewAgentBay(apiKey)
	if err != nil {
		fmt.Printf("Error initializing AgentBay client: %v\n", err)
		os.Exit(1)
	}

	// 1. Get skills metadata (no sandbox needed)
	fmt.Println("Getting skills metadata...")
	metadata, err := agentBay.BetaSkills.GetMetadata()
	if err != nil {
		fmt.Printf("GetMetadata failed: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Skills root path: %s\n", metadata.SkillsRootPath)
	fmt.Printf("Available skills: %d\n", len(metadata.Skills))
	for _, skill := range metadata.Skills {
		fmt.Printf("  - %s: %s\n", skill.Name, skill.Description)
	}

	// 2. Get metadata filtered by skill names
	fmt.Println("\nGetting skills metadata filtered by skill names...")
	filtered, err := agentBay.BetaSkills.GetMetadata(agentbay.GetMetadataOptions{
		SkillNames: []string{"5kvAvffm"},
	})
	if err != nil {
		fmt.Printf("GetMetadata with skillNames failed: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Filtered skills: %d\n", len(filtered.Skills))

	// 3. Create session with skills loaded
	fmt.Println("\nCreating session with skills...")
	params := agentbay.NewCreateSessionParams().WithLoadSkills(true)
	result, err := agentBay.Create(params)
	if err != nil {
		fmt.Printf("Create failed: %v\n", err)
		os.Exit(1)
	}
	if !result.Success || result.Session == nil {
		fmt.Printf("Session creation failed: %s\n", result.ErrorMessage)
		os.Exit(1)
	}

	session := result.Session
	defer func() {
		_, _ = agentBay.Delete(session)
		fmt.Println("\nSession deleted.")
	}()

	fmt.Printf("Session created: %s\n", session.SessionID)

	// 4. Get skills metadata and verify skills in sandbox
	metaOpts := agentbay.GetMetadataOptions{ImageID: session.ImageId}
	sessionMetadata, err := agentBay.BetaSkills.GetMetadata(metaOpts)
	if err != nil {
		fmt.Printf("GetMetadata for session failed: %v\n", err)
	} else {
		fmt.Printf("Skills root path: %s\n", sessionMetadata.SkillsRootPath)
		fmt.Printf("Skills count: %d\n", len(sessionMetadata.Skills))
		if sessionMetadata.SkillsRootPath != "" {
			cmdResult, err := session.Command.ExecuteCommand("ls " + sessionMetadata.SkillsRootPath)
			if err != nil {
				fmt.Printf("ExecuteCommand failed: %v\n", err)
			} else {
				fmt.Printf("\nSkills directory contents:\n%s\n", cmdResult.Output)
			}
		}
	}
}
