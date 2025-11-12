# Class: Command

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
It supports both synchronous command execution with configurable timeouts.

Handles command execution operations in the AgentBay cloud environment.

## Table of contents


### Methods

- [executeCommand](#executecommand)

## Methods

### executeCommand

▸ **executeCommand**(`command`, `timeoutMs?`): `Promise`\<`CommandResult`\>

Executes a shell command in the session environment.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `command` | `string` | `undefined` | The shell command to execute. |
| `timeoutMs` | `number` | `1000` | Timeout in milliseconds. Defaults to 1000ms. |

#### Returns

`Promise`\<`CommandResult`\>

Promise resolving to CommandResult containing:
         - success: Whether the command executed successfully
         - output: Combined stdout and stderr output
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if execution failed

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const cmdResult = await result.session.command.executeCommand('echo "Hello"', 3000);
  console.log('Command output:', cmdResult.output);
  await result.session.delete();
}
```

**`Remarks`**

**Behavior:**
- Executes in a Linux shell environment
- Combines stdout and stderr in the output
- Default timeout is 1000ms (1 second)
- Command runs with session user permissions

**`See`**

[FileSystem.readFile](filesystem.md#readfile), [FileSystem.writeFile](filesystem.md#writefile)

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands


## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)

