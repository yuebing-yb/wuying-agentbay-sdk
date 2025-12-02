import asyncio
import concurrent.futures
import json
import os
import sys
from typing import Any, Dict, Optional

from mcp import ClientSession, StdioServerParameters, stdio_client
from playwright.async_api import async_playwright

from agentbay import get_logger
from agentbay import AsyncBrowser as Browser, BrowserOption
from agentbay import AsyncSession
from agentbay.api.base_service import OperationResult
from agentbay import AsyncBrowserAgent
from agentbay import ActOptions

# Use the AgentBay _logger instead of the standard _logger
_logger = get_logger("local_page_agent")


class LocalMCPClient:
    def __init__(self, server: str, command: str, args: list[str]) -> None:
        self.server = server
        self.command = command
        self.args = args
        self.session: ClientSession | None = None
        self.worker_thread: concurrent.futures.Future | None = None
        self._tool_call_queue: asyncio.Queue | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def connect(self) -> None:
        if self.worker_thread is None:
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()

            def thread_target() -> None:
                async def _connect_and_list_tools() -> None:
                    success = False
                    _logger.info("Start connect to mcp server")
                    try:
                        _logger.debug(f"command = {self.command}, args = {self.args}")
                        server_params = StdioServerParameters(
                            command=self.command, args=self.args
                        )
                        async with stdio_client(server_params) as (
                            read_stream,
                            write_stream,
                        ):
                            async with ClientSession(
                                read_stream, write_stream
                            ) as session:
                                # Setup queue and event loop reference
                                self._tool_call_queue = asyncio.Queue()
                                self._loop = asyncio.get_running_loop()

                                self.session = session
                                _logger.info("Initialize MCP client session")
                                await self.session.initialize()
                                _logger.info(
                                    "Client initialized. Listing available tools..."
                                )
                                tools = await self.session.list_tools()
                                _logger.info(f"Tools: {tools}")
                                success = True
                                promise.set_result(success)
                                await self._interactive_loop()
                    except Exception as e:
                        _logger.error(f"Failed to connect to MCP server: {e}")
                        success = False
                        promise.set_result(success)

                asyncio.run(_connect_and_list_tools())

            self.worker_thread = concurrent.futures.ThreadPoolExecutor().submit(
                thread_target
            )
            promise.result()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if not self.session or not self._tool_call_queue or not self._loop:
            raise RuntimeError(
                "MCP client is not connected. Call connect() and ensure it returns True before calling callTool."
            )
        caller_loop = asyncio.get_running_loop()
        fut = caller_loop.create_future()
        await self._tool_call_queue.put((tool_name, arguments, fut))
        return await fut

    async def _interactive_loop(self):
        """Run interactive loop."""
        while True:
            if self._tool_call_queue is not None:
                try:
                    tool_name, arguments, future = await asyncio.wait_for(
                        self._tool_call_queue.get(), timeout=1.0
                    )
                    try:
                        _logger.info(
                            f"Call tool {tool_name} with arguments {arguments}"
                        )
                        if self.session is not None:
                            response = await self.session.call_tool(
                                tool_name, arguments
                            )
                            is_successful = not response.isError

                            mcp_response = OperationResult(
                                request_id="local_request_dummy_id",
                                success=is_successful,
                            )

                            # Extract text content from response
                            text_content = ""
                            if hasattr(response, "content") and response.content:
                                for content_item in response.content:
                                    if (
                                        hasattr(content_item, "text")
                                        and content_item.text
                                    ):
                                        text_content = content_item.text
                                        break
                                if is_successful:
                                    mcp_response.data = text_content
                                    _logger.info(
                                        f"MCP tool text response (data): {str(text_content)[:2000]}"
                                    )
                                else:
                                    mcp_response.error_message = text_content
                                    _logger.info(
                                        f"MCP tool text response (error): {str(text_content)[:2000]}"
                                    )

                            if asyncio.isfuture(future):
                                fut_loop = future.get_loop()
                                fut_loop.call_soon_threadsafe(
                                    future.set_result, mcp_response
                                )
                            elif isinstance(future, concurrent.futures.Future):
                                future.set_result(mcp_response)
                            else:
                                raise TypeError(
                                    f"Unexpected future type: {type(future)}"
                                )
                        else:
                            future.set_exception(
                                RuntimeError("MCP client session is not initialized.")
                            )
                    except Exception as e:
                        future.set_exception(e)
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(1)


class LocalPageAgent(AsyncBrowserAgent):
    def __init__(self, session, browser):
        super().__init__(session, browser)

        mcp_script = os.environ.get("PAGE_TASK_MCP_SERVER_SCRIPT", "")

        if mcp_script:
            self.mcp_client: LocalMCPClient | None = LocalMCPClient(
                server="PageUseAgent", command=sys.executable, args=[mcp_script]
            )
        else:
            self.mcp_client = None
            _logger.warning(
                "PAGE_TASK_MCP_SERVER_SCRIPT not set. MCP client will not be initialized."
            )

    def initialize(self):
        if self.mcp_client:
            self.mcp_client.connect()

    async def act_async(self, action_input, page=None):
        """Async wrapper for the act method"""
        # For local execution, we use direct Playwright calls if browser is available
        # Otherwise fallback to the standard synchronous act method
        try:
            if isinstance(action_input, str):
                action_options = ActOptions(action=action_input)
            else:
                action_options = action_input

            result = self.act(action_options, page)
            return result
        except Exception as e:
            # Fallback to synchronous method
            _logger.warning(f"act_async fallback due to error: {e}")
            if isinstance(action_input, str):
                action_options = ActOptions(action=action_input)
            else:
                action_options = action_input
            result = self.act(action_options, page)
            return result

    async def navigate_async(self, url: str) -> str:
        """Async wrapper for navigate method"""
        try:
            result = self.navigate(url)
            return result
        except Exception as e:
            _logger.warning(f"navigate_async fallback due to error: {e}")
            result = self.navigate(url)
            return result

    async def extract_async(self, options, page=None):
        """Async wrapper for extract method"""
        try:
            result = self.extract(options, page)
            return result
        except Exception as e:
            _logger.warning(f"extract_async fallback due to error: {e}")
            result = self.extract(options, page)
            return result

    async def observe_async(self, options, page=None):
        """Async wrapper for observe method"""
        try:
            result = self.observe(options, page)
            return result
        except Exception as e:
            _logger.warning(f"observe_async fallback due to error: {e}")
            result = self.observe(options, page)
            return result

    async def screenshot_async(self, page=None):
        """Async wrapper for screenshot method"""
        try:
            result = self.screenshot(page)
            return result
        except Exception as e:
            _logger.warning(f"screenshot_async fallback due to error: {e}")
            result = self.screenshot(page)
            return result

    def _call_mcp_tool(
        self,
        name: str,
        args: dict,
        read_timeout: int = None,
        connect_timeout: int = None,
    ) -> OperationResult:
        # If MCP client is not available or local mode, return a failed OperationResult
        # This avoids issues when no actual MCP server is running
        error_message = f"Local mode - cannot execute tool: {name}. Browser evaluation is running in local mode."

        return OperationResult(
            request_id="local_request_mock_id",
            success=False,
            data=None,
            error_message=error_message,
        )

    async def _call_mcp_tool_async(self, name: str, args: dict) -> OperationResult:
        if not self.mcp_client:
            raise RuntimeError("mcp_client is not set on LocalBrowserAgent.")
        return await self.mcp_client.call_tool(name, args)


class LocalBrowser(Browser):
    def __init__(self, session=None):
        # Optionally skip calling super().__init__ if not needed for tests
        self.contexts = []
        self._cdp_port = 9222
        self.agent: LocalPageAgent = LocalPageAgent(session, self)
        self._worker_thread = None

    async def initialize_async(self, options: BrowserOption) -> bool:
        if self._worker_thread is None:
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()

            def thread_target() -> None:
                async def _launch_local_browser() -> None:
                    success = False
                    _logger.info("Start launching local browser")
                    try:
                        async with async_playwright() as p:
                            # Define CDP port
                            # Recreate /tmp/chrome_cdp_ports.json with the required content
                            chrome_cdp_ports_path = "/tmp/chrome_cdp_ports.json"
                            with open(chrome_cdp_ports_path, "w") as f:
                                json.dump(
                                    {
                                        "chrome": str(self._cdp_port),
                                        "router": str(self._cdp_port),
                                        "local": str(self._cdp_port),
                                    },
                                    f,
                                )

                            # Launch headless browser and create a page for all tests
                            # use absolute path for user_data_dir
                            cwd = os.getcwd()
                            user_data_dir = os.path.join(cwd, "tmp/browser_user_data")

                            self._browser = await p.chromium.launch_persistent_context(
                                headless=True,
                                viewport={"width": 1280, "height": 1200},
                                args=[
                                    f"--remote-debugging-port={self._cdp_port}",
                                    "--disable-gpu",
                                    "--disable-software-rasterizer",
                                ],
                                user_data_dir=user_data_dir,
                            )

                            _logger.info("Local browser launched successfully:")
                            success = True
                            promise.set_result(success)
                            await self._playwright_interactive_loop()
                    except Exception as e:
                        _logger.error(f"Failed to connect to browser: {e}")
                        success = False
                        promise.set_result(success)

                asyncio.run(_launch_local_browser())

            self._worker_thread = concurrent.futures.ThreadPoolExecutor().submit(
                thread_target
            )
            if not promise.result():
                _logger.error("Failed to launch local browser")
                return False

        self.agent.initialize()
        return True

    async def initialize(self, option: Optional["BrowserOption"] = None) -> bool:
        return await self.initialize_async(option)

    def is_initialized(self) -> bool:
        return self._worker_thread is not None

    async def get_endpoint_url(self) -> str:
        return f"http://localhost:{self._cdp_port}"

    async def _playwright_interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            await asyncio.sleep(3)


class LocalSession(AsyncSession):
    def __init__(self):
        # Create a mock agent_bay with the required attributes
        mock_agent_bay = type(
            "MockAgentBay",
            (),
            {
                "api_key": os.environ.get("AGENTBAY_API_KEY", ""),
                "api_key_configured": bool(os.environ.get("AGENTBAY_API_KEY", "")),
            },
        )()
        mock_client = type(
            "MockClient",
            (),
            {
                "api_base_url": "",
                "get_session_status": lambda request: type(
                    "MockSessionStatus",
                    (),
                    {
                        "to_map": lambda: {
                            "success": True,
                            "data": {"status": "running"},
                        }
                    },
                )(),
                "call_mcp_tool": lambda name, args, **kwargs: type(
                    "MockMcpToolResult",
                    (),
                    {
                        "request_id": "mock_request_id",
                        "success": False,
                        "data": None,
                        "error_message": "Mock mode: Cannot execute tool calls without proper API connection",
                    },
                )(),
            },
        )()

        # Assign the mock client to the mock agent bay
        mock_agent_bay.client = mock_client

        super().__init__(mock_agent_bay, "local_session")
        self.browser = LocalBrowser(self)

    def call_mcp_tool(
        self,
        name: str,
        args: dict,
        read_timeout: int = None,
        connect_timeout: int = None,
    ):
        # Return a mock tool result that indicates the operation isn't supported in local mode
        return type(
            "OperationResult",
            (),
            {
                "request_id": "mock_request_id",
                "success": False,
                "data": None,
                "error_message": "Local mode: Cannot execute MCP tools without connection",
            },
        )()

    def delete(self, sync_context: bool = False) -> None:
        pass
