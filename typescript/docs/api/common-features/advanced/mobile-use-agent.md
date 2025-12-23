# Class: MobileUseAgent

An Agent to perform tasks on mobile devices.

## Table of contents


### Methods

- [executeTask](#executetask)
- [executeTaskAndWait](#executetaskandwait)
- [getTaskStatus](#gettaskstatus)
- [terminateTask](#terminatetask)

## Methods

### executeTask

▸ **executeTask**(`task`, `maxSteps?`, `maxStepRetries?`): `Promise`\<``ExecutionResult``\>

Execute a task in human language without waiting for completion (non-blocking). This is a fire-and-return interface that immediately provides a task ID. Call getTaskStatus to check the task status.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | - | Task description in human language. |
| `maxSteps` | `number` | `50` | Maximum number of steps (clicks/swipes/etc.) allowed. Used to prevent infinite loops or excessive resource consumption. |
| `maxStepRetries` | `number` | `3` | Maximum retry times for MCP tool call failures at SDK level. Used to retry when callMcpTool fails (e.g., network errors, timeouts). |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status, and error message if any.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const execResult = await result.session.agent.mobile.executeTask(
    'Open WeChat app', 100, 5
  );
  console.log(`Task ID: ${execResult.taskId}`);
  await result.session.delete();
}
```

___

### executeTaskAndWait

▸ **executeTaskAndWait**(`task`, `maxSteps?`, `maxStepRetries?`, `maxTryTimes?`): `Promise`\<``ExecutionResult``\>

Execute a specific task described in human language synchronously. This is a synchronous interface that blocks until the task is completed or an error occurs, or timeout happens. The default polling interval is 3 seconds.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | - | Task description in human language. |
| `maxSteps` | `number` | `50` | Maximum number of steps (clicks/swipes/etc.) allowed. Used to prevent infinite loops or excessive resource consumption. |
| `maxStepRetries` | `number` | `3` | Maximum retry times for MCP tool call failures at SDK level. Used to retry when callMcpTool fails (e.g., network errors, timeouts). |
| `maxTryTimes` | `number` | `300` | Maximum number of polling attempts (each 3 seconds). Used to control how long to wait for task completion. Default is 300 (about 15 minutes). |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status, and error message if any.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const execResult = await result.session.agent.mobile.executeTaskAndWait(
    'Open WeChat app', 100, 3, 200
  );
  console.log(`Task result: ${execResult.taskResult}`);
  await result.session.delete();
}
```

___

### getTaskStatus

▸ **getTaskStatus**(`taskId`): `Promise`\<``QueryResult``\>

Get the status of the task with the given task ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `taskId` | `string` | The ID of the task. |

#### Returns

`Promise`\<``QueryResult``\>

QueryResult containing task status, task action, and task product.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const execResult = await result.session.agent.mobile.executeTask(
    'Open WeChat app', 100, 5
  );
  const statusResult = await result.session.agent.mobile.getTaskStatus(
    execResult.taskId
  );
  console.log(`Task status: ${statusResult.taskStatus}`);
  await result.session.delete();
}
```

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

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'mobile_latest' });
if (result.success) {
  const taskResult = await result.session.agent.mobile.executeTask(
    'Open WeChat app', 100, 5
  );
  const terminateResult = await result.session.agent.mobile.terminateTask(
    taskResult.taskId
  );
  console.log(`Terminated: ${terminateResult.taskStatus}`);
  await result.session.delete();
}
```

