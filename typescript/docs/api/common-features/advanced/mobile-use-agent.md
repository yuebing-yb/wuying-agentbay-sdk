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
- [terminateTask](#terminatetask)

## Properties

### session

• `Protected` **session**: ``McpSession``

#### Inherited from

BaseTaskAgent.session

___

### toolPrefix

• `Protected` **toolPrefix**: `string` = `''`

#### Overrides

BaseTaskAgent.toolPrefix

## Methods

### executeTask

▸ **executeTask**(`task`, `maxSteps?`): `Promise`\<``ExecutionResult``\>

Execute a task in human language without waiting for completion
(non-blocking). This is a fire-and-return interface that immediately
provides a task ID. Call getTaskStatus to check the task status.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | `undefined` | Task description in human language. |
| `maxSteps` | `number` | `50` | Maximum number of steps (clicks/swipes/etc.) allowed. Used to prevent infinite loops or excessive resource consumption. Default is 50. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status,
    and error message if any.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const execResult = await result.session.agent.mobile.executeTask(
    'Open WeChat app', 100
  );
  console.log(`Task ID: ${execResult.taskId}`);
  await result.session.delete();
}
```

#### Overrides

BaseTaskAgent.executeTask

___

### executeTaskAndWait

▸ **executeTaskAndWait**(`task`, `timeout`, `maxSteps?`): `Promise`\<``ExecutionResult``\>

Execute a specific task described in human language synchronously.
This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is
3 seconds.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | `undefined` | Task description in human language. |
| `timeout` | `number` | `undefined` | Maximum time to wait for task completion (in seconds). Used to control how long to wait for task completion. |
| `maxSteps` | `number` | `50` | Maximum number of steps (clicks/swipes/etc.) allowed. Used to prevent infinite loops or excessive resource consumption. Default is 50. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status,
    and error message if any.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const execResult = await result.session.agent.mobile.executeTaskAndWait(
    'Open WeChat app', 180, 100
  );
  console.log(`Task result: ${execResult.taskResult}`);
  await result.session.delete();
}
```

#### Overrides

BaseTaskAgent.executeTaskAndWait

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
