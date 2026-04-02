/**
 * Options for the git clone operation.
 */
export interface GitCloneOpts {
  /** Target directory path for the cloned repository. If not specified, derived from the URL. */
  path?: string;

  /** Branch to clone. When specified, --single-branch is automatically added. */
  branch?: string;

  /** Create a shallow clone with the specified number of commits. */
  depth?: number;

  /** Timeout in milliseconds for the clone operation. Defaults to 300000 (5 minutes). */
  timeoutMs?: number;
}

/**
 * Result of a successful git clone operation.
 */
export interface GitCloneResult {
  /** The path where the repository was cloned to on the remote environment. */
  path: string;
}

// ---------------------------------------------------------------------------
// init
// ---------------------------------------------------------------------------

/**
 * Options for the git init operation.
 */
export interface GitInitOpts {
  /** Create a bare repository. */
  bare?: boolean;

  /** Name of the initial branch (e.g., "main"). Requires git >= 2.28. */
  initialBranch?: string;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Result of a successful git init operation.
 */
export interface GitInitResult {
  /** The path of the initialized repository. */
  path: string;
}

// ---------------------------------------------------------------------------
// add
// ---------------------------------------------------------------------------

/**
 * Options for the git add operation.
 */
export interface GitAddOpts {
  /** Specific files to add. If empty/undefined, behavior depends on `all`. */
  files?: string[];

  /**
   * When no files are specified:
   * - true (default): use `git add -A` to stage all changes
   * - false: use `git add .` to stage current directory only
   */
  all?: boolean;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// commit
// ---------------------------------------------------------------------------

/**
 * Options for the git commit operation.
 */
export interface GitCommitOpts {
  /** Author name. Applied via temporary `-c user.name=...` (not persisted). */
  authorName?: string;

  /** Author email. Applied via temporary `-c user.email=...` (not persisted). */
  authorEmail?: string;

  /** Allow creating a commit with no changes (--allow-empty). */
  allowEmpty?: boolean;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Result of a successful git commit operation.
 */
export interface GitCommitResult {
  /** The short commit hash, parsed from git output. May be undefined if parsing fails. */
  commitHash?: string;
}

// ---------------------------------------------------------------------------
// status
// ---------------------------------------------------------------------------

/**
 * Options for the git status operation.
 */
export interface GitStatusOpts {
  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Status of a single file in the working tree.
 */
export interface GitFileStatus {
  /** File path relative to the repository root. */
  path: string;

  /** Normalized status string (e.g. "modified", "added", "deleted", "renamed", "copied", "untracked", "conflict", "typechange", "unknown"). */
  status: string;

  /** Index (staging area) status character (X column in porcelain output). */
  indexStatus: string;

  /** Work-tree status character (Y column in porcelain output). */
  workTreeStatus: string;

  /** Whether the change is staged. */
  staged: boolean;

  /** Original path when the file was renamed. Only present for renamed files. */
  renamedFrom?: string;
}

/**
 * Result of a git status operation, parsed from `--porcelain=1 -b` output.
 * Enhanced to align with E2B's GitStatus interface.
 */
export interface GitStatusResult {
  /** Current branch name, if available. */
  currentBranch?: string;

  /** Upstream branch name, if available. */
  upstream?: string;

  /** Number of commits the branch is ahead of upstream. */
  ahead: number;

  /** Number of commits the branch is behind upstream. */
  behind: number;

  /** Whether HEAD is detached. */
  detached: boolean;

  /** List of files with changes. */
  files: GitFileStatus[];

  /** Whether the repository has no tracked or untracked file changes. */
  isClean: boolean;

  /** Whether the repository has any tracked or untracked file changes. */
  hasChanges: boolean;

  /** Whether there are staged changes. */
  hasStaged: boolean;

  /** Whether there are untracked files. */
  hasUntracked: boolean;

  /** Whether there are merge conflicts. */
  hasConflicts: boolean;

  /** Total number of changed files. */
  totalCount: number;

  /** Number of files with staged changes. */
  stagedCount: number;

  /** Number of files with unstaged changes. */
  unstagedCount: number;

  /** Number of untracked files. */
  untrackedCount: number;

  /** Number of files with merge conflicts. */
  conflictCount: number;
}

// ---------------------------------------------------------------------------
// log
// ---------------------------------------------------------------------------

/**
 * Options for the git log operation.
 */
export interface GitLogOpts {
  /** Maximum number of log entries to return (--max-count). */
  maxCount?: number;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * A single entry in the git log.
 */
export interface GitLogEntry {
  /** Full commit hash. */
  hash: string;

  /** Abbreviated commit hash. */
  shortHash: string;

  /** Author name. */
  authorName: string;

  /** Author email. */
  authorEmail: string;

  /** Author date in ISO 8601 format. */
  date: string;

  /** Commit subject (first line of the commit message). */
  message: string;
}

/**
 * Result of a git log operation.
 */
export interface GitLogResult {
  /** List of log entries, newest first. */
  entries: GitLogEntry[];
}

// ---------------------------------------------------------------------------
// branch
// ---------------------------------------------------------------------------

/**
 * Options for listing branches.
 */
export interface GitBranchListOpts {
  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Information about a single branch.
 */
export interface GitBranchInfo {
  /** Branch name. */
  name: string;

  /** Whether this is the currently checked-out branch. */
  isCurrent: boolean;
}

/**
 * Result of listing branches.
 */
export interface GitBranchListResult {
  /** All local branches. */
  branches: GitBranchInfo[];

  /** Name of the currently checked-out branch. Empty string if HEAD is detached. */
  current: string;
}

/**
 * Options for creating a branch.
 */
export interface GitBranchCreateOpts {
  /**
   * Whether to checkout the new branch after creation.
   * - true (default): uses `git checkout -b`
   * - false: uses `git branch`
   */
  checkout?: boolean;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Options for deleting a branch.
 */
export interface GitBranchDeleteOpts {
  /** Force delete the branch (-D instead of -d). */
  force?: boolean;

  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

/**
 * Options for checking out a branch.
 */
export interface GitCheckoutOpts {
  /** Timeout in milliseconds. Defaults to 30000 (30 seconds). */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// remote
// ---------------------------------------------------------------------------

/** Options for adding a remote. */
export interface GitRemoteAddOpts {
  /**
   * Fetch from the remote immediately after adding (-f).
   * Default: false.
   */
  fetch?: boolean;
  /**
   * If the remote already exists, update its URL instead of failing.
   * Implemented via: git remote add ... || git remote set-url ...
   * Default: false.
   */
  overwrite?: boolean;
  /** Timeout in milliseconds. Defaults to 30000. */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// reset
// ---------------------------------------------------------------------------

/** Valid modes for git reset. */
export type GitResetMode = "soft" | "mixed" | "hard" | "merge" | "keep";

/** Options for the git reset operation. */
export interface GitResetOpts {
  /** Reset mode. When omitted, git defaults to "mixed". */
  mode?: GitResetMode;
  /** Target commit/branch/ref. Defaults to HEAD when omitted. */
  target?: string;
  /**
   * Specific file paths to reset.
   * When provided, a -- separator is inserted before the paths.
   */
  paths?: string[];
  /** Timeout in milliseconds. Defaults to 30000. */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// restore
// ---------------------------------------------------------------------------

/** Options for the git restore operation. */
export interface GitRestoreOpts {
  /**
   * File paths to restore. Required. Use ['.'] to restore all files.
   */
  paths: string[];
  /**
   * Restore the working tree (--worktree).
   * Default: true when staged is not set; false when staged=true and worktree is unset.
   */
  worktree?: boolean;
  /**
   * Restore the index/staging area (--staged).
   * Default: false.
   */
  staged?: boolean;
  /** Restore from a specific commit/branch/ref (--source <source>). */
  source?: string;
  /** Timeout in milliseconds. Defaults to 30000. */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// pull
// ---------------------------------------------------------------------------

/** Options for the git pull operation. */
export interface GitPullOpts {
  /** Remote name (e.g., "origin"). Defaults to the upstream remote. */
  remote?: string;
  /** Branch name to pull. */
  branch?: string;
  /** Timeout in milliseconds. Defaults to 30000. */
  timeoutMs?: number;
}

// ---------------------------------------------------------------------------
// config
// ---------------------------------------------------------------------------

/** Scope for git config operations. */
export type GitConfigScope = "local" | "global";

/** Options for git config operations. */
export interface GitConfigOpts {
  /**
   * Configuration scope.
   * Default: "global" (matches E2B behavior).
   */
  scope?: GitConfigScope;
  /** Timeout in milliseconds. Defaults to 30000. */
  timeoutMs?: number;
}
