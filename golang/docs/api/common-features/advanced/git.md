# Git API Reference

## 🔀 Related Tutorial

- [Git Operations Guide](../../../../../docs/guides/common-features/advanced/git-operations.md) - Learn how to manage git repositories in cloud environments

## Overview

The Git module provides high-level git operations for managing
repositories in the AgentBay cloud environment. It wraps git CLI
commands and executes them via the Command module, supporting
clone, commit, branch management, and more.

## Requirements

- Requires `code_latest` or `linux_latest` image (any image with git pre-installed)

## Type AddOption

```go
type AddOption func(*addOptions)
```

AddOption configures the Add operation.

Parameters:
  - opts: pointer to addOptions struct to configure

### Related Functions

### WithAddAll

```go
func WithAddAll() AddOption
```

WithAddAll adds all files.

Returns:
  - AddOption: functional option to configure Add operation

### WithAddPaths

```go
func WithAddPaths(paths []string) AddOption
```

WithAddPaths sets the paths to add.

Parameters:
  - paths: list of file paths to stage

Returns:
  - AddOption: functional option to configure Add operation

### WithAddTimeout

```go
func WithAddTimeout(timeoutMs int) AddOption
```

WithAddTimeout sets the timeout for add operation.

Parameters:
  - timeoutMs: timeout in milliseconds

Returns:
  - AddOption: functional option to configure Add operation

## Type BranchCreateOption

```go
type BranchCreateOption func(*branchCreateOptions)
```

BranchCreateOption configures the CreateBranch operation.

### Related Functions

### WithBranchCreateCheckout

```go
func WithBranchCreateCheckout(checkout bool) BranchCreateOption
```

WithBranchCreateCheckout sets whether to checkout the new branch after creation. Default is true
(creates and switches to the new branch using "checkout -b"). Set to false to only create the branch
without switching (using "branch").

### WithBranchCreateTimeout

```go
func WithBranchCreateTimeout(timeoutMs int) BranchCreateOption
```

WithBranchCreateTimeout sets the timeout for create branch operation.

## Type BranchDeleteOption

```go
type BranchDeleteOption func(*branchDeleteOptions)
```

BranchDeleteOption configures the DeleteBranch operation.

### Related Functions

### WithBranchDeleteForce

```go
func WithBranchDeleteForce() BranchDeleteOption
```

WithBranchDeleteForce forces branch deletion even if unmerged.

### WithBranchDeleteTimeout

```go
func WithBranchDeleteTimeout(timeoutMs int) BranchDeleteOption
```

WithBranchDeleteTimeout sets the timeout for delete branch operation.

## Type BranchListOption

```go
type BranchListOption func(*branchListOptions)
```

BranchListOption configures the ListBranches operation.

### Related Functions

### WithBranchListRemote

```go
func WithBranchListRemote() BranchListOption
```

WithBranchListRemote lists remote branches.

### WithBranchListTimeout

```go
func WithBranchListTimeout(timeoutMs int) BranchListOption
```

WithBranchListTimeout sets the timeout for list branches operation.

## Type CheckoutOption

```go
type CheckoutOption func(*checkoutOptions)
```

CheckoutOption configures the Checkout operation.

### Related Functions

### WithCheckoutTimeout

```go
func WithCheckoutTimeout(timeoutMs int) CheckoutOption
```

WithCheckoutTimeout sets the timeout for checkout operation.

## Type CloneOption

```go
type CloneOption func(*cloneOptions)
```

CloneOption configures the Clone operation.

### Related Functions

### WithCloneBranch

```go
func WithCloneBranch(branch string) CloneOption
```

WithCloneBranch sets the branch to clone.

### WithCloneDepth

```go
func WithCloneDepth(depth int) CloneOption
```

WithCloneDepth sets the depth for shallow clone.

### WithClonePath

```go
func WithClonePath(path string) CloneOption
```

WithClonePath sets the destination path for clone.

### WithCloneTimeout

```go
func WithCloneTimeout(timeoutMs int) CloneOption
```

WithCloneTimeout sets the timeout for clone operation.

## Type CommitOption

```go
type CommitOption func(*commitOptions)
```

CommitOption configures the Commit operation.

Parameters:
  - opts: pointer to commitOptions struct to configure

### Related Functions

### WithCommitAllowEmpty

```go
func WithCommitAllowEmpty() CommitOption
```

WithCommitAllowEmpty allows empty commits.

Returns:
  - CommitOption: functional option to configure Commit operation

### WithCommitAuthorEmail

```go
func WithCommitAuthorEmail(email string) CommitOption
```

WithCommitAuthorEmail sets the author email for the commit (via git -c user.email=...).

Parameters:
  - email: author email for the commit

Returns:
  - CommitOption: functional option to configure Commit operation

### WithCommitAuthorName

```go
func WithCommitAuthorName(name string) CommitOption
```

WithCommitAuthorName sets the author name for the commit (via git -c user.name=...).

Parameters:
  - name: author name for the commit

Returns:
  - CommitOption: functional option to configure Commit operation

### WithCommitTimeout

```go
func WithCommitTimeout(timeoutMs int) CommitOption
```

WithCommitTimeout sets the timeout for commit operation.

Parameters:
  - timeoutMs: timeout in milliseconds

Returns:
  - CommitOption: functional option to configure Commit operation

## Type ConfigOption

```go
type ConfigOption func(*configOptions)
```

ConfigOption configures the Config operation.

### Related Functions

### WithConfigGlobal

```go
func WithConfigGlobal() ConfigOption
```

WithConfigGlobal sets configuration scope to global (user-specific).

### WithConfigLocal

```go
func WithConfigLocal() ConfigOption
```

WithConfigLocal sets configuration scope to local (repository-specific).

### WithConfigTimeout

```go
func WithConfigTimeout(timeoutMs int) ConfigOption
```

WithConfigTimeout sets the timeout for config operation.

## Type Git

```go
type Git struct {
	command		*command.Command
	gitOnce		sync.Once
	gitError	error
}
```

Git handles git operations in the AgentBay cloud environment.

This struct provides methods for common git operations such as clone, init, add, commit, push, pull,
branch management, and more. It executes git commands in the remote session environment and handles
errors appropriately.

### Methods

### Add

```go
func (g *Git) Add(repoPath string, opts ...AddOption) error
```

Add adds files to the staging area.

Parameters:
  - repoPath: absolute path to the git repository
  - opts: optional configuration functions for the Add operation

Returns:
  - error: returns an error if the operation fails, nil otherwise

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.Add("/home/user/my-project")
```

### CheckoutBranch

```go
func (g *Git) CheckoutBranch(repoPath string, branch string, opts ...CheckoutOption) error
```

CheckoutBranch switches to the specified branch.

Parameters:
  - repoPath: path to the git repository
  - branch: name of the branch to switch to
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.CheckoutBranch("/home/user/my-project", "main")
```

### Clone

```go
func (g *Git) Clone(url string, opts ...CloneOption) (*GitCloneResult, error)
```

Clone clones a git repository.

### Commit

```go
func (g *Git) Commit(repoPath string, message string, opts ...CommitOption) (*GitCommitResult, error)
```

Commit creates a new commit.

Parameters:
  - repoPath: absolute path to the git repository
  - message: commit message
  - opts: optional configuration functions for the Commit operation

Returns:
  - *GitCommitResult: result containing the commit hash
  - error: returns an error if the operation fails, nil otherwise

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
commitResult, _ := result.Session.Git.Commit("/home/user/my-project", "Initial commit")
```

### ConfigureUser

```go
func (g *Git) ConfigureUser(repoPath string, name string, email string, opts ...ConfigOption) error
```

ConfigureUser configures user name and email for the repository.

Parameters:
  - repoPath: path to the git repository
  - name: user name to configure
  - email: user email to configure
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.ConfigureUser("/home/user/my-project", "Agent", "agent@example.com")
```

### CreateBranch

```go
func (g *Git) CreateBranch(repoPath string, branch string, opts ...BranchCreateOption) error
```

CreateBranch creates a new branch in the repository.

Parameters:
  - repoPath: path to the git repository
  - branch: name of the branch to create
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.CreateBranch("/home/user/my-project", "feature/new")
```

### DeleteBranch

```go
func (g *Git) DeleteBranch(repoPath string, branch string, opts ...BranchDeleteOption) error
```

DeleteBranch deletes a branch from the repository.

Parameters:
  - repoPath: path to the git repository
  - branch: name of the branch to delete
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.DeleteBranch("/home/user/my-project", "feature/old")
```

### GetConfig

```go
func (g *Git) GetConfig(repoPath string, key string, opts ...ConfigOption) (string, error)
```

GetConfig gets a configuration value from the repository. Returns empty string (not error) if
the key does not exist (exit code 1, empty stderr). Other errors (e.g. not a git repository) are
returned as-is.

Parameters:
  - repoPath: path to the git repository
  - key: configuration key to retrieve
  - opts: optional configuration functions

Returns:
  - string: configuration value, or empty string if not found
  - error: error if the operation fails (excluding "not found" case)

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
value, _ := result.Session.Git.GetConfig("/home/user/my-project", "user.name")
```

### Init

```go
func (g *Git) Init(path string, opts ...InitOption) (*GitInitResult, error)
```

Init initializes a new git repository.

### ListBranches

```go
func (g *Git) ListBranches(repoPath string, opts ...BranchListOption) (*GitBranchListResult, error)
```

ListBranches lists all branches in the repository.

Parameters:
  - repoPath: path to the git repository
  - opts: optional configuration functions

Returns:
  - *GitBranchListResult: list of branches with HEAD indicator
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
branches, _ := result.Session.Git.ListBranches("/home/user/my-project")
```

### Log

```go
func (g *Git) Log(repoPath string, opts ...LogOption) (*GitLogResult, error)
```

Log shows the commit log.

Parameters:
  - repoPath: absolute path to the git repository
  - opts: optional configuration functions for the Log operation

Returns:
  - *GitLogResult: result containing list of commits with hash, author, date, and message
  - error: returns an error if the operation fails, nil otherwise

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
logResult, _ := result.Session.Git.Log("/home/user/my-project", git.WithLogMaxCount(10))
```

### Pull

```go
func (g *Git) Pull(repoPath string, opts ...PullOption) error
```

Pull fetches from and integrates with another repository.

Parameters:
  - repoPath: path to the git repository
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.Pull("/home/user/my-project")
```

### RemoteAdd

```go
func (g *Git) RemoteAdd(repoPath string, name string, url string, opts ...RemoteAddOption) error
```

RemoteAdd adds a remote repository to the local repository.

Parameters:
  - repoPath: path to the git repository
  - name: name of the remote (e.g., "origin")
  - url: URL of the remote repository
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.RemoteAdd("/home/user/my-project", "origin", "https://github.com/user/repo.git")
```

### RemoteGet

```go
func (g *Git) RemoteGet(repoPath string, name string, opts ...RemoteGetOption) (string, error)
```

RemoteGet gets the URL of a remote repository. Returns empty string (not error) if the remote does
not exist. Other errors (e.g. not a git repository) are returned as-is.

Parameters:
  - repoPath: path to the git repository
  - name: name of the remote
  - opts: optional configuration functions

Returns:
  - string: URL of the remote repository, or empty string if not found
  - error: error if the operation fails (excluding "not found" case)

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
url, _ := result.Session.Git.RemoteGet("/home/user/my-project", "origin")
```

### Reset

```go
func (g *Git) Reset(repoPath string, opts ...ResetOption) error
```

Reset resets the current HEAD to the specified state.

Parameters:
  - repoPath: path to the git repository
  - opts: optional configuration functions (must specify at least one mode or paths)

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.Reset("/home/user/my-project", git.WithResetHard())
```

### Restore

```go
func (g *Git) Restore(repoPath string, paths []string, opts ...RestoreOption) error
```

Restore restores working tree files to their original state.

Parameters:
  - repoPath: path to the git repository
  - paths: list of file paths to restore (at least one required)
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.Restore("/home/user/my-project", []string{"file.txt"})
```

### SetConfig

```go
func (g *Git) SetConfig(repoPath string, key string, value string, opts ...ConfigOption) error
```

SetConfig sets a configuration value in the repository.

Parameters:
  - repoPath: path to the git repository
  - key: configuration key (e.g., "user.name", "core.autocrlf")
  - value: configuration value
  - opts: optional configuration functions

Returns:
  - error: error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
_ = result.Session.Git.SetConfig("/home/user/my-project", "core.autocrlf", "true")
```

### Status

```go
func (g *Git) Status(repoPath string, opts ...StatusOption) (*GitStatusResult, error)
```

Status shows the working tree status.

Parameters:
  - repoPath: absolute path to the git repository
  - opts: optional configuration functions for the Status operation

Returns:
  - *GitStatusResult: result containing branch, staged, unstaged, and untracked files
  - error: returns an error if the operation fails, nil otherwise

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
statusResult, _ := result.Session.Git.Status("/home/user/my-project")
```

### Related Functions

### NewGit

```go
func NewGit(cmd *command.Command) *Git
```

NewGit creates a new Git instance.

Parameters:
  - cmd: The command executor to use for running git commands

Returns:
  - *Git: A new Git instance ready to perform git operations

## Type GitAuthError

```go
type GitAuthError struct {
	GitError
}
```

GitAuthError indicates that git authentication failed.

This error is returned when the remote server rejects credentials, the user lacks access
permissions, or credentials are missing entirely. Common triggers include invalid tokens, expired
SSH keys, and 403 responses.

## Type GitBranchInfo

```go
type GitBranchInfo struct {
	Name		string
	IsCurrent	bool
}
```

GitBranchInfo represents information about a git branch.

## Type GitBranchListResult

```go
type GitBranchListResult struct {
	Branches	[]GitBranchInfo
	Current		string
}
```

GitBranchListResult represents the result of a git branch list operation.

## Type GitCloneResult

```go
type GitCloneResult struct {
	Path string
}
```

GitCloneResult represents the result of a git clone operation.

## Type GitCommitResult

```go
type GitCommitResult struct {
	CommitHash string
}
```

GitCommitResult represents the result of a git commit operation.

## Type GitConflictError

```go
type GitConflictError struct {
	GitError
}
```

GitConflictError indicates that a merge or rebase conflict occurred.

This error is returned when git detects conflicting changes that cannot be automatically resolved,
such as during pull, merge, or rebase operations.

## Type GitError

```go
type GitError struct {
	Message		string
	ExitCode	int
	Stderr		string
}
```

GitError is the base error type for all git operations in the AgentBay cloud environment.

It contains the error message, the exit code from the git process, and the raw stderr output for
debugging. All other git error types embed this struct.

### Methods

### Error

```go
func (e *GitError) Error() string
```

Error returns a human-readable error string including the exit code.

## Type GitFileStatus

```go
type GitFileStatus struct {
	Path		string
	Status		string	// Combined status: "added", "modified", "deleted", "renamed", "copied", "typechange", "untracked", "conflict", "unknown"
	IndexStatus	string	// X in porcelain status output (' '=unmodified, M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked)
	WorkTreeStatus	string	// Y in porcelain status output (' '=unmodified, M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked)
	Staged		bool
	RenamedFrom	string
}
```

GitFileStatus represents the status of a single file in the working tree.

## Type GitInitResult

```go
type GitInitResult struct {
	Path string
}
```

GitInitResult represents the result of a git init operation.

## Type GitLogEntry

```go
type GitLogEntry struct {
	Hash		string
	ShortHash	string
	AuthorName	string
	AuthorEmail	string
	Date		string	// ISO 8601 format: 2006-01-02T15:04:05Z07:00
	Message		string
}
```

GitLogEntry represents a single commit in the git log.

## Type GitLogResult

```go
type GitLogResult struct {
	Entries []GitLogEntry
}
```

GitLogResult represents the result of a git log operation.

## Type GitNotARepoError

```go
type GitNotARepoError struct {
	GitError
}
```

GitNotARepoError indicates that the target path is not a git repository.

This error is returned when a git operation is attempted on a directory that has not been
initialized with git init or cloned.

## Type GitNotFoundError

```go
type GitNotFoundError struct {
	GitError
}
```

GitNotFoundError indicates that git is not installed or not available in PATH on the remote
environment.

This error is returned when the git binary cannot be found (exit code 127) or when the version check
fails during initialization.

## Type GitStatusResult

```go
type GitStatusResult struct {
	CurrentBranch	string
	Upstream	string
	Ahead		int
	Behind		int
	Detached	bool
	Files		[]GitFileStatus
}
```

GitStatusResult represents the result of a git status operation.

### Methods

### ConflictCount

```go
func (s *GitStatusResult) ConflictCount() int
```

ConflictCount returns the number of files with conflicts.

### HasChanges

```go
func (s *GitStatusResult) HasChanges() bool
```

HasChanges returns true if there are any changes (staged or unstaged).

### HasConflicts

```go
func (s *GitStatusResult) HasConflicts() bool
```

HasConflicts returns true if there are merge/rebase conflicts.

### HasStaged

```go
func (s *GitStatusResult) HasStaged() bool
```

HasStaged returns true if there are staged changes.

### HasUntracked

```go
func (s *GitStatusResult) HasUntracked() bool
```

HasUntracked returns true if there are untracked files.

### IsClean

```go
func (s *GitStatusResult) IsClean() bool
```

IsClean returns true if there are no changes in the working tree.

### StagedCount

```go
func (s *GitStatusResult) StagedCount() int
```

StagedCount returns the number of staged files.

### TotalCount

```go
func (s *GitStatusResult) TotalCount() int
```

TotalCount returns the total number of changed files.

### UnstagedCount

```go
func (s *GitStatusResult) UnstagedCount() int
```

UnstagedCount returns the number of unstaged files.

### UntrackedCount

```go
func (s *GitStatusResult) UntrackedCount() int
```

UntrackedCount returns the number of untracked files.

## Type InitOption

```go
type InitOption func(*initOptions)
```

InitOption configures the Init operation.

### Related Functions

### WithInitBare

```go
func WithInitBare() InitOption
```

WithInitBare creates a bare repository.

### WithInitBranch

```go
func WithInitBranch(branch string) InitOption
```

WithInitBranch sets the initial branch name.

### WithInitTimeout

```go
func WithInitTimeout(timeoutMs int) InitOption
```

WithInitTimeout sets the timeout for init operation.

## Type LogOption

```go
type LogOption func(*logOptions)
```

LogOption configures the Log operation.

Parameters:
  - opts: pointer to logOptions struct to configure

### Related Functions

### WithLogMaxCount

```go
func WithLogMaxCount(count int) LogOption
```

WithLogMaxCount sets the maximum number of commits.

Parameters:
  - count: maximum number of commits to return

Returns:
  - LogOption: functional option to configure Log operation

### WithLogTimeout

```go
func WithLogTimeout(timeoutMs int) LogOption
```

WithLogTimeout sets the timeout for log operation.

Parameters:
  - timeoutMs: timeout in milliseconds

Returns:
  - LogOption: functional option to configure Log operation

## Type PullOption

```go
type PullOption func(*pullOptions)
```

PullOption configures the Pull operation.

### Related Functions

### WithPullBranch

```go
func WithPullBranch(branch string) PullOption
```

WithPullBranch sets the branch to pull.

### WithPullRemote

```go
func WithPullRemote(remote string) PullOption
```

WithPullRemote sets the remote to pull from.

### WithPullTimeout

```go
func WithPullTimeout(timeoutMs int) PullOption
```

WithPullTimeout sets the timeout for pull operation.

## Type RemoteAddOption

```go
type RemoteAddOption func(*remoteAddOptions)
```

RemoteAddOption configures the RemoteAdd operation.

### Related Functions

### WithRemoteAddFetch

```go
func WithRemoteAddFetch() RemoteAddOption
```

WithRemoteAddFetch fetches from the remote after adding it. Note: git remote add -f means "fetch
after adding", not "force".

### WithRemoteAddOverwrite

```go
func WithRemoteAddOverwrite() RemoteAddOption
```

WithRemoteAddOverwrite enables idempotent mode: if remote already exists, update its URL. Uses "git
remote add ... || git remote set-url ..." pattern.

### WithRemoteAddTimeout

```go
func WithRemoteAddTimeout(timeoutMs int) RemoteAddOption
```

WithRemoteAddTimeout sets the timeout for remote add operation.

## Type RemoteGetOption

```go
type RemoteGetOption func(*remoteGetOptions)
```

RemoteGetOption configures the RemoteGet operation.

### Related Functions

### WithRemoteGetTimeout

```go
func WithRemoteGetTimeout(timeoutMs int) RemoteGetOption
```

WithRemoteGetTimeout sets the timeout for remote get operation.

## Type ResetOption

```go
type ResetOption func(*resetOptions)
```

ResetOption configures the Reset operation.

### Related Functions

### WithResetCommit

```go
func WithResetCommit(commit string) ResetOption
```

WithResetCommit sets the commit to reset to.

### WithResetHard

```go
func WithResetHard() ResetOption
```

WithResetHard performs a hard reset (discards all changes).

### WithResetMixed

```go
func WithResetMixed() ResetOption
```

WithResetMixed performs a mixed reset (default, unstages changes).

### WithResetPaths

```go
func WithResetPaths(paths []string) ResetOption
```

WithResetPaths sets the paths to reset (for path-specific reset).

### WithResetSoft

```go
func WithResetSoft() ResetOption
```

WithResetSoft performs a soft reset (keeps changes staged).

### WithResetTimeout

```go
func WithResetTimeout(timeoutMs int) ResetOption
```

WithResetTimeout sets the timeout for reset operation.

## Type RestoreOption

```go
type RestoreOption func(*restoreOptions)
```

RestoreOption configures the Restore operation.

### Related Functions

### WithRestoreSource

```go
func WithRestoreSource(source string) RestoreOption
```

WithRestoreSource sets the source tree to restore from.

### WithRestoreStaged

```go
func WithRestoreStaged() RestoreOption
```

WithRestoreStaged restores staged files to their original state.

### WithRestoreTimeout

```go
func WithRestoreTimeout(timeoutMs int) RestoreOption
```

WithRestoreTimeout sets the timeout for restore operation.

### WithRestoreWorktree

```go
func WithRestoreWorktree() RestoreOption
```

WithRestoreWorktree restores working tree files (explicit flag).

## Type StatusOption

```go
type StatusOption func(*statusOptions)
```

StatusOption configures the Status operation.

Parameters:
  - opts: pointer to statusOptions struct to configure

### Related Functions

### WithStatusTimeout

```go
func WithStatusTimeout(timeoutMs int) StatusOption
```

WithStatusTimeout sets the timeout for status operation.

Parameters:
  - timeoutMs: timeout in milliseconds

Returns:
  - StatusOption: functional option to configure Status operation

## Type addOptions

```go
type addOptions struct {
	paths		[]string
	all		bool
	timeoutMs	int
}
```

## Type branchCreateOptions

```go
type branchCreateOptions struct {
	checkout	bool
	timeoutMs	int
}
```

## Type branchDeleteOptions

```go
type branchDeleteOptions struct {
	force		bool
	timeoutMs	int
}
```

## Type branchListOptions

```go
type branchListOptions struct {
	remote		bool
	timeoutMs	int
}
```

## Type checkoutOptions

```go
type checkoutOptions struct {
	timeoutMs int
}
```

## Type cloneOptions

```go
type cloneOptions struct {
	path		string
	branch		string
	depth		int
	timeoutMs	int
}
```

## Type commitOptions

```go
type commitOptions struct {
	message		string
	authorName	string
	authorEmail	string
	allowEmpty	bool
	timeoutMs	int
}
```

## Type configOptions

```go
type configOptions struct {
	scope		string	// local, global
	timeoutMs	int
}
```

## Type initOptions

```go
type initOptions struct {
	initialBranch	string
	bare		bool
	timeoutMs	int
}
```

## Type logOptions

```go
type logOptions struct {
	maxCount	int
	timeoutMs	int
}
```

## Type pullOptions

```go
type pullOptions struct {
	remote		string
	branch		string
	timeoutMs	int
}
```

## Type remoteAddOptions

```go
type remoteAddOptions struct {
	fetch		bool
	overwrite	bool
	timeoutMs	int
}
```

## Type remoteGetOptions

```go
type remoteGetOptions struct {
	timeoutMs int
}
```

## Type resetOptions

```go
type resetOptions struct {
	mode		string	// soft, mixed, hard
	commit		string
	paths		[]string
	timeoutMs	int
}
```

## Type restoreOptions

```go
type restoreOptions struct {
	staged		bool
	worktree	bool
	source		string
	timeoutMs	int
}
```

## Type statusOptions

```go
type statusOptions struct {
	timeoutMs int
}
```

## Best Practices

1. Always configure user identity before committing
2. Use depth parameter for shallow clones to save bandwidth
3. Handle GitAuthError for operations requiring authentication
4. Use timeout_ms for long-running operations like clone and pull

## Related Resources

- [Session API Reference](../basics/session.md)
- [Command API Reference](../basics/command.md)

---

*Documentation generated automatically from Go source code.*
