package agentbay_test

import (
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"testing"
	"time"

	agentbay "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/git"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/agentbay/testutil"
)

const (
	TestGitPathPrefix = "/tmp/test-git-integration"
	TestGitImageID    = "code-space-debian-12"
	TestGitCloneURL   = "https://github.com/DingTalk-Real-AI/dingtalk-openclaw-connector.git"
)

func TestGitIntegration_BasicWorkflow(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	// Setup session with cleanup
	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Generate unique test path
	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-basic-%d", TestGitPathPrefix, timestamp)

	// Initialize git repository with explicit initial branch
	fmt.Println("Initializing git repository...")
	initResult, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Failed to initialize git repository: %v", err)
	}
	t.Logf("Git repository initialized at: %s", initResult.Path)

	// Configure user
	fmt.Println("Configuring git user...")
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("Failed to configure git user: %v", err)
	}
	t.Log("Git user configured successfully")

	// Create a test file using Command
	fmt.Println("Creating test file...")
	testFilePath := filepath.Join(testRepoPath, "test.txt")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'Hello, Git!' > %s", testFilePath))
	if err != nil {
		t.Fatalf("Failed to create test file: %v", err)
	}
	t.Log("Test file created successfully")

	// Check status - should show untracked file
	fmt.Println("Checking git status (untracked)...")
	statusResult, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to get git status: %v", err)
	}
	t.Logf("Status result: currentBranch=%s, isClean=%v, totalChanges=%d",
		statusResult.CurrentBranch, statusResult.IsClean(), statusResult.TotalCount())

	// Verify initial branch is "main" as specified by WithInitBranch
	if statusResult.CurrentBranch != "main" {
		t.Errorf("Expected current branch to be 'main', got '%s'", statusResult.CurrentBranch)
	}

	if statusResult.IsClean() {
		t.Errorf("Expected repository to have changes, but it is clean")
	}
	if statusResult.UntrackedCount() == 0 {
		t.Errorf("Expected untracked files, but found none")
	}

	// Add file to staging
	fmt.Println("Adding file to staging area...")
	err = session.Git.Add(testRepoPath, git.WithAddPaths([]string{testFilePath}))
	if err != nil {
		t.Fatalf("Failed to add file: %v", err)
	}
	t.Log("File added to staging area")

	// Check status - should show staged file
	fmt.Println("Checking git status (staged)...")
	statusResult, err = session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to get git status: %v", err)
	}
	t.Logf("Status result: stagedCount=%d", statusResult.StagedCount())

	if statusResult.StagedCount() == 0 {
		t.Errorf("Expected staged files, but found none")
	}

	// Commit the changes
	fmt.Println("Committing changes...")
	commitResult, err := session.Git.Commit(testRepoPath, "Initial commit")
	if err != nil {
		t.Fatalf("Failed to commit: %v", err)
	}
	t.Logf("Commit successful with CommitHash: %s", commitResult.CommitHash)

	// Check log
	fmt.Println("Checking git log...")
	logResult, err := session.Git.Log(testRepoPath, git.WithLogMaxCount(1))
	if err != nil {
		t.Fatalf("Failed to get git log: %v", err)
	}
	t.Logf("Log result: entryCount=%d", len(logResult.Entries))

	if len(logResult.Entries) == 0 {
		t.Errorf("Expected at least one log entry, but found none")
	} else {
		entry := logResult.Entries[0]
		if entry.Message != "Initial commit" {
			t.Errorf("Expected commit message 'Initial commit', got '%s'", entry.Message)
		}
		if entry.AuthorName != "Test User" {
			t.Errorf("Expected author 'Test User', got '%s'", entry.AuthorName)
		}
	}

	// Check status - should be clean
	fmt.Println("Checking git status (clean)...")
	statusResult, err = session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to get git status: %v", err)
	}
	t.Logf("Final status: isClean=%v", statusResult.IsClean())

	if !statusResult.IsClean() {
		t.Errorf("Expected repository to be clean, but it has changes")
	}

	t.Log("Basic workflow test completed successfully")
}

func TestGitIntegration_BranchOperations(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	// Setup session with cleanup
	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Generate unique test path
	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-branch-%d", TestGitPathPrefix, timestamp)

	// Initialize git repository and make initial commit
	fmt.Println("Initializing git repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Failed to initialize git repository: %v", err)
	}

	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("Failed to configure git user: %v", err)
	}

	// Create initial commit
	testFilePath := filepath.Join(testRepoPath, "initial.txt")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'Initial content' > %s", testFilePath))
	if err != nil {
		t.Fatalf("Failed to create initial file: %v", err)
	}

	err = session.Git.Add(testRepoPath, git.WithAddPaths([]string{testFilePath}))
	if err != nil {
		t.Fatalf("Failed to add initial file: %v", err)
	}

	_, err = session.Git.Commit(testRepoPath, "Initial commit")
	if err != nil {
		t.Fatalf("Failed to make initial commit: %v", err)
	}
	t.Log("Initial commit created successfully")

	// List branches - should show main only
	fmt.Println("Listing branches (before creating new branch)...")
	branchListResult, err := session.Git.ListBranches(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to list branches: %v", err)
	}
	t.Logf("Branches: count=%d, current=%s", len(branchListResult.Branches), branchListResult.Current)

	if len(branchListResult.Branches) != 1 {
		t.Errorf("Expected 1 branch, got %d", len(branchListResult.Branches))
	}
	if branchListResult.Current != "main" {
		t.Errorf("Expected current branch 'main', got '%s'", branchListResult.Current)
	}

	// Create and switch to new branch
	fmt.Println("Creating and switching to new branch 'feature-test'...")
	err = session.Git.CreateBranch(testRepoPath, "feature-test")
	if err != nil {
		t.Fatalf("Failed to create branch: %v", err)
	}
	t.Log("Branch 'feature-test' created and switched to successfully")

	// Verify we're on the new branch
	fmt.Println("Verifying current branch...")
	branchListResult, err = session.Git.ListBranches(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to list branches: %v", err)
	}
	t.Logf("Current branch: %s", branchListResult.Current)

	if branchListResult.Current != "feature-test" {
		t.Errorf("Expected current branch 'feature-test', got '%s'", branchListResult.Current)
	}

	// List branches - should show both main and feature-test
	fmt.Println("Listing branches (after creating new branch)...")
	if len(branchListResult.Branches) != 2 {
		t.Errorf("Expected 2 branches, got %d", len(branchListResult.Branches))
	}

	// Switch back to main
	fmt.Println("Switching back to main branch...")
	err = session.Git.CheckoutBranch(testRepoPath, "main")
	if err != nil {
		t.Fatalf("Failed to checkout main branch: %v", err)
	}
	t.Log("Switched back to main branch successfully")

	// Verify we're on main
	branchListResult, err = session.Git.ListBranches(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to list branches: %v", err)
	}
	if branchListResult.Current != "main" {
		t.Errorf("Expected current branch 'main', got '%s'", branchListResult.Current)
	}

	// Delete the feature branch
	fmt.Println("Deleting branch 'feature-test'...")
	err = session.Git.DeleteBranch(testRepoPath, "feature-test")
	if err != nil {
		t.Fatalf("Failed to delete branch: %v", err)
	}
	t.Log("Branch 'feature-test' deleted successfully")

	// Verify only main remains
	branchListResult, err = session.Git.ListBranches(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to list branches: %v", err)
	}
	if len(branchListResult.Branches) != 1 {
		t.Errorf("Expected 1 branch after deletion, got %d", len(branchListResult.Branches))
	}

	t.Log("Branch operations test completed successfully")
}

func TestGitIntegration_InitBare(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	// Setup session with cleanup
	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Generate unique test path
	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-bare-%d", TestGitPathPrefix, timestamp)

	// Initialize bare repository
	fmt.Println("Initializing bare git repository...")
	initResult, err := session.Git.Init(testRepoPath, git.WithInitBare())
	if err != nil {
		t.Fatalf("Failed to initialize bare git repository: %v", err)
	}
	t.Logf("Bare repository initialized at: %s", initResult.Path)

	// Verify it's a bare repository by checking the directory structure
	fmt.Println("Verifying bare repository structure...")
	cmdResult, err := session.Command.ExecuteCommand(fmt.Sprintf("ls -la %s", testRepoPath))
	if err != nil {
		t.Fatalf("Failed to list directory: %v", err)
	}

	output := cmdResult.Output
	t.Logf("Directory listing: %s", output)

	// Bare repository should have git-specific files/directories in the root, not in .git subdirectory
	if !strings.Contains(output, "HEAD") && !strings.Contains(output, "refs") && !strings.Contains(output, "objects") {
		t.Errorf("Expected bare repository to contain git files (HEAD, refs, objects), but output was: %s", output)
	}

	// Verify there's no .git subdirectory
	cmdResult, err = session.Command.ExecuteCommand(fmt.Sprintf("test -d %s/.git && echo 'exists' || echo 'not exists'", testRepoPath))
	if err != nil {
		t.Fatalf("Failed to check for .git directory: %v", err)
	}

	trimmedOutput := strings.TrimSpace(cmdResult.Output)
	if trimmedOutput == "exists" {
		t.Errorf("Expected bare repository to NOT have .git subdirectory, but it exists")
	}

	t.Log("Bare repository test completed successfully")
}

func TestGitIntegration_CommitWithAuthor(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	// Setup session with cleanup
	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Generate unique test path
	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-author-%d", TestGitPathPrefix, timestamp)

	// Initialize git repository
	fmt.Println("Initializing git repository...")
	_, err := session.Git.Init(testRepoPath)
	if err != nil {
		t.Fatalf("Failed to initialize git repository: %v", err)
	}

	err = session.Git.ConfigureUser(testRepoPath, "Default User", "default@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("Failed to configure git user: %v", err)
	}

	// Create a test file
	testFilePath := filepath.Join(testRepoPath, "test.txt")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'Test content' > %s", testFilePath))
	if err != nil {
		t.Fatalf("Failed to create test file: %v", err)
	}

	err = session.Git.Add(testRepoPath, git.WithAddPaths([]string{testFilePath}))
	if err != nil {
		t.Fatalf("Failed to add file: %v", err)
	}

	// Commit with custom author
	fmt.Println("Committing with custom author...")
	customAuthorName := "Custom Author"
	customAuthorEmail := "custom@example.com"
	commitResult, err := session.Git.Commit(
		testRepoPath,
		"Commit with custom author",
		git.WithCommitAuthorName(customAuthorName),
		git.WithCommitAuthorEmail(customAuthorEmail),
	)
	if err != nil {
		t.Fatalf("Failed to commit: %v", err)
	}
	t.Logf("Commit successful with CommitHash: %s", commitResult.CommitHash)

	// Verify author information in log
	fmt.Println("Verifying author information in log...")
	logResult, err := session.Git.Log(testRepoPath, git.WithLogMaxCount(1))
	if err != nil {
		t.Fatalf("Failed to get git log: %v", err)
	}

	if len(logResult.Entries) == 0 {
		t.Fatalf("Expected at least one log entry, but found none")
	}

	entry := logResult.Entries[0]
	t.Logf("Log entry: AuthorName=%s, AuthorEmail=%s", entry.AuthorName, entry.AuthorEmail)

	if entry.AuthorName != customAuthorName {
		t.Errorf("Expected author name '%s', got '%s'", customAuthorName, entry.AuthorName)
	}
	if entry.AuthorEmail != customAuthorEmail {
		t.Errorf("Expected author email '%s', got '%s'", customAuthorEmail, entry.AuthorEmail)
	}

	t.Log("Commit with author test completed successfully")
}

// helper: initRepoWithCommit initializes a git repo and makes a single commit.
// Returns the repo path (already configured with local user).
func gitFindFile(status *git.GitStatusResult, path string) *git.GitFileStatus {
	for i := range status.Files {
		if status.Files[i].Path == path {
			return &status.Files[i]
		}
	}
	return nil
}

func TestGitIntegration_RemoteOperations(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-remote-%d", TestGitPathPrefix, timestamp)

	// --- Setup: init repo + initial commit ---
	fmt.Println("[Remote] Initializing repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'init' > %s/init.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Create file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	_, err = session.Git.Commit(testRepoPath, "initial commit")
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// --- Step 1: RemoteAdd ---
	remoteURL := "https://github.com/example/test-remote.git"
	fmt.Println("[Remote] Adding remote 'origin'...")
	err = session.Git.RemoteAdd(testRepoPath, "origin", remoteURL)
	if err != nil {
		t.Fatalf("RemoteAdd failed: %v", err)
	}

	// --- Step 2: RemoteGet → should equal remoteURL ---
	fmt.Println("[Remote] Getting remote URL...")
	gotURL, err := session.Git.RemoteGet(testRepoPath, "origin")
	if err != nil {
		t.Fatalf("RemoteGet failed: %v", err)
	}
	if gotURL != remoteURL {
		t.Errorf("Expected remote URL '%s', got '%s'", remoteURL, gotURL)
	}
	t.Logf("[Remote] origin URL = %s", gotURL)

	// --- Step 3: RemoteAdd overwrite → new URL ---
	newRemoteURL := "https://github.com/example/test-remote-v2.git"
	fmt.Println("[Remote] Overwriting remote 'origin'...")
	err = session.Git.RemoteAdd(testRepoPath, "origin", newRemoteURL, git.WithRemoteAddOverwrite())
	if err != nil {
		t.Fatalf("RemoteAdd overwrite failed: %v", err)
	}
	gotURL2, err := session.Git.RemoteGet(testRepoPath, "origin")
	if err != nil {
		t.Fatalf("RemoteGet after overwrite failed: %v", err)
	}
	if gotURL2 != newRemoteURL {
		t.Errorf("Expected new remote URL '%s', got '%s'", newRemoteURL, gotURL2)
	}
	t.Logf("[Remote] origin URL after overwrite = %s", gotURL2)

	// --- Step 4: RemoteGet nonexistent → "" without error ---
	fmt.Println("[Remote] Getting nonexistent remote...")
	missingURL, err := session.Git.RemoteGet(testRepoPath, "nonexistent")
	if err != nil {
		t.Fatalf("RemoteGet nonexistent should not return error, got: %v", err)
	}
	if missingURL != "" {
		t.Errorf("Expected empty string for nonexistent remote, got '%s'", missingURL)
	}
	t.Log("[Remote] Nonexistent remote returns empty string as expected")

	t.Log("Remote operations test completed successfully")
}

func TestGitIntegration_ResetAndRestore(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-resetrestore-%d", TestGitPathPrefix, timestamp)

	// --- Setup: init repo + configure user ---
	fmt.Println("[ResetRestore] Initializing repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}

	// Initial commit with reset-test.txt
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'initial content' > %s/reset-test.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Create file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	_, err = session.Git.Commit(testRepoPath, "initial: add reset-test.txt")
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// --- Step 12: reset --mixed ---
	// Modify file and stage it, then reset --mixed (staged → worktree)
	fmt.Println("[ResetRestore] Testing reset --mixed...")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'modified' >> %s/reset-test.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Modify file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath, git.WithAddPaths([]string{"reset-test.txt"}))
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	statusBefore, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	stageBefore := findFile(statusBefore, "reset-test.txt")
	if stageBefore == nil || stageBefore.IndexStatus != "M" {
		t.Fatalf("Expected reset-test.txt to be staged (M), got %+v", stageBefore)
	}

	err = session.Git.Reset(testRepoPath, git.WithResetMixed())
	if err != nil {
		t.Fatalf("Reset --mixed failed: %v", err)
	}
	statusAfter, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status after reset failed: %v", err)
	}
	stageAfter := findFile(statusAfter, "reset-test.txt")
	if stageAfter == nil || stageAfter.IndexStatus != " " || stageAfter.WorkTreeStatus != "M" {
		t.Errorf("After --mixed reset: expected index=' ' worktree='M', got %+v", stageAfter)
	}
	t.Log("[ResetRestore] reset --mixed OK")

	// --- Step 13: reset --hard ---
	fmt.Println("[ResetRestore] Testing reset --hard...")
	err = session.Git.Reset(testRepoPath, git.WithResetHard())
	if err != nil {
		t.Fatalf("Reset --hard failed: %v", err)
	}
	statusClean, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	if !statusClean.IsClean() {
		t.Errorf("Expected clean repo after --hard reset, got %+v", statusClean.Files)
	}
	t.Log("[ResetRestore] reset --hard OK")

	// --- Step 14: restore worktree ---
	fmt.Println("[ResetRestore] Testing restore worktree...")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'restore test' >> %s/reset-test.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Modify file failed: %v", err)
	}
	s14, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	f14 := findFile(s14, "reset-test.txt")
	if f14 == nil || f14.WorkTreeStatus != "M" {
		t.Fatalf("Expected reset-test.txt modified in worktree, got %+v", f14)
	}

	err = session.Git.Restore(testRepoPath, []string{"reset-test.txt"})
	if err != nil {
		t.Fatalf("Restore worktree failed: %v", err)
	}
	s14after, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status after restore failed: %v", err)
	}
	if !s14after.IsClean() {
		t.Errorf("Expected clean repo after restore worktree, got %+v", s14after.Files)
	}
	t.Log("[ResetRestore] restore worktree OK")

	// --- Step 15: restore --staged ---
	fmt.Println("[ResetRestore] Testing restore --staged...")
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'staged restore' >> %s/reset-test.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Modify file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath, git.WithAddPaths([]string{"reset-test.txt"}))
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	s15, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	f15 := findFile(s15, "reset-test.txt")
	if f15 == nil || f15.IndexStatus != "M" {
		t.Fatalf("Expected reset-test.txt staged, got %+v", f15)
	}

	err = session.Git.Restore(testRepoPath, []string{"reset-test.txt"}, git.WithRestoreStaged())
	if err != nil {
		t.Fatalf("Restore --staged failed: %v", err)
	}
	s15after, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status after restore --staged failed: %v", err)
	}
	f15after := findFile(s15after, "reset-test.txt")
	if f15after == nil || f15after.IndexStatus != " " || f15after.WorkTreeStatus != "M" {
		t.Errorf("After restore --staged: expected index=' ' worktree='M', got %+v", f15after)
	}
	// Cleanup: hard reset
	_ = session.Git.Reset(testRepoPath, git.WithResetHard())
	t.Log("[ResetRestore] restore --staged OK")

	// --- Step 18: reset --paths ---
	// Add two files, then reset only one of them
	fmt.Println("[ResetRestore] Testing reset --paths...")
	_, err = session.Command.ExecuteCommand(
		fmt.Sprintf("echo 'a' > %s/file-a.txt && echo 'b' > %s/file-b.txt", testRepoPath, testRepoPath))
	if err != nil {
		t.Fatalf("Create files failed: %v", err)
	}
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add all failed: %v", err)
	}
	s18, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	fa := findFile(s18, "file-a.txt")
	fb := findFile(s18, "file-b.txt")
	if fa == nil || fa.IndexStatus != "A" {
		t.Fatalf("Expected file-a.txt staged as A, got %+v", fa)
	}
	if fb == nil || fb.IndexStatus != "A" {
		t.Fatalf("Expected file-b.txt staged as A, got %+v", fb)
	}

	// Reset only file-a.txt
	err = session.Git.Reset(testRepoPath, git.WithResetPaths([]string{"file-a.txt"}))
	if err != nil {
		t.Fatalf("Reset --paths failed: %v", err)
	}
	s18after, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status after reset --paths failed: %v", err)
	}
	fa2 := findFile(s18after, "file-a.txt")
	fb2 := findFile(s18after, "file-b.txt")
	// file-a.txt should be unstaged (untracked or worktree-only)
	if fa2 != nil && fa2.IndexStatus == "A" {
		t.Errorf("Expected file-a.txt to be unstaged after reset --paths, got %+v", fa2)
	}
	// file-b.txt should still be staged
	if fb2 == nil || fb2.IndexStatus != "A" {
		t.Errorf("Expected file-b.txt to remain staged, got %+v", fb2)
	}
	// Cleanup
	_ = session.Git.Reset(testRepoPath, git.WithResetMixed())
	_, _ = session.Command.ExecuteCommand(fmt.Sprintf("rm -f %s/file-a.txt %s/file-b.txt", testRepoPath, testRepoPath))
	t.Log("[ResetRestore] reset --paths OK")

	t.Log("Reset and Restore test completed successfully")
}

// findFile is a helper that looks up a file by path in GitStatusResult.Files.
func findFile(status *git.GitStatusResult, path string) *git.GitFileStatus {
	return gitFindFile(status, path)
}

func TestGitIntegration_ConfigOperations(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-config-%d", TestGitPathPrefix, timestamp)

	// --- Setup: init repo ---
	fmt.Println("[Config] Initializing repository...")
	_, err := session.Git.Init(testRepoPath)
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}

	// --- Step 16: ConfigureUser (local scope) + GetConfig ---
	fmt.Println("[Config] Configuring user (local scope)...")
	err = session.Git.ConfigureUser(testRepoPath, "Test Bot", "testbot@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}

	name, err := session.Git.GetConfig(testRepoPath, "user.name", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("GetConfig user.name failed: %v", err)
	}
	if name != "Test Bot" {
		t.Errorf("Expected user.name 'Test Bot', got '%s'", name)
	}
	t.Logf("[Config] user.name = %s", name)

	email, err := session.Git.GetConfig(testRepoPath, "user.email", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("GetConfig user.email failed: %v", err)
	}
	if email != "testbot@example.com" {
		t.Errorf("Expected user.email 'testbot@example.com', got '%s'", email)
	}
	t.Logf("[Config] user.email = %s", email)

	// --- Step 17: SetConfig + GetConfig ---
	fmt.Println("[Config] Setting core.autocrlf = false (local scope)...")
	err = session.Git.SetConfig(testRepoPath, "core.autocrlf", "false", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("SetConfig failed: %v", err)
	}

	val, err := session.Git.GetConfig(testRepoPath, "core.autocrlf", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("GetConfig core.autocrlf failed: %v", err)
	}
	if val != "false" {
		t.Errorf("Expected core.autocrlf 'false', got '%s'", val)
	}
	t.Logf("[Config] core.autocrlf = %s", val)

	// --- Step 17b: GetConfig for nonexistent key → "" without error ---
	fmt.Println("[Config] Getting nonexistent config key...")
	missing, err := session.Git.GetConfig(testRepoPath, "nonexistent.key", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("GetConfig nonexistent.key should not error, got: %v", err)
	}
	if missing != "" {
		t.Errorf("Expected empty string for nonexistent config key, got '%s'", missing)
	}
	t.Log("[Config] Nonexistent config key returns empty string as expected")

	t.Log("Config operations test completed successfully")
}

func TestGitIntegration_AddDefaultStageAll(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-adddefault-%d", TestGitPathPrefix, timestamp)

	// --- Setup: init repo + configure user ---
	fmt.Println("[AddDefault] Initializing repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}

	// Create two files
	fmt.Println("[AddDefault] Creating two files...")
	_, err = session.Command.ExecuteCommand(
		fmt.Sprintf("echo 'file a' > %s/file-a.txt && echo 'file b' > %s/file-b.txt", testRepoPath, testRepoPath))
	if err != nil {
		t.Fatalf("Create files failed: %v", err)
	}

	// Add with no options (default: stage all = -A)
	fmt.Println("[AddDefault] Calling Add() with no options (should stage all)...")
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add() with no options failed: %v", err)
	}

	// Verify both files are staged
	statusResult, err := session.Git.Status(testRepoPath)
	if err != nil {
		t.Fatalf("Status failed: %v", err)
	}
	t.Logf("[AddDefault] staged count = %d", statusResult.StagedCount())

	var fileAStaged, fileBStaged bool
	for _, f := range statusResult.Files {
		if f.Path == "file-a.txt" && f.IndexStatus == "A" {
			fileAStaged = true
		}
		if f.Path == "file-b.txt" && f.IndexStatus == "A" {
			fileBStaged = true
		}
	}
	if !fileAStaged {
		t.Errorf("Expected file-a.txt to be staged (A), but it was not")
	}
	if !fileBStaged {
		t.Errorf("Expected file-b.txt to be staged (A), but it was not")
	}

	t.Log("Add default stage-all test completed successfully")
}

func TestGitIntegration_Clone(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Clone with depth=1 for speed
	fmt.Printf("[Clone] Cloning %s (depth=1)...\n", TestGitCloneURL)
	cloneResult, err := session.Git.Clone(
		TestGitCloneURL,
		git.WithCloneDepth(1),
		git.WithCloneTimeout(600000),
	)
	if err != nil {
		// Tolerate network-related errors (TLS, timeout, curl, etc.)
		networkKeywords := []string{
			"GnuTLS", "TLS", "unable to access", "timed out", "timeout",
			"RPC", "HTTP2", "curl", "framing layer", "flush", "SSL",
		}
		errMsg := err.Error()
		for _, kw := range networkKeywords {
			if strings.Contains(errMsg, kw) {
				t.Skipf("[Clone] Skipping: network error detected: %v", err)
				return
			}
		}
		t.Fatalf("Clone failed (non-network error): %v", err)
	}

	expectedPath := "dingtalk-openclaw-connector"
	if cloneResult.Path != expectedPath {
		t.Errorf("Expected clone path '%s', got '%s'", expectedPath, cloneResult.Path)
	}
	t.Logf("[Clone] Cloned to: %s", cloneResult.Path)

	// Verify repository is clean
	statusResult, err := session.Git.Status(cloneResult.Path)
	if err != nil {
		t.Fatalf("Status after clone failed: %v", err)
	}
	if !statusResult.IsClean() {
		t.Errorf("Expected cloned repo to be clean, got %+v", statusResult.Files)
	}

	// Verify at least one commit in log
	logResult, err := session.Git.Log(cloneResult.Path, git.WithLogMaxCount(3))
	if err != nil {
		t.Fatalf("Log after clone failed: %v", err)
	}
	if len(logResult.Entries) == 0 {
		t.Errorf("Expected at least one log entry after clone, got none")
	} else {
		t.Logf("[Clone] Latest commit: %s | %s", logResult.Entries[0].ShortHash, logResult.Entries[0].Message)
	}

	t.Log("Clone test completed successfully")
}

func TestGitIntegration_CommitAllowEmpty(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-allowempty-%d", TestGitPathPrefix, timestamp)

	// Setup: init repo + configure user + initial commit
	fmt.Println("[AllowEmpty] Initializing repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'init' > %s/init.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Create file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	_, err = session.Git.Commit(testRepoPath, "initial commit")
	if err != nil {
		t.Fatalf("Initial commit failed: %v", err)
	}

	// Commit with --allow-empty (no staged changes)
	fmt.Println("[AllowEmpty] Creating allow-empty commit...")
	commitResult, err := session.Git.Commit(testRepoPath, "Empty commit", git.WithCommitAllowEmpty())
	if err != nil {
		t.Fatalf("Allow-empty commit failed: %v", err)
	}
	if commitResult.CommitHash == "" {
		t.Errorf("Expected non-empty commit hash for allow-empty commit")
	}
	t.Logf("[AllowEmpty] Commit hash: %s", commitResult.CommitHash)

	// Verify the empty commit appears in log
	logResult, err := session.Git.Log(testRepoPath, git.WithLogMaxCount(1))
	if err != nil {
		t.Fatalf("Log failed: %v", err)
	}
	if len(logResult.Entries) == 0 {
		t.Fatalf("Expected at least one log entry")
	}
	if logResult.Entries[0].Message != "Empty commit" {
		t.Errorf("Expected commit message 'Empty commit', got '%s'", logResult.Entries[0].Message)
	}

	t.Log("Allow-empty commit test completed successfully")
}

func TestGitIntegration_ErrorNotARepo(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	// Create a non-git directory
	timestamp := time.Now().UnixNano()
	nonRepoPath := fmt.Sprintf("/tmp/not-a-repo-%d", timestamp)
	_, err := session.Command.ExecuteCommand(fmt.Sprintf("mkdir -p %s", nonRepoPath))
	if err != nil {
		t.Fatalf("Failed to create directory: %v", err)
	}

	// Attempt to get status on a non-git directory → should return GitNotARepoError
	fmt.Println("[ErrorNotARepo] Attempting status on non-git directory...")
	_, err = session.Git.Status(nonRepoPath)
	if err == nil {
		t.Fatalf("Expected error for status on non-git directory, got nil")
	}

	// Verify the error is GitNotARepoError
	var notARepoErr *git.GitNotARepoError
	if errors.As(err, &notARepoErr) {
		t.Logf("[ErrorNotARepo] Correctly got GitNotARepoError: %v", err)
	} else {
		// Accept any error that contains "not a git repository" in the message
		if strings.Contains(err.Error(), "not a git repository") {
			t.Logf("[ErrorNotARepo] Got error with expected message: %v", err)
		} else {
			t.Errorf("Expected GitNotARepoError or error containing 'not a git repository', got: %T: %v", err, err)
		}
	}

	t.Log("Error not-a-repo test completed successfully")
}

func TestGitIntegration_ErrorEmptyCommit(t *testing.T) {
	apiKey := os.Getenv("AGENTBAY_API_KEY")
	if apiKey == "" {
		t.Skip("AGENTBAY_API_KEY not set, skipping integration test")
	}

	sessionParams := agentbay.NewCreateSessionParams().WithImageId(TestGitImageID)
	session, cleanup := testutil.SetupAndCleanup(t, sessionParams)
	defer cleanup()

	timestamp := time.Now().UnixNano()
	testRepoPath := fmt.Sprintf("%s-emptycommit-%d", TestGitPathPrefix, timestamp)

	// Setup: init repo + configure user + initial commit
	fmt.Println("[ErrorEmptyCommit] Initializing repository...")
	_, err := session.Git.Init(testRepoPath, git.WithInitBranch("main"))
	if err != nil {
		t.Fatalf("Init failed: %v", err)
	}
	err = session.Git.ConfigureUser(testRepoPath, "Test User", "test@example.com", git.WithConfigLocal())
	if err != nil {
		t.Fatalf("ConfigureUser failed: %v", err)
	}
	_, err = session.Command.ExecuteCommand(fmt.Sprintf("echo 'init' > %s/init.txt", testRepoPath))
	if err != nil {
		t.Fatalf("Create file failed: %v", err)
	}
	err = session.Git.Add(testRepoPath)
	if err != nil {
		t.Fatalf("Add failed: %v", err)
	}
	_, err = session.Git.Commit(testRepoPath, "initial commit")
	if err != nil {
		t.Fatalf("Initial commit failed: %v", err)
	}

	// Attempt to commit with no staged changes and no --allow-empty → should fail
	fmt.Println("[ErrorEmptyCommit] Attempting commit with no staged changes...")
	_, err = session.Git.Commit(testRepoPath, "This should fail")
	if err == nil {
		t.Fatalf("Expected error for commit with no staged changes, got nil")
	}

	// Verify it's a GitError (not a more specific subtype like GitAuthError)
	var gitErr *git.GitError
	if errors.As(err, &gitErr) {
		t.Logf("[ErrorEmptyCommit] Correctly got GitError: %v", err)
	} else {
		t.Errorf("Expected GitError, got: %T: %v", err, err)
	}

	t.Log("Error empty commit test completed successfully")
}
