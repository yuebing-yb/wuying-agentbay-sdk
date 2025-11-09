# Extension API Reference

## 🧩 Related Tutorial

- [Browser Extensions Guide](../../../../../docs/guides/browser-use/core-features/extension.md) - Learn how to use browser extensions



```python
logger = get_logger("extension")
```

#### EXTENSIONS\_BASE\_PATH

```python
EXTENSIONS_BASE_PATH = "/tmp/extensions"
```

## Extension Objects

```python
class Extension()
```

Represents a browser extension as a cloud resource.

## ExtensionOption Objects

```python
class ExtensionOption()
```

Configuration options for browser extension integration.

This class encapsulates the necessary parameters for setting up
browser extension synchronization and context management.

**Attributes**:

- `context_id` _str_ - ID of the extension context for browser extensions
- `extension_ids` _List[str]_ - List of extension IDs to be loaded/synchronized

#### validate

```python
def validate() -> bool
```

Validate the extension option configuration.

**Returns**:

    bool: True if configuration is valid, False otherwise.

## ExtensionsService Objects

```python
class ExtensionsService()
```

Provides methods to manage user browser extensions.
This service integrates with the existing context functionality for file operations.

**Usage** (Simplified - Auto-detection):
```python
# Service automatically detects if context exists and creates if needed
extensions_service = ExtensionsService(agent_bay, "browser_extensions")

# Or use with empty context_id to auto-generate context name
extensions_service = ExtensionsService(agent_bay)  # Uses default generated name

# Use the service immediately
extension = extensions_service.create("/path/to/plugin.zip")
```

**Integration with ExtensionOption (Simplified)**:
```python
# Create extensions and configure for browser sessions
extensions_service = ExtensionsService(agent_bay, "my_extensions")
ext1 = extensions_service.create("/path/to/ext1.zip")
ext2 = extensions_service.create("/path/to/ext2.zip")

# Create extension option for browser integration (no context_id needed!)
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Use with BrowserContext for session creation
browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True,
    extension_option=ext_option  # All extension config encapsulated
)
```

**Context Management**:
- If context_id provided and exists: Uses the existing context
- If context_id provided but doesn't exist: Creates context with provided name
- If context_id empty or not provided: Generates default name and creates context
- No need to manually manage context creation

#### list

```python
def list() -> List[Extension]
```

Lists all available browser extensions within this context from the cloud.
Uses the context service to list files under the extensions directory.

**Returns**:

    List[Extension]: List of all extensions in the context.
  

**Raises**:

    AgentBayError: If listing fails.
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.extension import ExtensionsService

agent_bay = AgentBay(api_key="your_api_key")

def list_all_extensions():
    try:
        # Create extensions service
        extensions_service = ExtensionsService(agent_bay, "my_extensions")

        # List all extensions
        extensions = extensions_service.list()

        if extensions:
            print(f"Found {len(extensions)} extension(s):")
            for ext in extensions:
                print(f"  - {ext.name} (ID: {ext.id})")
                if ext.created_at:
                    print(f"    Created at: {ext.created_at}")
        else:
            print("No extensions found")

        # Clean up
        extensions_service.cleanup()
    except Exception as e:
        print(f"Error: {e}")

list_all_extensions()
```

#### create

```python
def create(local_path: str) -> Extension
```

Uploads a new browser extension from a local path into the current context.

**Arguments**:

- `local_path` _str_ - Path to the local extension ZIP file.
  

**Returns**:

    Extension: Extension object with generated ID and metadata.
  

**Raises**:

    FileNotFoundError: If the local file doesn't exist.
    ValueError: If the file format is not supported (only ZIP files allowed).
    AgentBayError: If upload fails.
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.extension import ExtensionsService

agent_bay = AgentBay(api_key="your_api_key")

def upload_browser_extension():
    try:
        # Create extensions service
        extensions_service = ExtensionsService(agent_bay, "my_extensions")

        # Upload extension from local path
        extension = extensions_service.create("/path/to/my-extension.zip")

        print(f"Extension uploaded successfully:")
        print(f"  Name: {extension.name}")
        print(f"  ID: {extension.id}")

        # Clean up
        extensions_service.cleanup()
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Invalid file format: {e}")
    except Exception as e:
        print(f"Error: {e}")

upload_browser_extension()
```

#### update

```python
def update(extension_id: str, new_local_path: str) -> Extension
```

Updates an existing browser extension in the current context with a new file.

**Arguments**:

- `extension_id` _str_ - ID of the extension to update.
- `new_local_path` _str_ - Path to the new extension ZIP file.
  

**Returns**:

    Extension: Updated extension object.
  

**Raises**:

    FileNotFoundError: If the new local file doesn't exist.
    ValueError: If the extension ID doesn't exist in the context.
    AgentBayError: If update fails.
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.extension import ExtensionsService

agent_bay = AgentBay(api_key="your_api_key")

def update_browser_extension():
    try:
        # Create extensions service
        extensions_service = ExtensionsService(agent_bay, "my_extensions")

        # First, upload an extension
        extension = extensions_service.create("/path/to/extension-v1.zip")
        print(f"Extension created: {extension.id}")

        # Update the extension with a new version
        updated_ext = extensions_service.update(
            extension.id,
            "/path/to/extension-v2.zip"
        )

        print(f"Extension updated successfully:")
        print(f"  Name: {updated_ext.name}")
        print(f"  ID: {updated_ext.id}")

        # Clean up
        extensions_service.cleanup()
    except FileNotFoundError as e:
        print(f"File not found: {e}")
    except ValueError as e:
        print(f"Extension not found: {e}")
    except Exception as e:
        print(f"Error: {e}")

update_browser_extension()
```

#### cleanup

```python
def cleanup() -> bool
```

Cleans up the auto-created context if it was created by this service.

**Returns**:

    bool: True if cleanup was successful or not needed, False if cleanup failed.
  

**Notes**:

  This method only works if the context was auto-created by this service.
  For existing contexts, no cleanup is performed.

#### delete

```python
def delete(extension_id: str) -> bool
```

Deletes a browser extension from the current context.

**Arguments**:

- `extension_id` _str_ - ID of the extension to delete.
  

**Returns**:

    bool: True if deletion was successful, False otherwise.
  

**Example**:

  
```python
from agentbay import AgentBay
from agentbay.extension import ExtensionsService

agent_bay = AgentBay(api_key="your_api_key")

def delete_browser_extension():
    try:
        # Create extensions service
        extensions_service = ExtensionsService(agent_bay, "my_extensions")

        # Upload an extension
        extension = extensions_service.create("/path/to/extension.zip")
        print(f"Extension created: {extension.id}")

        # Delete the extension
        success = extensions_service.delete(extension.id)

        if success:
            print(f"Extension {extension.id} deleted successfully")
        else:
            print(f"Failed to delete extension {extension.id}")

        # Clean up
        extensions_service.cleanup()
    except Exception as e:
        print(f"Error: {e}")

delete_browser_extension()
```

#### create\_extension\_option

```python
def create_extension_option(extension_ids: List[str]) -> ExtensionOption
```

Create an ExtensionOption for the current context with specified extension IDs.

This is a convenience method that creates an ExtensionOption using the current
service's context_id and the provided extension IDs. This option can then be
used with BrowserContext for browser session creation.

**Arguments**:

- `extension_ids` _List[str]_ - List of extension IDs to include in the option.
  These should be extensions that exist in the current context.
  

**Returns**:

    ExtensionOption: Configuration object for browser extension integration.
  

**Raises**:

    ValueError: If extension_ids is empty or invalid.
  

**Example**:

  
```python
# Create extensions
ext1 = extensions_service.create("/path/to/ext1.zip")
ext2 = extensions_service.create("/path/to/ext2.zip")

# Create extension option for browser integration
ext_option = extensions_service.create_extension_option([ext1.id, ext2.id])

# Use with BrowserContext
browser_context = BrowserContext(
    context_id="browser_session",
    auto_upload=True,
    extension_context_id=ext_option.context_id,
    extension_ids=ext_option.extension_ids
)
```

## Related Resources

- [Browser API Reference](browser.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
