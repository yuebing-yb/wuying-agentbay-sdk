package git

import "fmt"

// GitError is the base error type for all git operations in the AgentBay cloud environment.
//
// It contains the error message, the exit code from the git process, and the raw stderr
// output for debugging. All other git error types embed this struct.
type GitError struct {
	Message  string
	ExitCode int
	Stderr   string
}

// Error returns a human-readable error string including the exit code.
func (e *GitError) Error() string {
	return fmt.Sprintf("%s (exit code %d)", e.Message, e.ExitCode)
}

// GitAuthError indicates that git authentication failed.
//
// This error is returned when the remote server rejects credentials, the user
// lacks access permissions, or credentials are missing entirely. Common triggers
// include invalid tokens, expired SSH keys, and 403 responses.
type GitAuthError struct {
	GitError
}

// GitNotFoundError indicates that git is not installed or not available in PATH
// on the remote environment.
//
// This error is returned when the git binary cannot be found (exit code 127)
// or when the version check fails during initialization.
type GitNotFoundError struct {
	GitError
}

// GitConflictError indicates that a merge or rebase conflict occurred.
//
// This error is returned when git detects conflicting changes that cannot be
// automatically resolved, such as during pull, merge, or rebase operations.
type GitConflictError struct {
	GitError
}

// GitNotARepoError indicates that the target path is not a git repository.
//
// This error is returned when a git operation is attempted on a directory
// that has not been initialized with git init or cloned.
type GitNotARepoError struct {
	GitError
}
