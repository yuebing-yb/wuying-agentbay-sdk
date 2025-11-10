# AgentBay API Reference

#### generate\_random\_context\_name

```python
def generate_random_context_name(length: int = 8,
                                 include_timestamp: bool = True) -> str
```

Generate a random context name string using alphanumeric characters with optional timestamp.

**Arguments**:

- `length` _int_ - Length of the random part. Defaults to 8.
- `include_timestamp` _bool_ - Whether to include timestamp prefix. Defaults to True.
  

**Returns**:

    str: Random alphanumeric string with optional timestamp prefix in format:
  - With timestamp: "YYYYMMDDHHMMSS_<random>" (e.g., "20250112143025_kG8hN2pQ")
  - Without timestamp: "<random>" (e.g., "kG8hN2pQ")
  

**Example**:

```python
from agentbay import AgentBay, generate_random_context_name

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_generate_context_name():
    try:
        # Generate context name with timestamp (default)
        name_with_timestamp = generate_random_context_name()
        print(f"Context name with timestamp: {name_with_timestamp}")
        # Output: Context name with timestamp: 20250112143025_kG8hN2pQ

        # Generate context name without timestamp
        name_without_timestamp = generate_random_context_name(8, False)
        print(f"Context name without timestamp: {name_without_timestamp}")
        # Output: Context name without timestamp: kG8hN2pQ

        # Generate longer random name
        long_name = generate_random_context_name(16, False)
        print(f"Long context name: {long_name}")
        # Output: Long context name: kG8hN2pQ7mX9vZ1L

        # Use generated name to create a context
        context_name = generate_random_context_name()
        result = agent_bay.context.get(context_name, create=True)
        if result.success:
            print(f"Created context: {result.context.name}")
            # Output: Created context: 20250112143025_kG8hN2pQ
            print(f"Context ID: {result.context.id}")
            # Output: Context ID: ctx-12345678

    except Exception as e:
        print(f"Error: {e}")

demonstrate_generate_context_name()
```
  

**Notes**:

  - Characters are randomly selected from a-zA-Z0-9
  - Timestamp format is YYYYMMDDHHMMSS (local time)
  - Useful for creating unique context names that can be sorted chronologically
  

**See Also**:

  AgentBay.context.get, AgentBay.context.create

## Config Objects

```python
class Config()
```

## AgentBay Objects

```python
class AgentBay()
```

AgentBay represents the main client for interacting with the AgentBay cloud runtime
environment.

#### create

```python
def create(params: Optional[CreateSessionParams] = None) -> SessionResult
```

Create a new session in the AgentBay cloud environment.

**Arguments**:

- `params` _Optional[CreateSessionParams], optional_ - Parameters for creating the session.
  Defaults to None (uses default configuration).
  

**Returns**:

    SessionResult: Result containing the created session and request ID.
  - success (bool): True if the operation succeeded
  - session (Session): The created session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    ValueError: If API key is not provided and AGENTBAY_API_KEY environment variable is not set.
    ClientException: If the API request fails due to network or authentication issues.
  

**Example**:

```python
from agentbay import AgentBay, CreateSessionParams

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session with default parameters
result = agent_bay.create()
if result.success:
    session = result.session
    print(f"Session created: {session.session_id}")
    # Output: Session created: session-04bdwfj7u22a1s30g
    print(f"Request ID: {result.request_id}")
    # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

    # Use the session
    info_result = session.info()
    if info_result.success:
        print(f"Session status: {info_result.data['Status']}")
        # Output: Session status: Running

    # Clean up
    session.delete()

# Create a session with custom parameters
params = CreateSessionParams(
    image_id="browser-chrome",
    labels={"project": "demo", "env": "test"}
)
result = agent_bay.create(params)
if result.success:
    print(f"Session created with labels: {result.session.session_id}")
    result.session.delete()

# Create a browser session with browser replay enabled
browser_params = CreateSessionParams(
    image_id="browser_latest",
    enable_browser_replay=True  # Enable browser replay
)
browser_result = agent_bay.create(browser_params)
if browser_result.success:
    browser_session = browser_result.session
    print(f"Created browser session with replay: {browser_session.session_id}")
    # Browser replay files are automatically generated for internal processing
    browser_session.delete()
```
  

**Notes**:

  - A default file transfer context is automatically created for each session
  - For VPC sessions, MCP tools information is automatically fetched
  - If context_syncs are provided, the method waits for synchronization to complete
  - Session is automatically cached in the AgentBay instance
  

**See Also**:

  AgentBay.get, AgentBay.list, Session.delete, CreateSessionParams

#### list

```python
def list(labels: Optional[Dict[str, str]] = None,
         page: Optional[int] = None,
         limit: Optional[int] = None) -> SessionListResult
```

Returns paginated list of session IDs filtered by labels.

**Arguments**:

- `labels` _Optional[Dict[str, str]], optional_ - Labels to filter sessions.
  Defaults to None (returns all sessions).
- `page` _Optional[int], optional_ - Page number for pagination (starting from 1).
  Defaults to None (returns first page).
- `limit` _Optional[int], optional_ - Maximum number of items per page.
  Defaults to None (uses default of 10).
  

**Returns**:

    SessionListResult: Paginated list of session IDs that match the labels.
  - success (bool): True if the operation succeeded
  - session_ids (List[str]): List of session IDs
  - request_id (str): Unique identifier for this API request
  - next_token (str): Token for fetching the next page (empty if no more pages)
  - max_results (int): Maximum number of results per page
  - total_count (int): Total number of sessions matching the filter
  - error_message (str): Error description (if success is False)
  

**Raises**:

    ClientException: If the API request fails due to network or authentication issues.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create some sessions with labels
for i in range(3):
    params = CreateSessionParams(labels={"project": "demo", "index": str(i)})
    result = agent_bay.create(params)
    if result.success:
        print(f"Created session {i}: {result.session.session_id}")

# List all sessions
result = agent_bay.list()
if result.success:
    print(f"Total sessions: {result.total_count}")
    # Output: Total sessions: 3
    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
    # Output: Session ID: session-04bdwfj7u22a1s30g
    # Output: Session ID: session-04bdwfj7u22a1s30h
    # Output: Session ID: session-04bdwfj7u22a1s30i

# List sessions with specific labels
result = agent_bay.list(labels={"project": "demo"})
if result.success:
    print(f"Sessions with project=demo: {len(result.session_ids)}")
    # Output: Sessions with project=demo: 3

# List sessions with pagination
result = agent_bay.list(labels={"project": "demo"}, page=1, limit=2)
if result.success:
    print(f"Page 1: {len(result.session_ids)} sessions")
    # Output: Page 1: 2 sessions
    print(f"Has more pages: {bool(result.next_token)}")
    # Output: Has more pages: True

# Get next page
result = agent_bay.list(labels={"project": "demo"}, page=2, limit=2)
if result.success:
    print(f"Page 2: {len(result.session_ids)} sessions")
    # Output: Page 2: 1 sessions
```
  

**Notes**:

  - Page numbers start from 1
  - Returns error if page number is less than 1
  - Returns error if requested page exceeds available pages
  - Empty labels dict returns all sessions
  

**See Also**:

  AgentBay.create, AgentBay.get, Session.info

#### delete

```python
def delete(session: Session, sync_context: bool = False) -> DeleteResult
```

Delete a session by session object.

**Arguments**:

- `session` _Session_ - The session to delete.
- `sync_context` _bool_ - Whether to sync context data (trigger file uploads)
  before deleting the session. Defaults to False.
  

**Returns**:

    DeleteResult: Result indicating success or failure and request ID.
  - success (bool): True if deletion succeeded
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_delete():
    try:
        # Create a session
        result = agent_bay.create()
        if result.success:
            session = result.session
            print(f"Created session: {session.session_id}")
            # Output: Created session: session-04bdwfj7u22a1s30g

            # Use the session
            info_result = session.info()
            if info_result.success:
                print(f"Session status: {info_result.data['Status']}")
                # Output: Session status: Running

            # Delete the session without syncing context
            delete_result = agent_bay.delete(session)
            if delete_result.success:
                print("Session deleted successfully")
                # Output: Session deleted successfully
                print(f"Request ID: {delete_result.request_id}")
                # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

        # Create another session and delete with context sync
        result = agent_bay.create()
        if result.success:
            session = result.session

            # Write some files to the session
            session.file_system.write_file("/tmp/test.txt", "test content")

            # Delete with context sync (triggers file upload to OSS)
            delete_result = agent_bay.delete(session, sync_context=True)
            if delete_result.success:
                print("Session deleted with context sync")
                # Output: Session deleted with context sync

    except Exception as e:
        print(f"Error: {e}")

demonstrate_delete()
```
  

**Notes**:

  - After deletion, the session object is removed from the AgentBay cache
  - If sync_context=True, context data is uploaded to OSS before deletion
  - Session cannot be used after deletion
  

**See Also**:

  Session.delete, AgentBay.create, AgentBay.get

#### get\_session

```python
def get_session(session_id: str) -> GetSessionResult
```

Get session information by session ID.

This method retrieves detailed session metadata from the API. Unlike `get()`,
this returns raw session data without creating a Session object.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve.
  

**Returns**:

    GetSessionResult: Result containing session information.
  - success (bool): True if the operation succeeded
  - data (GetSessionData): Session information object with fields:
  - session_id (str): Session ID
  - app_instance_id (str): Application instance ID
  - resource_id (str): Resource ID
  - resource_url (str): Resource URL for accessing the session
  - vpc_resource (bool): Whether this is a VPC resource
  - network_interface_ip (str): Network interface IP (for VPC sessions)
  - http_port (str): HTTP port (for VPC sessions)
  - token (str): Authentication token (for VPC sessions)
  - request_id (str): Unique identifier for this API request
  - http_status_code (int): HTTP status code
  - code (str): API response code
  - error_message (str): Error description (if success is False)
  

**Example**:

```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

def demonstrate_get_session():
    try:
        # Create a session first
        create_result = agent_bay.create()
        if create_result.success:
            session_id = create_result.session.session_id
            print(f"Created session: {session_id}")
            # Output: Created session: session-04bdwfj7u22a1s30g

            # Get session information
            get_result = agent_bay.get_session(session_id)
            if get_result.success:
                print("Session information retrieved:")
                # Output: Session information retrieved:
                print(f"  Session ID: {get_result.data.session_id}")
                # Output:   Session ID: session-04bdwfj7u22a1s30g
                print(f"  App Instance ID: {get_result.data.app_instance_id}")
                # Output:   App Instance ID: ai-12345678
                print(f"  Resource URL: {get_result.data.resource_url[:50]}...")
                # Output:   Resource URL: https://session.agentbay.com/...
                print(f"  VPC Resource: {get_result.data.vpc_resource}")
                # Output:   VPC Resource: False
                print(f"  Request ID: {get_result.request_id}")
                # Output:   Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B
            else:
                print(f"Failed to get session: {get_result.error_message}")

            # Clean up
            create_result.session.delete()

        # Try to get a non-existent session
        get_result = agent_bay.get_session("non-existent-session")
        if not get_result.success:
            print(f"Error: {get_result.error_message}")
            # Output: Error: Session non-existent-session not found

    except Exception as e:
        print(f"Error: {e}")

demonstrate_get_session()
```
  

**Notes**:

  - Returns session metadata without creating a Session object
  - Use `get()` instead if you need a Session object for API calls
  - Returns error if session does not exist or is no longer valid
  

**See Also**:

  AgentBay.get, AgentBay.create, Session.info

#### get

```python
def get(session_id: str) -> SessionResult
```

Get a session by its ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve. Must be a non-empty string.
  

**Returns**:

    SessionResult: Result containing the Session instance, request ID, and success status.
  - success (bool): True if the operation succeeded
  - session (Session): The session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

    ClientException: If the API request fails due to network or authentication issues.
  

**Example**:

```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session first
create_result = agent_bay.create()
if create_result.success:
    session_id = create_result.session.session_id
    print(f"Created session: {session_id}")
    # Output: Created session: session-04bdwfj7u22a1s30g

    # Get the session by ID
    get_result = agent_bay.get(session_id)
    if get_result.success:
        session = get_result.session
        print(f"Retrieved session: {session.session_id}")
        # Output: Retrieved session: session-04bdwfj7u22a1s30g
        print(f"Request ID: {get_result.request_id}")
        # Output: Request ID: 9E3F4A5B-2C6D-7E8F-9A0B-1C2D3E4F5A6B

        # Use the session
        info_result = session.info()
        if info_result.success:
            print(f"Session status: {info_result.data['Status']}")
            # Output: Session status: Running

        # Clean up
        session.delete()

# Handle session not found
result = agent_bay.get("non-existent-session")
if not result.success:
    print(f"Error: {result.error_message}")
    # Output: Error: Failed to get session non-existent-session: Session non-existent-session not found
```
  

**Notes**:

  - A default file transfer context is automatically created for the retrieved session
  - VPC-related information (network_interface_ip, http_port, token) is populated from the API response
  - Returns an error if session_id is empty or the session does not exist
  

**See Also**:

  AgentBay.create, AgentBay.list, Session.info

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
