# Session API Reference

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management


```python
logger = get_logger("session")
```

## SessionInfo Objects

```python
class SessionInfo()
```

SessionInfo contains information about a session.

## Session Objects

```python
class Session()
```

Session represents a session in the AgentBay cloud environment.

#### get\_api\_key

```python
def get_api_key() -> str
```

Return the API key for this session.

#### get\_client

```python
def get_client()
```

Return the HTTP client for this session.

#### get\_session\_id

```python
def get_session_id() -> str
```

Return the session_id for this session.

#### is\_vpc\_enabled

```python
def is_vpc_enabled() -> bool
```

Return whether this session uses VPC resources.

#### get\_network\_interface\_ip

```python
def get_network_interface_ip() -> str
```

Return the network interface IP for VPC sessions.

#### get\_http\_port

```python
def get_http_port() -> str
```

Return the HTTP port for VPC sessions.

#### get\_token

```python
def get_token() -> str
```

Return the token for VPC sessions.

#### find\_server\_for\_tool

```python
def find_server_for_tool(tool_name: str) -> str
```

Find the server that provides the given tool.

#### delete

```python
def delete(sync_context: bool = False) -> DeleteResult
```

Delete this session and release all associated resources.

**Arguments**:

- `sync_context` _bool, optional_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

- `DeleteResult` - Result indicating success or failure with request ID.
  - success (bool): True if deletion succeeded
  - error_message (str): Error details if deletion failed
  - request_id (str): Unique identifier for this API request
  

**Raises**:

- `SessionError` - If the deletion request fails or the response is invalid.
  
  Behavior:
  The deletion process follows these steps:
  1. If sync_context=True, synchronizes all context data before deletion
  2. If browser replay is enabled, automatically syncs recording context
  3. Calls the ReleaseMcpSession API to delete the session
  4. Returns success/failure status with request ID
  
  Context Synchronization:
  - When sync_context=True: Uploads all modified files in all contexts
  - When browser replay enabled: Uploads browser recording data
  - Synchronization failures do not prevent session deletion
  

**Example**:

    ```python
    from agentbay import AgentBay

    # Initialize the SDK
    agent_bay = AgentBay(api_key="your_api_key")

    # Create a session
    result = agent_bay.create()
    if result.success:
        session = result.session
        print(f"Session ID: {session.session_id}")
        # Output: Session ID: session-04bdwfj7u22a1s30g

        # Use the session for some work
        cmd_result = session.command.run("echo 'Hello World'")
        print(f"Command output: {cmd_result.data}")
        # Output: Command output: Hello World

        # Delete the session (without context sync)
        delete_result = session.delete()
        if delete_result.success:
            print("Session deleted successfully")
            # Output: Session deleted successfully
            print(f"Request ID: {delete_result.request_id}")
            # Output: Request ID: 7C1B2D7A-0E5F-5D8C-9A3B-4F6E8D2C1A9B
        else:
            print(f"Failed to delete: {delete_result.error_message}")

        # Example with context synchronization
        result2 = agent_bay.create()
        if result2.success:
            session2 = result2.session

            # Create a file in the session
            session2.file_system.write_file("/tmp/data.txt", "Important data")

            # Delete with context sync (uploads the file first)
            delete_result2 = session2.delete(sync_context=True)
            if delete_result2.success:
                print("Session deleted with context synced")
                # Output: Session deleted with context synced
    ```
  

**Notes**:

  - Always delete sessions when done to avoid resource leaks
  - Use sync_context=True if you need to preserve modified files
  - Browser replay data is automatically synced if enabled
  - The session object becomes invalid after deletion
  - Deletion is idempotent - deleting an already deleted session succeeds
  

**See Also**:

  AgentBay.create, AgentBay.delete, ContextManager.sync

#### set\_labels

```python
def set_labels(labels: Dict[str, str]) -> OperationResult
```

Sets the labels for this session.

**Arguments**:

- `labels` _Dict[str, str]_ - The labels to set for the session.
  

**Returns**:

- `OperationResult` - Result indicating success or failure with request ID.
  

**Raises**:

- `SessionError` - If the operation fails.

#### get\_labels

```python
def get_labels() -> OperationResult
```

Gets the labels for this session.

**Returns**:

- `OperationResult` - Result containing the labels as data and request ID.
  

**Raises**:

- `SessionError` - If the operation fails.

#### info

```python
def info() -> OperationResult
```

Get detailed information about this session.

**Returns**:

- `OperationResult` - Result containing SessionInfo object and request ID.
  - success (bool): Always True if no exception
  - data (SessionInfo): Session information object with fields:
  - session_id (str): The session identifier
  - resource_url (str): URL for accessing the session
  - app_id (str): Application ID (for desktop sessions)
  - auth_code (str): Authentication code
  - connection_properties (str): Connection configuration
  - resource_id (str): Resource identifier
  - resource_type (str): Type of resource (e.g., "Desktop")
  - ticket (str): Access ticket
  - request_id (str): Unique identifier for this API request
  

**Raises**:

- `SessionError` - If the API request fails or response is invalid.
  
  Behavior:
  This method calls the GetMcpResource API to retrieve session metadata.
  The returned SessionInfo contains:
  - session_id: The session identifier
  - resource_url: URL for accessing the session
  - Desktop-specific fields (app_id, auth_code, connection_properties, etc.)
  are populated from the DesktopInfo section of the API response
  

**Example**:

    ```python
    from agentbay import AgentBay

    # Initialize the SDK
    agent_bay = AgentBay(api_key="your_api_key")

    # Create a session
    result = agent_bay.create()
    if result.success:
        session = result.session

        # Get session information
        info_result = session.info()
        if info_result.success:
            info = info_result.data
            print(f"Session ID: {info.session_id}")
            # Output: Session ID: session-04bdwfj7u22a1s30g

            print(f"Resource URL: {info.resource_url}")
            # Output: Resource URL: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com

            print(f"Resource Type: {info.resource_type}")
            # Output: Resource Type: Desktop

            print(f"Request ID: {info_result.request_id}")
            # Output: Request ID: 8D2C3E4F-1A5B-6C7D-8E9F-0A1B2C3D4E5F

            # Use resource_url for external access
            if info.resource_url:
                print(f"Access session at: {info.resource_url}")
                # Output: Access session at: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com

        # Clean up
        session.delete()
    ```
  

**Notes**:

  - Session info is retrieved from the AgentBay API in real-time
  - The resource_url can be used for browser-based access
  - Desktop-specific fields (app_id, auth_code) are only populated for desktop sessions
  - This method does not modify the session state
  

**See Also**:

  AgentBay.create, Session.delete, Session.get_link

#### get\_link

```python
def get_link(protocol_type: Optional[str] = None,
             port: Optional[int] = None,
             options: Optional[str] = None) -> OperationResult
```

Get an access link for this session.

**Arguments**:

- `protocol_type` _Optional[str], optional_ - The protocol type for the link.
  Defaults to None (uses session default).
- `port` _Optional[int], optional_ - The port number to expose. Must be in range [30100, 30199].
  Defaults to None.
- `options` _Optional[str], optional_ - Additional configuration as JSON string.
  Defaults to None.
  

**Returns**:

- `OperationResult` - Result containing the access URL and request ID.
  - success (bool): True if the operation succeeded
  - data (str): The access URL
  - request_id (str): Unique identifier for this API request
  

**Raises**:

- `SessionError` - If port is out of valid range [30100, 30199] or the API request fails.
  

**Example**:

    ```python
    from agentbay import AgentBay

    # Initialize the SDK
    agent_bay = AgentBay(api_key="your_api_key")

    # Create a session
    result = agent_bay.create()
    if result.success:
        session = result.session

        # Get default link
        link_result = session.get_link()
        if link_result.success:
            print(f"Session link: {link_result.data}")
            # Output: Session link: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com
            print(f"Request ID: {link_result.request_id}")
            # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

        # Get link with specific port
        port_link_result = session.get_link(port=30150)
        if port_link_result.success:
            print(f"Link with port: {port_link_result.data}")
            # Output: Link with port: https://session-04bdwfj7u22a1s30g.agentbay.aliyun.com:30150

        # Clean up
        session.delete()
    ```
  

**Notes**:

  - Port must be in range [30100, 30199] if specified
  - The returned URL format depends on the session configuration
  - For mobile ADB connections, use session.mobile.get_adb_url() instead
  

**See Also**:

  Session.info, Session.get_link_async, Mobile.get_adb_url

#### get\_link\_async

```python
async def get_link_async(protocol_type: Optional[str] = None,
                         port: Optional[int] = None,
                         options: Optional[str] = None) -> OperationResult
```

Asynchronously get a link associated with the current session.

**Arguments**:

- `protocol_type` _Optional[str], optional_ - The protocol type to use for the
  link. Defaults to None.
- `port` _Optional[int], optional_ - The port to use for the link. Must be an integer in the range [30100, 30199].
  Defaults to None.
- `options` _Optional[str], optional_ - Additional options as a JSON string (e.g., for adb configuration).
  Defaults to None.
  

**Returns**:

- `OperationResult` - Result containing the link as data and request ID.
  

**Raises**:

- `SessionError` - If the request fails or the response is invalid.

#### list\_mcp\_tools

```python
def list_mcp_tools(image_id: Optional[str] = None)
```

List MCP tools available for this session.

**Arguments**:

- `image_id` - Optional image ID, defaults to session's image_id or "linux_latest"
  

**Returns**:

  Result containing tools list and request ID

#### call\_mcp\_tool

```python
def call_mcp_tool(tool_name: str,
                  args: Dict[str, Any],
                  read_timeout: Optional[int] = None,
                  connect_timeout: Optional[int] = None,
                  auto_gen_session: bool = False)
```

Call an MCP tool directly.

This is the unified public API for calling MCP tools. All feature modules
(Command, Code, Agent, etc.) use this method internally.

**Arguments**:

- `tool_name` - Name of the MCP tool to call
- `args` - Arguments to pass to the tool as a dictionary
- `read_timeout` - Optional read timeout in seconds
- `connect_timeout` - Optional connection timeout in seconds
- `auto_gen_session` - Whether to automatically generate session if not exists (default: False)
  

**Returns**:

- `McpToolResult` - Result containing success status, data, and error message
  

**Example**:

  >>> result = session.call_mcp_tool("shell", {"command": "ls", "timeout_ms": 1000})
  >>> if result.success:
  >>>     print(result.data)

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../../advanced/oss.md)
- [Application API Reference](../../computer-use/application.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
