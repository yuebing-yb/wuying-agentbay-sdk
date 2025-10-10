# AgentBay Class API Reference

The `AgentBay` class is the main entry point for interacting with the AgentBay cloud environment. It provides methods for creating, retrieving, listing, and deleting sessions.

## 📖 Related Tutorials

- [SDK Configuration Guide](../../../docs/guides/common-features/configuration/sdk-configuration.md) - Detailed tutorial on configuring the SDK
- [VPC Sessions Guide](../../../docs/guides/common-features/advanced/vpc-sessions.md) - Tutorial on creating sessions in VPC environments
- [Session Link Access Guide](../../../docs/guides/common-features/advanced/session-link-access.md) - Tutorial on accessing sessions via links

## Constructor

### AgentBay

```python
AgentBay(api_key=None, cfg=None)
```

**Parameters:**
- `api_key` (str, optional): The API key for authentication. If not provided, the SDK will look for the `AGENTBAY_API_KEY` environment variable.
- `cfg` (Config, optional): Configuration object containing region_id, endpoint, and timeout_ms. If not provided, default configuration is used.

**Raises:**
- `ValueError`: If no API key is provided and `AGENTBAY_API_KEY` environment variable is not set.

## Properties

###

```python
context
```
A `ContextService` instance for managing persistent contexts. See the [Context API Reference](context.md) for more details.

## Methods

Creates a new session in the AgentBay cloud environment.

```python
create(params: Optional[CreateSessionParams] = None) -> SessionResult
```

**Parameters:**
- `params` (CreateSessionParams, optional): Parameters for session creation. If None, default parameters will be used.

**Returns:**
- `SessionResult`: A result object containing the new Session instance, success status, request ID, and error message if any.

**Behavior:**
- When `params` includes valid `persistence_data_list`, after creating the session, the API will internally wait for context synchronization to complete.
- It will retrieve ContextStatusData via `session.context.info` and continuously monitor all data items' Status until all items show either "Success" or "Failed" status, or until the maximum retry limit (150 times with 2-second intervals) is reached.
- Any "Failed" status items will have their error messages printed.
- The create operation only returns after context status checking completes.

**Raises:**
- `AgentBayError`: If the session creation fails due to API errors or other issues.

**Example:**
```python
from agentbay import AgentBay, Config
from agentbay.session_params import CreateSessionParams
from agentbay.context_sync import ContextSync, SyncPolicy

# Initialize the SDK with default configuration
agent_bay = AgentBay(api_key="your_api_key")

# Or initialize with custom configuration
config = Config(
    region_id="us-west-1",
    endpoint="https://agentbay.example.com",
    timeout_ms=30000
)
agent_bay_with_config = AgentBay(api_key="your_api_key", cfg=config)

# Create a session with default parameters
default_result = agent_bay.create()
if default_result.success:
    default_session = default_result.session
    print(f"Created session with ID: {default_session.session_id}")

# Create a session with custom parameters
params = CreateSessionParams(
    image_id="linux_latest",
    labels={"project": "demo", "environment": "testing"},
    enable_browser_replay=True  # Enable browser replay for browser sessions
)
custom_result = agent_bay.create(params)
if custom_result.success:
    custom_session = custom_result.session
    print(f"Created custom session with ID: {custom_session.session_id}")

# Create a session with context synchronization
context_sync = ContextSync.new(
    context_id="your_context_id",
    path="/mnt/persistent",
    policy=SyncPolicy.default()
)
sync_params = CreateSessionParams(
    image_id="linux_latest",
    context_syncs=[context_sync]
)
sync_result = agent_bay.create(sync_params)
if sync_result.success:
    sync_session = sync_result.session
    print(f"Created session with context sync: {sync_session.session_id}")

# Create a browser session with browser replay enabled
browser_params = CreateSessionParams(
    image_id="browser_latest",
    enable_browser_replay=True,  # Enable browser replay
)
browser_result = agent_bay.create(browser_params)
if browser_result.success:
    browser_session = browser_result.session
    print(f"Created browser session with replay: {browser_session.session_id}")
    # Browser replay files are automatically generated for internal processing

# Create a mobile session with whitelist configuration
from agentbay.api.models import ExtraConfigs, MobileExtraConfig, AppManagerRule

app_whitelist_rule = AppManagerRule(
    rule_type="White",
    app_package_name_list=[
        "com.android.settings",
        "com.example.trusted.app",
        "com.system.essential.service"
    ]
)
mobile_config = MobileExtraConfig(
    lock_resolution=True,  # Lock screen resolution for consistent testing
    app_manager_rule=app_whitelist_rule
)
extra_configs = ExtraConfigs(mobile=mobile_config)

mobile_params = CreateSessionParams(
    image_id="mobile_latest",
    labels={"project": "mobile-testing", "config_type": "whitelist"},
    extra_configs=extra_configs
)
mobile_result = agent_bay.create(mobile_params)
if mobile_result.success:
    mobile_session = mobile_result.session
    print(f"Created mobile session with whitelist: {mobile_session.session_id}")

# Create a mobile session with blacklist configuration
app_blacklist_rule = AppManagerRule(
    rule_type="Black",
    app_package_name_list=[
        "com.malware.suspicious",
        "com.unwanted.adware",
        "com.social.distraction"
    ]
)
mobile_security_config = MobileExtraConfig(
    lock_resolution=False,  # Allow adaptive resolution
    app_manager_rule=app_blacklist_rule
)
security_extra_configs = ExtraConfigs(mobile=mobile_security_config)

mobile_security_params = CreateSessionParams(
    image_id="mobile_latest",
    labels={"project": "mobile-security", "config_type": "blacklist", "security": "enabled"},
    extra_configs=security_extra_configs
)
security_result = agent_bay.create(mobile_security_params)
if security_result.success:
    security_session = security_result.session
    print(f"Created secure mobile session with blacklist: {security_session.session_id}")
```

### get

Retrieves a session by its ID.

```python
get(session_id: str) -> SessionResult
```

**Parameters:**
- `session_id` (str): The ID of the session to retrieve.

**Returns:**
- `SessionResult`: A result object containing the Session instance, request ID, success status, and error message if any.

**Example:**
```python
from agentbay import AgentBay

agentbay = AgentBay(api_key="your_api_key")

create_result = agentbay.create()
if not create_result.success:
    print(f"Failed to create session: {create_result.error_message}")
    exit(1)

session_id = create_result.session.session_id
print(f"Created session with ID: {session_id}")
# Output: Created session with ID: session-xxxxxxxxxxxxxx

result = agentbay.get(session_id)
if result.success:
    print(f"Successfully retrieved session: {result.session.session_id}")
    # Output: Successfully retrieved session: session-xxxxxxxxxxxxxx
    print(f"Request ID: {result.request_id}")
    # Output: Request ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
    
    delete_result = result.session.delete()
    if delete_result.success:
        print(f"Session {session_id} deleted successfully")
        # Output: Session session-xxxxxxxxxxxxxx deleted successfully
else:
    print(f"Failed to get session: {result.error_message}")
```



```python
list_by_labels(params: Optional[Union[ListSessionParams, Dict[str, str]]] = None) -> SessionListResult
```

**Parameters:**
- `params` (ListSessionParams or Dict[str, str], optional): Parameters for filtering sessions by labels. If a dictionary is provided, it will be treated as labels. If None, all sessions will be returned.

**Returns:**
- `SessionListResult`: A result object containing the filtered sessions, pagination information, and request ID.

**Raises:**
- `AgentBayError`: If the session listing fails.

**Example:**
```python
from agentbay import AgentBay
from agentbay.session_params import ListSessionParams

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create pagination parameters
params = ListSessionParams(
    max_results=10,  # Maximum results per page
    next_token="",   # Token for the next page, empty for the first page
    labels={"environment": "production", "project": "demo"}  # Filter labels
)

# Get the first page of results
result = agent_bay.list_by_labels(params)

# Process the results
if result.success:
    # Print the current page sessions
    for session in result.sessions:
        print(f"Session ID: {session.session_id}")

    # Print pagination information
    print(f"Total count: {result.total_count}")
    print(f"Max results per page: {result.max_results}")
    print(f"Next token: {result.next_token}")

    # If there is a next page, retrieve it
    if result.next_token:
        params.next_token = result.next_token
        next_page_result = agent_bay.list_by_labels(params)
        # Process the next page...
```

### list

Returns paginated list of Sessions filtered by labels.

```python
list(labels: Optional[Dict[str, str]] = None, page: Optional[int] = None, limit: Optional[int] = None) -> SessionListResult
```

**Parameters:**
- `labels` (Optional[Dict[str, str]], optional): Labels to filter Sessions. Defaults to None (empty dict, returns all sessions).
- `page` (Optional[int], optional): Page number for pagination (starting from 1). Defaults to None (returns first page).
- `limit` (Optional[int], optional): Maximum number of items per page. Defaults to None (uses default of 10).

**Returns:**
- `SessionListResult`: Paginated list of session IDs that match the labels, including request_id, success status, and pagination information.

**Key Features:**
- **Simple Interface**: Pass labels directly as a dictionary parameter
- **Pagination Support**: Use `page` and `limit` parameters for easy pagination
- **Request ID**: All responses include a `request_id` for tracking and debugging
- **Flexible Filtering**: Filter by any combination of labels or list all sessions

**Example:**
```python
from agentbay import AgentBay

agent_bay = AgentBay(api_key="your_api_key")

# List all sessions
result = agent_bay.list()

# List sessions with specific labels
result = agent_bay.list(labels={"project": "demo"})

# List sessions with pagination (page 2, 10 items per page)
result = agent_bay.list(labels={"my-label": "my-value"}, page=2, limit=10)

if result.success:
    for session_id in result.session_ids:
        print(f"Session ID: {session_id}")
    print(f"Total count: {result.total_count}")
    print(f"Request ID: {result.request_id}")
else:
    print(f"Error: {result.error_message}")
```

### delete

```python
delete(session: Session, sync_context: bool = False) -> DeleteResult
```

**Parameters:**
- `session` (Session): The session to delete.
- `sync_context` (bool, optional): If True, the API will trigger a file upload via `session.context.sync` before actually releasing the session. Default is False.

**Returns:**
- `DeleteResult`: A result object containing success status, request ID, and error message if any.

**Behavior:**
- When `sync_context` is True, the API will first call `session.context.sync` to trigger file upload.
- It will then check `session.context.info` to retrieve ContextStatusData and monitor all data items' Status.
- The API waits until all items show either "Success" or "Failed" status, or until the maximum retry limit (150 times with 2-second intervals) is reached.
- Any "Failed" status items will have their error messages printed.
- The session deletion only proceeds after context sync status checking completes.

**Raises:**
- `AgentBayError`: If the session deletion fails.

**Example:**
```python
from agentbay import AgentBay

# Initialize the SDK
agent_bay = AgentBay(api_key="your_api_key")

# Create a session
result = agent_bay.create()
if result.success:
    session = result.session
    print(f"Created session with ID: {session.session_id}")

    # Use the session for operations...

    # Delete the session when done
    delete_result = agent_bay.delete(session)
    if delete_result.success:
        print("Session deleted successfully")
    else:
        print(f"Failed to delete session: {delete_result.error_message}")
```

## RecyclePolicy Configuration

The `RecyclePolicy` defines how long context data should be retained and which paths are subject to the policy. It is used within the `SyncPolicy` when creating sessions with context synchronization.

### Lifecycle Options

The `lifecycle` field determines the data retention period:

| Option | Retention Period | Description |
|--------|------------------|-------------|
| `Lifecycle.LIFECYCLE_1DAY` | 1 day | Data deleted after 1 day |
| `Lifecycle.LIFECYCLE_3DAYS` | 3 days | Data deleted after 3 days |
| `Lifecycle.LIFECYCLE_5DAYS` | 5 days | Data deleted after 5 days |
| `Lifecycle.LIFECYCLE_10DAYS` | 10 days | Data deleted after 10 days |
| `Lifecycle.LIFECYCLE_15DAYS` | 15 days | Data deleted after 15 days |
| `Lifecycle.LIFECYCLE_30DAYS` | 30 days | Data deleted after 30 days |
| `Lifecycle.LIFECYCLE_90DAYS` | 90 days | Data deleted after 90 days |
| `Lifecycle.LIFECYCLE_180DAYS` | 180 days | Data deleted after 180 days |
| `Lifecycle.LIFECYCLE_360DAYS` | 360 days | Data deleted after 360 days |
| `Lifecycle.LIFECYCLE_FOREVER` | Permanent | Data never deleted (default) |

**Default Value:** `Lifecycle.LIFECYCLE_FOREVER`

### Paths Configuration

The `paths` field specifies which directories or files should be subject to the recycle policy:

**Rules:**
- Must use exact directory/file paths
- **Wildcard patterns (`* ? [ ]`) are NOT supported**
- Empty string `""` means apply to all paths in the context
- Multiple paths can be specified as a list

**Default Value:** `[""]` (applies to all paths)

### Usage Examples

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.context_sync import ContextSync, SyncPolicy, RecyclePolicy, Lifecycle, UploadPolicy, DownloadPolicy, DeletePolicy, ExtractPolicy, BWList, WhiteList

# Example 1: Apply to all paths with 30-day retention
recycle_policy_1 = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_30DAYS,
    paths=[""]  # Apply to all paths
)

# Example 2: Apply to specific directories with 1-day retention
recycle_policy_2 = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp/logs", "/cache"]  # Apply only to these directories
)

# Example 3: Permanent retention for important data
recycle_policy_3 = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_FOREVER,
    paths=["/important/data"]
)

# Example 4: Create session with custom recycle policy
custom_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy.default(),
    download_policy=DownloadPolicy.default(),
    delete_policy=DeletePolicy.default(),
    extract_policy=ExtractPolicy.default(),
    recycle_policy=recycle_policy_1,  # Use the 30-day retention policy
    bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])])
)

context_sync = ContextSync(
    context_id="my-project-context",
    path="/tmp/data",
    policy=custom_sync_policy
)

params = CreateSessionParams(
    image_id="linux_latest",
    labels={"project": "data-processing", "lifecycle": "30days"},
    context_syncs=[context_sync]
)

agent_bay = AgentBay(api_key="your_api_key")
result = agent_bay.create(params)
if result.success:
    session = result.session
    print(f"Created session with custom recycle policy: {session.session_id}")

# Example 5: Different retention policies for different data types
# Short-term policy for temporary files
short_term_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp", "/cache/temp"]
)

# Long-term policy for backup data
long_term_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_90DAYS,
    paths=["/data/backups"]
)

# Create separate context syncs for different data types
temp_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy.default(),
    download_policy=DownloadPolicy.default(),
    delete_policy=DeletePolicy.default(),
    extract_policy=ExtractPolicy.default(),
    recycle_policy=short_term_policy,
    bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])])
)

backup_sync_policy = SyncPolicy(
    upload_policy=UploadPolicy.default(),
    download_policy=DownloadPolicy.default(),
    delete_policy=DeletePolicy.default(),
    extract_policy=ExtractPolicy.default(),
    recycle_policy=long_term_policy,
    bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])])
)

temp_context_sync = ContextSync(
    context_id="temp-context",
    path="/tmp/workspace",
    policy=temp_sync_policy
)

backup_context_sync = ContextSync(
    context_id="backup-context",
    path="/data/workspace",
    policy=backup_sync_policy
)

multi_context_params = CreateSessionParams(
    image_id="linux_latest",
    labels={"project": "multi-tier-storage"},
    context_syncs=[temp_context_sync, backup_context_sync]
)

multi_result = agent_bay.create(multi_context_params)
if multi_result.success:
    multi_session = multi_result.session
    print(f"Created session with multiple recycle policies: {multi_session.session_id}")
```

### Best Practices

1. **Use appropriate retention periods**: Choose lifecycle options based on your data importance and storage costs
2. **Specify exact paths**: Use precise directory paths instead of wildcards for better control
3. **Separate policies for different data types**: Use different recycle policies for temporary vs. persistent data
4. **Monitor storage usage**: Regularly review and adjust lifecycle settings to optimize storage costs
5. **Test path validation**: Ensure your paths don't contain wildcard characters (`* ? [ ]`) as they are not supported
6. **Consider data dependencies**: When setting short retention periods, ensure dependent processes can complete within the timeframe