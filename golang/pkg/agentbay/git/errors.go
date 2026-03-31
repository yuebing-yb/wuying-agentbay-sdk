package git

import "fmt"

// GitError is the base error for all Git operations.
type GitError struct {
	Message  string
	ExitCode int
	Stderr   string
}

func (e *GitError) Error() string {
	return fmt.Sprintf("%s (exit code %d)", e.Message, e.ExitCode)
}

// GitAuthError is raised when git authentication fails.
type GitAuthError struct {
	GitError
}

// GitNotFoundError is raised when git is not installed.
type GitNotFoundError struct {
	GitError
}

// GitConflictError is raised when a merge/rebase conflict occurs.
type GitConflictError struct {
	GitError
}

// GitNotARepoError is raised when the target is not a git repository.
type GitNotARepoError struct {
	GitError
}
