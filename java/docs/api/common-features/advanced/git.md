# 🔀 Git API Reference

## Overview

The Git module provides high-level git operations for managing
repositories in the AgentBay cloud environment. It wraps git CLI
commands and executes them via the Command module, supporting
clone, commit, branch management, and more.


## 📚 Tutorial

[Git Operations Guide](../../../../../docs/guides/common-features/advanced/git-operations.md)

Learn how to manage git repositories in cloud environments

## 📋 Requirements

- This feature requires `code_latest` image

## Git

Manage git operations in the AgentBay cloud environment.

<p>Provides a high-level interface for common git workflows (clone, commit,
branch, config, etc.) by executing git commands on the remote session via
the Command module. All commands run with {@code GIT_TERMINAL_PROMPT=0} to
prevent interactive credential prompts.

<p><b>Example:</b>
<pre>{@code
AgentBay agentBay = new AgentBay(apiKey);
Session session = agentBay.createSession();

GitCloneResult result = session.getGit().clone(
    "https://github.com/user/repo.git", null, "main", 1, null);
System.out.println("Cloned to: " + result.getPath());

session.close();
}</pre>

### Constructor

```java
public Git(Session session)
```

Constructs a new {@code Git} service bound to the given session.

**Parameters:**
- `session` (Session): the session to execute git commands on

### Methods

### init

```java
public GitInitResult init(String path) throws GitError
```

```java
public GitInitResult init(String path, String initialBranch, boolean bare, Integer timeoutMs) throws GitError
```

Initialize a new git repository.

<p>The directory does not need to exist beforehand; git will create it.

<p><b>Example:</b>
<pre>{@code
GitInitResult result = session.getGit().init(
    "/home/user/my-project", "main", false, null);
System.out.println("Initialized at: " + result.getPath());
}</pre>

**Parameters:**
- `path` (String): the directory path to initialize
- `initialBranch` (String): name of the initial branch; may be {@code null} for git default
- `bare` (boolean): {@code true} to create a bare repository
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `GitInitResult`: init result containing the repository path

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitError`: for other git errors

### add

```java
public void add(String repoPath) throws GitError
```

```java
public void add(String repoPath, List<String> files, boolean all, Integer timeoutMs) throws GitError
```

Stage files for the next commit.

<p><b>Example:</b>
<pre>{@code
// Stage specific files
session.getGit().add(repoPath,
    Arrays.asList("src/Main.java", "README.md"), false, null);

// Stage all changes
session.getGit().add(repoPath, null, true, null);
}</pre>

**Parameters:**
- `files` (List<String>): list of specific file paths to stage; may be {@code null}
- `repoPath` (String): the repository working directory
- `all` (boolean): {@code true} to stage all changes (equivalent to {@code git add -A})
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### commit

```java
public GitCommitResult commit(String repoPath, String message) throws GitError
```

```java
public GitCommitResult commit(String repoPath, String message, String authorName, String authorEmail, boolean allowEmpty, Integer timeoutMs) throws GitError
```

Commit staged changes with full options.

<p><b>Example:</b>
<pre>{@code
session.getGit().add(repoPath);
GitCommitResult result = session.getGit().commit(
    repoPath, "feat: add new feature",
    "John Doe", "john@example.com", false, null);
System.out.println("Commit: " + result.getCommitHash());
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `message` (String): the commit message
- `authorName` (String): custom author name; may be {@code null} to use git config
- `authorEmail` (String): custom author email; may be {@code null} to use git config
- `allowEmpty` (boolean): {@code true} to allow creating a commit with no changes
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `GitCommitResult`: commit result containing the commit hash

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### status

```java
public GitStatusResult status(String repoPath) throws GitError
```

```java
public GitStatusResult status(String repoPath, Integer timeoutMs) throws GitError
```

Get the current status of a git repository.

<p>Returns branch information, tracking status, and per-file change
details parsed from {@code git status --porcelain=1 -b}.

<p><b>Example:</b>
<pre>{@code
GitStatusResult status = session.getGit().status(repoPath, null);
System.out.println("Branch: " + status.getCurrentBranch());
System.out.println("Clean: " + status.isClean());
for (GitFileStatus f : status.getFiles()) {
    System.out.println(f.getStatus() + " " + f.getPath());
}
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `GitStatusResult`: parsed status result

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### log

```java
public GitLogResult log(String repoPath) throws GitError
```

```java
public GitLogResult log(String repoPath, Integer maxCount, Integer timeoutMs) throws GitError
```

Get the commit log of a repository.

<p><b>Example:</b>
<pre>{@code
GitLogResult log = session.getGit().log(repoPath, 10, null);
for (GitLogEntry entry : log.getEntries()) {
    System.out.println(entry.getShortHash() + " " + entry.getMessage());
}
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `maxCount` (Integer): maximum number of commits to return; may be {@code null} for all
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `GitLogResult`: log result containing commit entries

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### listBranches

```java
public GitBranchListResult listBranches(String repoPath) throws GitError
```

```java
public GitBranchListResult listBranches(String repoPath, Integer timeoutMs) throws GitError
```

List all branches in a repository.

<p><b>Example:</b>
<pre>{@code
GitBranchListResult branches = session.getGit().listBranches(repoPath, null);
System.out.println("Current: " + branches.getCurrent());
for (GitBranchInfo b : branches.getBranches()) {
    System.out.println((b.isCurrent() ? "* " : "  ") + b.getName());
}
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `GitBranchListResult`: branch list result containing all branches and current branch

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### createBranch

```java
public void createBranch(String repoPath, String branch) throws GitError
```

```java
public void createBranch(String repoPath, String branch, boolean checkout, Integer timeoutMs) throws GitError
```

Create a new branch, optionally checking it out immediately.

<p><b>Example:</b>
<pre>{@code
// Create and switch to the new branch
session.getGit().createBranch(repoPath, "feature/login", true, null);

// Create without switching
session.getGit().createBranch(repoPath, "release/v1.0", false, null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `branch` (String): the new branch name
- `checkout` (boolean): {@code true} to switch to the new branch after creation
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### deleteBranch

```java
public void deleteBranch(String repoPath, String branch) throws GitError
```

```java
public void deleteBranch(String repoPath, String branch, boolean force, Integer timeoutMs) throws GitError
```

Delete a branch.

<p><b>Example:</b>
<pre>{@code
// Safe delete (must be fully merged)
session.getGit().deleteBranch(repoPath, "feature/old", false, null);

// Force delete
session.getGit().deleteBranch(repoPath, "feature/abandoned", true, null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `branch` (String): the branch name to delete
- `force` (boolean): {@code true} to force delete (uses {@code -D}) even if not fully merged
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### remoteAdd

```java
public void remoteAdd(String repoPath, String name, String url) throws GitError
```

```java
public void remoteAdd(String repoPath, String name, String url, boolean fetch, boolean overwrite, Integer timeoutMs) throws GitError
```

Add a remote repository with full options.

<p><b>Example:</b>
<pre>{@code
// Add and immediately fetch
session.getGit().remoteAdd(repoPath,
    "origin", "https://github.com/user/repo.git",
    true, false, null);

// Overwrite an existing remote
session.getGit().remoteAdd(repoPath,
    "origin", "https://github.com/user/new-repo.git",
    false, true, null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `name` (String): the remote name (e.g., {@code "origin"})
- `url` (String): the remote URL
- `fetch` (boolean): {@code true} to fetch immediately after adding
- `overwrite` (boolean): {@code true} to remove and re-add if the remote already exists
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitAuthError`: if authentication fails during fetch
- `GitError`: for other git errors

### remoteGet

```java
public String remoteGet(String repoPath, String name) throws GitError
```

```java
public String remoteGet(String repoPath, String name, Integer timeoutMs) throws GitError
```

Get the URL of a named remote.

<p><b>Example:</b>
<pre>{@code
String url = session.getGit().remoteGet(repoPath, "origin", null);
if (url != null) {
    System.out.println("Origin URL: " + url);
}
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `name` (String): the remote name
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `String`: the remote URL, or {@code null} if the remote does not exist

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### reset

```java
public void reset(String repoPath) throws GitError
```

```java
public void reset(String repoPath, String mode, String target, List<String> paths, Integer timeoutMs) throws GitError
```

Reset the current HEAD to a specified state.

<p><b>Example:</b>
<pre>{@code
// Soft reset to the previous commit
session.getGit().reset(repoPath, "soft", "HEAD~1", null, null);

// Unstage specific files
session.getGit().reset(repoPath, null, null,
    Arrays.asList("file1.txt", "file2.txt"), null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `mode` (String): reset mode ({@code "soft"}, {@code "mixed"}, or {@code "hard"}); may be {@code null}
- `target` (String): the commit reference to reset to; may be {@code null}
- `paths` (List<String>): specific paths to reset; may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### restore

```java
public void restore(String repoPath, List<String> paths) throws GitError
```

```java
public void restore(String repoPath, List<String> paths, boolean staged, Boolean worktree, String source, Integer timeoutMs) throws GitError
```

Restore working tree and/or staged files.

<p>At least one path must be specified. When {@code staged} is {@code true}
and {@code worktree} is not explicitly set, only staged changes are restored.

<p><b>Example:</b>
<pre>{@code
// Discard working tree changes
session.getGit().restore(repoPath,
    Arrays.asList("src/Main.java"), false, null, null, null);

// Unstage a file
session.getGit().restore(repoPath,
    Arrays.asList("src/Main.java"), true, null, null, null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `paths` (List<String>): list of file paths to restore (must not be empty)
- `staged` (boolean): {@code true} to restore staged changes
- `worktree` (Boolean): explicitly control worktree restore; defaults to {@code !staged}
- `source` (String): source commit to restore from; may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitError`: if paths is empty or the operation fails

### pull

```java
public void pull(String repoPath) throws GitError
```

```java
public void pull(String repoPath, String remote, String branch, Integer timeoutMs) throws GitError
```

Pull changes from a remote repository.

<p><b>Example:</b>
<pre>{@code
session.getGit().pull(repoPath, "origin", "main", null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `remote` (String): the remote name (e.g., {@code "origin"}); may be {@code null}
- `branch` (String): the branch to pull; may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 120 000 (2 min)

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitAuthError`: if authentication fails
- `GitConflictError`: if there are merge conflicts
- `GitError`: for other git errors

### configureUser

```java
public void configureUser(String repoPath, String name, String email) throws GitError
```

```java
public void configureUser(String repoPath, String name, String email, String scope, Integer timeoutMs) throws GitError
```

Configure git user name and email.

<p><b>Example:</b>
<pre>{@code
session.getGit().configureUser(repoPath,
    "John Doe", "john@example.com", "local", null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `name` (String): the user name
- `email` (String): the user email
- `scope` (String): config scope ({@code "local"}, {@code "global"}); may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### setConfig

```java
public void setConfig(String repoPath, String key, String value) throws GitError
```

```java
public void setConfig(String repoPath, String key, String value, String scope, Integer timeoutMs) throws GitError
```

Set a git configuration value.

<p><b>Example:</b>
<pre>{@code
session.getGit().setConfig(repoPath,
    "core.autocrlf", "input", "local", null);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `key` (String): the config key (e.g., {@code "user.name"})
- `value` (String): the config value
- `scope` (String): config scope ({@code "local"}, {@code "global"}); may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors

### getConfig

```java
public String getConfig(String repoPath, String key) throws GitError
```

```java
public String getConfig(String repoPath, String key, String scope, Integer timeoutMs) throws GitError
```

Get a git configuration value.

<p>Returns {@code null} if the key is not found rather than throwing
an exception.

<p><b>Example:</b>
<pre>{@code
String userName = session.getGit().getConfig(repoPath,
    "user.name", "local", null);
System.out.println("User: " + userName);
}</pre>

**Parameters:**
- `repoPath` (String): the repository working directory
- `key` (String): the config key
- `scope` (String): config scope ({@code "local"}, {@code "global"}); may be {@code null}
- `timeoutMs` (Integer): timeout in milliseconds; defaults to 30 000

**Returns:**
- `String`: the config value, or {@code null} if the key is not set

**Throws:**
- `GitNotFoundError`: if git is not installed
- `GitNotARepoError`: if the path is not a git repository
- `GitError`: for other git errors



## GitCloneResult

Result of a {@code git clone} operation.

<p>Contains the local path where the repository was cloned to.

### Constructor

```java
public GitCloneResult(String path)
```

Constructs a new {@code GitCloneResult}.

**Parameters:**
- `path` (String): the local directory path of the cloned repository



## GitInitResult

Result of a {@code git init} operation.

<p>Contains the path of the newly initialized repository.

### Constructor

```java
public GitInitResult(String path)
```

Constructs a new {@code GitInitResult}.

**Parameters:**
- `path` (String): the directory path of the initialized repository



## GitCommitResult

Result of a {@code git commit} operation.

<p>Contains the hash of the newly created commit.

### Constructor

```java
public GitCommitResult(String commitHash)
```

Constructs a new {@code GitCommitResult}.

**Parameters:**
- `commitHash` (String): the SHA-1 hash of the created commit

### Methods

### getCommitHash

```java
public String getCommitHash()
```

Returns the SHA-1 hash of the created commit.

**Returns:**
- `String`: commit hash string, or {@code null} if unavailable



## GitStatusResult

Result of a {@code git status} operation.

<p>Contains the current branch name, upstream tracking information,
ahead/behind counts, detached HEAD state, and a list of individual
file statuses. Convenience methods are provided to query the
overall repository state.

### Constructor

```java
public GitStatusResult(String currentBranch, String upstream, int ahead, int behind, boolean detached, List<GitFileStatus> files)
```

Constructs a new {@code GitStatusResult}.

**Parameters:**
- `currentBranch` (String): the current branch name
- `upstream` (String): upstream tracking branch, or {@code null}
- `ahead` (int): number of commits ahead of upstream
- `behind` (int): number of commits behind upstream
- `detached` (boolean): whether HEAD is detached
- `files` (List<GitFileStatus>): list of file status entries

### Methods

### getCurrentBranch

```java
public String getCurrentBranch()
```

Returns the current branch name.

**Returns:**
- `String`: branch name, or {@code null} if unknown

### getUpstream

```java
public String getUpstream()
```

Returns the upstream tracking branch.

**Returns:**
- `String`: upstream branch name, or {@code null} if no upstream is set

### getAhead

```java
public int getAhead()
```

Returns the number of commits the local branch is ahead of upstream.

**Returns:**
- `int`: ahead count

### getBehind

```java
public int getBehind()
```

Returns the number of commits the local branch is behind upstream.

**Returns:**
- `int`: behind count

### isDetached

```java
public boolean isDetached()
```

Returns whether HEAD is in a detached state.

**Returns:**
- `boolean`: {@code true} if HEAD is detached

### getFiles

```java
public List<GitFileStatus> getFiles()
```

Returns the list of individual file status entries.

**Returns:**
- `List<GitFileStatus>`: list of {@link GitFileStatus} objects

### isClean

```java
public boolean isClean()
```

Returns whether the working tree is clean (no changes at all).

**Returns:**
- `boolean`: {@code true} if there are no modified, staged, or untracked files

### hasChanges

```java
public boolean hasChanges()
```

Returns whether the working tree has any changes.

**Returns:**
- `boolean`: {@code true} if there are any modified, staged, or untracked files

### hasStaged

```java
public boolean hasStaged()
```

Returns whether there are any staged changes.

**Returns:**
- `boolean`: {@code true} if at least one file is staged

### hasUntracked

```java
public boolean hasUntracked()
```

Returns whether there are any untracked files.

**Returns:**
- `boolean`: {@code true} if at least one file is untracked

### hasConflicts

```java
public boolean hasConflicts()
```

Returns whether there are any merge conflicts.

**Returns:**
- `boolean`: {@code true} if at least one file has a conflict status

### getTotalCount

```java
public int getTotalCount()
```

Returns the total number of files with changes.

**Returns:**
- `int`: total file count

### getStagedCount

```java
public int getStagedCount()
```

Returns the number of staged files.

**Returns:**
- `int`: staged file count

### getUnstagedCount

```java
public int getUnstagedCount()
```

Returns the number of unstaged (modified but not staged) files.

**Returns:**
- `int`: unstaged file count

### getUntrackedCount

```java
public int getUntrackedCount()
```

Returns the number of untracked files.

**Returns:**
- `int`: untracked file count

### getConflictCount

```java
public int getConflictCount()
```

Returns the number of files with merge conflicts.

**Returns:**
- `int`: conflict file count



## GitFileStatus

Status information for a single file in a git repository.

<p>Parsed from the {@code git status --porcelain=1} output. Each entry
describes the index and working-tree status of one file.

### Constructor

```java
public GitFileStatus(String path, String status, String indexStatus, String workTreeStatus, boolean staged, String renamedFrom)
```

Constructs a new {@code GitFileStatus}.

**Parameters:**
- `path` (String): file path relative to the repository root
- `status` (String): normalized status string
- `indexStatus` (String): index status character
- `workTreeStatus` (String): working-tree status character
- `staged` (boolean): whether the change is staged
- `renamedFrom` (String): original path before rename, or {@code null}

### Methods

### getIndexStatus

```java
public String getIndexStatus()
```

Returns the index (staging area) status character.

**Returns:**
- `String`: single-character status code

### getWorkTreeStatus

```java
public String getWorkTreeStatus()
```

Returns the working-tree status character.

**Returns:**
- `String`: single-character status code

### isStaged

```java
public boolean isStaged()
```

Returns whether this change is staged for the next commit.

**Returns:**
- `boolean`: {@code true} if staged

### getRenamedFrom

```java
public String getRenamedFrom()
```

Returns the original path before a rename operation.

**Returns:**
- `String`: original file path, or {@code null} if not renamed



## GitLogResult

Result of a {@code git log} operation.

<p>Contains a list of {@link GitLogEntry} objects, each representing
one commit in the log output.

### Constructor

```java
public GitLogResult(List<GitLogEntry> entries)
```

Constructs a new {@code GitLogResult}.

**Parameters:**
- `entries` (List<GitLogEntry>): list of commit log entries

### Methods

### getEntries

```java
public List<GitLogEntry> getEntries()
```

Returns the commit log entries.

**Returns:**
- `List<GitLogEntry>`: list of {@link GitLogEntry} objects



## GitLogEntry

A single commit entry from the git log.

<p>Each entry contains the commit hash, author information, date,
and commit message.

### Constructor

```java
public GitLogEntry(String hash, String shortHash, String authorName, String authorEmail, String date, String message)
```

Constructs a new {@code GitLogEntry}.

**Parameters:**
- `hash` (String): full SHA-1 hash
- `shortHash` (String): abbreviated hash
- `authorName` (String): author name
- `authorEmail` (String): author email address
- `date` (String): ISO 8601 formatted date
- `message` (String): commit subject line

### Methods

### getHash

```java
public String getHash()
```

Returns the full SHA-1 commit hash.

**Returns:**
- `String`: 40-character hex string

### getShortHash

```java
public String getShortHash()
```

Returns the abbreviated commit hash.

**Returns:**
- `String`: short hash string

### getAuthorName

```java
public String getAuthorName()
```

Returns the author name.

**Returns:**
- `String`: author name

### getAuthorEmail

```java
public String getAuthorEmail()
```

Returns the author email address.

**Returns:**
- `String`: email address

### getDate

```java
public String getDate()
```

Returns the author date in ISO 8601 format.

**Returns:**
- `String`: date string

### getMessage

```java
public String getMessage()
```

Returns the commit subject line.

**Returns:**
- `String`: commit message



## GitBranchListResult

Result of a {@code git branch --list} operation.

<p>Contains the list of all branches and the name of the currently
checked-out branch.

### Constructor

```java
public GitBranchListResult(List<GitBranchInfo> branches, String current)
```

Constructs a new {@code GitBranchListResult}.

**Parameters:**
- `branches` (List<GitBranchInfo>): list of branch information entries
- `current` (String): name of the currently checked-out branch, or {@code null}

### Methods

### getBranches

```java
public List<GitBranchInfo> getBranches()
```

Returns the list of all branches.

**Returns:**
- `List<GitBranchInfo>`: unmodifiable list of {@link GitBranchInfo} entries

### getCurrent

```java
public String getCurrent()
```

Returns the name of the currently checked-out branch.

**Returns:**
- `String`: current branch name, or {@code null} if in detached HEAD state



## GitBranchInfo

Information about a single git branch.

<p>Returned as part of {@link GitBranchListResult} when listing
repository branches.

### Constructor

```java
public GitBranchInfo(String name, boolean current)
```

Constructs a new {@code GitBranchInfo}.

**Parameters:**
- `name` (String): the branch name
- `current` (boolean): {@code true} if this is the currently checked-out branch

### Methods

### isCurrent

```java
public boolean isCurrent()
```

Returns whether this is the currently checked-out branch.

**Returns:**
- `boolean`: {@code true} if this branch is checked out



## GitError

Base exception for all git operations.

<p>Thrown when a git command executed in the remote session exits with
a non-zero status code. Subclasses provide finer-grained error
classification (authentication, conflict, etc.).

### Constructor

```java
public GitError(String message, int exitCode, String stderr)
```

Constructs a new {@code GitError}.

**Parameters:**
- `message` (String): human-readable error description
- `exitCode` (int): the exit code returned by the git command
- `stderr` (String): the stderr output from the git command

### Methods

### getExitCode

```java
public int getExitCode()
```

Returns the exit code of the failed git command.

**Returns:**
- `int`: non-zero exit code

### getStderr

```java
public String getStderr()
```

Returns the stderr output of the failed git command.

**Returns:**
- `String`: stderr text, may be empty but never {@code null}



## GitAuthError

Thrown when a git operation fails due to an authentication error.

<p>Common triggers include invalid credentials, missing SSH keys,
expired tokens, or accessing a private repository without proper
authorization.

### Constructor

```java
public GitAuthError(String message, int exitCode, String stderr)
```

Constructs a new {@code GitAuthError}.

**Parameters:**
- `message` (String): human-readable error description
- `exitCode` (int): the exit code returned by the git command
- `stderr` (String): the stderr output from the git command



## GitConflictError

Thrown when a git operation encounters a merge or rebase conflict.

<p>Typically raised during {@code merge}, {@code pull}, or {@code rebase}
when conflicting changes cannot be automatically resolved.

### Constructor

```java
public GitConflictError(String message, int exitCode, String stderr)
```

Constructs a new {@code GitConflictError}.

**Parameters:**
- `message` (String): human-readable error description
- `exitCode` (int): the exit code returned by the git command
- `stderr` (String): the stderr output from the git command



## GitNotARepoError

Thrown when a git operation targets a directory that is not a git repository.

<p>This typically occurs when a command like {@code status} or {@code log}
is run against a path that has not been initialized with {@code git init}
or cloned.

### Constructor

```java
public GitNotARepoError(String message, int exitCode, String stderr)
```

Constructs a new {@code GitNotARepoError}.

**Parameters:**
- `message` (String): human-readable error description
- `exitCode` (int): the exit code returned by the git command
- `stderr` (String): the stderr output from the git command



## GitNotFoundError

Thrown when the git executable is not found or not installed in the
remote session environment.

<p>Ensure the session image includes git (e.g., {@code ubuntu-2204}).

### Constructor

```java
public GitNotFoundError(String message, int exitCode, String stderr)
```

Constructs a new {@code GitNotFoundError}.

**Parameters:**
- `message` (String): human-readable error description
- `exitCode` (int): the exit code returned by the git command
- `stderr` (String): the stderr output from the git command



## 💡 Best Practices

- Always configure user identity before committing
- Use depth parameter for shallow clones to save bandwidth
- Handle GitAuthError for operations requiring authentication
- Use timeout_ms for long-running operations like clone and pull

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Command API Reference](../../../api/common-features/basics/command.md)

