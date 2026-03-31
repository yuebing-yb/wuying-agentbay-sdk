package git

import (
	"fmt"
	"log"
	neturl "net/url"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
)

var defaultGitEnv = map[string]string{"GIT_TERMINAL_PROMPT": "0"}

// Pre-compiled regex patterns (avoid recompiling on each call)
var (
	branchInfoPattern = regexp.MustCompile(`## ([^\s.]+)(?:\.\.\.([^\s]+))?(?: \[(.+)\])?`)
	aheadPattern      = regexp.MustCompile(`ahead (\d+)`)
	behindPattern     = regexp.MustCompile(`behind (\d+)`)
	commitHashPattern = regexp.MustCompile(`\[(?:[\w/]+ )?([a-f0-9]+)\]`)
)

const (
	// defaultGitTimeoutMs is the default timeout for git operations (30 seconds)
	defaultGitTimeoutMs = 30000
	// defaultCloneTimeoutMs is the default timeout for clone operations (5 minutes, as clone may download large repos)
	defaultCloneTimeoutMs = 300000
)

// Git handles git operations in the AgentBay cloud environment.
type Git struct {
	command  *command.Command
	gitOnce  sync.Once
	gitError error
}

// NewGit creates a new Git instance.
func NewGit(cmd *command.Command) *Git {
	return &Git{command: cmd}
}

// ==================== Private Helper Methods ====================

// shellEscape escapes a shell argument using single quotes (safest for shell).
func shellEscape(arg string) string {
	return "'" + strings.ReplaceAll(arg, "'", "'\\''") + "'"
}

// buildGitCommand builds a git command string.
func buildGitCommand(args []string, repoPath string) string {
	cmdParts := []string{"git"}
	if repoPath != "" {
		cmdParts = append(cmdParts, "-C", shellEscape(repoPath))
	}
	for _, arg := range args {
		cmdParts = append(cmdParts, shellEscape(arg))
	}
	return strings.Join(cmdParts, " ")
}

// runGit executes a git command.
func (g *Git) runGit(args []string, repoPath string, timeoutMs int) (*command.CommandResult, error) {
	cmd := buildGitCommand(args, repoPath)
	return g.runShell(cmd, timeoutMs)
}

// runShell executes a shell command.
func (g *Git) runShell(cmd string, timeoutMs int) (*command.CommandResult, error) {
	if timeoutMs <= 0 {
		timeoutMs = defaultGitTimeoutMs
	}
	return g.command.ExecuteCommand(cmd, command.WithTimeoutMs(timeoutMs), command.WithEnvs(defaultGitEnv))
}

// ensureGitAvailable checks if git is installed (thread-safe via sync.Once).
func (g *Git) ensureGitAvailable() error {
	g.gitOnce.Do(func() {
		result, err := g.runShell("git --version", 5000)
		if err != nil {
			g.gitError = err
			return
		}

		if !result.Success {
			g.gitError = &GitNotFoundError{
				GitError: GitError{
					Message:  "git is not installed or not available in PATH",
					ExitCode: result.ExitCode,
					Stderr:   result.Stderr,
				},
			}
		}
	})
	return g.gitError
}

// classifyError classifies git errors based on exit code and stderr.
func classifyError(operation string, result *command.CommandResult) error {
	if result.Success {
		return nil
	}
	
	stderr := strings.ToLower(result.Stderr)
	
	// Check for authentication errors
	if strings.Contains(stderr, "authentication") || 
	   strings.Contains(stderr, "permission denied") ||
	   strings.Contains(stderr, "could not read username") ||
	   strings.Contains(stderr, "invalid credentials") {
		return &GitAuthError{
			GitError: GitError{
				Message:  fmt.Sprintf("git authentication failed for %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}
	
	// Check for not a repository errors
	stdout := strings.ToLower(result.Stdout)
	if strings.Contains(stderr, "not a git repository") ||
	   strings.Contains(stderr, "does not appear to be a git repository") ||
	   strings.Contains(stdout, "not a git repository") {
		return &GitNotARepoError{
			GitError: GitError{
				Message:  fmt.Sprintf("not a git repository for %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}
	
	// Check for conflict errors (use original case stderr for precise matching)
	if strings.Contains(result.Stderr, "CONFLICT") ||
	   strings.Contains(result.Stderr, "Merge conflict") ||
	   strings.Contains(stderr, "automatic merge failed") {
		return &GitConflictError{
			GitError: GitError{
				Message:  fmt.Sprintf("merge/rebase conflict during %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}
	
	return &GitError{
		Message:  fmt.Sprintf("git %s failed", operation),
		ExitCode: result.ExitCode,
		Stderr:   result.Stderr,
	}
}

// deriveRepoDirFromURL extracts repository directory name from URL.
func deriveRepoDirFromURL(rawURL string) string {
	rawURL = strings.TrimSuffix(rawURL, "/")
	rawURL = strings.TrimSuffix(rawURL, ".git")
	// Handle URL-encoded characters (e.g., %20)
	if decoded, err := neturl.PathUnescape(rawURL); err == nil {
		rawURL = decoded
	}
	parts := strings.Split(rawURL, "/")
	if len(parts) > 0 {
		return parts[len(parts)-1]
	}
	return "repo"
}

// deriveStatus derives combined status from index and worktree status.
func deriveStatus(indexStatus, workTreeStatus string) string {
	switch {
	case indexStatus == "?" && workTreeStatus == "?":
		return "untracked"
	case indexStatus == "U" || workTreeStatus == "U" || indexStatus == "A" && workTreeStatus == "A":
		return "conflict"
	case indexStatus == "R":
		return "renamed"
	case indexStatus == "C":
		return "copied"
	case indexStatus == "A":
		return "added"
	case indexStatus == "D" || workTreeStatus == "D":
		return "deleted"
	case indexStatus == "T" || workTreeStatus == "T":
		return "typechange"
	case indexStatus == "M" || workTreeStatus == "M":
		return "modified"
	default:
		return "unknown"
	}
}

// parseGitStatus parses git status --porcelain -b output.
// The first line starting with "## " contains branch info.
func parseGitStatus(output string) *GitStatusResult {
	result := &GitStatusResult{
		Files: []GitFileStatus{},
	}

	lines := strings.Split(strings.TrimSpace(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}

		// Parse branch info line (## branch...upstream [ahead N, behind M])
		if strings.HasPrefix(line, "## ") {
			// Handle "## No commits yet on <branch>" format
			if strings.HasPrefix(line, "## No commits yet on ") {
				result.CurrentBranch = strings.TrimPrefix(line, "## No commits yet on ")
				continue
			}
			matches := branchInfoPattern.FindStringSubmatch(line)
			if len(matches) > 1 {
				result.CurrentBranch = matches[1]
				if len(matches) > 2 && matches[2] != "" {
					result.Upstream = matches[2]
				}
				if len(matches) > 3 && matches[3] != "" {
					trackingInfo := matches[3]
					aheadMatches := aheadPattern.FindStringSubmatch(trackingInfo)
					if len(aheadMatches) > 1 {
						result.Ahead, _ = strconv.Atoi(aheadMatches[1])
					}
					behindMatches := behindPattern.FindStringSubmatch(trackingInfo)
					if len(behindMatches) > 1 {
						result.Behind, _ = strconv.Atoi(behindMatches[1])
					}
				}
				result.Detached = matches[1] == "HEAD"
			}
			continue
		}

		if len(line) < 4 {
			continue
		}

		indexStatus := string(line[0])
		workTreeStatus := string(line[1])
		path := strings.TrimSpace(line[3:])

		status := deriveStatus(indexStatus, workTreeStatus)
		staged := indexStatus != " " && indexStatus != "?"

		renamedFrom := ""
		if indexStatus == "R" {
			parts := strings.SplitN(path, " -> ", 2)
			if len(parts) == 2 {
				renamedFrom = parts[0]
				path = parts[1]
			}
		}

		result.Files = append(result.Files, GitFileStatus{
			Path:           path,
			Status:         status,
			IndexStatus:    indexStatus,
			WorkTreeStatus: workTreeStatus,
			Staged:         staged,
			RenamedFrom:    renamedFrom,
		})
	}

	return result
}

// parseGitLog parses git log output using \x00/\x01 separator format.
// Expected format: %H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00
func parseGitLog(output string) *GitLogResult {
	result := &GitLogResult{
		Entries: []GitLogEntry{},
	}

	output = strings.TrimSpace(output)
	if output == "" {
		return result
	}

	// Split entries by \x00 (null byte)
	entries := strings.Split(output, "\x00")
	for _, entry := range entries {
		entry = strings.TrimSpace(entry)
		if entry == "" {
			continue
		}

		// Split fields by \x01 (SOH byte)
		fields := strings.Split(entry, "\x01")
		if len(fields) < 6 {
			continue
		}

		hash := strings.TrimSpace(fields[0])
		shortHash := strings.TrimSpace(fields[1])
		if shortHash == "" && len(hash) >= 7 {
			shortHash = hash[:7]
		}

		result.Entries = append(result.Entries, GitLogEntry{
			Hash:        hash,
			ShortHash:   shortHash,
			AuthorName:  strings.TrimSpace(fields[2]),
			AuthorEmail: strings.TrimSpace(fields[3]),
			Date:        strings.TrimSpace(fields[4]),
			Message:     strings.TrimSpace(fields[5]),
		})
	}

	return result
}

// parseGitBranches parses git branch --format=%(refname:short)\t%(HEAD) output.
// Each line is: branch_name\t* (current) or branch_name\t  (other).
func parseGitBranches(output string) *GitBranchListResult {
	result := &GitBranchListResult{
		Branches: []GitBranchInfo{},
	}
	
	lines := strings.Split(strings.TrimSpace(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}
		
		parts := strings.SplitN(line, "\t", 2)
		name := strings.TrimSpace(parts[0])
		if name == "" {
			continue
		}
		
		isCurrent := len(parts) > 1 && strings.TrimSpace(parts[1]) == "*"
		if isCurrent {
			result.Current = name
		}
		
		result.Branches = append(result.Branches, GitBranchInfo{
			Name:      name,
			IsCurrent: isCurrent,
		})
	}
	
	return result
}

// ==================== Functional Options for Clone ====================

type cloneOptions struct {
	path      string
	branch    string
	depth     int
	timeoutMs int
}

// CloneOption configures the Clone operation.
type CloneOption func(*cloneOptions)

// WithClonePath sets the destination path for clone.
func WithClonePath(path string) CloneOption {
	return func(opts *cloneOptions) {
		opts.path = path
	}
}

// WithCloneBranch sets the branch to clone.
func WithCloneBranch(branch string) CloneOption {
	return func(opts *cloneOptions) {
		opts.branch = branch
	}
}

// WithCloneDepth sets the depth for shallow clone.
func WithCloneDepth(depth int) CloneOption {
	return func(opts *cloneOptions) {
		opts.depth = depth
	}
}

// WithCloneTimeout sets the timeout for clone operation.
func WithCloneTimeout(timeoutMs int) CloneOption {
	return func(opts *cloneOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Clone clones a git repository.
func (g *Git) Clone(url string, opts ...CloneOption) (*GitCloneResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &cloneOptions{
		timeoutMs: defaultCloneTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"clone"}
	if options.branch != "" {
		args = append(args, "--branch", options.branch, "--single-branch")
	}
	if options.depth > 0 {
		args = append(args, "--depth", strconv.Itoa(options.depth))
	}
	args = append(args, url)
	
	if options.path != "" {
		args = append(args, options.path)
	}
	
	result, err := g.runGit(args, "", options.timeoutMs)
	if err != nil {
		return nil, err
	}
	
	if !result.Success {
		return nil, classifyError("clone", result)
	}
	
	path := options.path
	if path == "" {
		path = deriveRepoDirFromURL(url)
	}
	
	return &GitCloneResult{Path: path}, nil
}

// ==================== Functional Options for Init ====================

type initOptions struct {
	initialBranch string
	bare          bool
	timeoutMs     int
}

// InitOption configures the Init operation.
type InitOption func(*initOptions)

// WithInitBranch sets the initial branch name.
func WithInitBranch(branch string) InitOption {
	return func(opts *initOptions) {
		opts.initialBranch = branch
	}
}

// WithInitBare creates a bare repository.
func WithInitBare() InitOption {
	return func(opts *initOptions) {
		opts.bare = true
	}
}

// WithInitTimeout sets the timeout for init operation.
func WithInitTimeout(timeoutMs int) InitOption {
	return func(opts *initOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Init initializes a new git repository.
func (g *Git) Init(path string, opts ...InitOption) (*GitInitResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &initOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"init"}
	if options.initialBranch != "" {
		args = append(args, "--initial-branch", options.initialBranch)
	}
	if options.bare {
		args = append(args, "--bare")
	}
	
	result, err := g.runGit(args, path, options.timeoutMs)
	if err != nil {
		return nil, err
	}
	
	if !result.Success {
		return nil, classifyError("init", result)
	}
	
	return &GitInitResult{Path: path}, nil
}

// ==================== Functional Options for Add ====================

type addOptions struct {
	paths     []string
	all       bool
	update    bool
	force     bool
	timeoutMs int
}

// AddOption configures the Add operation.
type AddOption func(*addOptions)

// WithAddPaths sets the paths to add.
func WithAddPaths(paths []string) AddOption {
	return func(opts *addOptions) {
		opts.paths = paths
	}
}

// WithAddAll adds all files.
func WithAddAll() AddOption {
	return func(opts *addOptions) {
		opts.all = true
	}
}

// WithAddUpdate adds only updated files.
func WithAddUpdate() AddOption {
	return func(opts *addOptions) {
		opts.update = true
	}
}

// WithAddForce forces adding.
func WithAddForce() AddOption {
	return func(opts *addOptions) {
		opts.force = true
	}
}

// WithAddTimeout sets the timeout for add operation.
func WithAddTimeout(timeoutMs int) AddOption {
	return func(opts *addOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Add adds files to the staging area.
func (g *Git) Add(repoPath string, opts ...AddOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &addOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Validate: at least one path or --all/--update must be specified
	if !options.all && !options.update && len(options.paths) == 0 {
		return fmt.Errorf("git add requires at least one path, or use WithAddAll()/WithAddUpdate()")
	}
	
	args := []string{"add"}
	if options.all {
		args = append(args, "--all")
	}
	if options.update {
		args = append(args, "--update")
	}
	if options.force {
		args = append(args, "--force")
	}
	args = append(args, options.paths...)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("add", result)
	}
	
	return nil
}

// ==================== Functional Options for Commit ====================

type commitOptions struct {
	message     string
	authorName  string
	authorEmail string
	amend       bool
	allowEmpty  bool
	skipHooks   bool
	timeoutMs   int
}

// CommitOption configures the Commit operation.
type CommitOption func(*commitOptions)

// WithCommitAmend amends the previous commit.
func WithCommitAmend() CommitOption {
	return func(opts *commitOptions) {
		opts.amend = true
	}
}

// WithCommitAllowEmpty allows empty commits.
func WithCommitAllowEmpty() CommitOption {
	return func(opts *commitOptions) {
		opts.allowEmpty = true
	}
}

// WithCommitSkipHooks skips pre-commit and commit-msg hooks.
func WithCommitSkipHooks() CommitOption {
	return func(opts *commitOptions) {
		opts.skipHooks = true
	}
}

// WithCommitAuthorName sets the author name for the commit (via git -c user.name=...).
func WithCommitAuthorName(name string) CommitOption {
	return func(opts *commitOptions) {
		opts.authorName = name
	}
}

// WithCommitAuthorEmail sets the author email for the commit (via git -c user.email=...).
func WithCommitAuthorEmail(email string) CommitOption {
	return func(opts *commitOptions) {
		opts.authorEmail = email
	}
}

// WithCommitTimeout sets the timeout for commit operation.
func WithCommitTimeout(timeoutMs int) CommitOption {
	return func(opts *commitOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Commit creates a new commit.
func (g *Git) Commit(repoPath string, message string, opts ...CommitOption) (*GitCommitResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &commitOptions{
		message:   message,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Build command manually to support -c global args before the "commit" subcommand.
	// Command format: git -C <path> [-c user.name=xxx] [-c user.email=xxx] commit -m "msg" [flags]
	cmdParts := []string{"git"}
	if repoPath != "" {
		cmdParts = append(cmdParts, "-C", shellEscape(repoPath))
	}
	// -c parameters must come BEFORE the 'commit' subcommand (git requirement)
	if options.authorName != "" {
		cmdParts = append(cmdParts, "-c", shellEscape(fmt.Sprintf("user.name=%s", options.authorName)))
	}
	if options.authorEmail != "" {
		cmdParts = append(cmdParts, "-c", shellEscape(fmt.Sprintf("user.email=%s", options.authorEmail)))
	}
	
	subArgs := []string{"commit"}
	if options.amend {
		subArgs = append(subArgs, "--amend")
	}
	if options.allowEmpty {
		subArgs = append(subArgs, "--allow-empty")
	}
	if options.skipHooks {
		subArgs = append(subArgs, "--no-verify")
	}
	subArgs = append(subArgs, "-m", options.message)
	for _, arg := range subArgs {
		cmdParts = append(cmdParts, shellEscape(arg))
	}
	
	cmd := strings.Join(cmdParts, " ")
	result, err := g.runShell(cmd, options.timeoutMs)
	if err != nil {
		return nil, err
	}
	
	if !result.Success {
		return nil, classifyError("commit", result)
	}
	
	// Extract commit hash from output
	matches := commitHashPattern.FindStringSubmatch(result.Stdout)
	if len(matches) > 1 {
		return &GitCommitResult{CommitHash: matches[1]}, nil
	}
	
	// Fallback: get the latest commit hash (this should rarely happen)
	log.Printf("[WARNING] git commit succeeded but could not parse commit hash from output, falling back to rev-parse HEAD")
	hashResult, err := g.runGit([]string{"rev-parse", "HEAD"}, repoPath, 5000)
	if err == nil && hashResult.Success {
		return &GitCommitResult{CommitHash: strings.TrimSpace(hashResult.Stdout)}, nil
	}
	
	return &GitCommitResult{CommitHash: ""}, nil
}

// ==================== Functional Options for Status ====================

type statusOptions struct {
	timeoutMs int
}

// StatusOption configures the Status operation.
type StatusOption func(*statusOptions)

// WithStatusTimeout sets the timeout for status operation.
func WithStatusTimeout(timeoutMs int) StatusOption {
	return func(opts *statusOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Status shows the working tree status.
func (g *Git) Status(repoPath string, opts ...StatusOption) (*GitStatusResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &statusOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Get porcelain status with branch info in a single command
	result, err := g.runGit([]string{"status", "--porcelain=1", "-b"}, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("status", result)
	}

	return parseGitStatus(result.Stdout), nil
}

// ==================== Functional Options for Log ====================

type logOptions struct {
	maxCount  int
	timeoutMs int
}

// LogOption configures the Log operation.
type LogOption func(*logOptions)

// WithLogMaxCount sets the maximum number of commits.
func WithLogMaxCount(count int) LogOption {
	return func(opts *logOptions) {
		opts.maxCount = count
	}
}

// WithLogTimeout sets the timeout for log operation.
func WithLogTimeout(timeoutMs int) LogOption {
	return func(opts *logOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Log shows the commit log.
func (g *Git) Log(repoPath string, opts ...LogOption) (*GitLogResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &logOptions{
		maxCount:  0,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"log"}
	if options.maxCount > 0 {
		args = append(args, "-n", strconv.Itoa(options.maxCount))
	}
	args = append(args, "--format=%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00")
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}
	
	if !result.Success {
		return nil, classifyError("log", result)
	}
	
	return parseGitLog(result.Stdout), nil
}

// ==================== Functional Options for ListBranches ====================

type branchListOptions struct {
	remote    bool
	timeoutMs int
}

// BranchListOption configures the ListBranches operation.
type BranchListOption func(*branchListOptions)

// WithBranchListRemote lists remote branches.
func WithBranchListRemote() BranchListOption {
	return func(opts *branchListOptions) {
		opts.remote = true
	}
}

// WithBranchListTimeout sets the timeout for list branches operation.
func WithBranchListTimeout(timeoutMs int) BranchListOption {
	return func(opts *branchListOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// ListBranches lists all branches.
func (g *Git) ListBranches(repoPath string, opts ...BranchListOption) (*GitBranchListResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}
	
	options := &branchListOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Use structured format output for reliable parsing (matches TS/Python)
	args := []string{"branch", "--format=%(refname:short)\t%(HEAD)"}
	if options.remote {
		args = append(args, "-r")
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("branch", result)
	}

	return parseGitBranches(result.Stdout), nil
}

// ==================== Functional Options for CreateBranch ====================

type branchCreateOptions struct {
	force     bool
	checkout  bool
	timeoutMs int
}

// BranchCreateOption configures the CreateBranch operation.
type BranchCreateOption func(*branchCreateOptions)

// WithBranchCreateForce forces branch creation.
func WithBranchCreateForce() BranchCreateOption {
	return func(opts *branchCreateOptions) {
		opts.force = true
	}
}

// WithBranchCreateCheckout sets whether to checkout the new branch after creation.
// Default is true (creates and switches to the new branch using "checkout -b").
// Set to false to only create the branch without switching (using "branch").
func WithBranchCreateCheckout(checkout bool) BranchCreateOption {
	return func(opts *branchCreateOptions) {
		opts.checkout = checkout
	}
}

// WithBranchCreateTimeout sets the timeout for create branch operation.
func WithBranchCreateTimeout(timeoutMs int) BranchCreateOption {
	return func(opts *branchCreateOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// CreateBranch creates a new branch.
func (g *Git) CreateBranch(repoPath string, branch string, opts ...BranchCreateOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &branchCreateOptions{
		checkout:  true,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	var args []string
	if options.checkout {
		// Create and switch to the new branch (default behavior, matches TS/Python)
		flag := "-b"
		if options.force {
			flag = "-B" // Force create: overwrite existing branch
		}
		args = []string{"checkout", flag, branch}
	} else {
		// Only create the branch without switching
		args = []string{"branch"}
		if options.force {
			args = append(args, "-f")
		}
		args = append(args, branch)
	}
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("branch", result)
	}
	
	return nil
}

// ==================== Functional Options for Checkout ====================

type checkoutOptions struct {
	force     bool
	timeoutMs int
}

// CheckoutOption configures the Checkout operation.
type CheckoutOption func(*checkoutOptions)

// WithCheckoutForce forces checkout.
func WithCheckoutForce() CheckoutOption {
	return func(opts *checkoutOptions) {
		opts.force = true
	}
}

// WithCheckoutTimeout sets the timeout for checkout operation.
func WithCheckoutTimeout(timeoutMs int) CheckoutOption {
	return func(opts *checkoutOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// CheckoutBranch switches to a branch.
func (g *Git) CheckoutBranch(repoPath string, branch string, opts ...CheckoutOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &checkoutOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"checkout"}
	if options.force {
		args = append(args, "-f")
	}
	args = append(args, branch)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("checkout", result)
	}
	
	return nil
}

// ==================== Functional Options for DeleteBranch ====================

type branchDeleteOptions struct {
	force     bool
	timeoutMs int
}

// BranchDeleteOption configures the DeleteBranch operation.
type BranchDeleteOption func(*branchDeleteOptions)

// WithBranchDeleteForce forces branch deletion.
func WithBranchDeleteForce() BranchDeleteOption {
	return func(opts *branchDeleteOptions) {
		opts.force = true
	}
}

// WithBranchDeleteTimeout sets the timeout for delete branch operation.
func WithBranchDeleteTimeout(timeoutMs int) BranchDeleteOption {
	return func(opts *branchDeleteOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// DeleteBranch deletes a branch.
func (g *Git) DeleteBranch(repoPath string, branch string, opts ...BranchDeleteOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &branchDeleteOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"branch"}
	if options.force {
		args = append(args, "-D")
	} else {
		args = append(args, "-d")
	}
	args = append(args, branch)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("branch", result)
	}
	
	return nil
}

// ==================== Functional Options for RemoteAdd ====================

type remoteAddOptions struct {
	fetch     bool
	overwrite bool
	timeoutMs int
}

// RemoteAddOption configures the RemoteAdd operation.
type RemoteAddOption func(*remoteAddOptions)

// WithRemoteAddFetch fetches from the remote after adding it.
// Note: git remote add -f means "fetch after adding", not "force".
func WithRemoteAddFetch() RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.fetch = true
	}
}

// WithRemoteAddOverwrite enables idempotent mode: if remote already exists, update its URL.
// Uses "git remote add ... || git remote set-url ..." pattern.
func WithRemoteAddOverwrite() RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.overwrite = true
	}
}

// WithRemoteAddTimeout sets the timeout for remote add operation.
func WithRemoteAddTimeout(timeoutMs int) RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// RemoteAdd adds a remote repository.
func (g *Git) RemoteAdd(repoPath string, name string, url string, opts ...RemoteAddOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &remoteAddOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	addArgs := []string{"remote", "add"}
	if options.fetch {
		addArgs = append(addArgs, "-f")
	}
	addArgs = append(addArgs, name, url)
	
	if !options.overwrite {
		// Simple mode: direct git remote add
		result, err := g.runGit(addArgs, repoPath, options.timeoutMs)
		if err != nil {
			return err
		}
		if !result.Success {
			return classifyError("remote", result)
		}
	} else {
		// Idempotent mode: add fails, fallback to set-url
		addCmd := buildGitCommand(addArgs, repoPath)
		setUrlCmd := buildGitCommand([]string{"remote", "set-url", name, url}, repoPath)
		cmd := addCmd + " || " + setUrlCmd
		if options.fetch {
			fetchCmd := buildGitCommand([]string{"fetch", name}, repoPath)
			cmd = "(" + cmd + ") && " + fetchCmd
		}
		result, err := g.runShell(cmd, options.timeoutMs)
		if err != nil {
			return err
		}
		if !result.Success {
			return classifyError("remote", result)
		}
	}
	
	return nil
}

// ==================== Functional Options for RemoteGet ====================

type remoteGetOptions struct {
	timeoutMs int
}

// RemoteGetOption configures the RemoteGet operation.
type RemoteGetOption func(*remoteGetOptions)

// WithRemoteGetTimeout sets the timeout for remote get operation.
func WithRemoteGetTimeout(timeoutMs int) RemoteGetOption {
	return func(opts *remoteGetOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// RemoteGet gets the URL of a remote repository.
func (g *Git) RemoteGet(repoPath string, name string, opts ...RemoteGetOption) (string, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return "", err
	}
	
	options := &remoteGetOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"remote", "get-url", name}
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return "", err
	}
	
	if !result.Success {
		return "", classifyError("remote", result)
	}
	
	return strings.TrimSpace(result.Stdout), nil
}

// ==================== Functional Options for Reset ====================

type resetOptions struct {
	mode      string // soft, mixed, hard
	commit    string
	timeoutMs int
}

// ResetOption configures the Reset operation.
type ResetOption func(*resetOptions)

// WithResetSoft performs a soft reset.
func WithResetSoft() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "soft"
	}
}

// WithResetMixed performs a mixed reset (default).
func WithResetMixed() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "mixed"
	}
}

// WithResetHard performs a hard reset.
func WithResetHard() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "hard"
	}
}

// WithResetCommit sets the commit to reset to.
func WithResetCommit(commit string) ResetOption {
	return func(opts *resetOptions) {
		opts.commit = commit
	}
}

// WithResetTimeout sets the timeout for reset operation.
func WithResetTimeout(timeoutMs int) ResetOption {
	return func(opts *resetOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Reset resets the current HEAD to the specified state.
func (g *Git) Reset(repoPath string, opts ...ResetOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &resetOptions{
		mode:      "mixed",
		commit:    "HEAD",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"reset"}
	if options.mode != "" {
		args = append(args, "--"+options.mode)
	}
	args = append(args, options.commit)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("reset", result)
	}
	
	return nil
}

// ==================== Functional Options for Restore ====================

type restoreOptions struct {
	staged    bool
	worktree  bool
	source    string
	timeoutMs int
}

// RestoreOption configures the Restore operation.
type RestoreOption func(*restoreOptions)

// WithRestoreStaged restores staged files.
func WithRestoreStaged() RestoreOption {
	return func(opts *restoreOptions) {
		opts.staged = true
	}
}

// WithRestoreWorktree restores working tree files (explicit flag).
func WithRestoreWorktree() RestoreOption {
	return func(opts *restoreOptions) {
		opts.worktree = true
	}
}

// WithRestoreSource sets the source tree.
func WithRestoreSource(source string) RestoreOption {
	return func(opts *restoreOptions) {
		opts.source = source
	}
}

// WithRestoreTimeout sets the timeout for restore operation.
func WithRestoreTimeout(timeoutMs int) RestoreOption {
	return func(opts *restoreOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Restore restores working tree files.
func (g *Git) Restore(repoPath string, paths []string, opts ...RestoreOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &restoreOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Validate: at least one path must be specified
	if len(paths) == 0 {
		return fmt.Errorf("git restore requires at least one path")
	}
	
	args := []string{"restore"}
	if options.staged {
		args = append(args, "--staged")
	}
	if options.worktree {
		args = append(args, "--worktree")
	}
	if options.source != "" {
		args = append(args, "--source", options.source)
	}
	args = append(args, paths...)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("restore", result)
	}
	
	return nil
}

// ==================== Functional Options for Pull ====================

type pullOptions struct {
	remote    string
	branch    string
	rebase    bool
	timeoutMs int
}

// PullOption configures the Pull operation.
type PullOption func(*pullOptions)

// WithPullRemote sets the remote to pull from.
func WithPullRemote(remote string) PullOption {
	return func(opts *pullOptions) {
		opts.remote = remote
	}
}

// WithPullBranch sets the branch to pull.
func WithPullBranch(branch string) PullOption {
	return func(opts *pullOptions) {
		opts.branch = branch
	}
}

// WithPullRebase uses rebase instead of merge.
func WithPullRebase() PullOption {
	return func(opts *pullOptions) {
		opts.rebase = true
	}
}

// WithPullTimeout sets the timeout for pull operation.
func WithPullTimeout(timeoutMs int) PullOption {
	return func(opts *pullOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Pull fetches from and integrates with another repository.
func (g *Git) Pull(repoPath string, opts ...PullOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &pullOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"pull"}
	if options.rebase {
		args = append(args, "--rebase")
	}
	if options.remote != "" {
		args = append(args, options.remote)
		if options.branch != "" {
			args = append(args, options.branch)
		}
	}
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("pull", result)
	}
	
	return nil
}

// ==================== Functional Options for Config ====================

type configOptions struct {
	scope     string // local, global, system
	timeoutMs int
}

// ConfigOption configures the Config operation.
type ConfigOption func(*configOptions)

// WithConfigLocal sets local scope.
func WithConfigLocal() ConfigOption {
	return func(opts *configOptions) {
		opts.scope = "local"
	}
}

// WithConfigGlobal sets global scope.
func WithConfigGlobal() ConfigOption {
	return func(opts *configOptions) {
		opts.scope = "global"
	}
}

// WithConfigSystem sets system scope.
func WithConfigSystem() ConfigOption {
	return func(opts *configOptions) {
		opts.scope = "system"
	}
}

// WithConfigTimeout sets the timeout for config operation.
func WithConfigTimeout(timeoutMs int) ConfigOption {
	return func(opts *configOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// ConfigureUser configures user name and email.
func (g *Git) ConfigureUser(repoPath string, name string, email string, opts ...ConfigOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	// Set user name
	nameArgs := []string{"config"}
	if options.scope != "" {
		nameArgs = append(nameArgs, "--"+options.scope)
	}
	nameArgs = append(nameArgs, "user.name", name)
	
	nameResult, err := g.runGit(nameArgs, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	if !nameResult.Success {
		return classifyError("config", nameResult)
	}
	
	// Set user email
	emailArgs := []string{"config"}
	if options.scope != "" {
		emailArgs = append(emailArgs, "--"+options.scope)
	}
	emailArgs = append(emailArgs, "user.email", email)
	
	emailResult, err := g.runGit(emailArgs, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	if !emailResult.Success {
		return classifyError("config", emailResult)
	}
	
	return nil
}

// SetConfig sets a configuration value.
func (g *Git) SetConfig(repoPath string, key string, value string, opts ...ConfigOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}
	
	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"config"}
	if options.scope != "" {
		args = append(args, "--"+options.scope)
	}
	args = append(args, key, value)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	
	if !result.Success {
		return classifyError("config", result)
	}
	
	return nil
}

// GetConfig gets a configuration value.
func (g *Git) GetConfig(repoPath string, key string, opts ...ConfigOption) (string, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return "", err
	}
	
	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}
	
	args := []string{"config"}
	if options.scope != "" {
		args = append(args, "--"+options.scope)
	}
	args = append(args, "--get", key)
	
	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return "", err
	}
	
	if !result.Success {
		return "", classifyError("config", result)
	}
	
	return strings.TrimSpace(result.Stdout), nil
}
