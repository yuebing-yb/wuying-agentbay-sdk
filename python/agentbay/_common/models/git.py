from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class GitCloneResult:
    """Result of a successful git clone operation."""
    path: str

@dataclass
class GitInitResult:
    """Result of a successful git init operation."""
    path: str

@dataclass
class GitCommitResult:
    """Result of a successful git commit operation."""
    commit_hash: Optional[str] = None

@dataclass
class GitFileStatus:
    """Parsed git status entry for a file.

    :param path: Path relative to the repository root
    :param status: Normalized status string (e.g. "modified", "added", "deleted", "renamed", "untracked", "conflict")
    :param index_status: Index status character from porcelain output
    :param work_tree_status: Working tree status character from porcelain output
    :param staged: Whether the change is staged
    :param renamed_from: Original path when the file was renamed
    """
    path: str
    status: str
    index_status: str
    work_tree_status: str
    staged: bool
    renamed_from: Optional[str] = None

@dataclass
class GitStatusResult:
    """Parsed git repository status (E2B-aligned).

    :param current_branch: Current branch name, if available
    :param upstream: Upstream branch name, if available
    :param ahead: Number of commits the branch is ahead of upstream
    :param behind: Number of commits the branch is behind upstream
    :param detached: Whether HEAD is detached
    :param files: List of file status entries
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
    """A single entry in the git log."""
    hash: str
    short_hash: str
    author_name: str
    author_email: str
    date: str
    message: str

@dataclass
class GitLogResult:
    """Result of a git log operation."""
    entries: List[GitLogEntry] = field(default_factory=list)

@dataclass
class GitBranchInfo:
    """Information about a single branch."""
    name: str
    is_current: bool

@dataclass
class GitBranchListResult:
    """Result of listing branches."""
    branches: List[GitBranchInfo] = field(default_factory=list)
    current: str = ""