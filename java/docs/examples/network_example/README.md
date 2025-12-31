# Network Example

This example demonstrates how to use the Network API to create shared networks and enable communication between multiple sessions.

## Overview

The Network API allows you to:
- Create isolated networks
- Bind multiple sessions to the same network
- Enable communication between sessions on the same network
- Maintain network isolation between different networks

## Running the Example

### Prerequisites

1. Set your API key as an environment variable:
```bash
export AGENTBAY_API_KEY="your-api-key-here"
```

2. Ensure you have the AgentBay SDK installed

### Run the Example

```bash
cd java/agentbay
mvn exec:java -Dexec.mainClass="com.aliyun.agentbay.examples.NetworkExample"
```

Or compile and run directly:

```bash
cd java/agentbay
mvn clean compile
java -cp target/classes:$(mvn dependency:build-classpath | grep -v '\[INFO\]') \
  com.aliyun.agentbay.examples.NetworkExample
```

## What the Example Does

### Example 1: Create a Network
- Creates a new network with auto-generated ID
- Displays network ID and token
- Shows request ID for tracking

### Example 2: Check Network Status
- Queries the network status
- Displays whether the network is online
- Useful for monitoring network health

### Example 3: Create Sessions on Same Network
- Creates two sessions bound to the same network
- Both sessions can communicate with each other
- Demonstrates basic network setup

### Example 4: Test Network Communication
- Starts an HTTP server on session 1
- Session 2 connects to the server on session 1
- Demonstrates actual inter-session communication
- Cleans up by stopping the server

### Example 5: Verify Network Isolation
- Creates a second network
- Creates session 3 on the new network
- Shows that sessions on different networks are isolated
- Session 3 cannot communicate with sessions 1 & 2

## Key Concepts

### Network Creation

```java
// Create network with auto-generated ID
NetworkResult result = agentBay.getNetwork().create();
String networkId = result.getNetworkId();
String networkToken = result.getNetworkToken();

// Or create with custom ID
NetworkResult result = agentBay.getNetwork().create("my-network-id");
```

### Binding Sessions to Network

```java
CreateSessionParams params = new CreateSessionParams();
params.setImageId("linux_latest");
params.setNetworkId(networkId);  // Bind to network

SessionResult session = agentBay.create(params);
```

### Checking Network Status

```java
NetworkStatusResult status = agentBay.getNetwork().describe(networkId);
boolean isOnline = status.isOnline();
```

## Use Cases

### 1. Distributed Workflows
- Create multiple sessions that need to communicate
- Use for microservices testing
- Simulate distributed systems

### 2. Multi-Tenant Isolation
- Create separate networks for different projects/users
- Ensure complete isolation between tenants
- Manage network resources per project

### 3. Network Testing
- Test network connectivity between services
- Verify firewall rules
- Simulate network conditions

## Best Practices

1. **Reuse Networks**: Create one network for related sessions rather than creating multiple networks
2. **Meaningful IDs**: Use descriptive network IDs like "project-name-network" for easier management
3. **Status Checks**: Verify network is online before binding sessions
4. **Cleanup**: Sessions will be automatically deleted, and networks cleaned up when all sessions are gone
5. **Error Handling**: Always check `isSuccess()` on results and handle errors appropriately

## Troubleshooting

### Network Creation Fails
- Verify your API key is valid
- Check network quota limits
- Review error message in `result.getErrorMessage()`

### Sessions Cannot Communicate
- Verify both sessions are on the same network ID
- Check if network is online using `describe()`
- Ensure proper ports are used in communication

### Network Not Found
- Network may have been automatically cleaned up
- Verify network ID is correct
- Create a new network if needed

## Related Documentation

- [Network API Reference](../../api/common-features/advanced/network.md)
- [CreateSessionParams](../../api/common-features/basics/session-params.md)
- [Session Management](../../api/common-features/basics/session.md)

## Example Output

```
Creating AgentBay client...

============================================================
Example 1: Create a network
============================================================
✅ Network created successfully!
   Network ID: network-abc123
   Network Token: token-xyz789
   Request ID: req-12345

============================================================
Example 2: Check network status
============================================================
✅ Network status retrieved successfully!
   Network ID: network-abc123
   Online: true
   Request ID: req-12346

============================================================
Example 3: Create sessions on the same network
============================================================

Creating session 1...
✅ Session 1 created successfully!
   Session ID: session-111
   Network ID: network-abc123

Creating session 2...
✅ Session 2 created successfully!
   Session ID: session-222
   Network ID: network-abc123

============================================================
Example 4: Test network communication between sessions
============================================================

🌐 Starting HTTP server on session 1...
✅ HTTP server started on session 1
   PID: 12345

📡 Testing connection from session 2 to session 1...
✅ Successfully connected from session 2 to session 1!
   Response preview:
   <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
   <html>
   <head>
   <meta http-equiv="Content-Type" content="text/html;

🛑 Stopping HTTP server on session 1...
✅ HTTP server stopped

============================================================
Example 5: Verify network isolation
============================================================

🔒 Creating session 3 on a different network...
✅ Second network created: network-def456
✅ Session 3 created on different network: session-333

🔍 Verifying network isolation...
   Session 1 & 2 are on network: network-abc123
   Session 3 is on network: network-def456
   Sessions on different networks cannot communicate with each other

============================================================
Cleaning up...
============================================================
✅ Session 1 deleted
✅ Session 2 deleted
✅ Session 3 deleted

✅ All examples completed successfully!
```
