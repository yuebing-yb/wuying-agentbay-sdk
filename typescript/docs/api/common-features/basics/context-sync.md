# Interface: ContextSyncResult

## 🔄 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn how context synchronization works and how to persist data across sessions

## Overview

Context Sync provides a mechanism to persist files and directories across sessions by synchronizing local paths to a named context. It supports policies for upload/download behavior and selective path inclusion.

Base interface for API responses

## Hierarchy

- ``ApiResponse``

  ↳ **`ContextSyncResult`**

## Table of contents

### Properties

- `errorMessage`
- `requestId`

## Properties

```typescript
success: `boolean`
```


### errorMessage

• `Optional` **errorMessage**: `string`

Optional error message if the operation failed

#### Overrides

`ApiResponse`.`errorMessage`

___

### requestId

• `Optional` **requestId**: `string`

Optional request identifier for tracking API calls

#### Inherited from

`ApiResponse`.`requestId`

___

#### Overrides

`ApiResponse`.`success`

## Related Resources

- [Context Manager API Reference](context-manager.md)
- [Session API Reference](session.md)

