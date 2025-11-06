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

Delete this session.

**Arguments**:

- `sync_context` _bool_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

- `DeleteResult` - Result indicating success or failure and request ID.

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

Gets information about this session.

**Returns**:

- `OperationResult` - Result containing the session information as data and
  request ID.
  

**Raises**:

- `SessionError` - If the operation fails.

#### get\_link

```python
def get_link(protocol_type: Optional[str] = None,
             port: Optional[int] = None,
             options: Optional[str] = None) -> OperationResult
```

Get a link associated with the current session.

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
