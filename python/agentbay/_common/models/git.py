from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GitCloneResult:
    """
    Result of a successful git clone operation.

    Attributes:
        path: The local path where the repository was cloned.
    """
    path: str

@dataclass
class GitInitResult:
    """
    Result of a successful git init operation.

    Attributes:
        path: The local path where the repository was initialized.
    """
    path: str

@dataclass
class GitCommitResult:
    """
    Result of a successful git commit operation.

    Attributes:
        commit_hash: The short hash of the created commit, or ``None``
            if it could not be parsed.
    """
    commit_hash: Optional[str] = None

@dataclass
class GitFileStatus:
    """
    Parsed git status entry for a single file.

    Attributes:
        path: Path relative to the repository root.
        status: Normalized status string (e.g., ``"modified"``, ``"added"``,
            ``"deleted"``, ``"renamed"``, ``"untracked"``, ``"conflict"``).
        index_status: Index status character from porcelain output.
        work_tree_status: Working tree status character from porcelain output.
        staged: Whether the change is staged.
        renamed_from: Original path when the file was renamed.
    """
    path: str
    status: str
    index_status: str
    work_tree_status: str
    staged: bool
    renamed_from: Optional[str] = None

@dataclass
class GitStatusResult:
    """
    Parsed git repository status.

    Attributes:
        current_branch: Current branch name, if available.
        upstream: Upstream tracking branch name, if available.
        ahead: Number of commits the branch is ahead of upstream.
        behind: Number of commits the branch is behind upstream.
        detached: Whether HEAD is in detached state.
        files: List of file status entries.
    """
    current_branch: Optional[str] = None
    upstream: Optional[str] = None
    ahead: int = 0
    behind: int = 0
    detached: bool = False
    files: List[GitFileStatus] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """Return True when there are no tracked or untracked file changes."""
        return len(self.files) == 0

    @property
    def has_changes(self) -> bool:
        """Return True when there are any tracked or untracked file changes."""
        return len(self.files) > 0

    @property
    def has_staged(self) -> bool:
        """Return True when at least one file has staged changes."""
        return any(f.staged for f in self.files)

    @property
    def has_untracked(self) -> bool:
        """Return True when at least one file is untracked."""
        return any(f.status == "untracked" for f in self.files)

    @property
    def has_conflicts(self) -> bool:
        """Return True when at least one file is in conflict."""
        return any(f.status == "conflict" for f in self.files)

    @property
    def total_count(self) -> int:
        """Return the total number of changed files."""
        return len(self.files)

    @property
    def staged_count(self) -> int:
        """Return the number of files with staged changes."""
        return sum(1 for f in self.files if f.staged)

    @property
    def unstaged_count(self) -> int:
        """Return the number of tracked files with unstaged changes (excludes untracked)."""
        return sum(1 for f in self.files if not f.staged and f.status != "untracked")

    @property
    def untracked_count(self) -> int:
        """Return the number of untracked files."""
        return sum(1 for f in self.files if f.status == "untracked")

    @property
    def conflict_count(self) -> int:
        """Return the number of files with merge conflicts."""
        return sum(1 for f in self.files if f.status == "conflict")

@dataclass
class GitLogEntry:
    """
    A single entry in the git log.

    Attributes:
        hash: Full commit hash.
        short_hash: Abbreviated commit hash.
        author_name: Author name.
        author_email: Author email.
        date: Commit date in ISO 8601 format.
        message: Commit subject line.
    """
    hash: str
    short_hash: str
    author_name: str
    author_email: str
    date: str
    message: str

@dataclass
class GitLogResult:
    """
    Result of a git log operation.

    Attributes:
        entries: List of GitLogEntry objects.
    """
    entries: List[GitLogEntry] = field(default_factory=list)

@dataclass
class GitBranchInfo:
    """
    Information about a single git branch.

    Attributes:
        name: Branch name.
        is_current: Whether this branch is currently checked out.
    """
    name: str
    is_current: bool

@dataclass
class GitBranchListResult:
    """
    Result of listing git branches.

    Attributes:
        branches: List of GitBranchInfo objects.
        current: Name of the currently checked-out branch.
    """
    branches: List[GitBranchInfo] = field(default_factory=list)
    current: str = ""