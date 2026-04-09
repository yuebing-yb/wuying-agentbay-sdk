"""
Session lifecycle functional helpers.

Provides two classes for managing session lifecycles:
  - AsyncSessionLifecycle  (for AsyncAgentBay)
  - SyncSessionLifecycle   (for AgentBay / sync)

Both classes support:
  - Creating a session (default or with ContextSync)
  - Deleting the session
  - Querying session status via get_status()

Errors during create / delete raise SessionLifecycleError so that test code
can catch them explicitly.
"""

from __future__ import annotations

import os
from typing import Optional

from agentbay import AsyncAgentBay, AgentBay, CreateSessionParams, BrowserContext
from agentbay._common.exceptions import SessionError
from agentbay._common.params.context_sync import ContextSync


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class SessionLifecycleError(Exception):
    """Raised when a session lifecycle operation (create / delete) fails."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

    def __str__(self) -> str:
        base = super().__str__()
        if self.cause is not None:
            return f"{base} | caused by: {self.cause!r}"
        return base


# ---------------------------------------------------------------------------
# Async variant
# ---------------------------------------------------------------------------


class AsyncSessionLifecycle:
    """
    Manages a single AsyncAgentBay session lifecycle.

    Usage example (pytest)::

        @pytest.fixture(scope="module")
        async def lifecycle():
            mgr = AsyncSessionLifecycle()
            yield mgr
            await mgr.delete()

        @pytest.mark.asyncio
        async def test_something(lifecycle):
            result = await lifecycle.default_create("linux_latest")
            assert result.success
            status = await lifecycle.get_status()
            assert status.success
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Args:
            api_key: AgentBay API key. Falls back to ``AGENTBAY_API_KEY`` env var.
        """
        resolved_key = api_key or os.environ.get("AGENTBAY_API_KEY") or ""
        if not resolved_key:
            raise SessionLifecycleError(
                "API key is required. Set AGENTBAY_API_KEY or pass api_key."
            )
        self._agent_bay = AsyncAgentBay(api_key=resolved_key)
        # Stores the SessionResult from the last create call
        self._result = None

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------

    async def default_create(self, image_id: str) -> object:
        """
        Create a session with the given image_id and cache the result.

        Args:
            image_id: The image ID to create the session with.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        params = CreateSessionParams(image_id=image_id)
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session: {result.error_message}"
            )
        self._result = result
        return result

    async def create_with_context_sync(
        self,
        image_id: str,
        context_sync: ContextSync,
    ) -> object:
        """
        Create a session with the given image_id and a ContextSync configuration.

        Args:
            image_id: The image ID to create the session with.
            context_sync: A :class:`ContextSync` instance describing the context
                          sync policy to apply when creating the session.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
        )
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create (with context_sync) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session with context_sync: {result.error_message}"
            )
        self._result = result
        return result

    async def create_with_browser_context(
        self,
        image_id: str,
        browser_context: Optional[BrowserContext] = None,
    ) -> object:
        """
        Create a browser session with the given image_id and optional BrowserContext.

        Args:
            image_id: The image ID to create the session with (e.g. ``"browser_latest"``）.
            browser_context: An optional :class:`BrowserContext` instance to attach
                             persistent context / extension options to the session.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If session creation or browser initialization fails.
        """
        params = CreateSessionParams(image_id=image_id)
        if browser_context is not None:
            params.browser_context = browser_context
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create (with browser_option) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create browser session: {result.error_message}"
            )

        self._result = result
        return result

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_status(self) -> str:
        """
        Call ``session.get_status()`` on the currently cached session.

        Returns:
            str: The session status string (e.g. ``"Running"``） when the call succeeds.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call returns success=False, or if an
                                   unexpected exception occurs.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create() or create_with_context_sync() first."
            )
        try:
            status_result = await self._result.session.get_status()
        except SessionError:
            raise
        except Exception as exc:
            raise SessionLifecycleError(
                "get_status() raised an unexpected exception",
                cause=exc,
            ) from exc

        if not status_result.success:
            raise SessionLifecycleError(
                f"get_status() failed: {status_result.error_message}"
            )
        return status_result.status

    # ------------------------------------------------------------------
    # Session deletion
    # ------------------------------------------------------------------

    async def delete(self) -> object:
        """
        Delete the currently cached session.

        Returns:
            DeleteResult.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call raises, or if deletion returns
                                   success=False.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create() or create_with_context_sync() first."
            )
        session = self._result.session
        try:
            result = await self._agent_bay.delete(session)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.delete raised an exception",
                cause=exc,
            ) from exc

        if not result.success:
            raise SessionLifecycleError(
                f"Failed to delete session: {result.error_message}"
            )

        self._result = None
        return result


# ---------------------------------------------------------------------------
# Sync variant
# ---------------------------------------------------------------------------


class SyncSessionLifecycle:
    """
    Manages a single AgentBay (sync) session lifecycle.

    Usage example (pytest)::

        @pytest.fixture(scope="module")
        def lifecycle():
            mgr = SyncSessionLifecycle()
            yield mgr
            mgr.delete()

        def test_something(lifecycle):
            result = lifecycle.default_create("linux_latest")
            assert result.success
            status = lifecycle.get_status()
            assert status.success
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Args:
            api_key: AgentBay API key. Falls back to ``AGENTBAY_API_KEY`` env var.
        """
        resolved_key = api_key or os.environ.get("AGENTBAY_API_KEY") or ""
        if not resolved_key:
            raise SessionLifecycleError(
                "API key is required. Set AGENTBAY_API_KEY or pass api_key."
            )
        self._agent_bay = AgentBay(api_key=resolved_key)
        # Stores the SessionResult from the last create call
        self._result = None

    # ------------------------------------------------------------------
    # Session creation
    # ------------------------------------------------------------------

    def default_create(self, image_id: str) -> object:
        """
        Create a session with the given image_id and cache the result.

        Args:
            image_id: The image ID to create the session with.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        params = CreateSessionParams(image_id=image_id)
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session: {result.error_message}"
            )
        self._result = result
        return result

    def create_with_context_sync(
        self,
        image_id: str,
        context_sync: ContextSync,
    ) -> object:
        """
        Create a session with the given image_id and a ContextSync configuration.

        Args:
            image_id: The image ID to create the session with.
            context_sync: A :class:`ContextSync` instance describing the context
                          sync policy to apply when creating the session.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
        )
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create (with context_sync) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session with context_sync: {result.error_message}"
            )
        self._result = result
        return result

    def create_with_browser_context(
        self,
        image_id: str,
        browser_context: Optional[BrowserContext] = None,
    ) -> object:
        """
        Create a browser session with the given image_id and optional BrowserContext.

        Args:
            image_id: The image ID to create the session with (e.g. ``"browser_latest"``）.
            browser_context: An optional :class:`BrowserContext` instance to attach
                             persistent context / extension options to the session.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If session creation fails.
        """
        params = CreateSessionParams(image_id=image_id)
        if browser_context is not None:
            params.browser_context = browser_context
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create (with browser_context) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create browser session: {result.error_message}"
            )

        self._result = result
        return result

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> str:
        """
        Call ``session.get_status()`` on the currently cached session.

        Returns:
            str: The session status string (e.g. ``"Running"``） when the call succeeds.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call returns success=False, or if an
                                   unexpected exception occurs.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create() or create_with_context_sync() first."
            )
        try:
            status_result = self._result.session.get_status()
        except SessionError:
            raise
        except Exception as exc:
            raise SessionLifecycleError(
                "get_status() raised an unexpected exception",
                cause=exc,
            ) from exc

        if not status_result.success:
            raise SessionLifecycleError(
                f"get_status() failed: {status_result.error_message}"
            )
        return status_result.status

    # ------------------------------------------------------------------
    # Session deletion
    # ------------------------------------------------------------------

    def delete(self) -> object:
        """
        Delete the currently cached session.

        Returns:
            DeleteResult.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call raises, or if deletion returns
                                   success=False.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create() or create_with_context_sync() first."
            )
        session = self._result.session
        try:
            result = self._agent_bay.delete(session)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.delete raised an exception",
                cause=exc,
            ) from exc

        if not result.success:
            raise SessionLifecycleError(
                f"Failed to delete session: {result.error_message}"
            )

        self._result = None
        return result
