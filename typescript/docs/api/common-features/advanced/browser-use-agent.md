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

### initialize

▸ **initialize**(`options`): `Promise`\<``InitializationResult``\>

Initialize the browser agent with specific options.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `options` | ``AgentOptions`` | agent initialization options |

#### Returns

`Promise`\<``InitializationResult``\>

InitializationResult containing success status, task output,
    and error message if any.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ imageId: 'linux_latest' });
if (result.success) {
  options:AgentOptions = new AgentOptions(use_vision=False,
output_schema=""); const initResult = await
result.session.agent.browser.initialize(options); console.log(`Initialize
success: ${initResult.success}`); await result.session.delete();
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
