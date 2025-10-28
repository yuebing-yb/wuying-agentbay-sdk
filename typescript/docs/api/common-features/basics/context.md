# Context API Reference

The Context API provides functionality for managing persistent storage contexts in the AgentBay cloud environment. Contexts allow you to persist data across sessions and reuse it in future sessions.

## Context Class

The `Context` class represents a persistent storage context in the AgentBay cloud environment.

### Properties

```typescript
id  // The unique identifier of the context
name  // The name of the context
createdAt  // Date and time when the Context was created
lastUsedAt  // Date and time when the Context was last used
```

## ContextService Class

The `ContextService` class provides methods for managing persistent contexts in the AgentBay cloud environment.

### list

Lists all available contexts with pagination support.

```typescript
list(params?: ContextListParams): Promise<ContextListResult>
```

**Parameters:**
- `params` (ContextListParams, optional): Pagination parameters. If not provided, default values are used (maxResults=10).

**Returns:**
- `Promise<ContextListResult>`: A promise that resolves to a result object containing the list of Context objects, pagination info, and request ID.

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// List all contexts (using default pagination)
async function listContexts() {
  try {
    const result = await agentBay.context.list();
    if (result.success) {
      console.log(`Found ${result.contexts.length} contexts:`);
      // Expected: Found X contexts (where X is the number of contexts, max 10 by default)
      console.log(`Request ID: ${result.requestId}`);
      // Expected: A valid UUID-format request ID
      result.contexts.slice(0, 3).forEach(context => {
        console.log(`Context ID: ${context.id}, Name: ${context.name}`);
        // Expected output: Context ID: SdkCtx-xxx, Name: xxx
      });
    } else {
      console.log('Failed to list contexts');
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

listContexts();
```

### get

Gets a context by name. Optionally creates it if it doesn't exist.

```typescript
get(name: string, create?: boolean): Promise<ContextResult>
```

**Parameters:**
- `name` (string): The name of the context to get.
- `create` (boolean, optional): Whether to create the context if it doesn't exist. Defaults to false.

**Returns:**
- `Promise<ContextResult>`: A promise that resolves to a result object containing the Context object and request ID.

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Get a context, creating it if it doesn't exist
async function getOrCreateContext() {
  try {
    const result = await agentBay.context.get('my-persistent-context', true);
    if (result.success) {
      const context = result.context;
      console.log(`Context ID: ${context.id}, Name: ${context.name}`);
      // Expected output: Context ID: SdkCtx-xxx, Name: my-persistent-context
      console.log(`Request ID: ${result.requestId}`);
      // Expected: A valid UUID-format request ID
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

getOrCreateContext();
```

### create

Creates a new context.

```typescript
create(name: string): Promise<ContextResult>
```

**Parameters:**
- `name` (string): The name of the context to create.

**Returns:**
- `Promise<ContextResult>`: A promise that resolves to a result object containing the created Context object and request ID.

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Create a new context
async function createContext() {
  try {
    const result = await agentBay.context.create('my-new-context');
    if (result.success) {
      const context = result.context;
      console.log(`Created context with ID: ${context.id}, Name: ${context.name}`);
    } else {
      console.log(`Failed to create context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

createContext();
```

### update

Updates an existing context.

```typescript
update(context: Context): Promise<OperationResult>
```

**Parameters:**
- `context` (Context): The context object to update.

**Returns:**
- `Promise<OperationResult>`: A promise that resolves to a result object containing success status, request ID, and error message if any.

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Update an existing context
async function updateContext() {
  try {
    // Get an existing context
    const result = await agentBay.context.get('my-context');
    if (result.success) {
      const context = result.context;

      // Update the context name
      context.name = 'my-updated-context';

      // Save the changes
      const updateResult = await agentBay.context.update(context);
      if (updateResult.success) {
        console.log(`Context updated successfully, request ID: ${updateResult.requestId}`);
      } else {
        console.log(`Failed to update context: ${updateResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

updateContext();
```

### delete

Deletes a context.

```typescript
delete(context: Context): Promise<OperationResult>
```

**Parameters:**
- `context` (Context): The context object to delete.

**Returns:**
- `Promise<OperationResult>`: A promise that resolves to a result object containing success status, request ID, and error message if any.

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Delete an existing context
async function deleteContext() {
  try {
    // Get an existing context
    const result = await agentBay.context.get('my-context');
    if (result.success) {
      const context = result.context;

      // Delete the context
      const deleteResult = await agentBay.context.delete(context);
      if (deleteResult.success) {
        console.log(`Context deleted successfully, request ID: ${deleteResult.requestId}`);
      } else {
        console.log(`Failed to delete context: ${deleteResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

deleteContext();
```

### clear

Clears the context's persistent data.

```typescript
clear(contextId: string, timeout?: number, pollInterval?: number): Promise<ClearContextResult>
```

**Parameters:**
- `contextId` (string): The unique identifier of the context to clear.
- `timeout` (number, optional): Timeout in seconds to wait for task completion. Default is 60 seconds.
- `pollInterval` (number, optional): Interval in seconds between status polls. Default is 2.0 seconds.

**Returns:**
- `Promise<ClearContextResult>`: A promise that resolves to a result object containing the final task result. The status field will be "available" on success.

**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
- "in-use": Context is being used
- "pre-available": Context is being prepared

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Clear context data
async function clearContext() {
  try {
    // Get an existing context
    const result = await agentBay.context.get('my-context');
    if (result.success && result.context) {
      const context = result.context;

      // Clear context data synchronously (wait for completion)
      const clearResult = await agentBay.context.clear(context.id);
      if (clearResult.success) {
        console.log(`Context data cleared successfully`);
        console.log(`Final Status: ${clearResult.status}`);
        // Expected output: Final Status: available
        console.log(`Request ID: ${clearResult.requestId}`);
        // Expected: A valid UUID-format request ID
      } else {
        console.log(`Failed to clear context: ${clearResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

clearContext();
```

### clearAsync

Asynchronously initiates a task to clear the context's persistent data.

```typescript
clearAsync(contextId: string): Promise<ClearContextResult>
```

**Parameters:**
- `contextId` (string): The unique identifier of the context to clear.

**Returns:**
- `Promise<ClearContextResult>`: A promise that resolves to a result object indicating the task has been successfully started, with status field set to "clearing".

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Start clearing context data asynchronously
async function clearContextAsync() {
  try {
    // Get an existing context
    const result = await agentBay.context.get('my-context');
    if (result.success && result.context) {
      const context = result.context;

      // Start clearing context data asynchronously (non-blocking)
      const clearResult = await agentBay.context.clearAsync(context.id);
      if (clearResult.success) {
        console.log(`Clear task started: Success=${clearResult.success}, Status=${clearResult.status}`);
        // Expected output: Clear task started: Success=true, Status=clearing
        console.log(`Request ID: ${clearResult.requestId}`);
        // Expected: A valid UUID-format request ID
      } else {
        console.log(`Failed to start clear: ${clearResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

clearContextAsync();
```

### getClearStatus

Queries the status of the clearing task.

```typescript
getClearStatus(contextId: string): Promise<ClearContextResult>
```

**Parameters:**
- `contextId` (string): The unique identifier of the context to check.

**Returns:**
- `Promise<ClearContextResult>`: A promise that resolves to a result object containing the current task status.

**State Transitions:**
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)
- "in-use": Context is being used
- "pre-available": Context is being prepared

**Example:**
```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

// Initialize the SDK
const agentBay = new AgentBay({ apiKey: 'your_api_key' });

// Check clearing status
async function checkClearStatus() {
  try {
    // Get an existing context
    const result = await agentBay.context.get('my-context');
    if (result.success && result.context) {
      const context = result.context;

      // Check clearing status
      const statusResult = await agentBay.context.getClearStatus(context.id);
      if (statusResult.success) {
        console.log(`Current status: ${statusResult.status}`);
        console.log(`Request ID: ${statusResult.requestId}`);
        // Expected: Current status: clearing/available/in-use/pre-available
      } else {
        console.log(`Failed to get status: ${statusResult.errorMessage}`);
      }
    } else {
      console.log(`Failed to get context: ${result.errorMessage}`);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

checkClearStatus();
```

## Related Resources

- [Session API Reference](session.md)
- [ContextManager API Reference](context-manager.md)