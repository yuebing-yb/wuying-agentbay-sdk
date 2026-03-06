# Class: BrowserUseAgent

## Hierarchy

- `BaseTaskAgent`

  ↳ **`BrowserUseAgent`**

## Table of contents


### Properties

- [session](#session)
- [toolPrefix](#toolprefix)

### Methods

- [executeTask](#executetask)
- [executeTaskAndWait](#executetaskandwait)
- [initialize](#initialize)
- [terminateTask](#terminatetask)

## Properties

### session

• `Protected` **session**: ``McpSession``

#### Inherited from

BaseTaskAgent.session

___

### toolPrefix

• `Protected` **toolPrefix**: `string` = `'browser_use'`

#### Overrides

BaseTaskAgent.toolPrefix

## Methods

### executeTask

▸ **executeTask**\<`TSchema`\>(`task`, `use_vision?`, `output_schema?`): `Promise`\<``ExecutionResult``\>

Execute a task described in human language on a browser without waiting for completion
(non-blocking). This is a fire-and-return interface that immediately
provides a task ID. Call getTaskStatus to check the task status.

#### Type parameters

| Name | Type |
| :------ | :------ |
| `TSchema` | extends `ZodType`\<`any`, `any`, `any`, `TSchema`\> |

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | `undefined` | Task description in human language. |
| `use_vision` | `boolean` | `true` | Whether to use vision in the task. |
| `output_schema?` | `TSchema` | `undefined` | Optional Zod schema for a structured task output if you need. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status,
    and error message if any.

**`Example`**

```typescript
const WeatherSchema = z.object({city: z.string(), weather:z.string()});
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'linux_latest' });
if (result.success) {
  const execResult = await result.session.agent.browser.executeTask(
    'Query the weather in Shanghai', false, WeatherSchema
  );
  console.log(`Task ID: ${execResult.taskId}`);
  await result.session.delete();
}
```

#### Overrides

BaseTaskAgent.executeTask

___

### executeTaskAndWait

▸ **executeTaskAndWait**\<`TSchema`\>(`task`, `timeout`, `use_vision?`, `output_schema?`): `Promise`\<``ExecutionResult``\>

Execute a task described in human language on a browser synchronously.
This is a synchronous interface that blocks until the task is completed or
an error occurs, or timeout happens. The default polling interval is 3 seconds.

#### Type parameters

| Name | Type |
| :------ | :------ |
| `TSchema` | extends `ZodType`\<`any`, `any`, `any`, `TSchema`\> |

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `task` | `string` | `undefined` | Task description in human language. |
| `timeout` | `number` | `undefined` | Maximum time to wait for task completion (in seconds). Used to control how long to wait for task completion. |
| `use_vision` | `boolean` | `true` | Whether to use vision in the task. |
| `output_schema?` | `TSchema` | `undefined` | Optional Zod schema for a structured task output if you need. |

#### Returns

`Promise`\<``ExecutionResult``\>

ExecutionResult containing success status, task ID, task status,
    and error message if any.

**`Example`**

```typescript
const WeatherSchema = z.object({city: z.string(), weather:z.string()});
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'linux_latest' });
if (result.success) {
  const execResult = await result.session.agent.browser.executeTask(
    'Query the weather in Shanghai', false, WeatherSchema
  );
  console.log(`Task ID: ${execResult.taskId}`);
  const pollInterval = 3;
  const timeout = 180;
  const maxPollAttempts = Math.floor(timeout / pollInterval);
  let triedTime = 0;
  while(triedTime < maxPollAttempts) {
    const queryResult = await result.session.agent.browser.getTaskStatus(execResult.taskId);
    if (queryResult.taskStatus === 'finished') {
      console.log(`Task ${execResult.taskId} finished with result: ${queryResult.taskResult}`);
      break;
    }
    triedTime++;
  }
  await result.session.delete();
}
```

#### Overrides

BaseTaskAgent.executeTaskAndWait

### initialize

▸ **initialize**(`option?`): `Promise`\<`boolean`\>

Initialize the browser on which the agent performs tasks.
You are supposed to call this API before executeTask is called, but it's optional.
If you want to perform a hybrid usage of browser, you must call this API before executeTask is called.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `option?` | ``BrowserOption`` | Browser configuration options. If not provided, default options will be used. |

#### Returns

`Promise`\<`boolean`\>

Promise<boolean> - True if the browser is successfully initialized, False otherwise.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
const result = await agentBay.create({ imageId: 'browser_latest' });
if (result.success) {
  const success = await result.session.agent.browser.initialize();
  console.log('Browser initialized:', success);
  await result.session.delete();
}
```

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

#### Inherited from

BaseTaskAgent.terminateTask
