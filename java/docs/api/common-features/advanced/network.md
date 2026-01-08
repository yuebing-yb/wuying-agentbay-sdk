# Beta Network API Reference

## Overview

The Network module provides network isolation and session communication capabilities. By creating a network and binding multiple sessions to it, you can enable communication between sessions while maintaining network isolation from other sessions.

## BetaNetworkService

```java
public class BetaNetworkService
```

Service for managing networks that can be shared across sessions.

### betaGetNetworkBindToken

```java
public NetworkResult betaGetNetworkBindToken()
public NetworkResult betaGetNetworkBindToken(String networkId)
```

Create a new network. If `networkId` is not provided, a unique ID will be generated automatically.

**Parameters:**
- `networkId` (String, optional): Custom network ID. If null or empty, a unique ID is generated.

**Returns:**
- `NetworkResult`: Result containing the created network ID and network token

**Example:**

```java
// Create network with auto-generated ID
NetworkResult result = agentBay.getBetaNetwork().betaGetNetworkBindToken();
if (result.isSuccess()) {
    String networkId = result.getNetworkId();
    String networkToken = result.getNetworkToken();
    System.out.println("Network created: " + networkId);
}

// Create network with custom ID
NetworkResult result = agentBay.getBetaNetwork().betaGetNetworkBindToken("my-custom-network");
if (result.isSuccess()) {
    System.out.println("Network created with custom ID: " + result.getNetworkId());
}
```

### betaDescribe

```java
public NetworkStatusResult betaDescribe(String networkId)
```

Get the status of a network.

**Parameters:**
- `networkId` (String): The network ID to query

**Returns:**
- `NetworkStatusResult`: Result containing the network online status

**Example:**

```java
NetworkStatusResult result = agentBay.getBetaNetwork().betaDescribe(networkId);
if (result.isSuccess()) {
    boolean online = result.isOnline();
    System.out.println("Network online: " + online);
}
```

## NetworkResult

Result object returned by network creation operations.

**Fields:**
- `requestId` (String): Request ID from the API
- `success` (boolean): Whether the operation succeeded
- `networkId` (String): The created network ID
- `networkToken` (String): Network authentication token
- `errorMessage` (String): Error message if operation failed

**Methods:**
- `getRequestId()`: Get request ID
- `isSuccess()`: Check if operation succeeded
- `getNetworkId()`: Get network ID
- `getNetworkToken()`: Get network token
- `getErrorMessage()`: Get error message

## NetworkStatusResult

Result object returned by network status queries.

**Fields:**
- `requestId` (String): Request ID from the API
- `success` (boolean): Whether the operation succeeded
- `online` (boolean): Whether the network is online
- `errorMessage` (String): Error message if operation failed

**Methods:**
- `getRequestId()`: Get request ID
- `isSuccess()`: Check if operation succeeded
- `isOnline()`: Check if network is online
- `getErrorMessage()`: Get error message

## Binding Sessions to Network

To bind a session to a network, set the `betaNetworkId` in `CreateSessionParams`:

```java
// Create a network
NetworkResult networkResult = agentBay.getBetaNetwork().betaGetNetworkBindToken();
String networkId = networkResult.getNetworkId();

// Create sessions bound to the same network
CreateSessionParams params1 = new CreateSessionParams();
params1.setBetaNetworkId(networkId);
params1.setImageId("linux_latest");

SessionResult session1 = agentBay.create(params1);

CreateSessionParams params2 = new CreateSessionParams();
params2.setBetaNetworkId(networkId);
params2.setImageId("linux_latest");

SessionResult session2 = agentBay.create(params2);

// Now session1 and session2 can communicate with each other
```

## Use Cases

### 1. Multi-Session Communication

Enable communication between multiple sessions for distributed workflows:

```java
// Create a shared network
NetworkResult networkResult = agentBay.getBetaNetwork().betaGetNetworkBindToken();
String networkId = networkResult.getNetworkId();

// Create multiple sessions on the same network
CreateSessionParams params1 = new CreateSessionParams();
params1.setBetaNetworkId(networkId);
params1.setImageId("linux_latest");
SessionResult session1 = agentBay.create(params1);

CreateSessionParams params2 = new CreateSessionParams();
params2.setBetaNetworkId(networkId);
params2.setImageId("linux_latest");
SessionResult session2 = agentBay.create(params2);

// Sessions can now communicate via network
// For example, session1 starts a web server
CommandResult result1 = session1.getSession().getCommand()
    .executeCommand("python3 -m http.server 8080");

// Session2 can access the server
CommandResult result2 = session2.getSession().getCommand()
    .executeCommand("curl http://localhost:8080");
```

### 2. Network Isolation

Isolate different projects or tenants using separate networks:

```java
// Project A network
NetworkResult networkA = agentBay.getBetaNetwork().betaGetNetworkBindToken("project-a-network");

CreateSessionParams paramsA = new CreateSessionParams();
paramsA.setBetaNetworkId(networkA.getNetworkId());
SessionResult sessionA = agentBay.create(paramsA);

// Project B network (isolated from A)
NetworkResult networkB = agentBay.getBetaNetwork().betaGetNetworkBindToken("project-b-network");

CreateSessionParams paramsB = new CreateSessionParams();
paramsB.setBetaNetworkId(networkB.getNetworkId());
SessionResult sessionB = agentBay.create(paramsB);

// Sessions in different networks cannot communicate with each other
```

### 3. Network Status Monitoring

Monitor network status before creating sessions:

```java
String networkId = "my-network";

// Check if network is online
NetworkStatusResult status = agentBay.getBetaNetwork().betaDescribe(networkId);
if (status.isSuccess() && status.isOnline()) {
    // Network is online, safe to create sessions
    CreateSessionParams params = new CreateSessionParams();
    params.setBetaNetworkId(networkId);
    SessionResult session = agentBay.create(params);
} else {
    System.out.println("Network is offline or does not exist");
}
```

## Best Practices

1. **Reuse Networks**: Create one network and bind multiple sessions to it for better resource utilization
2. **Custom Network IDs**: Use meaningful network IDs (e.g., "project-name-network") for easier management
3. **Status Checking**: Check network status before binding sessions to avoid connection issues
4. **Network Token**: Store the network token securely if needed for authentication
5. **Cleanup**: Networks are automatically cleaned up when all bound sessions are deleted

## Error Handling

```java
NetworkResult result = agentBay.getBetaNetwork().betaGetNetworkBindToken();
if (!result.isSuccess()) {
    System.err.println("Failed to create network: " + result.getErrorMessage());
    System.err.println("Request ID: " + result.getRequestId());
}

NetworkStatusResult status = agentBay.getBetaNetwork().betaDescribe(networkId);
if (!status.isSuccess()) {
    System.err.println("Failed to get network status: " + status.getErrorMessage());
}
```

## Related APIs

- [CreateSessionParams](../basics/session-params.md) - Session configuration parameters
- [Session](../basics/session.md) - Session management
- [Command](../basics/command.md) - Command execution for network operations
