# AgentBay API Reference

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

- `params` _Optional[CreateSessionParams], optional_ - Parameters for
  creating the session.Defaults to None.
  

**Returns**:

- `SessionResult` - Result containing the created session and request ID.

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
  Defaults to None (empty dict).
- `page` _Optional[int], optional_ - Page number for pagination (starting from 1).
  Defaults to None (returns first page).
- `limit` _Optional[int], optional_ - Maximum number of items per page.
  Defaults to None (uses default of 10).
  

**Returns**:

- `SessionListResult` - Paginated list of session IDs that match the labels,
  including request_id, success status, and pagination information.
  

**Example**:

    ```python
    from agentbay import AgentBay

    agent_bay = AgentBay(api_key="your_api_key")

    # List all sessions
    result = agent_bay.list()

    # List sessions with specific labels
    result = agent_bay.list(labels={"project": "demo"})

    # List sessions with pagination
    result = agent_bay.list(labels={"my-label": "my-value"}, page=2, limit=10)

    if result.success:
        for session_id in result.session_ids:
            print(f"Session ID: {session_id}")
        print(f"Total count: {result.total_count}")
        print(f"Request ID: {result.request_id}")
    ```

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

This method retrieves a session by calling the GetSession API
and returns a SessionResult containing the Session object and request ID.

**Arguments**:

- `session_id` _str_ - The ID of the session to retrieve.
  

**Returns**:

- `SessionResult` - Result containing the Session instance, request ID, and success status.
  

**Example**:

  >>> result = agentbay.get("my-session-id")
  >>> if result.success:
  >>>     print(result.session.session_id)
  >>>     print(result.request_id)

---

*Documentation generated automatically from source code using pydoc-markdown.*
