# AsyncGit API Reference

## 🔀 Related Tutorial

- [Git Operations Guide](../../../../docs/guides/common-features/advanced/git-operations.md) - Learn how to manage git repositories in cloud environments

## Overview

The Git module provides high-level git operations for managing
repositories in the AgentBay cloud environment. It wraps git CLI
commands and executes them via the Command module, supporting
clone, commit, branch management, and more.


## Requirements

- Requires `code_latest` or `linux_latest` image (any image with git pre-installed)



## AsyncGit

```python
class AsyncGit(AsyncBaseService)
```

Manage git operations in the AgentBay cloud environment.

Provides a high-level interface for common git workflows (clone, commit,
branch, config, etc.) by executing git commands on the remote session via
the Command module. All commands run with ``GIT_TERMINAL_PROMPT=0`` to
prevent interactive credential prompts.

**Example**:

agent_bay = AsyncAgentBay(api_key="your_api_key")
result = await agent_bay.create()
session = result.session

clone_result = await session.git.clone(
"https://github.com/user/repo.git",
branch="main",
depth=1,
)
print("Cloned to:", clone_result.path)

### __init__

```python
def __init__(self, session)
```

### clone

```python
async def clone(url: str,
                *,
                path: Optional[str] = None,
                branch: Optional[str] = None,
                depth: Optional[int] = None,
                timeout_ms: Optional[int] = None) -> GitCloneResult
```

Clone a git repository into the remote session environment.

Supports public repositories. When *branch* is specified,
``--single-branch`` is automatically added.

**Arguments**:

    url: The repository URL to clone (HTTPS or SSH).
    path: Target directory path. If omitted, derived from the URL.
    branch: Branch to clone (adds ``--single-branch``).
    depth: Create a shallow clone with the given number of commits.
    timeout_ms: Timeout in milliseconds (default: 300 000, i.e. 5 min).
  

**Returns**:

  GitCloneResult with the cloned repository path.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitAuthError: If authentication fails.
    GitError: For other git errors.
  

**Example**:

result = await session.git.clone(
"https://github.com/user/repo.git",
branch="main",
depth=1,
)
print(result.path)

### init

```python
async def init(path: str,
               *,
               initial_branch: Optional[str] = None,
               bare: bool = False,
               timeout_ms: Optional[int] = None) -> GitInitResult
```

Initialize a new git repository in the remote session environment.

**Arguments**:

    path: Directory path to initialize as a git repository.
    initial_branch: Name of the initial branch (e.g., ``"main"``).
    bare: If True, create a bare repository.
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  GitInitResult with the initialized repository path.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitError: For other git errors.
  

**Example**:

result = await session.git.init("/home/user/project", initial_branch="main")
print(result.path)

### add

```python
async def add(repo_path: str,
              *,
              files: Optional[List[str]] = None,
              stage_all: bool = True,
              timeout_ms: Optional[int] = None) -> None
```

Add files to the git staging area.

By default (no *files* specified and *stage_all* is ``True``), stages
all changes using ``git add -A``.

**Arguments**:

    repo_path: The repository path.
    files: Specific files to add. Overrides *stage_all*.
    stage_all: Use ``git add -A`` when no files specified (default: True).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.add("/home/user/project")
await session.git.add("/home/user/project", files=["README.md"])

### commit

```python
async def commit(repo_path: str,
                 message: str,
                 *,
                 author_name: Optional[str] = None,
                 author_email: Optional[str] = None,
                 allow_empty: bool = False,
                 timeout_ms: Optional[int] = None) -> GitCommitResult
```

Create a git commit with the staged changes.

Author information, when provided, is applied as temporary ``-c``
configuration and is **not** persisted to git config.

**Arguments**:

    repo_path: The repository path.
    message: The commit message.
    author_name: Author name (temporary, not persisted).
    author_email: Author email (temporary, not persisted).
    allow_empty: Allow creating a commit with no changes.
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  GitCommitResult containing the commit hash.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.add("/home/user/project")
result = await session.git.commit("/home/user/project", "Initial commit")
print(result.commit_hash)

### status

```python
async def status(repo_path: str,
                 *,
                 timeout_ms: Optional[int] = None) -> GitStatusResult
```

Get the status of the working tree and staging area.

Returns a structured result parsed from
``git status --porcelain=1 -b``.

**Arguments**:

    repo_path: The repository path.
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  GitStatusResult with branch info and file statuses.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

status = await session.git.status("/home/user/project")
print(status.current_branch, status.is_clean)

### log

```python
async def log(repo_path: str,
              *,
              max_count: Optional[int] = None,
              timeout_ms: Optional[int] = None) -> GitLogResult
```

Get the commit history of the repository.

**Arguments**:

    repo_path: The repository path.
    max_count: Maximum number of log entries to return.
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  GitLogResult with structured commit entries.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

log = await session.git.log("/home/user/project", max_count=5)
for entry in log.entries:
print(entry.short_hash, entry.message)

### list_branches

```python
async def list_branches(
        repo_path: str,
        *,
        timeout_ms: Optional[int] = None) -> GitBranchListResult
```

List all local branches in the repository.

**Arguments**:

    repo_path: The repository path.
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  GitBranchListResult with branch info and current branch.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

branches = await session.git.list_branches("/home/user/project")
print(branches.current)

### create_branch

```python
async def create_branch(repo_path: str,
                        branch: str,
                        *,
                        checkout: bool = True,
                        timeout_ms: Optional[int] = None) -> None
```

Create a new branch in the repository.

By default the new branch is also checked out (``git checkout -b``).
Set *checkout* to ``False`` to create without switching.

**Arguments**:

    repo_path: The repository path.
    branch: The name of the new branch.
    checkout: Whether to checkout the new branch (default: True).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.create_branch("/home/user/project", "feature-x")

### checkout_branch

```python
async def checkout_branch(repo_path: str,
                          branch: str,
                          *,
                          timeout_ms: Optional[int] = None) -> None
```

Switch to an existing branch.

**Arguments**:

    repo_path: The repository path.
    branch: The branch name to switch to.
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.checkout_branch("/home/user/project", "main")

### delete_branch

```python
async def delete_branch(repo_path: str,
                        branch: str,
                        *,
                        force: bool = False,
                        timeout_ms: Optional[int] = None) -> None
```

Delete a local branch.

**Arguments**:

    repo_path: The repository path.
    branch: The branch name to delete.
    force: Force delete (``-D`` instead of ``-d``).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.delete_branch("/home/user/project", "old-branch")

### remote_add

```python
async def remote_add(repo_path: str,
                     name: str,
                     url: str,
                     *,
                     fetch: bool = False,
                     overwrite: bool = False,
                     timeout_ms: Optional[int] = None) -> None
```

Add a remote repository.

When *overwrite* is ``True``, the remote URL is updated if the remote
already exists (idempotent behaviour).

**Arguments**:

    repo_path: The repository path.
    name: The remote name (e.g., ``"origin"``).
    url: The remote URL.
    fetch: Fetch from the remote immediately after adding.
    overwrite: Update the URL if the remote already exists.
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.remote_add(
"/home/user/project", "origin",
"https://github.com/user/repo.git",
)

### remote_get

```python
async def remote_get(repo_path: str,
                     name: str,
                     *,
                     timeout_ms: Optional[int] = None) -> Optional[str]
```

Get the URL of a remote repository.

**Arguments**:

    repo_path: The repository path.
    name: The remote name (e.g., ``"origin"``).
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  The remote URL, or ``None`` if the remote does not exist.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
  

**Example**:

url = await session.git.remote_get("/home/user/project", "origin")
print(url)

### reset

```python
async def reset(repo_path: str,
                *,
                mode: Optional[str] = None,
                target: Optional[str] = None,
                paths: Optional[List[str]] = None,
                timeout_ms: Optional[int] = None) -> None
```

Reset the repository to a specific state.

**Arguments**:

    repo_path: The repository path.
    mode: Reset mode (``"soft"``, ``"mixed"``, ``"hard"``,
  ``"merge"``, or ``"keep"``).
    target: Target commit / branch / ref (defaults to HEAD).
    paths: Specific file paths to reset.
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    ValueError: If *mode* is not a valid reset mode.
    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.reset("/home/user/project", mode="hard", target="HEAD~1")

### restore

```python
async def restore(repo_path: str,
                  paths: List[str],
                  *,
                  staged: bool = False,
                  worktree: Optional[bool] = None,
                  source: Optional[str] = None,
                  timeout_ms: Optional[int] = None) -> None
```

Restore files from the index or working tree.

**Arguments**:

    repo_path: The repository path.
    paths: File paths to restore. Use ``["."]`` to restore all files.
    staged: Restore the index / staging area (``--staged``).
    worktree: Restore the working tree (``--worktree``).
  Defaults to ``True`` when *staged* is ``False``.
    source: Restore from a specific commit / branch / ref
  (``--source``).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.restore("/home/user/project", ["file.txt"])

### pull

```python
async def pull(repo_path: str,
               *,
               remote: Optional[str] = None,
               branch: Optional[str] = None,
               timeout_ms: Optional[int] = None) -> None
```

Pull changes from a remote repository.

**Arguments**:

    repo_path: The repository path.
    remote: Remote name (e.g., ``"origin"``).
    branch: Branch name to pull.
    timeout_ms: Timeout in milliseconds (default: 120 000, i.e. 2 min).
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
    GitError: For other git errors.
  

**Example**:

await session.git.pull("/home/user/project", remote="origin", branch="main")

### configure_user

```python
async def configure_user(repo_path: str,
                         name: str,
                         email: str,
                         *,
                         scope: str = "global",
                         timeout_ms: Optional[int] = None) -> None
```

Configure git user name and email.

**Arguments**:

    repo_path: The repository path.
    name: The user name.
    email: The user email.
    scope: Configuration scope (``"global"`` or ``"local"``,
    default: ``"global"``).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
  

**Example**:

await session.git.configure_user(
"/home/user/project", "Alice", "alice@example.com",
)

### set_config

```python
async def set_config(repo_path: str,
                     key: str,
                     value: str,
                     *,
                     scope: str = "global",
                     timeout_ms: Optional[int] = None) -> None
```

Set a git configuration value.

**Arguments**:

    repo_path: The repository path.
    key: The configuration key (e.g., ``"core.autocrlf"``).
    value: The configuration value.
    scope: Configuration scope (``"global"`` or ``"local"``,
    default: ``"global"``).
    timeout_ms: Timeout in milliseconds.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
  

**Example**:

await session.git.set_config("/home/user/project", "core.autocrlf", "false")

### get_config

```python
async def get_config(repo_path: str,
                     key: str,
                     *,
                     scope: str = "global",
                     timeout_ms: Optional[int] = None) -> Optional[str]
```

Get a git configuration value.

**Arguments**:

    repo_path: The repository path.
    key: The configuration key (e.g., ``"user.name"``).
    scope: Configuration scope (``"global"`` or ``"local"``,
    default: ``"global"``).
    timeout_ms: Timeout in milliseconds.
  

**Returns**:

  The configuration value, or ``None`` if the key is not found.
  

**Raises**:

    GitNotFoundError: If git is not installed.
    GitNotARepoError: If the path is not a git repository.
  

**Example**:

name = await session.git.get_config("/home/user/project", "user.name")
print(name)

## Best Practices

1. Always configure user identity before committing
2. Use depth parameter for shallow clones to save bandwidth
3. Handle GitAuthError for operations requiring authentication
4. Use timeout_ms for long-running operations like clone and pull

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

**Related APIs:**
- [Session API Reference](./async-session.md)
- [Command API Reference](./async-command.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
