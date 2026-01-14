# Network API Reference

## 🌐 Related Tutorial

- [Network (Beta) Guide](../../../../../docs/guides/common-features/advanced/network.md) - Redirect cloud traffic through your local network

## Overview

The Network module provides network redirection between your local environment and the AgentBay cloud runtime.
It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.

## Type BetaNetworkService

```go
type BetaNetworkService struct {
	AgentBay *AgentBay
}
```

BetaNetworkService provides beta methods to manage networks.

### Methods

### BetaDescribe

```go
func (ns *BetaNetworkService) BetaDescribe(networkId string) (*BetaNetworkStatusResult, error)
```

BetaDescribe queries beta network status (online/offline).

### BetaGetNetworkBindToken

```go
func (ns *BetaNetworkService) BetaGetNetworkBindToken(networkId string) (*BetaNetworkResult, error)
```

BetaGetNetworkBindToken creates a network (or reuses provided networkId) and returns networkId +
networkToken.

## Type BetaNetworkResult

```go
type BetaNetworkResult struct {
	models.ApiResponse
	Success		bool
	NetworkId	string
	NetworkToken	string
	ErrorMessage	string
}
```

BetaNetworkResult wraps beta network bind token result and RequestID.

## Type BetaNetworkStatusResult

```go
type BetaNetworkStatusResult struct {
	models.ApiResponse
	Success		bool
	Online		bool
	ErrorMessage	string
}
```

BetaNetworkStatusResult wraps beta network status result and RequestID.

## Best Practices

1. Keep network tokens secure and never commit them to source control
2. Ensure the local binding process is running and reachable while the session is active
3. Check network readiness before creating sessions bound to it
4. Use a dedicated custom image when required by your environment policy

## Related Resources

- [AgentBay API Reference](../basics/agentbay.md)
- [Session Params API Reference](../basics/session-params.md)
- [Session API Reference](../basics/session.md)
- [Command API Reference](../basics/command.md)

---

*Documentation generated automatically from Go source code.*
