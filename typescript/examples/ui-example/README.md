# UI Interaction Example

This example demonstrates how to use the AgentBay SDK to interact with a mobile device UI within a session.

## Features Demonstrated

- UI Inspection:
  - Taking screenshots
  - Getting all UI elements
  - Getting clickable UI elements

- UI Interaction:
  - Sending key events
  - Inputting text
  - Clicking at specific screen positions
  - Performing swipe gestures

## Running the Example

Make sure you have set your AgentBay API key as an environment variable:

```bash
export AGENTBAY_API_KEY="your-api-key-here"
```

Then run the example:

```bash
npx ts-node ui-example.ts
```

## Note

This example requires a session with the `mobile_latest` image to support UI operations. The example includes comments for saving screenshots to disk - these sections can be uncommented if you want to see the actual screenshots captured.

Some UI operations might be specific to the device configuration in the session. The example includes error handling to gracefully handle cases where operations are not supported. 