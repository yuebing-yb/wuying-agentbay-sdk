# 🌐 Network API Reference

## Overview

The Network module provides network redirection between your local environment and the AgentBay cloud runtime.
It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.


## 📚 Tutorial

[Network (Beta) Guide](../../../../../docs/guides/common-features/advanced/network.md)

Redirect cloud traffic through your local network

## BetaNetworkService

Beta network service (trial feature).

### Constructor

```java
public BetaNetworkService(AgentBay agentBay)
```

### Methods

### betaGetNetworkBindToken

```java
public NetworkResult betaGetNetworkBindToken()
```

```java
public NetworkResult betaGetNetworkBindToken(String networkId)
```

### betaDescribe

```java
public NetworkStatusResult betaDescribe(String networkId)
```



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

