# 🌐 Network API Reference

## Overview

The Network module provides network redirection between your local environment and the AgentBay cloud runtime.
It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.


## 📚 Tutorial

[Network (Beta) Guide](../../../../../docs/guides/common-features/advanced/network.md)

Redirect cloud traffic through your local network

## BetaNetworkService

Beta network service for managing network bindings in the AgentBay cloud environment.
This is a trial feature that allows sessions to connect to specific networks.

### Constructor

```java
public BetaNetworkService(AgentBay agentBay)
```

Initialize a BetaNetworkService instance.

**Parameters:**
- `agentBay` (AgentBay): The AgentBay client instance

### Methods

### betaGetNetworkBindToken

```java
public NetworkResult betaGetNetworkBindToken()
```

```java
public NetworkResult betaGetNetworkBindToken(String networkId)
```

This method creates a network (or reuses provided networkId) and returns networkId + networkToken.
networkId is optional: pass no args to create a new network; pass one value to reuse an existing network.

**Parameters:**
- `networkId` (String): Optional network ID to bind to. If null, creates a new network.

**Returns:**
- `NetworkResult`: NetworkResult containing the network ID, token, and request ID

### betaDescribe

```java
public NetworkStatusResult betaDescribe(String networkId)
```

This method queries beta network status (online/offline).

**Parameters:**
- `networkId` (String): The network ID to describe. Must be a non-empty string.

**Returns:**
- `NetworkStatusResult`: NetworkStatusResult containing the online status and request ID



## 💡 Best Practices

- Keep network tokens secure and never commit them to source control
- Ensure the local binding process is running and reachable while the session is active
- Check network readiness before creating sessions bound to it
- Use a dedicated custom image when required by your environment policy

## 🔗 Related Resources

- [AgentBay API Reference](../../../api/common-features/basics/agentbay.md)
- [Session Params API Reference](../../../api/common-features/basics/session-params.md)
- [Session API Reference](../../../api/common-features/basics/session.md)
- [Command API Reference](../../../api/common-features/basics/command.md)

