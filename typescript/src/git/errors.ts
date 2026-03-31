import { AgentBayError } from "../exceptions";

/**
 * Base error for all Git operations.
 * Contains the exit code and stderr from the git command.
 */
export class GitError extends AgentBayError {
  exitCode: number;
  stderr: string;

  constructor(message: string, exitCode: number, stderr: string) {
    super(message, { exitCode, stderr });
    this.name = "GitError";
    this.exitCode = exitCode;
    this.stderr = stderr;
    Object.setPrototypeOf(this, GitError.prototype);
  }
}

/**
 * Raised when git authentication fails (e.g., invalid credentials, missing access).
 */
export class GitAuthError extends GitError {
  constructor(message: string, exitCode: number, stderr: string) {
    super(message, exitCode, stderr);
    this.name = "GitAuthError";
    Object.setPrototypeOf(this, GitAuthError.prototype);
  }
}

/**
 * Raised when git is not installed or not found on the remote environment.
 */
export class GitNotFoundError extends GitError {
  constructor(message: string, exitCode: number, stderr: string) {
    super(message, exitCode, stderr);
    this.name = "GitNotFoundError";
    Object.setPrototypeOf(this, GitNotFoundError.prototype);
  }
}

/**
 * Raised when a git merge/rebase conflict occurs.
 */
export class GitConflictError extends GitError {
  constructor(message: string, exitCode: number, stderr: string) {
    super(message, exitCode, stderr);
    this.name = "GitConflictError";
    Object.setPrototypeOf(this, GitConflictError.prototype);
  }
}

/**
 * Raised when the target directory is not a git repository.
 */
export class GitNotARepoError extends GitError {
  constructor(message: string, exitCode: number, stderr: string) {
    super(message, exitCode, stderr);
    this.name = "GitNotARepoError";
    Object.setPrototypeOf(this, GitNotARepoError.prototype);
  }
}
