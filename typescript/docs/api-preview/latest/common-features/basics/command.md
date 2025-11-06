# Class: Command

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

Handles command execution operations in the AgentBay cloud environment.

## Table of contents

### Constructors

- [constructor](command.md#constructor)

### Methods

- [executeCommand](command.md#executecommand)

## Constructors

### constructor

• **new Command**(`session`): [`Command`](command.md)

Initialize a Command object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | [`Session`](session.md) | The Session instance that this Command belongs to. |

#### Returns

[`Command`](command.md)

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

## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)

