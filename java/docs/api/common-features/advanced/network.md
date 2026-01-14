# Beta Network API Reference

## Overview

The Network module provides **network redirection** between your local environment and the AgentBay cloud runtime.
It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.

## BetaNetworkService

```java
public class BetaNetworkService
```

Service for managing networks used for redirection.

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

**Next Step (Local Binding):**

Bind the returned token in your local environment:

```bash
./rick-cli -m bind -t <network-token>
```

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

Query the network status and configuration.

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

To bind a session to a network for redirection, set the `betaNetworkId` in `CreateSessionParams`:

```java
// Create a network
NetworkResult networkResult = agentBay.getBetaNetwork().betaGetNetworkBindToken();
String networkId = networkResult.getNetworkId();

// Create a session bound to the same network (for redirection)
CreateSessionParams params1 = new CreateSessionParams();
params1.setBetaNetworkId(networkId);
params1.setImageId("imgc-12345678");

SessionResult session1 = agentBay.create(params1);
```

## Use Cases

### Network readiness check

Check network status before creating sessions:

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

1. **Token security**: Keep the network token secure and never commit it to source control
2. **Local binding**: Ensure the local binding process stays running and reachable while the session is active
3. **Status checking**: Check network status before binding sessions to avoid connection issues
4. **Custom image**: Use a dedicated custom image when required by your environment policy

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
