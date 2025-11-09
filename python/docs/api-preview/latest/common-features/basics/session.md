# Session API Reference

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management



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

**Returns**:

    str: The API key used for authentication
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_api_key():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Get API key (useful for debugging or logging)
            api_key = session.get_api_key()
            print(f"Using API key: {api_key[:10]}...")
            # Output: Using API key: sk-1234567...

            # Verify API key is set
            if api_key:
                print("API key is configured")
                # Output: API key is configured

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_api_key()
```
  

**See Also**:

  AgentBay.__init__, Session.get_session_id

#### get\_client

```python
def get_client()
```

Return the HTTP client for this session.

**Returns**:

    Client: The HTTP client instance used for API calls
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_client():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Get the HTTP client
            client = session.get_client()
            print(f"Client type: {type(client).__name__}")
            # Output: Client type: Client

            # Client is used internally for API calls
            # You typically don't need to use it directly
            print("HTTP client is available for advanced usage")
            # Output: HTTP client is available for advanced usage

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_client()
```
  

**Notes**:

  This method is primarily for internal use by the SDK.
  Most users should use the high-level session methods instead.
  

**See Also**:

  Session.get_api_key, Session.call_mcp_tool

#### get\_session\_id

```python
def get_session_id() -> str
```

Return the session_id for this session.

**Returns**:

    str: The session ID
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def get_session_details():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Get session ID using helper method
            session_id = session.get_session_id()
            print(f"Session ID: {session_id}")
            # Output: Session ID: session-04bdwfj7u22a1s30g

            # Use session ID in logging or tracking
            print(f"Working with session: {session_id}")
            # Output: Working with session: session-04bdwfj7u22a1s30g

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

get_session_details()
```
  

**See Also**:

  Session.get_api_key, Session.info

#### is\_vpc\_enabled

```python
def is_vpc_enabled() -> bool
```

Return whether this session uses VPC resources.

**Returns**:

    bool: True if session uses VPC, False otherwise
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_vpc_status():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Check if VPC is enabled
            if session.is_vpc_enabled():
                print("Session uses VPC resources")
                # Output: Session uses VPC resources

                # Get VPC network details
                ip = session.get_network_interface_ip()
                port = session.get_http_port()
                token = session.get_token()

                print(f"VPC IP: {ip}")
                # Output: VPC IP: 172.16.0.10
                print(f"VPC Port: {port}")
                # Output: VPC Port: 8080
                print(f"Token: {token[:10]}...")
                # Output: Token: abc123def4...
            else:
                print("Session uses standard (non-VPC) resources")
                # Output: Session uses standard (non-VPC) resources

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_vpc_status()
```
  

**Notes**:

  VPC sessions have enhanced network configuration and security features.
  VPC-specific methods (`get_network_interface_ip`, `get_http_port`, `get_token`)
  only return meaningful values when VPC is enabled.
  

**See Also**:

  Session.get_network_interface_ip, Session.get_http_port, Session.get_token

#### get\_network\_interface\_ip

```python
def get_network_interface_ip() -> str
```

Return the network interface IP for VPC sessions.

**Returns**:

    str: The VPC network interface IP address
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_network_ip():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Check if VPC is enabled
            if session.is_vpc_enabled():
                # Get network interface IP
                network_ip = session.get_network_interface_ip()
                print(f"VPC Network Interface IP: {network_ip}")
                # Output: VPC Network Interface IP: 172.16.0.10
            else:
                print("Session is not VPC-enabled")
                # Output: Session is not VPC-enabled
                network_ip = session.get_network_interface_ip()
                print(f"Network IP: {network_ip}")
                # Output: Network IP:

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_network_ip()
```
  

**Notes**:

  This method returns an empty string for non-VPC sessions.
  Use `is_vpc_enabled()` to check if VPC is active.
  

**See Also**:

  Session.is_vpc_enabled, Session.get_http_port

#### get\_http\_port

```python
def get_http_port() -> str
```

Return the HTTP port for VPC sessions.

**Returns**:

    str: The VPC HTTP port number
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_http_port():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Check if VPC is enabled
            if session.is_vpc_enabled():
                # Get HTTP port
                http_port = session.get_http_port()
                print(f"VPC HTTP Port: {http_port}")
                # Output: VPC HTTP Port: 8080
            else:
                print("Session is not VPC-enabled")
                # Output: Session is not VPC-enabled
                http_port = session.get_http_port()
                print(f"HTTP Port: {http_port}")
                # Output: HTTP Port:

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_http_port()
```
  

**Notes**:

  This method returns an empty string for non-VPC sessions.
  Use `is_vpc_enabled()` to check if VPC is active.
  

**See Also**:

  Session.is_vpc_enabled, Session.get_network_interface_ip

#### get\_token

```python
def get_token() -> str
```

Return the token for VPC sessions.

**Returns**:

    str: The VPC authentication token
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def check_vpc_token():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Check if VPC is enabled
            if session.is_vpc_enabled():
                # Get VPC authentication token
                token = session.get_token()
                print(f"VPC Token: {token[:10]}...")
                # Output: VPC Token: abc123def4...
            else:
                print("Session is not VPC-enabled")
                # Output: Session is not VPC-enabled
                token = session.get_token()
                print(f"Token: {token}")
                # Output: Token:

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

check_vpc_token()
```
  

**Notes**:

  This method returns an empty string for non-VPC sessions.
  Use `is_vpc_enabled()` to check if VPC is active.
  

**See Also**:

  Session.is_vpc_enabled, Session.call_mcp_tool

#### find\_server\_for\_tool

```python
def find_server_for_tool(tool_name: str) -> str
```

Find the server that provides the given MCP tool.

**Arguments**:

- `tool_name` _str_ - Name of the MCP tool to find
  

**Returns**:

    str: The server name that provides the tool, or empty string if not found
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def find_tool_server():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session

            # List available tools first
            tools_result = session.list_mcp_tools()
            print(f"Found {len(tools_result.tools)} tools")
            # Output: Found 69 tools

            # Find server for a specific tool
            server = session.find_server_for_tool("shell")
            if server:
                print(f"The 'shell' tool is provided by: {server}")
                # Output: The 'shell' tool is provided by: mcp-server-system
            else:
                print("Tool 'shell' not found")

            # Find server for another tool
            file_server = session.find_server_for_tool("read_file")
            if file_server:
                print(f"The 'read_file' tool is provided by: {file_server}")
                # Output: The 'read_file' tool is provided by: mcp-server-filesystem

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

find_tool_server()
```
  

**Notes**:

  This method searches the session's cached mcp_tools list.
  Call `list_mcp_tools()` first to populate the tool list.
  

**See Also**:

  Session.list_mcp_tools, Session.call_mcp_tool

#### delete

```python
def delete(sync_context: bool = False) -> DeleteResult
```

Delete this session and release all associated resources.

**Arguments**:

- `sync_context` _bool, optional_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

    DeleteResult: Result indicating success or failure with request ID.
  - success (bool): True if deletion succeeded
  - error_message (str): Error details if deletion failed
  - request_id (str): Unique identifier for this API request
  

**Raises**:

    SessionError: If the deletion request fails or the response is invalid.
  
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

    OperationResult: Result indicating success or failure with request ID.
  

**Raises**:

    SessionError: If the operation fails.
  

**Example**:

```python
# Set session labels
labels = {
    "project": "demo",
    "environment": "testing",
    "version": "1.0.0"
}
result = session.set_labels(labels)
if result.success:
    print("Labels set successfully")
    # Output: Labels set successfully
    print(f"Request ID: {result.request_id}")
    # Output: Request ID: B1F98082-52F0-17F7-A149-7722D6205AD6
else:
    print(f"Failed to set labels: {result.error_message}")
```

#### get\_labels

```python
def get_labels() -> OperationResult
```

Gets the labels for this session.

**Returns**:

    OperationResult: Result containing the labels as data and request ID.
  

**Raises**:

    SessionError: If the operation fails.
  

**Example**:

```python
# Get session labels
try:
    result = session.get_labels()
    if result.success:
        print(f"Session labels: {result.data}")
        # Output: Session labels: {'environment': 'testing', 'project': 'demo', 'version': '1.0.0'}
    else:
        print(f"Failed to get labels: {result.error_message}")
except AgentBayError as e:
    print(f"Failed to get labels: {e}")
```

#### info

```python
def info() -> OperationResult
```

Get detailed information about this session.

**Returns**:

    OperationResult: Result containing SessionInfo object and request ID.
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

    SessionError: If the API request fails or response is invalid.
  
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

    OperationResult: Result containing the access URL and request ID.
  - success (bool): True if the operation succeeded
  - data (str): The access URL
  - request_id (str): Unique identifier for this API request
  

**Raises**:

    SessionError: If port is out of valid range [30100, 30199] or the API request fails.
  

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

    OperationResult: Result containing the link as data and request ID.
  

**Raises**:

    SessionError: If the request fails or the response is invalid.

#### list\_mcp\_tools

```python
def list_mcp_tools(image_id: Optional[str] = None)
```

List MCP tools available for this session.

**Arguments**:

    image_id: Optional image ID, defaults to session's image_id or "linux_latest"
  

**Returns**:

  Result containing tools list and request ID
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_list_mcp_tools():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session
            print(f"Session created: {session.session_id}")
            # Output: Session created: session-04bdwfj7u22a1s30g

            # List all available MCP tools
            tools_result = session.list_mcp_tools()
            print(f"Found {len(tools_result.tools)} MCP tools")
            # Output: Found 69 MCP tools
            print(f"Request ID: {tools_result.request_id}")
            # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

            # Display first 3 tools
            for tool in tools_result.tools[:3]:
                print(f"Tool: {tool.name}")
                # Output: Tool: shell
                print(f"  Description: {tool.description}")
                # Output:   Description: Execute shell commands in the cloud environment
                print(f"  Server: {tool.server}")
                # Output:   Server: mcp-server-system

            # Clean up
            session.delete()
    except Exception as e:
        print(f"Error: {e}")

demonstrate_list_mcp_tools()
```

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

    tool_name: Name of the MCP tool to call
    args: Arguments to pass to the tool as a dictionary
    read_timeout: Optional read timeout in seconds
    connect_timeout: Optional connection timeout in seconds
    auto_gen_session: Whether to automatically generate session if not exists (default: False)
  

**Returns**:

    McpToolResult: Result containing success status, data, and error message
  

**Example**:

```python
# Call the shell tool to execute a command
result = session.call_mcp_tool("shell", {
    "command": "echo 'Hello World'",
    "timeout_ms": 1000
})

if result.success:
    print(f"Output: {result.data}")
    # Output: Hello World
    print(f"Request ID: {result.request_id}")
else:
    print(f"Error: {result.error_message}")

# Call with custom timeouts
result = session.call_mcp_tool(
    "shell",
    {"command": "pwd", "timeout_ms": 1000},
    read_timeout=30,
    connect_timeout=10
)

# Example with error handling
result = session.call_mcp_tool("shell", {
    "command": "invalid_command_12345",
    "timeout_ms": 1000
})
if not result.success:
    print(f"Command failed: {result.error_message}")
    # Output: Command failed: sh: 1: invalid_command_12345: not found
```

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../../common-features/advanced/oss.md)
- [Application API Reference](../../computer-use/application.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
