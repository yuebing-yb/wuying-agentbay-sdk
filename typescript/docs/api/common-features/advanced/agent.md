# Class: Agent

## 🤖 Related Tutorial

- [Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md) - Learn about agent modules and custom agents

An Agent to manipulate applications to complete specific tasks.

## Table of contents


### Methods

- [executeTask](agent.md#executetask)
- [terminateTask](agent.md#terminatetask)

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

**`Example`**

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateAgentTask() {
  try {
    const result = await agentBay.create({ imageId: 'windows_latest' });
    if (result.success) {
      const session = result.session;

      // Execute a task with the agent
      const taskResult = await session.agent.executeTask(
        'Open notepad and type Hello World',
        10
      );

      if (taskResult.success) {
        console.log('Task completed successfully');
        // Output: Task completed successfully
        console.log(`Task ID: ${taskResult.taskId}`);
        console.log(`Task Status: ${taskResult.taskStatus}`);
        // Output: Task Status: finished
      } else {
        console.error(`Task failed: ${taskResult.errorMessage}`);
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateAgentTask().catch(console.error);
```

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
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateTerminateTask() {
  try {
    const result = await agentBay.create({ imageId: 'windows_latest' });
    if (result.success) {
      const session = result.session;

      // Start a long-running task
      const taskResult = await session.agent.executeTask(
        'Open notepad and wait for 10 minutes',
        5
      );

      if (taskResult.taskId) {
        // Terminate the task after some time
        const terminateResult = await session.agent.terminateTask(taskResult.taskId);

        if (terminateResult.success) {
          console.log('Task terminated successfully');
          // Output: Task terminated successfully
          console.log(`Task ID: ${terminateResult.taskId}`);
          console.log(`Task Status: ${terminateResult.taskStatus}`);
          // Output: Task Status: terminated
        } else {
          console.error(`Failed to terminate task: ${terminateResult.errorMessage}`);
        }
      }

      await session.delete();
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateTerminateTask().catch(console.error);
```

## Related Resources

- [Session API Reference](../../common-features/basics/session.md)

