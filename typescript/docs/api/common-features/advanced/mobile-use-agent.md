# Class: MobileUseAgent

An Agent to perform tasks on mobile devices.

## Hierarchy

- `BaseTaskAgent`

  ↳ **`MobileUseAgent`**

## Table of contents


### Properties

- [session](#session)
- [toolPrefix](#toolprefix)

### Methods

- [executeTask](#executetask)
- [executeTaskAndWait](#executetaskandwait)
- [executeTaskStreamWs](#executetaskstreamws)
- [hasStreamingParams](#hasstreamingparams)
- [resolveAgentTarget](#resolveagenttarget)
- [startTaskStreamWs](#starttaskstreamws)
- [terminateTask](#terminatetask)

## Properties

### session

• `Protected` **session**: ``McpSession``

#### Inherited from

BaseTaskAgent.session

___

### toolPrefix

• `Protected` **toolPrefix**: `string` = `""`

#### Overrides

BaseTaskAgent.toolPrefix

## Methods

### executeTask

▸ **executeTask**(`task`, `options?`): `Promise`\<``TaskExecution``\>

Execute a task in human language without waiting for completion
(non-blocking). Returns TaskExecution; call wait() to block until done.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `task` | `string` | Task description in human language. |
| `options?` | ``MobileTaskOptions`` | Optional MobileTaskOptions (maxSteps, streaming callbacks). |

#### Returns

`Promise`\<``TaskExecution``\>

TaskExecution with taskId and wait() method.

#### Overrides

BaseTaskAgent.executeTask

___

### executeTaskAndWait

▸ **executeTaskAndWait**(`task`, `timeout`, `options?`): `Promise`\<``ExecutionResult``\>

Execute a task described in human language synchronously.
Blocks until the task is completed, an error occurs, or timeout.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `task` | `string` | Task description in human language. |
| `timeout` | `number` | Maximum time to wait for task completion (in seconds). |
| `options?` | ``MobileTaskOptions`` | Optional MobileTaskOptions (maxSteps, streaming callbacks). |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status.

#### Overrides

BaseTaskAgent.executeTaskAndWait

___

### executeTaskStreamWs

▸ **executeTaskStreamWs**(`params`): `Promise`\<``ExecutionResult``\>

Execute a task via WebSocket streaming channel.

#### Parameters

| Name | Type |
| :------ | :------ |
| `params` | `Object` |
| `params.options?` | ``AgentStreamingOptions`` \| ``MobileTaskOptions`` |
| `params.taskParams` | `Record`\<`string`, `any`\> |
| `params.timeout` | `number` |

#### Returns

`Promise`\<``ExecutionResult``\>

#### Inherited from

BaseTaskAgent.executeTaskStreamWs

### hasStreamingParams

▸ **hasStreamingParams**(`options?`): `boolean`

Check if any streaming option is provided.

#### Parameters

| Name | Type |
| :------ | :------ |
| `options?` | ``AgentStreamingOptions`` \| ``MobileTaskOptions`` |

#### Returns

`boolean`

#### Inherited from

BaseTaskAgent.hasStreamingParams

___

### resolveAgentTarget

▸ **resolveAgentTarget**(): `string`

Resolve the WS target for this agent from MCP tools list.

#### Returns

`string`

#### Inherited from

BaseTaskAgent.resolveAgentTarget

___

### startTaskStreamWs

▸ **startTaskStreamWs**(`params`): `Promise`\<\{ `context`: \{ `errors`: `Error`[] ; `finalContentParts`: `string`[] ; `lastError`: `undefined` \| `Record`\<`string`, `any`\>  } ; `handle`: \{ `cancel`: () => `Promise`\<`void`\> ; `invocationId`: `string` ; `waitEnd`: () => `Promise`\<`any`\> ; `write`: (`data`: `Record`\<`string`, `any`\>) => `Promise`\<`void`\>  }  }\>

Start a task via WebSocket streaming channel. Returns handle and context
immediately without blocking. Use handle.waitEnd() to await completion.

#### Parameters

| Name | Type |
| :------ | :------ |
| `params` | `Object` |
| `params.options?` | ``AgentStreamingOptions`` \| ``MobileTaskOptions`` |
| `params.taskParams` | `Record`\<`string`, `any`\> |

#### Returns

`Promise`\<\{ `context`: \{ `errors`: `Error`[] ; `finalContentParts`: `string`[] ; `lastError`: `undefined` \| `Record`\<`string`, `any`\>  } ; `handle`: \{ `cancel`: () => `Promise`\<`void`\> ; `invocationId`: `string` ; `waitEnd`: () => `Promise`\<`any`\> ; `write`: (`data`: `Record`\<`string`, `any`\>) => `Promise`\<`void`\>  }  }\>

#### Inherited from

BaseTaskAgent.startTaskStreamWs

___

### terminateTask

▸ **terminateTask**(`taskId`): `Promise`\<``ExecutionResult``\>

Terminate a task with a specified task ID.

#### Parameters

| Name | Type |
| :------ | :------ |
| `taskId` | `string` |

#### Returns

`Promise`\<``ExecutionResult``\>

#### Overrides

BaseTaskAgent.terminateTask
