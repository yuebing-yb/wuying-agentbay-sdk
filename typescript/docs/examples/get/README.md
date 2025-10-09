# Get API Example

This example demonstrates how to use the `get` API to retrieve a session by its ID.

## Description

The `get` API allows you to retrieve a session object by providing its session ID. This is useful when you have a session ID from a previous operation and want to access or manage that session.

## Prerequisites

- Node.js 16 or higher
- TypeScript 4.5 or higher
- Valid API key set in `AGENTBAY_API_KEY` environment variable
- wuying-agentbay-sdk package installed

## Installation

```bash
npm install wuying-agentbay-sdk
# or
yarn add wuying-agentbay-sdk
```

## Usage

```bash
# Set your API key
export AGENTBAY_API_KEY="your-api-key-here"

# Compile and run the example
npx ts-node main.ts
```

## Code Example

```typescript
import { AgentBay } from "wuying-agentbay-sdk";

async function main() {
  // Initialize AgentBay client
  const apiKey = process.env.AGENTBAY_API_KEY;
  const agentBay = new AgentBay({ apiKey });

  // Retrieve a session by ID
  const sessionId = "your-session-id";
  const session = await agentBay.get(sessionId);

  console.log(`Retrieved session: ${session.sessionId}`);

  // Use the session for further operations
  // ...
}

main();
```

## API Reference

### get

```typescript
async get(sessionId: string): Promise<Session>
```

Get a session by its ID.

**Parameters:**
- `sessionId` (string): The ID of the session to retrieve

**Returns:**
- `Promise<Session>`: Promise resolving to the Session instance

**Throws:**
- `Error`: If `sessionId` is not provided or is empty
- `Error`: If the API call fails or session is not found

## Expected Output

```
Creating a session...
Created session with ID: session-xxxxxxxxxxxxx

Retrieving session using Get API...
Successfully retrieved session:
  Session ID: session-xxxxxxxxxxxxx

Session is ready for use

Cleaning up...
Session session-xxxxxxxxxxxxx deleted successfully
```

## Notes

- The session ID must be valid and from an existing session
- The get API internally calls the GetSession API endpoint
- The returned session object can be used for all session operations (commands, files, etc.)
- Always clean up sessions when done to avoid resource waste

## Error Handling

The `get` method will throw errors in the following cases:

1. **Error**: When session_id is empty or undefined
   ```typescript
   try {
     await agentBay.get("");
   } catch (error) {
     console.error("Invalid input:", error);
   }
   ```

2. **Error**: When the API call fails or session is not found
   ```typescript
   try {
     await agentBay.get("non-existent-session-id");
   } catch (error) {
     console.error("API error:", error);
   }
   ```

## TypeScript Support

This example is fully typed with TypeScript. The `get` method returns a typed `Session` object with full IDE autocomplete support.

```typescript
import { AgentBay, Session } from "wuying-agentbay-sdk";

const agentBay = new AgentBay({ apiKey: "your-key" });
const session: Session = await agentBay.get("session-id");
// TypeScript knows all methods and properties of session
```

