# AgentBay API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session



```python
logger = get_logger("agentbay")
```

#### generate\_random\_context\_name

```python
def generate_random_context_name(length: int = 8,
                                 include_timestamp: bool = True) -> str
```

Generate a random context name string using alphanumeric characters with optional timestamp.

**Arguments**:

- `length` _int_ - Length of the random part. Defaults to 16.
- `include_timestamp` _bool_ - Whether to include timestamp. Defaults to True.
  

**Returns**:

- `str` - Random alphanumeric string with optional timestamp prefix
  

**Examples**:

  generate_random_context_name()  # Returns: "20250912143025_kG8hN2pQ7mX9vZ1L"
  generate_random_context_name(8, False)  # Returns: "kG8hN2pQ"

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

- `SessionResult` - Result containing the created session and request ID.
  - success (bool): True if the operation succeeded
  - session (Session): The created session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `ValueError` - If API key is not provided and AGENTBAY_API_KEY environment variable is not set.
- `ClientException` - If the API request fails due to network or authentication issues.
  

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

#### list\_by\_labels

```python
@deprecated(
    reason="This method is deprecated and will be removed in a future version.",
    replacement="list()",
)
def list_by_labels(
    params: Optional[Union[ListSessionParams, Dict[str, str]]] = None
) -> SessionListResult
```

Lists sessions filtered by the provided labels with pagination support.
It returns sessions that match all the specified labels.

**Arguments**:

  params (Optional[Union[ListSessionParams, Dict[str, str]]], optional):
  Parameters for listing sessions or a dictionary of labels.
  Defaults to None.
  

**Returns**:

- `SessionListResult` - Result containing a list of sessions and pagination
  information.

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

- `SessionListResult` - Paginated list of session IDs that match the labels.
  - success (bool): True if the operation succeeded
  - session_ids (List[str]): List of session IDs
  - request_id (str): Unique identifier for this API request
  - next_token (str): Token for fetching the next page (empty if no more pages)
  - max_results (int): Maximum number of results per page
  - total_count (int): Total number of sessions matching the filter
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `ClientException` - If the API request fails due to network or authentication issues.
  

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

- `DeleteResult` - Result indicating success or failure and request ID.

#### get\_session

```python
def get_session(session_id: str) -> GetSessionResult
```

Get session information by session ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve.
  

**Returns**:

- `GetSessionResult` - Result containing session information.

#### get

```python
def get(session_id: str) -> SessionResult
```

Get a session by its ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve. Must be a non-empty string.
  

**Returns**:

- `SessionResult` - Result containing the Session instance, request ID, and success status.
  - success (bool): True if the operation succeeded
  - session (Session): The session object (if success is True)
  - request_id (str): Unique identifier for this API request
  - error_message (str): Error description (if success is False)
  

**Raises**:

- `ClientException` - If the API request fails due to network or authentication issues.
  

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
