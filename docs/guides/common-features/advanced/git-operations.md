# Git Operations

The Git module provides high-level git operations for managing repositories in the AgentBay cloud environment, wrapping git CLI commands and executing them via the Command module.

> **Multi-language support:** Code examples use Python. These APIs are available in all SDKs with similar patterns. See: [Python](../../../../python/README.md) | [TypeScript](../../../../typescript/README.md) | [Golang](../../../../golang/README.md) | [Java](../../../../java/README.md)

## Overview

The Git module provides:
- **Repository Management**: Clone, init, and manage git repositories
- **Branch Operations**: Create, checkout, list, and delete branches
- **Staging & Committing**: Add files, create commits, view status and history
- **Remote Management**: Add remotes, pull changes, configure URLs
- **Configuration**: Set user identity and arbitrary git config values
- **Error Classification**: Typed exceptions for auth, conflict, not-a-repo, and not-found errors

## Prerequisites

Before using Git operations, you need:
1. An active AgentBay session with `code_latest` or `linux_latest` image (any image with git pre-installed)
2. A valid AgentBay API Key

## Quick Start

A complete clone → status → commit workflow:

```python
import os
from agentbay import AgentBay
from agentbay import CreateSessionParams

agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

params = CreateSessionParams(image_id="code_latest")
result = agent_bay.create(params)
session = result.session

try:
    # Clone a repository
    clone_result = session.git.clone(
        "https://github.com/user/repo.git",
        branch="main",
        depth=1,
    )
    print(f"Cloned to: {clone_result.path}")

    repo = clone_result.path

    # Check repository status
    status = session.git.status(repo)
    print(f"Branch: {status.current_branch}, Clean: {status.is_clean}")

    # Make changes, stage, and commit
    session.command.execute_command(f"echo 'hello' > {repo}/new_file.txt")
    session.git.add(repo)
    commit = session.git.commit(
        repo, "Add new file",
        author_name="Alice", author_email="alice@example.com",
    )
    print(f"Committed: {commit.commit_hash}")

finally:
    agent_bay.delete(session)
```

## Common Scenarios

### Repository Management

#### Clone a Repository

```python
# Basic clone
result = session.git.clone("https://github.com/user/repo.git")
print(result.path)

# Shallow clone with specific branch
result = session.git.clone(
    "https://github.com/user/repo.git",
    branch="develop",
    depth=1,
)

# Clone to a custom path with extended timeout
result = session.git.clone(
    "https://github.com/user/large-repo.git",
    path="/home/user/my-project",
    timeout_ms=600000,  # 10 minutes
)
```

#### Initialize a New Repository

```python
# Initialize with default branch
result = session.git.init("/home/user/new-project", initial_branch="main")
print(result.path)

# Initialize a bare repository
result = session.git.init("/home/user/bare-repo.git", bare=True)
```

### Branch Operations

```python
repo = "/home/user/project"

# List all local branches
branches = session.git.list_branches(repo)
print(f"Current branch: {branches.current}")
for b in branches.branches:
    marker = " *" if b.is_current else ""
    print(f"  {b.name}{marker}")

# Create and checkout a new branch
session.git.create_branch(repo, "feature-x")

# Create without checking out
session.git.create_branch(repo, "feature-y", checkout=False)

# Switch to an existing branch
session.git.checkout_branch(repo, "main")

# Delete a branch
session.git.delete_branch(repo, "feature-y")

# Force delete an unmerged branch
session.git.delete_branch(repo, "old-branch", force=True)
```

### Staging and Committing

```python
repo = "/home/user/project"

# Stage all changes
session.git.add(repo)

# Stage specific files
session.git.add(repo, files=["README.md", "src/main.py"])

# Commit with inline author (not persisted to git config)
result = session.git.commit(
    repo, "Fix bug in parser",
    author_name="Bob", author_email="bob@example.com",
)
print(f"Commit hash: {result.commit_hash}")

# Check status
status = session.git.status(repo)
print(f"Branch: {status.current_branch}")
print(f"Clean: {status.is_clean}")
for f in status.files:
    print(f"  [{f.status}] {f.path} (staged={f.staged})")

# View commit history
log = session.git.log(repo, max_count=5)
for entry in log.entries:
    print(f"  {entry.short_hash} {entry.message} ({entry.author_name})")
```

### Remote Repositories

```python
repo = "/home/user/project"

# Add a remote
session.git.remote_add(repo, "origin", "https://github.com/user/repo.git")

# Add with fetch and idempotent overwrite
session.git.remote_add(
    repo, "origin", "https://github.com/user/repo.git",
    fetch=True, overwrite=True,
)

# Get remote URL
url = session.git.remote_get(repo, "origin")
print(f"Origin URL: {url}")  # None if remote doesn't exist

# Pull changes
session.git.pull(repo, remote="origin", branch="main")
```

### Reset and Restore

```python
repo = "/home/user/project"

# Soft reset (keep changes staged)
session.git.reset(repo, mode="soft", target="HEAD~1")

# Hard reset (discard all changes)
session.git.reset(repo, mode="hard", target="HEAD")

# Reset specific files
session.git.reset(repo, paths=["file.txt"])

# Restore a file from working tree
session.git.restore(repo, ["file.txt"])

# Unstage a file (restore from staging area)
session.git.restore(repo, ["file.txt"], staged=True)

# Restore from a specific commit
session.git.restore(repo, ["file.txt"], source="HEAD~2")
```

### Configuration

```python
repo = "/home/user/project"

# Configure user identity (recommended before committing)
session.git.configure_user(repo, "Alice", "alice@example.com")

# Use local scope (per-repository)
session.git.configure_user(
    repo, "Alice", "alice@example.com", scope="local",
)

# Set arbitrary config values
session.git.set_config(repo, "core.autocrlf", "false")

# Get config values
name = session.git.get_config(repo, "user.name")
print(f"User: {name}")  # None if not set
```

## Error Handling

The Git module raises typed exceptions for different failure scenarios:

```python
from agentbay.git import (
    GitError,
    GitAuthError,
    GitConflictError,
    GitNotARepoError,
    GitNotFoundError,
)

try:
    session.git.clone("https://github.com/private/repo.git")
except GitAuthError as e:
    print(f"Authentication failed: {e}")
    print(f"Exit code: {e.exit_code}, Stderr: {e.stderr}")
except GitNotFoundError as e:
    print(f"Git not installed: {e}")
except GitError as e:
    print(f"Git error: {e}")
```

**Exception Hierarchy:**

| Exception | Trigger |
|---|---|
| `GitError` | Base class for all git errors |
| `GitAuthError` | Authentication or permission failures |
| `GitConflictError` | Merge or rebase conflicts |
| `GitNotARepoError` | Path is not a git repository |
| `GitNotFoundError` | Git is not installed or not accessible |

All exceptions include `exit_code` and `stderr` attributes for diagnostics.

## Complete Example

```python
import os
from agentbay import AgentBay, CreateSessionParams
from agentbay.git import GitAuthError, GitError

agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

params = CreateSessionParams(image_id="code_latest")
result = agent_bay.create(params)
session = result.session

try:
    # 1. Initialize a new repository
    init_result = session.git.init("/home/user/demo", initial_branch="main")
    repo = init_result.path
    print(f"✓ Initialized repo at {repo}")

    # 2. Configure user identity
    session.git.configure_user(repo, "Alice", "alice@example.com")
    print("✓ User configured")

    # 3. Create a file and make initial commit
    session.command.execute_command(f"echo '# Demo' > {repo}/README.md")
    session.git.add(repo)
    commit = session.git.commit(repo, "Initial commit")
    print(f"✓ Initial commit: {commit.commit_hash}")

    # 4. Create a feature branch and make changes
    session.git.create_branch(repo, "feature")
    session.command.execute_command(f"echo 'new feature' > {repo}/feature.txt")
    session.git.add(repo)
    session.git.commit(repo, "Add feature")
    print("✓ Feature branch committed")

    # 5. Switch back to main and view branches
    session.git.checkout_branch(repo, "main")
    branches = session.git.list_branches(repo)
    print(f"✓ Branches: {[b.name for b in branches.branches]}")

    # 6. View commit history
    log = session.git.log(repo, max_count=10)
    for entry in log.entries:
        print(f"  {entry.short_hash} - {entry.message}")

    # 7. Check status
    status = session.git.status(repo)
    print(f"✓ Status: branch={status.current_branch}, clean={status.is_clean}")

except GitAuthError as e:
    print(f"✗ Auth error: {e}")
except GitError as e:
    print(f"✗ Git error: {e}")
finally:
    agent_bay.delete(session)
    print("✓ Session deleted")
```

## Best Practices

1. **Configure User Identity First**: Always call `configure_user()` before committing to avoid "Author identity unknown" errors
2. **Use Shallow Clones**: Set `depth=1` for large repositories to save bandwidth and disk space
3. **Set Timeouts for Long Operations**: Use `timeout_ms` for clone and pull operations on large repositories
4. **Handle Authentication Errors**: Catch `GitAuthError` when working with private repositories
5. **Use Idempotent Remote Add**: Set `overwrite=True` in `remote_add()` to avoid errors when re-running scripts
6. **Check Status Before Committing**: Call `status()` to verify there are staged changes before `commit()`
7. **Clean Up Sessions**: Always delete sessions in a `finally` block to avoid resource leaks

## Limitations

1. **Session Requirement**: All git operations require an active AgentBay session
2. **Image Compatibility**: Git must be pre-installed in the session image; use `code_latest` for guaranteed availability
3. **No Push Support**: The current API does not include a `push()` method; use `session.command.execute_command("git push ...")` as a workaround
4. **Local Branches Only**: `list_branches()` returns local branches only; use `session.command.execute_command("git branch -r")` for remote branches

## Related Documentation

- [Session Management](../basics/session-management.md)
- [Command Execution](../basics/command-execution.md)
