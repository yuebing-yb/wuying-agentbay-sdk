# Mobile GetAdbUrl Example

This example demonstrates how to retrieve an ADB (Android Debug Bridge) connection URL for a mobile session.

## Prerequisites

- Node.js 14 or higher
- AgentBay API key
- A mobile session (`mobile_latest` image)

## Installation

```bash
npm install @aliyun/wuying-agentbay-sdk
```

## Usage

1. Set your API key:
```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Run the example:
```bash
npx ts-node index.ts
```

## Expected Output

```
=== Mobile GetAdbUrl Example ===

Creating mobile session...
✅ Session created successfully
   Session ID: session-xxxxx
   Image ID: mobile_latest

Getting ADB connection URL...
✅ ADB URL retrieved successfully
   URL: adb connect xx.xx.xx.xx:xxxxx
   Request ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

You can now connect to the mobile device using:
   adb connect xx.xx.xx.xx:xxxxx

=== Example completed successfully ===

Cleaning up session...
✅ Session deleted successfully (RequestID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
```

## Using the ADB Connection

Once you have the ADB URL, you can connect to the mobile device:

```bash
# Connect to the device
adb connect xx.xx.xx.xx:xxxxx

# Verify the connection
adb devices

# Now you can use standard ADB commands
adb shell
adb install app.apk
adb logcat
adb pull /sdcard/file.txt
adb push file.txt /sdcard/
```

## Important Notes

1. **Environment Requirement**: This method only works with `mobile_latest` image sessions
2. **ADB Public Key**: You need to provide your ADB public key for authentication
3. **Connection URL Format**: The returned URL is in the format `adb connect <IP>:<Port>`
4. **Session Cleanup**: Always delete the session when done to avoid resource leaks

## Error Handling

The example includes proper error handling for common scenarios:
- Missing API key
- Session creation failure
- ADB URL retrieval failure
- Session deletion issues

## See Also

- [Mobile API Documentation](../../../api/mobile-use/mobile.md)
- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md)
- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md)

