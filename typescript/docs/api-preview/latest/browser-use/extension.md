# Class: ExtensionsService

## 🧩 Related Tutorial

- [Browser Extensions Guide](../../../../../docs/guides/browser-use/core-features/extension.md) - Learn how to use browser extensions

Provides methods to manage user browser extensions.
This service integrates with the existing context functionality for file operations.

**Usage** (Simplified - Auto-detection):
```typescript
// Service automatically detects if context exists and creates if needed
const extensionsService = new ExtensionsService(agentBay, "browser_extensions");

// Or use with empty contextId to auto-generate context name
const extensionsService = new ExtensionsService(agentBay);  // Uses default generated name

// Use the service immediately - initialization happens automatically
const extension = await extensionsService.create("/path/to/plugin.zip");
```

**Integration with ExtensionOption (Simplified)**:
```typescript
// Create extensions and configure for browser sessions
const extensionsService = new ExtensionsService(agentBay, "my_extensions");
const ext1 = await extensionsService.create("/path/to/ext1.zip");
const ext2 = await extensionsService.create("/path/to/ext2.zip");

// Create extension option for browser integration (no contextId needed!)
const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);

// Use with BrowserContext for session creation
const browserContext = new BrowserContext({
  contextId: "browser_session",
  autoUpload: true,
  extensionOption: extOption  // All extension config encapsulated
});
```

**Context Management**:
- If contextId provided and exists: Uses the existing context
- If contextId provided but doesn't exist: Creates context with provided name
- If contextId empty or not provided: Generates default name and creates context
- No need to manually manage context creation or call initialize()
- Context initialization happens automatically on first method call

## Table of contents

### Constructors

- [constructor](extension.md#constructor)

### Methods

- [cleanup](extension.md#cleanup)
- [create](extension.md#create)
- [createExtensionOption](extension.md#createextensionoption)
- [delete](extension.md#delete)
- [list](extension.md#list)
- [update](extension.md#update)

## Constructors

### constructor

• **new ExtensionsService**(`agentBay`, `contextId?`): [`ExtensionsService`](extension.md)

Initializes the ExtensionsService with a context.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `agentBay` | [`AgentBay`](../common-features/basics/agentbay.md) | `undefined` | The AgentBay client instance. |
| `contextId` | `string` | `""` | The context ID or name. If empty or not provided, a default context name will be generated automatically. If the context doesn't exist, it will be automatically created. Note: The service automatically detects if the context exists. If not, it creates a new context with the provided name or a generated default name. Context initialization is handled lazily on first use. |

#### Returns

[`ExtensionsService`](extension.md)

## Methods

### cleanup

▸ **cleanup**(): `Promise`\<`boolean`\>

Cleans up the auto-created context if it was created by this service.

#### Returns

`Promise`\<`boolean`\>

Promise that resolves to true if cleanup was successful or not needed, false if cleanup failed.

Note:
  This method only works if the context was auto-created by this service.
  For existing contexts, no cleanup is performed.

___

### create

▸ **create**(`localPath`): `Promise`\<``Extension``\>

Uploads a new browser extension from a local path into the current context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `localPath` | `string` | Path to the local extension file (must be a .zip file). |

#### Returns

`Promise`\<``Extension``\>

Promise that resolves to an Extension object.

**`Throws`**

If the local file doesn't exist.

**`Throws`**

If the file format is not supported (only .zip is supported).

**`Throws`**

If upload fails.

___

### createExtensionOption

▸ **createExtensionOption**(`extensionIds`): ``ExtensionOption``

Create an ExtensionOption for the current context with specified extension IDs.

This is a convenience method that creates an ExtensionOption using the current
service's contextId and the provided extension IDs. This option can then be
used with BrowserContext for browser session creation.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `extensionIds` | `string`[] | List of extension IDs to include in the option. These should be extensions that exist in the current context. |

#### Returns

``ExtensionOption``

ExtensionOption configuration object for browser extension integration.

**`Throws`**

If extensionIds is empty or invalid.

**`Example`**

```typescript
// Create extensions
const ext1 = await extensionsService.create("/path/to/ext1.zip");
const ext2 = await extensionsService.create("/path/to/ext2.zip");

// Create extension option for browser integration
const extOption = extensionsService.createExtensionOption([ext1.id, ext2.id]);

// Use with BrowserContext
const browserContext = new BrowserContext({
  contextId: "browser_session",
  autoUpload: true,
  extensionContextId: extOption.contextId,
  extensionIds: extOption.extensionIds
});
```

___

### delete

▸ **delete**(`extensionId`): `Promise`\<`boolean`\>

Deletes a browser extension from the current context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `extensionId` | `string` | ID of the extension to delete. |

#### Returns

`Promise`\<`boolean`\>

Promise that resolves to true if deletion was successful, false otherwise.

___

### list

▸ **list**(): `Promise`\<``Extension``[]\>

Lists all available browser extensions within this context from the cloud.
Uses the context service to list files under the extensions directory.

#### Returns

`Promise`\<``Extension``[]\>

Promise that resolves to an array of Extension objects.

**`Throws`**

If listing extensions fails.

___

### update

▸ **update**(`extensionId`, `newLocalPath`): `Promise`\<``Extension``\>

Updates an existing browser extension in the current context with a new file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :---## Related Resources

- [Browser API Reference](../../browser-use/browser.md)


--- |
| `extensionId` | `string` | ID of the extension to update. |
| `newLocalPath` | `string` | Path to the new local extension file. |

#### Returns

`Promise`\<``Extension``\>

Promise that resolves to an Extension object.

**`Throws`**

If the new local file doesn't exist.

**`Throws`**

If the extension doesn't exist in the context.

**`Throws`**

If update fails.
