# Class: Agent

An Agent to manipulate applications to complete specific tasks.

## Table of contents

### Constructors

- [constructor](agent.md#constructor)

### Methods

- [executeTask](agent.md#executetask)
- [getTaskStatus](agent.md#gettaskstatus)
- [terminateTask](agent.md#terminatetask)

## Constructors

### constructor

• **new Agent**(`session`): [`Agent`](agent.md)

Initialize an Agent object.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `session` | ``McpSession`` | The Session instance that this Agent belongs to. |

#### Returns

[`Agent`](agent.md)

## Methods

### executeTask

▸ **executeTask**(`task`, `maxTryTimes`): `Promise`\<``ExecutionResult``\>

Execute a specific task described in human language.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `task` | `string` | Task description in human language. |
| `maxTryTimes` | `number` | Maximum number of retry attempts. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task output, and error message if any.

___

### getTaskStatus

▸ **getTaskStatus**(`taskId`): `Promise`\<``QueryResult``\>

Get the status of the task with the given task ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `taskId` | `string` | Task ID |

#### Returns

`Promise`\<``QueryResult``\>

QueryResult containing the task status

___

### terminateTask

▸ **terminateTask**(`taskId`): `Promise`\<``ExecutionResult``\>

Terminate a task with a specified task ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `taskId` | `string` | The ID of the running task. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task output, and error message if any.
