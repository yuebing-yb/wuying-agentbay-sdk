import asyncio
import json
import os
import random
import string
import time
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional, Union

from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_openapi.exceptions._client import ClientException

from .._common.config import _BROWSER_DATA_PATH, _load_config
from .._common.logger import (
    _log_api_call,
    _log_api_response,
    _log_api_response_with_details,
    _log_info_with_color,
    _log_operation_error,
    _log_operation_start,
    _log_operation_success,
    _log_warning,
    _mask_sensitive_data,
    get_logger,
)
from .._common.models import (
    DeleteResult,
    GetSessionData,
    GetSessionResult,
    SessionListResult,
    SessionPauseResult,
    SessionResult,
    SessionResumeResult,
    extract_request_id,
)
from .._common.version import __is_release__, __version__
from ..api.client import Client as mcp_client
from ..api.models import CreateMcpSessionRequest, GetSessionRequest, ListSessionRequest
from .context import AsyncContextService
from .mobile_simulate import AsyncMobileSimulateService
from .session import AsyncSession
from .session_params import CreateSessionParams, ListSessionParams

# Initialize logger for this module
_logger = get_logger("agentbay")


def _generate_random_context_name(
    length: int = 8, include_timestamp: bool = True
) -> str:
    """
    Generate a random context name string using alphanumeric characters with optional timestamp.

    This is an internal helper function used by the SDK to generate unique context names.

    Args:
        length (int): Length of the random part. Defaults to 8.
        include_timestamp (bool): Whether to include timestamp prefix. Defaults to True.

    Returns:
        str: Random alphanumeric string with optional timestamp prefix in format:
            - With timestamp: "YYYYMMDDHHMMSS_<random>" (e.g., "20250112143025_kG8hN2pQ")
            - Without timestamp: "<random>" (e.g., "kG8hN2pQ")

    Note:
        - This is a private function for internal SDK use only
        - Characters are randomly selected from a-zA-Z0-9
        - Timestamp format is YYYYMMDDHHMMSS (local time)
        - Useful for creating unique context names that can be sorted chronologically
    """
    import time

    random_part = "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )

    if include_timestamp:
        # Format: YYYYMMDDHHMMSS
        timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
        return f"{timestamp}_{random_part}"
    else:
        return random_part


class Config:
    def __init__(self, endpoint: str, timeout_ms: int):
        self.endpoint = endpoint
        self.timeout_ms = timeout_ms


class AsyncAgentBay:
    """
    AsyncAgentBay represents the main client for interacting with the AgentBay cloud runtime
    environment asynchronously.
    """

    def __init__(
        self,
        api_key: str = "",
        cfg: Optional[Config] = None,
        env_file: Optional[str] = None,
    ):
        """
        Initialize AsyncAgentBay client.

        Args:
            api_key: API key for authentication. If not provided, will read from AGENTBAY_API_KEY environment variable.
            cfg: Configuration object. If not provided, will load from environment variables and .env file.
            env_file: Custom path to .env file. If not provided, will search upward from current directory.
        """
        if not api_key:
            api_key = os.getenv("AGENTBAY_API_KEY") or ""
            if not api_key:
                raise ValueError(
                    "API key is required. Provide it as a parameter or set the "
                    "AGENTBAY_API_KEY environment variable"
                )

        # Load configuration with optional custom env file path
        config_data = _load_config(cfg, env_file)

        self.api_key = api_key

        config = open_api_models.Config()
        config.endpoint = config_data["endpoint"]
        config.read_timeout = config_data["timeout_ms"]
        config.connect_timeout = config_data["timeout_ms"]

        self.client = mcp_client(config)
        self._sessions = {}
        self._lock = Lock()

        # Initialize context service
        self.context = AsyncContextService(self)
        self._file_transfer_context: Optional[Any] = None
        
        # Initialize mobile simulate service
        self.mobile_simulate = AsyncMobileSimulateService(self)

    def _safe_serialize(self, obj):
        """
        Helper function to serialize objects to JSON-compatible format.

        Args:
            obj: The object to serialize.

        Returns:
            JSON-serializable representation of the object.
        """
        try:
            if isinstance(obj, Enum):
                return obj.value
            elif hasattr(obj, "__dict__") and callable(obj.__dict__):
                return obj.__dict__()
            elif hasattr(obj, "__dict__"):
                return obj.__dict__
            elif hasattr(obj, "to_map"):
                return obj.to_map()
            elif hasattr(obj, "to_dict"):
                return obj.to_dict()
            else:
                return str(obj)
        except:
            return str(obj)

    def _build_session_from_response(
        self,
        response_data: dict,
        params: CreateSessionParams,
        record_context_id: Optional[str] = None,
    ) -> AsyncSession:
        """
        Build Session object from API response data.

        Args:
            response_data: Data field from API response
            params: Parameters for creating the session
            record_context_id: Request ID

        Returns:
            AsyncSession: Built Session object
        """
        session_id = response_data.get("SessionId")
        if not session_id:
            raise ValueError("SessionId not found in response data")

        resource_url = response_data.get("ResourceUrl", "")

        _logger.info(f"🆔 Session created: {session_id}")
        _logger.debug(f"🔗 Resource URL: {resource_url}")

        # Create Session object
        session = AsyncSession(self, session_id)

        # Set VPC-related information from response
        session.is_vpc = params.is_vpc
        if response_data.get("NetworkInterfaceIp"):
            session.network_interface_ip = response_data["NetworkInterfaceIp"]
        if response_data.get("HttpPort"):
            session.http_port = response_data["HttpPort"]
        if response_data.get("Token"):
            session.token = response_data["Token"]

        # Set ResourceUrl
        session.resource_url = resource_url

        # Set browser recording state
        session.enableBrowserReplay = params.enable_browser_replay

        # Store the file transfer context ID if we created one
        session.file_transfer_context_id = (
            self._file_transfer_context.id if self._file_transfer_context else None
        )

        # Store the browser recording context ID if we created one
        session.record_context_id = record_context_id

        # Store image_id used for this session
        setattr(session, "image_id", params.image_id)

        # Process mobile configuration if provided
        if (
            hasattr(params, "extra_configs")
            and params.extra_configs
            and params.extra_configs.mobile
        ):
            session.mobile.configure(params.extra_configs.mobile)

        # Store session in cache
        with self._lock:
            self._sessions[session_id] = session

        return session

    async def _fetch_mcp_tools_for_vpc_session(self, session: AsyncSession) -> None:
        """
        Fetch MCP tools information for VPC sessions asynchronously.

        Args:
            session: The session to fetch MCP tools for
        """
        _log_operation_start("Fetching MCP tools", "VPC session detected")
        try:
            tools_result = await session.list_mcp_tools()
            _log_operation_success(
                f"Fetched {len(tools_result.tools)} MCP tools",
                f"RequestID: {tools_result.request_id}",
            )
        except Exception as e:
            _log_warning(f"Failed to fetch MCP tools for VPC session: {e}")
            # Continue with session creation even if tools fetch fails

    async def _wait_for_context_synchronization(self, session: AsyncSession) -> None:
        """
        Wait for context synchronization to complete asynchronously.

        Args:
            session: The session to wait for context synchronization
        """
        _log_operation_start("Context synchronization", "Waiting for completion")

        # Wait for context synchronization to complete
        max_retries = 150  # Maximum number of retries
        retry_interval = 2.0  # Seconds to wait between retries

        for retry in range(max_retries):
            # Get context status data
            info_result = await session.context.info()

            # Check if all context items have status "Success" or "Failed"
            all_completed = True
            has_failure = False

            for item in info_result.context_status_data:
                _logger.info(
                    f"📁 Context {item.context_id} status: {item.status}, path: {item.path}"
                )

                if item.status != "Success" and item.status != "Failed":
                    all_completed = False
                    break

                if item.status == "Failed":
                    has_failure = True
                    _logger.error(
                        f"❌ Context synchronization failed for {item.context_id}: {item.error_message}"
                    )

            if all_completed or not info_result.context_status_data:
                if has_failure:
                    _log_warning("Context synchronization completed with failures")
                else:
                    _log_operation_success("Context synchronization")
                break

            _logger.debug(
                f"⏳ Waiting for context synchronization, attempt {retry+1}/{max_retries}"
            )
            await asyncio.sleep(retry_interval)

    def _log_request_debug_info(self, request: CreateMcpSessionRequest) -> None:
        """
        Log debug information for the request with masked authorization.

        Args:
            request: The request object to log
        """
        try:
            req_map = request.to_map()
            if "Authorization" in req_map and isinstance(req_map["Authorization"], str):
                auth = req_map["Authorization"]
                if len(auth) > 12:
                    req_map["Authorization"] = (
                        auth[:6] + "*" * (len(auth) - 10) + auth[-4:]
                    )
                else:
                    req_map["Authorization"] = auth[:2] + "****" + auth[-2:]
            request_body = json.dumps(req_map, ensure_ascii=False, indent=2)
            _logger.debug(f"📤 CreateMcpSessionRequest body:\n{request_body}")
        except Exception:
            _logger.debug(f"📤 CreateMcpSessionRequest: {request}")

    async def _update_browser_replay_context(
        self, response_data: dict, record_context_id: str
    ) -> None:
        """
        Update browser replay context with AppInstanceId from response data asynchronously.

        Args:
            response_data: Response data containing AppInstanceId
            record_context_id: The record context ID to update
        """
        # Check if record_context_id is provided
        if not record_context_id:
            return

        try:
            # Extract AppInstanceId from response data
            app_instance_id = response_data.get("AppInstanceId")
            if not app_instance_id:
                _logger.warning(
                    "AppInstanceId not found in response data, skipping browser replay context update"
                )
                return

            # Create context name with prefix
            context_name = f"browserreplay-{app_instance_id}"

            # Create Context object for update
            from .context import Context

            context_obj = Context(id=record_context_id, name=context_name)

            # Call context.update interface
            _logger.info(
                f"Updating browser replay context: {context_name} -> {record_context_id}"
            )
            update_result = await self.context.update(context_obj)

            if update_result.success:
                _logger.info(
                    f"✅ Successfully updated browser replay context: {context_name}"
                )
            else:
                _logger.warning(
                    f"⚠️ Failed to update browser replay context: {update_result.error_message}"
                )

        except Exception as e:
            _logger.error(f"❌ Error updating browser replay context: {e}")
            # Continue execution even if context update fails

    async def create(
        self, params: Optional[CreateSessionParams] = None
    ) -> SessionResult:
        """
        Create a new session in the AgentBay cloud environment asynchronously.

        Args:
            params (Optional[CreateSessionParams], optional): Parameters for creating the session.
                Defaults to None (uses default configuration).

        Returns:
            SessionResult: Result containing the created session and request ID.
                - success (bool): True if the operation succeeded
                - session (AsyncSession): The created session object (if success is True)
                - request_id (str): Unique identifier for this API request
                - error_message (str): Error description (if success is False)

        Raises:
            ValueError: If API key is not provided and AGENTBAY_API_KEY environment variable is not set.
            ClientException: If the API request fails due to network or authentication issues.

        Example:
            ```python
            result = await agent_bay.create()
            session = result.session
            info_result = await session.info()
            print(f"Session ID: {info_result.session_id}")
            await session.delete()
            ```
        """
        try:
            if params is None:
                params = CreateSessionParams()

            # Create a default context for file transfer operations if none provided
            # and no context_syncs are specified
            import time

            context_name = f"file-transfer-context-{int(time.time())}"
            context_result = await self.context.get(context_name, create=True)
            if context_result.success and context_result.context:
                self._file_transfer_context = context_result.context
                # Add the context to the session params for file transfer operations
                from .context_sync import ContextSync

                file_transfer_context_sync = ContextSync(
                    context_id=context_result.context.id,
                    path="/tmp/file-transfer",
                )
                if not hasattr(params, "context_syncs") or params.context_syncs is None:
                    params.context_syncs = []
                _logger.info(
                    f"Adding context sync for file transfer operations: {file_transfer_context_sync}"
                )
                params.context_syncs.append(file_transfer_context_sync)

            request = CreateMcpSessionRequest(authorization=f"Bearer {self.api_key}")

            # Add SDK stats for tracking
            framework = (
                params.framework if params and hasattr(params, "framework") else ""
            )
            sdk_stats_json = f'{{"source":"sdk","sdk_language":"python","sdk_version":"{__version__}","is_release":{str(__is_release__).lower()},"framework":"{framework}"}}'
            request.sdk_stats = sdk_stats_json

            # Add PolicyId if specified
            if hasattr(params, "policy_id") and params.policy_id:
                request.mcp_policy_id = params.policy_id

            # Add VPC resource if specified
            request.vpc_resource = params.is_vpc

            # Flag to indicate if we need to wait for context synchronization
            needs_context_sync = False

            # Add context_syncs if provided
            if hasattr(params, "context_syncs") and params.context_syncs:
                from ..api.models import CreateMcpSessionRequestPersistenceDataList

                persistence_data_list = []
                for cs in params.context_syncs:
                    policy_json = None
                    if cs.policy is not None:
                        # Serialize policy to JSON string
                        import json as _json

                        policy_json = _json.dumps(
                            cs.policy, default=self._safe_serialize, ensure_ascii=False
                        )
                    persistence_data_list.append(
                        CreateMcpSessionRequestPersistenceDataList(
                            context_id=cs.context_id, path=cs.path, policy=policy_json
                        )
                    )
                request.persistence_data_list = persistence_data_list
                needs_context_sync = len(persistence_data_list) > 0

            # Add BrowserContext as a ContextSync if provided
            if hasattr(params, "browser_context") and params.browser_context:
                from ..api.models import CreateMcpSessionRequestPersistenceDataList
                from .context_sync import (
                    BWList,
                    RecyclePolicy,
                    SyncPolicy,
                    UploadPolicy,
                    WhiteList,
                )

                # Create a new SyncPolicy with default values for browser context
                upload_policy = UploadPolicy(
                    auto_upload=params.browser_context.auto_upload
                )

                # Create BWList with white lists for browser data paths
                white_lists = [
                    WhiteList(path="/Local State", exclude_paths=[]),
                    WhiteList(path="/Default/Cookies", exclude_paths=[]),
                    WhiteList(path="/Default/Cookies-journal", exclude_paths=[]),
                ]
                bw_list = BWList(white_lists=white_lists)

                # Use custom recycle_policy if provided, otherwise use default
                recycle_policy = RecyclePolicy.default()

                sync_policy = SyncPolicy(
                    upload_policy=upload_policy,
                    bw_list=bw_list,
                    recycle_policy=recycle_policy,
                )

                # Serialize policy to JSON string
                import json as _json

                policy_json = _json.dumps(
                    sync_policy, default=self._safe_serialize, ensure_ascii=False
                )

                # Create browser context sync item
                browser_context_sync = CreateMcpSessionRequestPersistenceDataList(
                    context_id=params.browser_context.context_id,
                    path=_BROWSER_DATA_PATH,  # Using a constant path for browser data
                    policy=policy_json,
                )

                # Add to persistence data list or create new one if not exists
                if (
                    not hasattr(request, "persistence_data_list")
                    or request.persistence_data_list is None
                ):
                    request.persistence_data_list = []
                request.persistence_data_list.append(browser_context_sync)
                _logger.info(
                    f"📋 Added browser context to persistence_data_list. Total items: {len(request.persistence_data_list)}"
                )
                for i, item in enumerate(request.persistence_data_list):
                    _logger.info(
                        f"📋 persistence_data_list[{i}]: context_id={item.context_id}, path={item.path}, policy_length={len(item.policy) if item.policy else 0}"
                    )
                    _logger.info(
                        f"📋 persistence_data_list[{i}] policy content: {item.policy}"
                    )

                needs_context_sync = True

            # Add labels if provided
            if params.labels:
                # Convert labels to JSON string
                request.labels = json.dumps(params.labels)

            if params.image_id:
                request.image_id = params.image_id

            # Add browser recording persistence if enabled
            record_context_id = ""  # Initialize record_context_id
            if (
                hasattr(params, "enable_browser_replay")
                and params.enable_browser_replay
            ):
                from ..api.models import CreateMcpSessionRequestPersistenceDataList

                # Create browser recording persistence configuration
                record_path = "/home/wuying/record"
                record_context_name = _generate_random_context_name()
                result = await self.context.get(record_context_name, True)
                record_context_id = result.context_id if result.success else ""
                record_persistence = CreateMcpSessionRequestPersistenceDataList(
                    context_id=record_context_id, path=record_path
                )

                # Add to persistence data list or create new one if not exists
                if (
                    not hasattr(request, "persistence_data_list")
                    or request.persistence_data_list is None
                ):
                    request.persistence_data_list = []
                request.persistence_data_list.append(record_persistence)

            # Add extra_configs if provided
            if hasattr(params, "extra_configs") and params.extra_configs:
                request.extra_configs = params.extra_configs

            self._log_request_debug_info(request)

            # Use async client method
            response = await self.client.create_mcp_session_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
            except Exception:
                response_body = str(response)

            session_data = response.to_map()

            if not isinstance(session_data, dict):
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format: expected a dictionary",
                )

            body = session_data.get("body", {})
            if not isinstance(body, dict):
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format: "
                    "'body' field is not a dictionary",
                )

            # Check for API-level errors
            if not body.get("Success", True) and body.get("Code"):
                code = body.get("Code", "Unknown")
                message = body.get("Message", "Unknown error")
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{code}] {message}",
                )

            data = body.get("Data", {})
            if not isinstance(data, dict):
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format: "
                    "'Data' field is not a dictionary",
                )

            # Check if the session creation was successful
            if data.get("Success") is False:
                error_msg = data.get("ErrMsg", "Session creation failed")
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=error_msg,
                )

            session_id = data.get("SessionId")
            if not session_id:
                return SessionResult(
                    request_id=request_id,
                    success=False,
                    error_message="SessionId not found in response",
                )

            # Log API response with key details
            resource_url = data.get("ResourceUrl", "")
            _log_api_response_with_details(
                api_name="CreateSession",
                request_id=request_id,
                success=True,
                key_fields={"session_id": session_id, "resource_url": resource_url},
                full_response=response_body,
            )

            # Build Session object from response data
            session = self._build_session_from_response(data, params, record_context_id)

            # Update browser replay context if enabled
            if (
                hasattr(params, "enable_browser_replay")
                and params.enable_browser_replay
            ):
                await self._update_browser_replay_context(data, record_context_id)

            # For VPC sessions, automatically fetch MCP tools information
            if params.is_vpc:
                await self._fetch_mcp_tools_for_vpc_session(session)

            # If we have persistence data, wait for context synchronization
            if needs_context_sync:
                await self._wait_for_context_synchronization(session)

            # Return SessionResult with request ID
            return SessionResult(request_id=request_id, success=True, session=session)

        except ClientException as e:
            _log_operation_error(
                "create_mcp_session - ClientException", str(e), exc_info=True
            )
            return SessionResult(
                request_id="",
                success=False,
                error_message=f"Failed to create session: {e}",
            )
        except Exception as e:
            _log_operation_error("create_mcp_session", str(e), exc_info=True)
            return SessionResult(
                request_id="",
                success=False,
                error_message=f"Unexpected error creating session: {e}",
            )

    async def list(
        self,
        labels: Optional[Dict[str, str]] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> SessionListResult:
        """
        Returns paginated list of session IDs filtered by labels asynchronously.

        Args:
            labels (Optional[Dict[str, str]], optional): Labels to filter sessions.
                Defaults to None (returns all sessions).
            page (Optional[int], optional): Page number for pagination (starting from 1).
                Defaults to None (returns first page).
            limit (Optional[int], optional): Maximum number of items per page.
                Defaults to None (uses default of 10).

        Returns:
            SessionListResult: Paginated list of session IDs that match the labels.
        """
        try:
            # Set default values
            if labels is None:
                labels = {}
            if limit is None:
                limit = 10

            # Validate page number
            if page is not None and page < 1:
                return SessionListResult(
                    request_id="",
                    success=False,
                    error_message=f"Cannot reach page {page}: Page number must be >= 1",
                    session_ids=[],
                    next_token="",
                    max_results=limit,
                    total_count=0,
                )

            # Calculate next_token based on page number
            next_token = ""
            if page is not None and page > 1:
                # We need to fetch pages 1 through page-1 to get the next_token
                current_page = 1
                while current_page < page:
                    # Make API call to get next_token
                    labels_json = json.dumps(labels)
                    request = ListSessionRequest(
                        authorization=f"Bearer {self.api_key}",
                        labels=labels_json,
                        max_results=limit,
                    )
                    if next_token:
                        request.next_token = next_token

                    # Async API call
                    response = await self.client.list_session_async(request)
                    request_id = extract_request_id(response)
                    response_map = response.to_map()
                    body = response_map.get("body", {})

                    if not body.get("Success", False):
                        error_message = body.get(
                            "Message", body.get("Code", "Unknown error")
                        )
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Cannot reach page {page}: {error_message}",
                            session_ids=[],
                            next_token="",
                            max_results=limit,
                            total_count=0,
                        )

                    next_token = body.get("NextToken", "")
                    if not next_token:
                        # No more pages available
                        return SessionListResult(
                            request_id=request_id,
                            success=False,
                            error_message=f"Cannot reach page {page}: No more pages available",
                            session_ids=[],
                            next_token="",
                            max_results=limit,
                            total_count=body.get("TotalCount", 0),
                        )
                    current_page += 1

            # Make the actual request for the desired page
            labels_json = json.dumps(labels)
            request = ListSessionRequest(
                authorization=f"Bearer {self.api_key}",
                labels=labels_json,
                max_results=limit,
            )
            if next_token:
                request.next_token = next_token

            request_details = f"Labels={labels_json}, MaxResults={limit}"
            if request.next_token:
                request_details += f", NextToken={request.next_token}"
            _log_api_call("list_session", request_details)

            # Make the API call asynchronously
            response = await self.client.list_session_async(request)

            # Extract request ID
            request_id = extract_request_id(response)

            response_map = response.to_map()
            body = response_map.get("body", {})

            # Check for errors in the response
            if isinstance(body, dict) and body.get("Success") is False:
                error_message = body.get("Message", body.get("Code", "Unknown error"))
                return SessionListResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to list sessions: {error_message}",
                    session_ids=[],
                    next_token="",
                    max_results=limit,
                    total_count=0,
                )

            session_ids = []
            next_token = ""
            max_results = limit  # Use the requested max_results
            total_count = 0

            try:
                response_body = json.dumps(body, ensure_ascii=False, indent=2)
            except Exception:
                response_body = str(body)

            # Extract pagination information
            if isinstance(body, dict):
                next_token = body.get("NextToken", "")
                # Use API response MaxResults if present, otherwise use requested value
                max_results = int(body.get("MaxResults", limit))
                total_count = int(body.get("TotalCount", 0))

            # Extract session data
            response_data = body.get("Data")

            # Handle both list and dict responses
            if isinstance(response_data, list):
                # Data is a list of session objects
                for session_data in response_data:
                    if isinstance(session_data, dict):
                        session_id = session_data.get("SessionId")
                        if session_id:
                            session_ids.append(session_id)

            # Log API response with key details
            _log_api_response_with_details(
                api_name="ListSession",
                request_id=request_id,
                success=True,
                key_fields={
                    "total_count": total_count,
                    "returned_count": len(session_ids),
                    "has_more": "yes" if next_token else "no",
                },
                full_response=response_body,
            )

            # Return SessionListResult with request ID and pagination info
            return SessionListResult(
                request_id=request_id,
                success=True,
                session_ids=session_ids,
                next_token=next_token,
                max_results=max_results,
                total_count=total_count,
            )

        except Exception as e:
            _log_operation_error("list_session", str(e), exc_info=True)
            return SessionListResult(
                request_id="",
                success=False,
                session_ids=[],
                error_message=f"Failed to list sessions: {e}",
            )

    async def delete(
        self, session: AsyncSession, sync_context: bool = False
    ) -> DeleteResult:
        """
        Delete a session by session object asynchronously.

        Args:
            session (AsyncSession): The session to delete.
            sync_context (bool): Whether to sync context data (trigger file uploads)
                before deleting the session. Defaults to False.

        Returns:
            DeleteResult: Result indicating success or failure and request ID.
        """
        try:
            # Delete the session and get the result
            delete_result = await session.delete(sync_context=sync_context)

            with self._lock:
                self._sessions.pop(session.session_id, None)

            # Return the DeleteResult obtained from session.delete()
            return delete_result

        except Exception as e:
            _log_operation_error("delete_session", str(e), exc_info=True)
            return DeleteResult(
                request_id="",
                success=False,
                error_message=f"Failed to delete session {session.session_id}: {e}",
            )

    async def get_session(self, session_id: str) -> GetSessionResult:
        """
        Get session information by session ID asynchronously.

        This method retrieves detailed session metadata from the API. Unlike `get()`,
        this returns raw session data without creating a Session object.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            GetSessionResult: Result containing session information.
        """
        try:
            _log_api_call("GetSession", f"SessionId={session_id}")
            request = GetSessionRequest(
                authorization=f"Bearer {self.api_key}", session_id=session_id
            )
            # Async API call
            response = await self.client.get_session_async(request)

            request_id = extract_request_id(response)

            try:
                response_body = json.dumps(
                    response.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
            except Exception:
                response_body = str(response)

            try:
                response_map = response.to_map()
                body = response_map.get("body", {})
                http_status_code = body.get("HttpStatusCode", 0)
                code = body.get("Code", "")
                success = body.get("Success", False)
                message = body.get("Message", "")

                # Check for API-level errors
                if not success and code:
                    return GetSessionResult(
                        request_id=request_id,
                        http_status_code=http_status_code,
                        code=code,
                        success=False,
                        data=None,
                        error_message=f"[{code}] {message or 'Unknown error'}",
                    )

                data = None
                if body.get("Data"):
                    data_dict = body.get("Data", {})
                    data = GetSessionData(
                        app_instance_id=data_dict.get("AppInstanceId", ""),
                        resource_id=data_dict.get("ResourceId", ""),
                        session_id=data_dict.get("SessionId", ""),
                        success=data_dict.get("Success", False),
                        http_port=data_dict.get("HttpPort", ""),
                        network_interface_ip=data_dict.get("NetworkInterfaceIp", ""),
                        token=data_dict.get("Token", ""),
                        vpc_resource=data_dict.get("VpcResource", False),
                        resource_url=data_dict.get("ResourceUrl", ""),
                        status=data_dict.get("Status", ""),
                    )

                # Log API response with key details
                key_fields = {}
                if data:
                    key_fields["session_id"] = data.session_id
                    key_fields["vpc_resource"] = "yes" if data.vpc_resource else "no"
                _log_api_response_with_details(
                    api_name="GetSession",
                    request_id=request_id,
                    success=success,
                    key_fields=key_fields,
                    full_response=response_body,
                )

                return GetSessionResult(
                    request_id=request_id,
                    http_status_code=http_status_code,
                    code=code,
                    success=success,
                    data=data,
                    error_message="",
                )

            except Exception as e:
                _logger.exception(f"Failed to parse response: {str(e)}")
                return GetSessionResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )
        except ClientException as e:
            # Check if this is an expected business error (e.g., session not found)
            error_str = str(e)
            if "InvalidMcpSession.NotFound" in error_str or "NotFound" in error_str:
                # This is an expected error - session doesn't exist
                # Use info level logging without stack trace, but with red color for visibility
                _log_info_with_color(f"Session not found: {session_id}")
                _logger.debug(f"GetSession error details: {error_str}")
                return GetSessionResult(
                    request_id="",
                    success=False,
                    error_message=f"Session {session_id} not found",
                )
            else:
                # This is an unexpected error - log with stack trace
                _logger.error(f"Error calling GetSession: {e}")
                return GetSessionResult(
                    request_id="",
                    success=False,
                    error_message=f"Failed to get session {session_id}: {e}",
                )
        except Exception as e:
            # Unexpected system error - log with stack trace
            _logger.exception(f"Unexpected error calling GetSession: {e}")
            return GetSessionResult(
                request_id="",
                success=False,
                error_message=f"Failed to get session {session_id}: {e}",
            )

    async def get(self, session_id: str) -> SessionResult:
        """
        Get a session by its ID asynchronously.

        Args:
            session_id (str): The ID of the session to retrieve. Must be a non-empty string.

        Returns:
            SessionResult: Result containing the Session instance, request ID, and success status.
        """
        # Validate input
        if not session_id or (isinstance(session_id, str) and not session_id.strip()):
            return SessionResult(
                request_id="",
                success=False,
                error_message="session_id is required",
            )

        # Call GetSession API
        get_result = await self.get_session(session_id)

        # Check if the API call was successful
        if not get_result.success:
            error_msg = get_result.error_message or "Unknown error"
            return SessionResult(
                request_id=get_result.request_id,
                success=False,
                error_message=f"Failed to get session {session_id}: {error_msg}",
            )

        # Create the Session object
        session = AsyncSession(self, session_id)

        # Set VPC-related information and ResourceUrl from GetSession response
        if get_result.data:
            session.is_vpc = get_result.data.vpc_resource
            session.network_interface_ip = get_result.data.network_interface_ip
            session.http_port = get_result.data.http_port
            session.token = get_result.data.token
            session.resource_url = get_result.data.resource_url

        # Create a default context for file transfer operations for the recovered session
        import time

        context_name = f"file-transfer-context-{int(time.time())}"
        context_result = await self.context.get(context_name, create=True)
        if context_result.success and context_result.context:
            session.file_transfer_context_id = context_result.context.id
            _logger.info(
                f"📁 Created file transfer context for recovered session: {context_result.context.id}"
            )
        else:
            _logger.warning(
                f"⚠️  Failed to create file transfer context for recovered session: {context_result.error_message if hasattr(context_result, 'error_message') else 'Unknown error'}"
            )

        return SessionResult(
            request_id=get_result.request_id,
            success=True,
            session=session,
        )

    async def pause(
        self, session: AsyncSession, timeout: int = 600, poll_interval: float = 2.0
    ) -> SessionPauseResult:
        """
        Asynchronously pause a session, putting it into a dormant state.

        This method internally calls the PauseSessionAsync API and then polls the GetSession API
        to check the session status until it becomes PAUSED or until timeout.

        Args:
            session (AsyncSession): The session to pause.
            timeout (int, optional): Timeout in seconds to wait for the session to pause.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionPauseResult: Result containing the request ID, success status, and final session status.
        """
        try:
            # Call session's pause method
            return await session.pause(timeout, poll_interval)
        except Exception as e:
            _log_operation_error("pause_session", str(e), exc_info=True)
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=f"Failed to pause session {session.session_id}: {e}",
            )

    async def pause_async(self, session: AsyncSession) -> SessionPauseResult:
        """
        Asynchronously pause a session, putting it into a dormant state.

        This method directly calls the PauseSessionAsync API without waiting for the session
        to reach the PAUSED state. For behavior that waits for the PAUSED state,
        use the pause() method instead.

        Args:
            session (AsyncSession): The session to pause.

        Returns:
            SessionPauseResult: Result containing the request ID and success status.
        """
        # This method is somewhat redundant in async SDK if pause() is already async,
        # but pause() awaits completion, while this just initiates.
        # It's good to keep for API parity.
        # Note: AsyncSession doesn't have explicit pause_async method (it has pause which does both?).
        # Wait, AsyncSession has `pause` which polls.
        # Does it have `pause_async`?
        # In `python/agentbay/_async/session.py`, I see `pause` method.
        # I don't see `pause_async` method in `AsyncSession` snippet I read.
        # Let's check `_async/session.py` again.
        # I implemented `pause` and `resume` in `AsyncSession`.
        # I did NOT implement `pause_async` and `resume_async` in `AsyncSession`.
        # So `AsyncAgentBay.pause_async` should implement the logic or call client directly?
        # `AgentBay.pause_async` called `session.pause_async`.
        # I should probably add `pause_async` to `AsyncSession` as well, or implement it here.
        # Implementing here is fine as `AsyncSession` holds `client` via `agent_bay`.

        try:
            request = open_api_models.PauseSessionAsyncRequest(
                authorization=f"Bearer {self.api_key}",
                session_id=session.session_id,
            )

            _log_api_call("PauseSessionAsync", f"SessionId={session.session_id}")

            response = await self.client.pause_session_async_async(request)

            request_id = extract_request_id(response)

            response_map = response.to_map()
            if not response_map:
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format",
                )

            body = response_map.get("body", {})
            success = body.get("Success", False)

            if not success:
                code = body.get("Code", "")
                message = body.get("Message", "")
                return SessionPauseResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{code}] {message}",
                    code=code,
                    message=message,
                )

            return SessionPauseResult(request_id=request_id, success=True)

        except Exception as e:
            _log_operation_error("pause_session_async", str(e), exc_info=True)
            return SessionPauseResult(
                request_id="",
                success=False,
                error_message=f"Failed to pause session {session.session_id}: {e}",
            )

    async def resume(
        self, session: AsyncSession, timeout: int = 600, poll_interval: float = 2.0
    ) -> SessionResumeResult:
        """
        Asynchronously resume a session from a paused state.

        This method internally calls the ResumeSessionAsync API and then polls the GetSession API
        to check the session status until it becomes RUNNING or until timeout.

        Args:
            session (AsyncSession): The session to resume.
            timeout (int, optional): Timeout in seconds to wait for the session to resume.
                Defaults to 600 seconds.
            poll_interval (float, optional): Interval in seconds between status polls.
                Defaults to 2.0 seconds.

        Returns:
            SessionResumeResult: Result containing the request ID, success status, and final session status.
        """
        try:
            # Call session's resume method
            return await session.resume(timeout, poll_interval)
        except Exception as e:
            _log_operation_error("resume_session", str(e), exc_info=True)
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Failed to resume session {session.session_id}: {e}",
            )

    async def resume_async(self, session: AsyncSession) -> SessionResumeResult:
        """
        Asynchronously resume a session from a paused state.

        This method directly calls the ResumeSessionAsync API without waiting for the session
        to reach the RUNNING state. For behavior that waits for the RUNNING state,
        use the resume() method instead.

        Args:
            session (AsyncSession): The session to resume.

        Returns:
            SessionResumeResult: Result containing the request ID and success status.
        """
        try:
            request = open_api_models.ResumeSessionAsyncRequest(
                authorization=f"Bearer {self.api_key}",
                session_id=session.session_id,
            )

            _log_api_call("ResumeSessionAsync", f"SessionId={session.session_id}")

            response = await self.client.resume_session_async_async(request)

            request_id = extract_request_id(response)

            response_map = response.to_map()
            if not response_map:
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message="Invalid response format",
                )

            body = response_map.get("body", {})
            success = body.get("Success", False)

            if not success:
                code = body.get("Code", "")
                message = body.get("Message", "")
                return SessionResumeResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{code}] {message}",
                    code=code,
                    message=message,
                )

            return SessionResumeResult(request_id=request_id, success=True)

        except Exception as e:
            _log_operation_error("resume_session_async", str(e), exc_info=True)
            return SessionResumeResult(
                request_id="",
                success=False,
                error_message=f"Failed to resume session {session.session_id}: {e}",
            )
