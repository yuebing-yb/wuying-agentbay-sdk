# Application Window Management Example

This example demonstrates how to use the AgentBay SDK to interact with applications and windows on the system.

## Features Demonstrated

- Application Management:
  - Getting a list of installed applications
  - Listing visible (running) applications

- Window Management:
  - Listing root windows in the system
  - Getting the currently active window
  - Getting window information by ID

## Running the Example

Make sure you have set your AgentBay API key as an environment variable:

```bash
export AGENTBAY_API_KEY="your-api-key-here"
```

Then run the example:

```bash
npx ts-node application-window.ts
```

## Note

Some of the demonstrated functionality may be platform-specific and might not work on all operating systems or session types. The example includes error handling to deal with cases where certain operations are not supported. 