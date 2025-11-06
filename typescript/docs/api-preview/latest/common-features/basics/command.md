# Class: Command

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

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

Execute a command in the session environment.
Corresponds to Python's execute_command() method

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :---## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)


--- |
| `command` | `string` | `undefined` | The command to execute |
| `timeoutMs` | `number` | `1000` | The timeout in milliseconds. Default is 1000ms. |

#### Returns

`Promise`\<`CommandResult`\>

CommandResult with command output and requestId

**`Throws`**

APIError if the operation fails.
