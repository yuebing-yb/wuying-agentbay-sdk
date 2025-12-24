# Class: ComputerUseAgent

An Agent to perform tasks on the computer.

## Hierarchy

- `BaseTaskAgent`

  ↳ **`ComputerUseAgent`**

## Table of contents


### Properties

- [session](#session)
- [toolPrefix](#toolprefix)

### Methods

- [executeTask](#executetask)
- [terminateTask](#terminatetask)

## Properties

### session

• `Protected` **session**: ``McpSession``

#### Inherited from

BaseTaskAgent.session

___

### toolPrefix

• `Protected` **toolPrefix**: `string` = `'flux'`

#### Overrides

BaseTaskAgent.toolPrefix

## Methods

### executeTask

▸ **executeTask**(`task`, `maxTryTimes`): `Promise`\<``ExecutionResult``\>

Execute a specific task described in human language.

#### Parameters

| Name | Type |
| :------ | :------ |
| `task` | `string` |
| `maxTryTimes` | `number` |

#### Returns

`Promise`\<``ExecutionResult``\>

#### Inherited from

BaseTaskAgent.executeTask

### terminateTask

▸ **terminateTask**(`taskId`): `Promise`\<``ExecutionResult``\>

Terminate a task with a specified task ID.

#### Parameters

| Name | Type |
| :------ | :------ |
| `taskId` | `string` |

#### Returns

`Promise`\<``ExecutionResult``\>

#### Inherited from

BaseTaskAgent.terminateTask
