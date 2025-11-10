# Class: Command

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
It supports both synchronous command execution with configurable timeouts.


## Requirements

- Any session image (browser_latest, code_latest, windows_latest, mobile_latest)

Handles command execution operations in the AgentBay cloud environment.

## Table of contents


### Methods

- [executeCommand](command.md#executecommand)

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
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();

if (result.success) {
  const session = result.session;

  // Execute a simple command
  const cmdResult = await session.command.executeCommand('echo "Hello"');
  if (cmdResult.success) {
    console.log(`Output: ${cmdResult.output}`);
    // Output: Output: Hello
  }

  // Execute with custom timeout
  const longCmd = await session.command.executeCommand(
    'sleep 2 && echo "Done"',
    3000
  );

  await session.delete();
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

