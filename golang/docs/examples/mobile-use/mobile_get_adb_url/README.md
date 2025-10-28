# Mobile GetAdbUrl Example

This example demonstrates how to use the `GetAdbUrl` method to retrieve an ADB (Android Debug Bridge) connection URL for a mobile session.

## Prerequisites

- Go 1.18 or higher
- AgentBay API key (set as environment variable `AGENTBAY_API_KEY`)
- ADB public key (for production use)

## What This Example Does

1. Creates a mobile session using `mobile_latest` image
2. Calls `session.Mobile.GetAdbUrl()` with an ADB public key
3. Retrieves the ADB connection URL
4. Cleans up the session

## Important Notes

- **Mobile Environment Required**: The `GetAdbUrl` method only works with mobile sessions (`mobile_latest` image). Using other image types will result in an error.
- **ADB Public Key**: You need to provide your ADB public key. The example uses a desensitized placeholder key.
- **Connection URL Format**: The returned URL follows the format: `adb connect <IP>:<Port>`

## Running the Example

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the example
go run main.go
```

## Expected Output

```
=== Mobile GetAdbUrl Example ===

Creating mobile session...
✅ Session created successfully
   Session ID: session-xxxxxxxxx
   Image ID: mobile_latest

Getting ADB connection URL...
✅ ADB URL retrieved successfully
   URL: adb connect xx.xx.xx.xx:xxxxx
   Request ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

You can now connect to the mobile device using:
   adb connect xx.xx.xx.xx:xxxxx

Cleaning up session...
✅ Session deleted successfully (RequestID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

=== Example completed successfully ===
```

## Using the ADB Connection

Once you have the ADB connection URL, you can use it to connect to the mobile device:

```bash
# Connect to the mobile device
adb connect xx.xx.xx.xx:xxxxx

# Verify the connection
adb devices

# Now you can use standard ADB commands
adb shell
adb install app.apk
adb logcat
```

## Error Handling

The example includes error handling for common scenarios:

- Missing API key
- Session creation failure
- Non-mobile environment (wrong image type)
- ADB URL retrieval failure

## Related Documentation

- [Mobile API Documentation](../../api/mobile.md)
- [Session Creation Guide](../session_creation/README.md)
- [Basic Usage Example](../basic_usage/README.md)

