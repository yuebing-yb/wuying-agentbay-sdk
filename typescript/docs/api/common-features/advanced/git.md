# Class: Git

## 🔀 Related Tutorial

- [Git Operations Guide](../../../../../docs/guides/common-features/advanced/git-operations.md) - Learn how to manage git repositories in cloud environments

## Overview

The Git module provides high-level git operations for managing
repositories in the AgentBay cloud environment. It wraps git CLI
commands and executes them via the Command module, supporting
clone, commit, branch management, and more.


## Requirements

- This feature requires `code_latest` image

Provides high-level git operations in the AgentBay cloud environment.

This module wraps git CLI commands and executes them on the remote session
via the Command module. All commands run with `GIT_TERMINAL_PROMPT=0` to
prevent interactive credential prompts, and `LC_ALL=C` to ensure consistent
English output for reliable parsing. Supports repository management, branch
operations, staging, committing, and configuration.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const cloneResult = await result.session.git.clone('https://github.com/user/repo.git');
  console.log('Cloned to:', cloneResult.path);
  await result.session.delete();
}
```

## Table of contents


### Methods

- [add](#add)
- [checkoutBranch](#checkoutbranch)
- [clone](#clone)
- [commit](#commit)
- [configureUser](#configureuser)
- [createBranch](#createbranch)
- [deleteBranch](#deletebranch)
- [init](#init)
- [listBranches](#listbranches)
- [log](#log)
- [pull](#pull)
- [remoteAdd](#remoteadd)
- [remoteGet](#remoteget)
- [reset](#reset)
- [restore](#restore)
- [setConfig](#setconfig)
- [status](#status)

## Methods

### add

▸ **add**(`repoPath`, `opts?`): `Promise`\<`void`\>

Add files to the git staging area.

By default (when no files are specified and `all` is not explicitly false),
stages all changes using `git add -A`. Specific files can be staged by
providing them in `opts.files`. A `--` separator is automatically inserted
before file paths to prevent them from being interpreted as options.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitAddOpts`` | Optional add settings (files, all, timeoutMs) |

#### Returns

`Promise`\<`void`\>

**`Throws`**

When git is not installed

**`Throws`**

When the path is not a git repository

**`Throws`**

When the add operation fails

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.add('/home/user/my-project');
  await result.session.delete();
}
```

___

### checkoutBranch

▸ **checkoutBranch**(`repoPath`, `branch`, `opts?`): `Promise`\<`void`\>

Switch to an existing branch.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `branch` | `string` | The branch name to switch to |
| `opts?` | ``GitCheckoutOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors (e.g., branch does not exist)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.checkoutBranch('/home/user/my-project', 'main');
  await result.session.delete();
}
```

___

### clone

▸ **clone**(`url`, `opts?`): `Promise`\<``GitCloneResult``\>

Clone a git repository into the remote session environment.

Clones a repository from the given URL into the remote session. When a
branch is specified, `--single-branch` is automatically added to reduce
data transfer. The target directory is derived from the URL if not
explicitly provided via `opts.path`. Currently supports public
repositories only; authentication support will be added in a future phase.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `url` | `string` | The repository URL to clone (HTTPS or SSH) |
| `opts?` | ``GitCloneOpts`` | Optional clone settings (path, branch, depth, timeoutMs) |

#### Returns

`Promise`\<``GitCloneResult``\>

Promise resolving to `GitCloneResult` with the cloned repository path

**`Throws`**

When git is not installed on the remote environment

**`Throws`**

When authentication fails (e.g., private repo without credentials)

**`Throws`**

When the clone operation fails for other reasons

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const cloneResult = await result.session.git.clone('https://github.com/user/repo.git');
  console.log('Cloned to:', cloneResult.path);
  await result.session.delete();
}
```

___

### commit

▸ **commit**(`repoPath`, `message`, `opts?`): `Promise`\<``GitCommitResult``\>

Create a git commit with the staged changes.

Author information can be provided via `authorName` and `authorEmail`,
which are applied as temporary `-c` configuration (not persisted to git config).

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `message` | `string` | The commit message |
| `opts?` | ``GitCommitOpts`` | Optional commit settings |

#### Returns

`Promise`\<``GitCommitResult``\>

Promise resolving to GitCommitResult with the commit hash

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const commitResult = await result.session.git.commit('/home/user/my-project', 'Initial commit');
  console.log('Commit hash:', commitResult.commitHash);
  await result.session.delete();
}
```

___

### configureUser

▸ **configureUser**(`repoPath`, `name`, `email`, `opts?`): `Promise`\<`void`\>

Configure git user information.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `name` | `string` | The user name |
| `email` | `string` | The user email |
| `opts?` | ``GitConfigOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.configureUser('/home/user/my-project', 'Agent', 'agent@example.com');
  await result.session.delete();
}
```

___

### createBranch

▸ **createBranch**(`repoPath`, `branch`, `opts?`): `Promise`\<`void`\>

Create a new branch in the repository.

By default, also checks out the new branch (using `git checkout -b`).
Set `opts.checkout = false` to create without switching (using `git branch`).

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `branch` | `string` | The name of the new branch |
| `opts?` | ``GitBranchCreateOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors (e.g., branch already exists)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.createBranch('/home/user/my-project', 'feature/new-feature');
  await result.session.delete();
}
```

___

### deleteBranch

▸ **deleteBranch**(`repoPath`, `branch`, `opts?`): `Promise`\<`void`\>

Delete a local branch.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `branch` | `string` | The branch name to delete |
| `opts?` | ``GitBranchDeleteOpts`` | Optional settings. Use `force: true` for `-D` (force delete) |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors (e.g., branch not fully merged)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.deleteBranch('/home/user/my-project', 'feature/old');
  await result.session.delete();
}
```

### init

▸ **init**(`path`, `opts?`): `Promise`\<``GitInitResult``\>

Initialize a new git repository in the remote session environment.

Creates an empty git repository at the specified path. Optionally sets the
initial branch name (requires git >= 2.28) and supports creating bare
repositories for server-side use.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `path` | `string` | The directory path to initialize as a git repository |
| `opts?` | ``GitInitOpts`` | Optional init settings (initialBranch, bare, timeoutMs) |

#### Returns

`Promise`\<``GitInitResult``\>

Promise resolving to `GitInitResult` with the initialized repository path

**`Throws`**

When git is not installed on the remote environment

**`Throws`**

When the init operation fails

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const initResult = await result.session.git.init('/home/user/my-project');
  console.log('Initialized at:', initResult.path);
  await result.session.delete();
}
```

___

### listBranches

▸ **listBranches**(`repoPath`, `opts?`): `Promise`\<``GitBranchListResult``\>

List all local branches in the repository.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitBranchListOpts`` | Optional settings |

#### Returns

`Promise`\<``GitBranchListResult``\>

Promise resolving to GitBranchListResult with branch info

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const branches = await result.session.git.listBranches('/home/user/my-project');
  console.log('Current branch:', branches.current);
  await result.session.delete();
}
```

___

### log

▸ **log**(`repoPath`, `opts?`): `Promise`\<``GitLogResult``\>

Get the commit history of the repository.

Returns a structured result with parsed commit entries.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitLogOpts`` | Optional log settings |

#### Returns

`Promise`\<``GitLogResult``\>

Promise resolving to GitLogResult with commit entries

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const log = await result.session.git.log('/home/user/my-project');
  console.log('Total commits:', log.entries.length);
  await result.session.delete();
}
```

___

### pull

▸ **pull**(`repoPath`, `opts?`): `Promise`\<`void`\>

Pull changes from a remote repository.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitPullOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors (e.g., no upstream configured)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.pull('/home/user/my-project');
  await result.session.delete();
}
```

___

### remoteAdd

▸ **remoteAdd**(`repoPath`, `name`, `url`, `opts?`): `Promise`\<`void`\>

Add a remote repository.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `name` | `string` | The remote name (e.g., "origin") |
| `url` | `string` | The remote URL |
| `opts?` | ``GitRemoteAddOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.remoteAdd('/home/user/my-project', 'origin', 'https://github.com/user/repo.git');
  await result.session.delete();
}
```

___

### remoteGet

▸ **remoteGet**(`repoPath`, `name`, `opts?`): `Promise`\<`undefined` \| `string`\>

Get the URL of a remote repository.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `name` | `string` | The remote name (e.g., "origin") |
| `opts?` | `Object` | Optional settings |
| `opts.timeoutMs?` | `number` | - |

#### Returns

`Promise`\<`undefined` \| `string`\>

The remote URL, or undefined if the remote does not exist

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const url = await result.session.git.remoteGet('/home/user/my-project', 'origin');
  console.log('Remote URL:', url);
  await result.session.delete();
}
```

___

### reset

▸ **reset**(`repoPath`, `opts?`): `Promise`\<`void`\>

Reset the repository to a specific state.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitResetOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.reset('/home/user/my-project');
  await result.session.delete();
}
```

___

### restore

▸ **restore**(`repoPath`, `opts`): `Promise`\<`void`\>

Restore files from the index or working tree.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts` | ``GitRestoreOpts`` | Restore options including paths (required) |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.restore('/home/user/my-project', { paths: ['src/index.ts'] });
  await result.session.delete();
}
```

___

### setConfig

▸ **setConfig**(`repoPath`, `key`, `value`, `opts?`): `Promise`\<`void`\>

Set a git configuration value.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `key` | `string` | The configuration key |
| `value` | `string` | The configuration value |
| `opts?` | ``GitConfigOpts`` | Optional settings |

#### Returns

`Promise`\<`void`\>

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  await result.session.git.setConfig('/home/user/my-project', 'pull.rebase', 'true');
  await result.session.delete();
}
```

___

### status

▸ **status**(`repoPath`, `opts?`): `Promise`\<``GitStatusResult``\>

Get the status of the working tree and staging area.

Returns a structured result parsed from `git status --porcelain=1 -b`.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `repoPath` | `string` | The repository path |
| `opts?` | ``GitStatusOpts`` | Optional status settings |

#### Returns

`Promise`\<``GitStatusResult``\>

Promise resolving to GitStatusResult with branch info and file statuses

**`Throws`**

GitNotFoundError if git is not installed

**`Throws`**

GitNotARepoError if the path is not a git repository

**`Throws`**

GitError for other git errors

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create();
if (result.success) {
  const status = await result.session.git.status('/home/user/my-project');
  console.log('Branch:', status.branch);
  console.log('Clean:', status.isClean);
  await result.session.delete();
}
```

## Best Practices

1. Always configure user identity before committing
2. Use depth parameter for shallow clones to save bandwidth
3. Handle GitAuthError for operations requiring authentication
4. Use timeout_ms for long-running operations like clone and pull


## Related Resources

- [Session API Reference](../../common-features/basics/session.md)
- [Command API Reference](../../common-features/basics/command.md)

