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


### Methods

- [cleanup](extension.md#cleanup)
- [create](extension.md#create)
- [createExtensionOption](extension.md#createextensionoption)
- [delete](extension.md#delete)
- [list](extension.md#list)
- [update](extension.md#update)

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

**`Example`**

```typescript
import { AgentBay, ExtensionsService } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateCleanup() {
  try {
    // Create extensions service with auto-generated context
    const extensionsService = new ExtensionsService(agentBay);

    // Upload an extension
    const extension = await extensionsService.create('/path/to/my-extension.zip');
    console.log(`Extension created: ${extension.id}`);
    // Output: Extension created: ext_a1b2c3d4...

    // List extensions
    const extensions = await extensionsService.list();
    console.log(`Total extensions: ${extensions.length}`);
    // Output: Total extensions: 1

    // Clean up the auto-created context and all extensions
    const success = await extensionsService.cleanup();
    if (success) {
      console.log('Extension context cleaned up successfully');
      // Output: Extension context cleaned up successfully
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateCleanup().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay, ExtensionsService } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateCreateExtension() {
  try {
    // Create extensions service with auto-generated context
    const extensionsService = new ExtensionsService(agentBay);

    // Upload a browser extension
    const extension = await extensionsService.create('/path/to/my-extension.zip');
    if (extension) {
      console.log(`Extension uploaded successfully`);
      // Output: Extension uploaded successfully
      console.log(`Extension ID: ${extension.id}`);
      // Output: Extension ID: ext_a1b2c3d4e5f6...
      console.log(`Extension name: ${extension.name}`);
      // Output: Extension name: my-extension.zip
    }

    // Clean up the auto-created context
    await extensionsService.cleanup();
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateCreateExtension().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay, ExtensionsService } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateDeleteExtension() {
  try {
    // Create extensions service
    const extensionsService = new ExtensionsService(agentBay, 'my_extensions');

    // Upload an extension
    const extension = await extensionsService.create('/path/to/my-extension.zip');
    console.log(`Extension created: ${extension.id}`);
    // Output: Extension created: ext_a1b2c3d4...

    // Verify the extension exists
    const extensions = await extensionsService.list();
    console.log(`Total extensions: ${extensions.length}`);
    // Output: Total extensions: 1

    // Delete the extension
    const success = await extensionsService.delete(extension.id);
    if (success) {
      console.log('Extension deleted successfully');
      // Output: Extension deleted successfully
    } else {
      console.log('Failed to delete extension');
    }

    // Verify deletion
    const remainingExtensions = await extensionsService.list();
    console.log(`Remaining extensions: ${remainingExtensions.length}`);
    // Output: Remaining extensions: 0

    // Clean up
    await extensionsService.cleanup();
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateDeleteExtension().catch(console.error);
```

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

**`Example`**

```typescript
import { AgentBay, ExtensionsService } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateListExtensions() {
  try {
    // Create extensions service
    const extensionsService = new ExtensionsService(agentBay, 'my_extensions');

    // Upload some extensions
    await extensionsService.create('/path/to/ext1.zip');
    await extensionsService.create('/path/to/ext2.zip');

    // List all extensions
    const extensions = await extensionsService.list();
    console.log(`Found ${extensions.length} extensions`);
    // Output: Found 2 extensions

    extensions.forEach(ext => {
      console.log(`- Extension: ${ext.name} (ID: ${ext.id})`);
      // Output: - Extension: ext1.zip (ID: ext_a1b2c3d4...)
      // Output: - Extension: ext2.zip (ID: ext_e5f6g7h8...)
    });

    // Clean up
    await extensionsService.cleanup();
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateListExtensions().catch(console.error);
```

___

### update

▸ **update**(`extensionId`, `newLocalPath`): `Promise`\<``Extension``\>

Updates an existing browser extension in the current context with a new file.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
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

**`Example`**

```typescript
import { AgentBay, ExtensionsService } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay({ apiKey: 'your_api_key' });

async function demonstrateUpdateExtension() {
  try {
    // Create extensions service
    const extensionsService = new ExtensionsService(agentBay, 'my_extensions');

    // Upload initial extension
    const extension = await extensionsService.create('/path/to/my-extension-v1.zip');
    console.log(`Extension created: ${extension.id}`);
    // Output: Extension created: ext_a1b2c3d4...

    // Update the extension with a new version
    const updatedExtension = await extensionsService.update(
      extension.id,
      '/path/to/my-extension-v2.zip'
    );
    if (updatedExtension) {
      console.log('Extension updated successfully');
      // Output: Extension updated successfully
      console.log(`Updated extension name: ${updatedExtension.name}`);
      // Output: Updated extension name: my-extension-v2.zip
    }

    // Clean up
    await extensionsService.cleanup();
  } catch (error) {
    console.error('Error:', error);
  }
}

demonstrateUpdateExtension().catch(console.error);
```

## Related Resources

- [Browser API Reference](browser.md)

