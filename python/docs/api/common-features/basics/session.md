# Session Class

The `Session` class represents a session in the AgentBay cloud environment. It provides methods for managing file systems, executing commands, and more.

## 📖 Related Tutorial

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management

## Properties

```python
agent_bay  # The AgentBay instance that created this session
session_id  # The ID of this session
file_system  # The FileSystem instance for this session
command  # The Command instance for this session
code  # The Code instance for this session
oss  # The Oss instance for this session
application  # The ApplicationManager instance for this session
window  # The WindowManager instance for this session
computer  # The Computer instance for this session
mobile  # The Mobile instance for this session
ui  # The UI instance for this session
context  # The ContextManager instance for this session
browser  # The Browser instance for this session
agent  # The Agent instance for this session
is_vpc  # Whether this session uses VPC resources
network_interface_ip  # Network interface IP for VPC sessions
http_port  # HTTP port for VPC sessions
token  # Token for VPC sessions
resource_url  # Resource URL for accessing the session
mcp_tools  # MCP tools available for this session
image_id  # The image ID used for this session
```

## Methods

### delete

Deletes this session.

```python
delete(sync_context: bool = False) -> DeleteResult
```

**Parameters:**
- `sync_context` (bool, optional): If True, the API will trigger a file upload via `self.context.sync` before actually releasing the session. Default is False.

**Returns:**
- `DeleteResult`: A result object containing success status, request ID, and error message if any.

**Behavior:**
- When `sync_context` is True, the API will first call `context.sync` to trigger file upload.
- It will then retrieve ContextStatusData via `context.info` and monitor only upload task items' Status.
- The API waits until all upload tasks show either "Success" or "Failed" status, or until the maximum retry limit (150 times with 2-second intervals) is reached.
- Any "Failed" status upload tasks will have their error messages printed.
- The session deletion only proceeds after context sync status checking for upload tasks completes.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session
result = agent_bay.create()
if result.success:
    session = result.session
    print(f"Session created with ID: {session.session_id}")
    # Output: Session created with ID: session-04bdwfj7u22a1s30g

    # Use the session...

    # Delete the session with context synchronization
    delete_result = session.delete(sync_context=True)
    if delete_result.success:
        print(f"Session deleted successfully with synchronized context")
        # Output: Session deleted successfully with synchronized context
        print(f"Request ID: {delete_result.request_id}")
        # Output: Request ID: D9E69976-9DE0-107D-8047-EE4B4D63AA5D
    else:
        print(f"Failed to delete session: {delete_result.error_message}")
```

### set_labels

Sets labels for this session.

```python
set_labels(labels: Dict[str, str]) -> OperationResult
```

**Parameters:**
- `labels` (Dict[str, str]): Key-value pairs representing the labels to set.

**Returns:**
- `OperationResult`: A result object containing success status, request ID, and error message if any.

**Raises:**
- `AgentBayError`: If setting labels fails due to API errors or other issues.

**Example:**
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

### get_labels

Gets the labels for this session.

```python
get_labels() -> OperationResult
```

**Returns:**
- `OperationResult`: A result object containing success status, request ID, and error message if any, and the labels data.

**Raises:**
- `AgentBayError`: If getting labels fails due to API errors or other issues.

**Example:**
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

### info

Gets information about this session.

```python
info() -> OperationResult
```

**Returns:**
- `OperationResult`: A result object containing success status, request ID, and the session information as data.

**Raises:**
- `AgentBayError`: If getting session information fails due to API errors or other issues.

**Example:**
```python
# Get session information
try:
    result = session.info()
    if result.success:
        info = result.data
        print(f"Session ID: {info.session_id}")
        # Output: Session ID: session-04bdwfj7u22a1s30k
        print(f"Resource URL: {info.resource_url[:80]}...")
        # Output: Resource URL: https://pre-myspace-wuying.aliyun.com/app/InnoArchClub/mcp_container/mcp.html?au...
        print(f"App ID: {info.app_id}")
        # Output: App ID: mcp-server-ubuntu
    else:
        print(f"Failed to get session info: {result.error_message}")
except AgentBayError as e:
    print(f"Failed to get session info: {e}")
```

### get_link

Gets a link for this session.

```python
get_link(protocol_type: Optional[str] = None, port: Optional[int] = None, options: Optional[str] = None) -> OperationResult
```

**Parameters:**
- `protocol_type` (str, optional): The protocol type for the link.
- `port` (int, optional): The port for the link. Must be an integer in the range [30100, 30199]. If not specified, the default port will be used.
- `options` (str, optional): Additional options as a JSON string (e.g., for adb configuration). Defaults to None.

**Returns:**
- `OperationResult`: A result object containing success status, request ID, and the link URL as data.

**Raises:**
- `SessionError`: If the port value is invalid (not an integer or outside the valid range [30100, 30199]).
- `AgentBayError`: If getting the link fails due to API errors or other issues.

**Example:**
```python
# Get link with specific protocol and valid port
# Note: For ComputerUse images, port must be explicitly specified
try:
    result = session.get_link("https", 30150)
    if result.success:
        link = result.data
        print(f"Session link: {link[:80]}...")
        # Output: Session link: https://gw-cn-hangzhou-i-ai-test0-linux.wuyinggw.com:8008/request_ai/00Lw4a5HtJ9...
        print(f"Request ID: {result.request_id}")
        # Output: Request ID: 5CA891B8-1E45-13B0-9975-0258228008CB
    else:
        print(f"Failed to get link: {result.error_message}")

    # Example with invalid port (will raise SessionError)
    try:
        invalid_result = session.get_link(port=8080)  # Invalid: outside [30100, 30199]
    except SessionError as e:
        print(f"Port validation error: {e}")
        # Output: Port validation error: Invalid port value: 8080. Port must be an integer in the range [30100, 30199].

except AgentBayError as e:
    print(f"Failed to get link: {e}")
```

### get_link_async

Asynchronously gets a link for this session.

```python
async get_link_async(protocol_type: Optional[str] = None, port: Optional[int] = None, options: Optional[str] = None) -> OperationResult
```

**Parameters:**
- `protocol_type` (str, optional): The protocol type for the link.
- `port` (int, optional): The port for the link. Must be an integer in the range [30100, 30199]. If not specified, the default port will be used.
- `options` (str, optional): Additional options as a JSON string (e.g., for adb configuration). Defaults to None.

**Returns:**
- `OperationResult`: A result object containing success status, request ID, and the link URL as data.

**Raises:**
- `SessionError`: If the port value is invalid (not an integer or outside the valid range [30100, 30199]).
- `AgentBayError`: If getting the link fails due to API errors or other issues.

**Example:**
```python
import asyncio

async def get_session_link():
    try:
        # Get session link with default settings
        result = await session.get_link_async()
        if result.success:
            link = result.data
            print(f"Session link: {link}")
        else:
            print(f"Failed to get link: {result.error_message}")

        # Get link with specific protocol and valid port
        custom_result = await session.get_link_async("wss", 30199)
        if custom_result.success:
            custom_link = custom_result.data
            print(f"Custom WebSocket link: {custom_link}")
        else:
            print(f"Failed to get custom link: {custom_result.error_message}")

    except SessionError as e:
        print(f"Port validation error: {e}")
    except AgentBayError as e:
        print(f"Failed to get link: {e}")

# Run the async function
asyncio.run(get_session_link())
```

### list_mcp_tools

Lists MCP tools available for this session.

```python
list_mcp_tools(image_id: Optional[str] = None) -> McpToolsResult
```

**Parameters:**
- `image_id` (str, optional): The image ID to list tools for. Defaults to the session's image_id or "linux_latest".

**Returns:**
- `McpToolsResult`: A result object containing success status, request ID, and the list of MCP tools.

**Raises:**
- `AgentBayError`: If listing MCP tools fails due to API errors or other issues.

**Example:**
```python
# List all available MCP tools
result = session.list_mcp_tools()
print(f"Found {len(result.tools)} MCP tools")
# Output: Found 69 MCP tools

# Display first 3 tools
for tool in result.tools[:3]:
    print(f"Tool: {tool.name}")
    print(f"  Description: {tool.description}")
    print(f"  Server: {tool.server}")
```

### call_mcp_tool

Call an MCP tool directly. This is the unified public API for calling MCP tools. All feature modules (Command, Code, Agent, etc.) use this method internally.

```python
call_mcp_tool(
    tool_name: str,
    args: Dict[str, Any],
    read_timeout: Optional[int] = None,
    connect_timeout: Optional[int] = None
) -> McpToolResult
```

**Parameters:**
- `tool_name` (str): Name of the MCP tool to call
- `args` (Dict[str, Any]): Arguments to pass to the tool as a dictionary
- `read_timeout` (int, optional): Read timeout in seconds
- `connect_timeout` (int, optional): Connection timeout in seconds

**Returns:**
- `McpToolResult`: Result containing:
  - `success` (bool): Whether the tool call was successful
  - `data` (str): Tool output data
  - `error_message` (str): Error message if the call failed
  - `request_id` (str): Unique identifier for the API request

**Raises:**
- `AgentBayError`: If calling the MCP tool fails due to API errors or other issues.

**Behavior:**
- Automatically detects VPC vs non-VPC mode
- In VPC mode, uses HTTP requests to the VPC endpoint
- In non-VPC mode, uses traditional API calls
- Parses response data to extract text content
- Handles both successful results and error responses

**Example:**
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

**See Also:**
- For a complete example, see [MCP Tool Direct Call Example](../../../../examples/common-features/basics/mcp_tool_direct_call/README.md)

### pause

Synchronously pause this session, putting it into a dormant state to reduce resource usage and costs.

```python
pause(timeout: int = 600, poll_interval: float = 2.0) -> SessionPauseResult
```

**Parameters:**
- `timeout` (int, optional): Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Defaults to 2.0 seconds.

**Returns:**
- `SessionPauseResult`: A result object containing:
  - `success` (bool): Whether the pause operation was successful
  - `request_id` (str): Unique identifier for the API request
  - `status` (str): Current status of the session ("PAUSED" when successful)
  - `error_message` (str): Error message if the operation failed

**Behavior:**
- Calls the PauseSessionAsync API to initiate the pause operation
- Polls the GetSession API to check session status until it becomes "PAUSED" or timeout
- During pause, compute resources are suspended but storage is preserved
- Resource usage and costs are lower during pause

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK and create a session
agent_bay = AgentBay(api_key="your_api_key")
session_result = agent_bay.create()
session = session_result.session

# Perform your tasks...

# Pause the session to reduce resource usage
pause_result = session.pause()
if pause_result.success:
    print("Session paused successfully")
    print(f"Request ID: {pause_result.request_id}")
    # Output: Session paused successfully
    # Output: Request ID: B1F98082-52F0-17F7-A149-7722D6205AD6
else:
    print(f"Failed to pause session: {pause_result.error_message}")
```

### pause_async

Asynchronously pause this session, putting it into a dormant state to reduce resource usage and costs.

```python
async pause_async(timeout: int = 600, poll_interval: float = 2.0) -> SessionPauseResult
```

**Parameters:**
- `timeout` (int, optional): Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Defaults to 2.0 seconds.

**Returns:**
- `SessionPauseResult`: A result object containing:
  - `success` (bool): Whether the pause operation was successful
  - `request_id` (str): Unique identifier for the API request
  - `status` (str): Current status of the session ("PAUSED" when successful)
  - `error_message` (str): Error message if the operation failed

**Behavior:**
- Calls the PauseSessionAsync API to initiate the pause operation
- Polls the GetSession API to check session status until it becomes "PAUSED" or timeout
- During pause, compute resources are suspended but storage is preserved
- Resource usage and costs are lower during pause

**Example:**
```python
import asyncio
from agentbay import AgentBay

async def pause_session_example():
    # Initialize the SDK and create a session
    agent_bay = AgentBay(api_key="your_api_key")
    session_result = agent_bay.create()
    session = session_result.session

    # Perform your tasks...

    # Asynchronously pause the session to reduce resource usage
    pause_result = await session.pause_async()
    if pause_result.success:
        print("Session paused successfully")
        print(f"Request ID: {pause_result.request_id}")
        # Output: Session paused successfully
        # Output: Request ID: B1F98082-52F0-17F7-A149-7722D6205AD6
    else:
        print(f"Failed to pause session: {pause_result.error_message}")

# Run the async function
asyncio.run(pause_session_example())
```

### resume

Synchronously resume this session from a paused state to continue work.

```python
resume(timeout: int = 600, poll_interval: float = 2.0) -> SessionResumeResult
```

**Parameters:**
- `timeout` (int, optional): Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Defaults to 2.0 seconds.

**Returns:**
- `SessionResumeResult`: A result object containing:
  - `success` (bool): Whether the resume operation was successful
  - `request_id` (str): Unique identifier for the API request
  - `status` (str): Current status of the session ("RUNNING" when successful)
  - `error_message` (str): Error message if the operation failed

**Behavior:**
- Calls the ResumeSessionAsync API to initiate the resume operation
- Polls the GetSession API to check session status until it becomes "RUNNING" or timeout
- All session state is preserved during pause and resume operations

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK and get a paused session
agent_bay = AgentBay(api_key="your_api_key")
# Assuming you have a paused session with session_id
get_result = agent_bay.get("your_paused_session_id")
if get_result.success:
    session = get_result.session
    
    # Resume the session to continue work
    resume_result = session.resume()
    if resume_result.success:
        print("Session resumed successfully")
        print(f"Request ID: {resume_result.request_id}")
        # Output: Session resumed successfully
        # Output: Request ID: C2A87193-63E1-28G8-B25A-8833E7316BE7
        
        # Continue with your tasks...
        result = session.command.execute_command("echo 'Hello after resume!'")
        print(f"Command output: {result.output}")
    else:
        print(f"Failed to resume session: {resume_result.error_message}")
else:
    print(f"Failed to get session: {get_result.error_message}")
```

### resume_async

Asynchronously resume this session from a paused state to continue work.

```python
async resume_async(timeout: int = 600, poll_interval: float = 2.0) -> SessionResumeResult
```

**Parameters:**
- `timeout` (int, optional): Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
- `poll_interval` (float, optional): Interval in seconds between status polls. Defaults to 2.0 seconds.

**Returns:**
- `SessionResumeResult`: A result object containing:
  - `success` (bool): Whether the resume operation was successful
  - `request_id` (str): Unique identifier for the API request
  - `status` (str): Current status of the session ("RUNNING" when successful)
  - `error_message` (str): Error message if the operation failed

**Behavior:**
- Calls the ResumeSessionAsync API to initiate the resume operation
- Polls the GetSession API to check session status until it becomes "RUNNING" or timeout
- All session state is preserved during pause and resume operations

**Example:**
```python
import asyncio
from agentbay import AgentBay

async def resume_session_example():
    # Initialize the SDK and get a paused session
    agent_bay = AgentBay(api_key="your_api_key")
    # Assuming you have a paused session with session_id
    get_result = agent_bay.get("your_paused_session_id")
    if get_result.success:
        session = get_result.session
        
        # Asynchronously resume the session to continue work
        resume_result = await session.resume_async()
        if resume_result.success:
            print("Session resumed successfully")
            print(f"Request ID: {resume_result.request_id}")
            # Output: Session resumed successfully
            # Output: Request ID: C2A87193-63E1-28G8-B25A-8833E7316BE7
            
            # Continue with your tasks...
            result = session.command.execute_command("echo 'Hello after async resume!'")
            print(f"Command output: {result.output}")
        else:
            print(f"Failed to resume session: {resume_result.error_message}")
    else:
        print(f"Failed to get session: {get_result.error_message}")

# Run the async function
asyncio.run(resume_session_example())
```

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [UI API Reference](../../computer-use/ui.md)
- [Window API Reference](../../computer-use/window.md)
- [OSS API Reference](../advanced/oss.md)
- [Application API Reference](../../computer-use/application.md)
- [Context API Reference](context-manager.md)
