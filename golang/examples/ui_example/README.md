# UI Example

This example demonstrates how to use the AgentBay SDK's UI module to interact with mobile device interfaces in the cloud environment.

## Features Demonstrated

- Taking screenshots
- Getting all UI elements
- Getting clickable UI elements
- Sending key events
- Inputting text
- Clicking at specific screen positions
- Performing swipe gestures

## Prerequisites

- Go 1.16 or later
- AgentBay API key (set as `AGENTBAY_API_KEY` environment variable)

## Running the Example

1. Set your API key:
   ```bash
   export AGENTBAY_API_KEY="your-api-key-here"
   ```

2. Run the example:
   ```bash
   go run main.go
   ```

## Expected Output

The example will create a session, perform various UI operations, and clean up afterwards. 
You should see output showing the results of each operation, including:

- Screenshot data information
- UI element details
- Clickable UI element details
- Key event status
- Text input status
- Click operation status
- Swipe operation status

## Notes

- This example requires a session created with the `mobile_latest` image to support UI operations
- The example includes code to save screenshots, which is commented out by default
- Screen coordinates used in the example are based on common mobile resolutions
- The session is automatically deleted at the end of the example
- The `parseBounds` helper function demonstrates how to extract UI element coordinates from bounds strings 