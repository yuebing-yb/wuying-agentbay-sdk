package git

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// ==================== shellEscape Tests ====================

func TestShellEscape_Simple(t *testing.T) {
	result := shellEscape("hello")
	assert.Equal(t, "'hello'", result)
}

func TestShellEscape_WithSingleQuote(t *testing.T) {
	result := shellEscape("it's")
	assert.Equal(t, "'it'\\''s'", result)
}

func TestShellEscape_WithSpaces(t *testing.T) {
	result := shellEscape("hello world")
	assert.Equal(t, "'hello world'", result)
}

func TestShellEscape_Empty(t *testing.T) {
	result := shellEscape("")
	assert.Equal(t, "''", result)
}

// ==================== buildGitCommand Tests ====================

func TestBuildGitCommand_NoRepoPath(t *testing.T) {
	result := buildGitCommand([]string{"status", "--porcelain=1"}, "")
	assert.Equal(t, "git 'status' '--porcelain=1'", result)
}

func TestBuildGitCommand_WithRepoPath(t *testing.T) {
	result := buildGitCommand([]string{"status"}, "/tmp/repo")
	assert.Equal(t, "git -C '/tmp/repo' 'status'", result)
}

func TestBuildGitCommand_WithSpecialChars(t *testing.T) {
	result := buildGitCommand([]string{"commit", "-m", "it's a test"}, "/tmp/my repo")
	assert.Equal(t, "git -C '/tmp/my repo' 'commit' '-m' 'it'\\''s a test'", result)
}

// ==================== deriveRepoDirFromURL Tests ====================

func TestDeriveRepoDirFromURL_HTTPS(t *testing.T) {
	result := deriveRepoDirFromURL("https://github.com/user/my-repo")
	assert.Equal(t, "my-repo", result)
}

func TestDeriveRepoDirFromURL_WithGitSuffix(t *testing.T) {
	result := deriveRepoDirFromURL("https://github.com/user/my-repo.git")
	assert.Equal(t, "my-repo", result)
}

func TestDeriveRepoDirFromURL_WithTrailingSlash(t *testing.T) {
	result := deriveRepoDirFromURL("https://github.com/user/my-repo/")
	assert.Equal(t, "my-repo", result)
}

func TestDeriveRepoDirFromURL_URLEncoded(t *testing.T) {
	result := deriveRepoDirFromURL("https://github.com/user/my%20repo.git")
	assert.Equal(t, "my repo", result)
}

// ==================== deriveStatus Tests ====================

func TestDeriveStatus_Untracked(t *testing.T) {
	assert.Equal(t, "untracked", deriveStatus("?", "?"))
}

func TestDeriveStatus_Added(t *testing.T) {
	assert.Equal(t, "added", deriveStatus("A", " "))
}

func TestDeriveStatus_Modified_Index(t *testing.T) {
	assert.Equal(t, "modified", deriveStatus("M", " "))
}

func TestDeriveStatus_Modified_Worktree(t *testing.T) {
	assert.Equal(t, "modified", deriveStatus(" ", "M"))
}

func TestDeriveStatus_Deleted_Index(t *testing.T) {
	assert.Equal(t, "deleted", deriveStatus("D", " "))
}

func TestDeriveStatus_Deleted_Worktree(t *testing.T) {
	assert.Equal(t, "deleted", deriveStatus(" ", "D"))
}

func TestDeriveStatus_Renamed(t *testing.T) {
	assert.Equal(t, "renamed", deriveStatus("R", " "))
}

func TestDeriveStatus_Copied(t *testing.T) {
	assert.Equal(t, "copied", deriveStatus("C", " "))
}

func TestDeriveStatus_Conflict_UU(t *testing.T) {
	assert.Equal(t, "conflict", deriveStatus("U", "U"))
}

func TestDeriveStatus_Conflict_AA(t *testing.T) {
	assert.Equal(t, "conflict", deriveStatus("A", "A"))
}

func TestDeriveStatus_TypeChange(t *testing.T) {
	assert.Equal(t, "typechange", deriveStatus("T", " "))
}

func TestDeriveStatus_Unknown(t *testing.T) {
	assert.Equal(t, "unknown", deriveStatus(" ", " "))
}

// ==================== parseGitStatus Tests ====================

func TestParseGitStatus_CleanRepo(t *testing.T) {
	output := "## main"
	result := parseGitStatus(output)
	assert.Equal(t, "main", result.CurrentBranch)
	assert.Empty(t, result.Files)
	assert.True(t, result.IsClean())
}

func TestParseGitStatus_WithBranchAndUpstream(t *testing.T) {
	output := "## main...origin/main"
	result := parseGitStatus(output)
	assert.Equal(t, "main", result.CurrentBranch)
	assert.Equal(t, "origin/main", result.Upstream)
}

func TestParseGitStatus_WithAheadBehind(t *testing.T) {
	output := "## main...origin/main [ahead 3, behind 2]"
	result := parseGitStatus(output)
	assert.Equal(t, "main", result.CurrentBranch)
	assert.Equal(t, "origin/main", result.Upstream)
	assert.Equal(t, 3, result.Ahead)
	assert.Equal(t, 2, result.Behind)
}

func TestParseGitStatus_ModifiedFiles(t *testing.T) {
	output := "## main\n M src/index.ts"
	result := parseGitStatus(output)
	assert.Equal(t, 1, len(result.Files))
	assert.Equal(t, "src/index.ts", result.Files[0].Path)
	assert.Equal(t, "modified", result.Files[0].Status)
	assert.Equal(t, " ", result.Files[0].IndexStatus)
	assert.Equal(t, "M", result.Files[0].WorkTreeStatus)
	assert.False(t, result.Files[0].Staged)
}

func TestParseGitStatus_UntrackedFiles(t *testing.T) {
	output := "## main\n?? untracked-file.txt"
	result := parseGitStatus(output)
	assert.Equal(t, 1, len(result.Files))
	assert.Equal(t, "untracked-file.txt", result.Files[0].Path)
	assert.Equal(t, "untracked", result.Files[0].Status)
	assert.False(t, result.Files[0].Staged)
}

func TestParseGitStatus_StagedFiles(t *testing.T) {
	output := "## main\nM  src/index.ts"
	result := parseGitStatus(output)
	assert.Equal(t, 1, len(result.Files))
	assert.Equal(t, "src/index.ts", result.Files[0].Path)
	assert.Equal(t, "modified", result.Files[0].Status)
	assert.Equal(t, "M", result.Files[0].IndexStatus)
	assert.True(t, result.Files[0].Staged)
}

func TestParseGitStatus_RenamedFiles(t *testing.T) {
	output := "## main\nR  old-name.txt -> new-name.txt"
	result := parseGitStatus(output)
	assert.Equal(t, 1, len(result.Files))
	assert.Equal(t, "new-name.txt", result.Files[0].Path)
	assert.Equal(t, "renamed", result.Files[0].Status)
	assert.Equal(t, "old-name.txt", result.Files[0].RenamedFrom)
	assert.True(t, result.Files[0].Staged)
}

func TestParseGitStatus_ConflictFiles(t *testing.T) {
	output := "## main\nUU conflicted-file.txt"
	result := parseGitStatus(output)
	assert.Equal(t, 1, len(result.Files))
	assert.Equal(t, "conflicted-file.txt", result.Files[0].Path)
	assert.Equal(t, "conflict", result.Files[0].Status)
}

func TestParseGitStatus_MixedStatus(t *testing.T) {
	output := "## main...origin/main\nM  staged.txt\n M unstaged.txt\n?? untracked.txt\nA  added.txt"
	result := parseGitStatus(output)
	assert.Equal(t, 4, len(result.Files))
	assert.True(t, result.HasChanges())
	assert.True(t, result.HasStaged())
	assert.True(t, result.HasUntracked())
	assert.Equal(t, 4, result.TotalCount())
	// staged.txt and added.txt are staged
	assert.Equal(t, 2, result.StagedCount())
	// unstaged.txt is unstaged (not untracked)
	assert.Equal(t, 1, result.UnstagedCount())
	// untracked.txt
	assert.Equal(t, 1, result.UntrackedCount())
}

func TestParseGitStatus_DetachedHead(t *testing.T) {
	output := "## HEAD (no branch)"
	result := parseGitStatus(output)
	assert.Equal(t, "HEAD", result.CurrentBranch)
	assert.True(t, result.Detached)
}

func TestParseGitStatus_NoCommitsYet(t *testing.T) {
	output := "## No commits yet on main"
	result := parseGitStatus(output)
	assert.NotNil(t, result)
	// Should correctly extract the branch name "main"
	assert.Equal(t, "main", result.CurrentBranch)
}

// ==================== parseGitBranches Tests ====================

func TestParseGitBranches_SingleBranch(t *testing.T) {
	output := "main\t*"
	result := parseGitBranches(output)
	assert.Equal(t, 1, len(result.Branches))
	assert.Equal(t, "main", result.Branches[0].Name)
	assert.True(t, result.Branches[0].IsCurrent)
	assert.Equal(t, "main", result.Current)
}

func TestParseGitBranches_MultipleBranches(t *testing.T) {
	output := "develop\t \nfeature/login\t \nmain\t*"
	result := parseGitBranches(output)
	assert.Equal(t, 3, len(result.Branches))
	assert.Equal(t, "main", result.Current)
	assert.False(t, result.Branches[0].IsCurrent)
	assert.False(t, result.Branches[1].IsCurrent)
	assert.True(t, result.Branches[2].IsCurrent)
}

func TestParseGitBranches_CurrentBranch(t *testing.T) {
	output := "feature\t*\nmain\t "
	result := parseGitBranches(output)
	assert.Equal(t, "feature", result.Current)
	assert.True(t, result.Branches[0].IsCurrent)
	assert.False(t, result.Branches[1].IsCurrent)
}

func TestParseGitBranches_EmptyOutput(t *testing.T) {
	output := ""
	result := parseGitBranches(output)
	assert.Equal(t, 0, len(result.Branches))
	assert.Equal(t, "", result.Current)
}

// ==================== parseGitLog Tests ====================

func TestParseGitLog_SingleEntry(t *testing.T) {
	output := "abc1234567890\x01abc1234\x01John Doe\x01john@example.com\x012024-01-15T10:30:00+08:00\x01Initial commit\x00"
	result := parseGitLog(output)
	assert.Equal(t, 1, len(result.Entries))
	assert.Equal(t, "abc1234567890", result.Entries[0].Hash)
	assert.Equal(t, "abc1234", result.Entries[0].ShortHash)
	assert.Equal(t, "John Doe", result.Entries[0].AuthorName)
	assert.Equal(t, "john@example.com", result.Entries[0].AuthorEmail)
	assert.Equal(t, "2024-01-15T10:30:00+08:00", result.Entries[0].Date)
	assert.Equal(t, "Initial commit", result.Entries[0].Message)
}

func TestParseGitLog_MultipleEntries(t *testing.T) {
	output := "hash1\x01short1\x01Author1\x01a1@test.com\x012024-01-15\x01First\x00hash2\x01short2\x01Author2\x01a2@test.com\x012024-01-16\x01Second\x00"
	result := parseGitLog(output)
	assert.Equal(t, 2, len(result.Entries))
	assert.Equal(t, "First", result.Entries[0].Message)
	assert.Equal(t, "Second", result.Entries[1].Message)
}

func TestParseGitLog_EmptyOutput(t *testing.T) {
	result := parseGitLog("")
	assert.Equal(t, 0, len(result.Entries))
}

func TestParseGitLog_ShortHashFallback(t *testing.T) {
	// When shortHash is empty, it should fallback to first 7 chars of hash
	output := "abcdef1234567890\x01\x01Author\x01a@test.com\x012024-01-15\x01Test\x00"
	result := parseGitLog(output)
	assert.Equal(t, 1, len(result.Entries))
	assert.Equal(t, "abcdef1", result.Entries[0].ShortHash)
}
