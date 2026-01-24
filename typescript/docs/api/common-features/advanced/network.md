# Class: BetaNetworkService

## 🌐 Related Tutorial

- [Network (Beta) Guide](../../../../../docs/guides/common-features/advanced/network.md) - Redirect cloud traffic through your local network

## Overview

The Network module provides network redirection between your local environment and the AgentBay cloud runtime.
It allows a cloud session to use your local network egress, which can help reduce risk-control issues in certain websites or mobile apps.

Beta network service (trial feature).

## Table of contents


### Methods

- [create](#create)
- [describe](#describe)

## Methods

### create

▸ **create**(`networkId?`): `Promise`\<`NetworkResult`\>

Deprecated: use getNetworkBindToken().

#### Parameters

| Name | Type |
| :------ | :------ |
| `networkId?` | `string` |

#### Returns

`Promise`\<`NetworkResult`\>

___

### describe

▸ **describe**(`networkId`): `Promise`\<`NetworkStatusResult`\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `networkId` | `string` |

#### Returns

`Promise`\<`NetworkStatusResult`\>

## Best Practices

1. Keep network tokens secure and never commit them to source control
2. Ensure the local binding process is running and reachable while the session is active
3. Check network readiness before creating sessions bound to it
4. Use a dedicated custom image when required by your environment policy


## Related Resources

- [AgentBay API Reference](../../common-features/basics/agentbay.md)
- [Session Params API Reference](../../common-features/basics/session-params.md)
- [Session API Reference](../../common-features/basics/session.md)
- [Command API Reference](../../common-features/basics/command.md)

