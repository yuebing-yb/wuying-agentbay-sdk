from typing import Optional, List, Dict, Any, Callable
from agentbay.api.models import GetContextInfoRequest, SyncContextRequest
from agentbay.model.response import ApiResponse, extract_request_id
from .logger import get_logger, _log_api_call, _log_api_response, _log_api_response_with_details
import json
import time
import threading
import asyncio

# Initialize logger for this module
_logger = get_logger("context_manager")


class ContextStatusData:
    def __init__(
        self,
        context_id: str = "",
        path: str = "",
        error_message: str = "",
        status: str = "",
        start_time: int = 0,
        finish_time: int = 0,
        task_type: str = "",
    ):
        self.context_id = context_id
        self.path = path
        self.error_message = error_message
        self.status = status
        self.start_time = start_time
        self.finish_time = finish_time
        self.task_type = task_type

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ContextStatusData":
        return cls(
            context_id=data.get("contextId", ""),
            path=data.get("path", ""),
            error_message=data.get("errorMessage", ""),
            status=data.get("status", ""),
            start_time=data.get("startTime", 0),
            finish_time=data.get("finishTime", 0),
            task_type=data.get("taskType", ""),
        )


class ContextInfoResult(ApiResponse):
    def __init__(
        self,
        request_id: str = "",
        success: bool = True,
        context_status_data: Optional[List[ContextStatusData]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.context_status_data = context_status_data or []
        self.error_message = error_message


class ContextSyncResult(ApiResponse):
    def __init__(
        self, request_id: str = "", success: bool = False, error_message: str = ""
    ):
        super().__init__(request_id)
        self.success = success
        self.error_message = error_message


class ContextManager:
    """
    Manages context operations within a session in the AgentBay cloud environment.

    The ContextManager provides methods to get information about context synchronization
    status and to synchronize contexts with the session.

    Example:
        ```python
        result = agent_bay.create()
        session = result.session
        info_result = session.context.info()
        print(f"Found {len(info_result.context_status_data)} context items")
        session.delete()
        ```
    """
    def __init__(self, session):
        self.session = session

    def info(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        task_type: Optional[str] = None,
    ) -> ContextInfoResult:
        """
        Get information about context synchronization status.

        Args:
            context_id: Optional ID of the context to get information for
            path: Optional path where the context is mounted
            task_type: Optional type of task to get information for (e.g., "upload", "download")

        Returns:
            ContextInfoResult: Result object containing context status data and request ID

        Example:
            ```python
            result = agent_bay.create()
            session = result.session
            info_result = session.context.info()
            for item in info_result.context_status_data:
                print(f"Context {item.context_id}: {item.status}")
            session.delete()
            ```
        """
        request = GetContextInfoRequest(
            authorization=f"Bearer {self.session._get_api_key()}",
            session_id=self.session._get_session_id(),
        )
        if context_id:
            request.context_id = context_id
        if path:
            request.path = path
        if task_type:
            request.task_type = task_type
        _log_api_call(
            "GetContextInfo",
            f"SessionId={self.session._get_session_id()}, ContextId={context_id}, Path={path}, TaskType={task_type}",
        )
        response = self.session._get_client().get_context_info(request)

        # Extract request ID
        request_id = extract_request_id(response)
        response_map = response.to_map()

        context_status_data: List[ContextStatusData] = []

        if isinstance(response_map, dict):
            body = response_map.get("body", {})
            try:
                response_body = json.dumps(body, ensure_ascii=False, indent=2)
            except Exception:
                response_body = str(body)

            # Check for API-level errors
            if not body.get("Success", True) and body.get("Code"):
                code = body.get("Code", "Unknown")
                message = body.get("Message", "Unknown error")
                _log_api_response_with_details(
                    api_name="GetContextInfo",
                    request_id=request_id,
                    success=False,
                    full_response=response_body
                )
                return ContextInfoResult(
                    request_id=request_id,
                    success=False,
                    context_status_data=[],
                    error_message=f"[{code}] {message}",
                )

            data = body.get("Data", {})
            context_status_str = data.get("ContextStatus", "")

            # Parse the context status data
            if context_status_str:
                try:
                    # First, parse the outer array
                    status_items = json.loads(context_status_str)
                    for item in status_items:
                        if item.get("type") == "data":
                            # Parse the inner data string
                            data_items = json.loads(item.get("data", "[]"))
                            for data_item in data_items:
                                context_status_data.append(
                                    ContextStatusData.from_dict(data_item)
                                )
                except json.JSONDecodeError as e:
                    _logger.error(f"❌ Error parsing context status: {e}")
                except Exception as e:
                    _logger.error(f"❌ Unexpected error parsing context status: {e}")

        # Log successful context info retrieval
        _log_api_response_with_details(
            api_name="GetContextInfo",
            request_id=request_id,
            success=True,
            key_fields={
                "context_id": context_id,
                "status_count": len(context_status_data)
            }
        )

        return ContextInfoResult(
            request_id=request_id,
            success=True,
            context_status_data=context_status_data,
            error_message="",
        )

    async def sync(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        mode: Optional[str] = None,
        callback: Optional[Callable[[bool], None]] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> ContextSyncResult:
        """
        Synchronize a context with the session.

        This method supports two modes:
        - Async mode (default): When called with await, it waits for the sync operation to complete
        - Callback mode: When a callback is provided, it returns immediately and calls the callback when complete

        Args:
            context_id: Optional ID of the context to synchronize
            path: Optional path where the context should be mounted
            mode: Optional synchronization mode (e.g., "upload", "download")
            callback: Optional callback function that receives success status. If provided, the method
                     runs in background and calls callback when complete
            max_retries: Maximum number of retries for polling completion status (default: 150)
            retry_interval: Milliseconds to wait between retries (default: 1500)

        Returns:
            ContextSyncResult: Result object containing success status and request ID

        Example:
            Async mode - waits for completion:
            ```python
            result = agent_bay.create()
            session = result.session
            context = agent_bay.context.get('my-context', True).context
            sync_result = await session.context.sync(context.id, "/mnt/data")
            print(f"Sync success: {sync_result.success}")
            session.delete()
            ```

            Callback mode - returns immediately:
            ```python
            result = agent_bay.create()
            session = result.session

            def on_complete(success: bool):
                print(f"Sync completed: {success}")

            context = agent_bay.context.get('my-context', True).context
            await session.context.sync(context.id, "/mnt/data", callback=on_complete)
            session.delete()
            ```
        """
        request = SyncContextRequest(
            authorization=f"Bearer {self.session._get_api_key()}",
            session_id=self.session._get_session_id(),
        )
        if context_id:
            request.context_id = context_id
        if path:
            request.path = path
        if mode:
            request.mode = mode
        _log_api_call(
            "SyncContext",
            f"SessionId={self.session._get_session_id()}, ContextId={context_id}, Path={path}, Mode={mode}",
        )
        response = self.session._get_client().sync_context(request)

        # Extract request ID
        request_id = extract_request_id(response)
        response_map = response.to_map()

        success = False  # Initialize success variable

        if isinstance(response_map, dict):
            body = response_map.get("body", {})
            try:
                response_body = json.dumps(body, ensure_ascii=False, indent=2)
            except Exception:
                response_body = str(body)

            # Check for API-level errors
            if not body.get("Success", True) and body.get("Code"):
                code = body.get("Code", "Unknown")
                message = body.get("Message", "Unknown error")
                _log_api_response_with_details(
                    api_name="SyncContext",
                    request_id=request_id,
                    success=False,
                    full_response=response_body
                )
                return ContextSyncResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"[{code}] {message}",
                )

            success = body.get("Success", False)

        # Log successful sync context call
        if success:
            _log_api_response_with_details(
                api_name="SyncContext",
                request_id=request_id,
                success=True,
                key_fields={
                    "context_id": context_id,
                    "path": path or "default"
                }
            )

        # If callback is provided, start polling in background thread (sync mode)
        if callback is not None and success:
            # Check if we're in an event loop
            try:
                asyncio.get_running_loop()
                # We're in an event loop, start polling in background thread
                poll_thread = threading.Thread(
                    target=self._poll_for_completion,
                    args=(callback, context_id, path, max_retries, retry_interval),
                    daemon=True,
                )
                poll_thread.start()
                return ContextSyncResult(request_id=request_id, success=success)
            except RuntimeError:
                # No event loop running, start polling in background thread
                poll_thread = threading.Thread(
                    target=self._poll_for_completion,
                    args=(callback, context_id, path, max_retries, retry_interval),
                    daemon=True,
                )
                poll_thread.start()
                return ContextSyncResult(request_id=request_id, success=success)

        # If no callback, wait for completion (async mode)
        if success:
            final_success = await self._poll_for_completion_async(
                context_id, path, max_retries, retry_interval
            )
            return ContextSyncResult(request_id=request_id, success=final_success)

        return ContextSyncResult(request_id=request_id, success=success)

    def _poll_for_completion(
        self,
        callback: Callable[[bool], None],
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> None:
        """
        Polls the info interface to check if sync is completed and calls callback.

        Args:
            callback: Callback function that receives success status
            context_id: ID of the context to check
            path: Path to check
            max_retries: Maximum number of retries
            retry_interval: Milliseconds to wait between retries
        """
        for retry in range(max_retries):
            try:
                # Get context status data
                info_result = self.info(context_id=context_id, path=path)

                # Check if all sync tasks are completed
                all_completed = True
                has_failure = False
                has_sync_tasks = False

                for item in info_result.context_status_data:
                    # We only care about sync tasks (upload/download)
                    if item.task_type not in ["upload", "download"]:
                        continue

                    has_sync_tasks = True
                    _logger.info(
                        f"🔄 Sync task {item.context_id} status: {item.status}, path: {item.path}"
                    )

                    if item.status not in ["Success", "Failed"]:
                        all_completed = False
                        break

                    if item.status == "Failed":
                        has_failure = True
                        _logger.error(
                            f"❌ Sync failed for context {item.context_id}: {item.error_message}"
                        )

                if all_completed or not has_sync_tasks:
                    # All tasks completed or no sync tasks found
                    if has_failure:
                        _logger.warning("Context sync completed with failures")
                        callback(False)
                    elif has_sync_tasks:
                        _logger.info("✅ Context sync completed successfully")
                        callback(True)
                    else:
                        _logger.info("ℹ️  No sync tasks found")
                        callback(True)
                    break

                _logger.info(
                    f"⏳ Waiting for context sync to complete, attempt {retry+1}/{max_retries}"
                )
                time.sleep(retry_interval / 1000.0)

            except Exception as e:
                _logger.error(
                    f"❌ Error checking context status on attempt {retry+1}: {e}"
                )
                time.sleep(retry_interval / 1000.0)

        # If we've exhausted all retries, call callback with failure
        if retry == max_retries - 1:
            _logger.error(
                f"❌ Context sync polling timed out after {max_retries} attempts"
            )
            callback(False)

    async def _poll_for_completion_async(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        max_retries: int = 150,
        retry_interval: int = 1500,
    ) -> bool:
        """
        Async version of polling for sync completion.

        Args:
            context_id: ID of the context to check
            path: Path to check
            max_retries: Maximum number of retries
            retry_interval: Milliseconds to wait between retries

        Returns:
            bool: True if sync completed successfully, False otherwise
        """
        for retry in range(max_retries):
            try:
                # Get context status data
                info_result = self.info(context_id=context_id, path=path)

                # Check if all sync tasks are completed
                all_completed = True
                has_failure = False
                has_sync_tasks = False

                for item in info_result.context_status_data:
                    # We only care about sync tasks (upload/download)
                    if item.task_type not in ["upload", "download"]:
                        continue

                    has_sync_tasks = True
                    _logger.info(
                        f"🔄 Sync task {item.context_id} status: {item.status}, path: {item.path}"
                    )

                    if item.status not in ["Success", "Failed"]:
                        all_completed = False
                        break

                    if item.status == "Failed":
                        has_failure = True
                        _logger.error(
                            f"❌ Sync failed for context {item.context_id}: {item.error_message}"
                        )

                if all_completed or not has_sync_tasks:
                    # All tasks completed or no sync tasks found
                    if has_failure:
                        _logger.warning("Context sync completed with failures")
                        return False
                    elif has_sync_tasks:
                        _logger.info("✅ Context sync completed successfully")
                        return True
                    else:
                        _logger.info("ℹ️  No sync tasks found")
                        return True

                _logger.info(
                    f"⏳ Waiting for context sync to complete, attempt {retry+1}/{max_retries}"
                )
                await asyncio.sleep(retry_interval / 1000.0)

            except Exception as e:
                _logger.error(
                    f"❌ Error checking context status on attempt {retry+1}: {e}"
                )
                await asyncio.sleep(retry_interval / 1000.0)

        # If we've exhausted all retries, return failure
        _logger.error(f"❌ Context sync polling timed out after {max_retries} attempts")
        return False
