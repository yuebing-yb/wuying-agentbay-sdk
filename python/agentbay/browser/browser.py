from typing import TYPE_CHECKING, Optional, Literal, Union
import asyncio
import time
import os
import typing
import base64
from agentbay.api.models import InitBrowserRequest
from agentbay.browser.browser_agent import BrowserAgent
from agentbay.api.base_service import BaseService
from agentbay.exceptions import BrowserError
from agentbay.config import _BROWSER_DATA_PATH, _BROWSER_FINGERPRINT_PERSIST_PATH
from agentbay.logger import get_logger, _log_api_response_with_details

# Initialize logger for this module
_logger = get_logger("browser")

if TYPE_CHECKING:
    from agentbay.session import Session
    from agentbay.browser.fingerprint import FingerprintFormat


class BrowserFingerprintContext:
    """
    Browser fingerprint context configuration.
    """
    def __init__(self, fingerprint_context_id: str):
        """
        Initialize FingerprintContext with context id.
        
        Args:
            fingerprint_context_id (str): ID of the fingerprint context for browser fingerprint.
        
        Raises:
            ValueError: If fingerprint_context_id is empty.
        """
        if not fingerprint_context_id or not fingerprint_context_id.strip():
            raise ValueError("fingerprint_context_id cannot be empty")

        self.fingerprint_context_id = fingerprint_context_id


class BrowserProxy:
    """
    Browser proxy configuration.
    Supports two types of proxy: custom proxy, wuying proxy.
    wuying proxy support two strategies: restricted and polling.
    """
    def __init__(
        self,
        proxy_type: Literal["custom", "wuying"],
        server: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        strategy: Optional[Literal["restricted", "polling"]] = None,
        pollsize: int = 10
    ):
        """
        Initialize a BrowserProxy.

        Args:
            proxy_type: Type of proxy - "custom" or "wuying"
            server: Proxy server address (required for custom type)
            username: Proxy username (optional for custom type)
            password: Proxy password (optional for custom type)
            strategy: Strategy for wuying support "restricted" and "polling"
            pollsize: Pool size (optional for proxy_type wuying and strategy polling)

            example:
            # custom proxy
            proxy_type: custom
            server: "127.0.0.1:9090"
            username: "username"
            password: "password"

            # wuying proxy with polling strategy
            proxy_type: wuying
            strategy: "polling"
            pollsize: 10

            # wuying proxy with restricted strategy
            proxy_type: wuying
            strategy: "restricted"
        """
        self.type = proxy_type
        self.server = server
        self.username = username
        self.password = password
        self.strategy = strategy
        self.pollsize = pollsize

        # Validation
        if proxy_type not in ["custom", "wuying"]:
            raise ValueError("proxy_type must be custom or wuying")

        if proxy_type == "custom" and not server:
            raise ValueError("server is required for custom proxy type")

        if proxy_type == "wuying" and not strategy:
            raise ValueError("strategy is required for wuying proxy type")

        if proxy_type == "wuying" and strategy not in ["restricted", "polling"]:
            raise ValueError("strategy must be restricted or polling for wuying proxy type")

        if proxy_type == "wuying" and strategy == "polling" and pollsize <= 0:
            raise ValueError("pollsize must be greater than 0 for polling strategy")
    def _to_map(self):
        """
        Convert BrowserProxy to dictionary format.

        Returns:
            dict: Dictionary representation of the proxy configuration.

        Example:
            ```python
            proxy = BrowserProxy(proxy_type="custom", server="127.0.0.1:8080", username="user", password="pass")
            proxy_dict = proxy._to_map()
            print(proxy_dict)
            ```
        """
        proxy_map = {
            "type": self.type
        }

        if self.type == "custom":
            proxy_map["server"] = self.server
            if self.username:
                proxy_map["username"] = self.username
            if self.password:
                proxy_map["password"] = self.password
        elif self.type == "wuying":
            proxy_map["strategy"] = self.strategy
            if self.strategy == "polling":
                proxy_map["pollsize"] = self.pollsize


        return proxy_map

    @classmethod
    def _from_map(cls, m: dict = None):
        """
        Create BrowserProxy from dictionary format.

        Args:
            m (dict): Dictionary containing proxy configuration.

        Returns:
            BrowserProxy: BrowserProxy instance created from the dictionary, or None if m is None.

        Raises:
            ValueError: If the proxy configuration is invalid.

        Example:
            ```python
            proxy_dict = {"type": "custom", "server": "127.0.0.1:8080"}
            proxy = BrowserProxy._from_map(proxy_dict)
            print(f"Proxy type: {proxy.type}, Server: {proxy.server}")
            ```
        """
        if not m:
            return None

        proxy_type = m.get("type")
        if not proxy_type:
            raise ValueError("type is required in proxy configuration")

        if proxy_type == "custom":
            return cls(
                proxy_type=proxy_type,
                server=m.get("server"),
                username=m.get("username"),
                password=m.get("password")
            )
        elif proxy_type == "wuying":
            return cls(
                proxy_type=proxy_type,
                strategy=m.get("strategy"),
                pollsize=m.get("pollsize", 10)
            )
        else:
            raise ValueError(f"Unsupported proxy type: {proxy_type}")

class BrowserViewport:
    """
    Browser viewport options.
    """
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def _to_map(self):
        """
        Convert BrowserViewport to dictionary format.

        Returns:
            dict: Dictionary representation of the viewport configuration.

        Example:
            ```python
            viewport = BrowserViewport(width=1920, height=1080)
            viewport_dict = viewport._to_map()
            print(viewport_dict)
            ```
        """
        viewport_map = dict()
        if self.width is not None:
            viewport_map['width'] = self.width
        if self.height is not None:
            viewport_map['height'] = self.height
        return viewport_map

    def _from_map(self, m: dict = None):
        """
        Update BrowserViewport from dictionary format.

        Args:
            m (dict): Dictionary containing viewport configuration.

        Returns:
            BrowserViewport: Updated viewport instance.

        Example:
            ```python
            viewport = BrowserViewport()
            viewport._from_map({"width": 1280, "height": 720})
            print(f"Viewport: {viewport.width}x{viewport.height}")
            ```
        """
        m = m or dict()
        if m.get('width') is not None:
            self.width = m.get('width')
        if m.get('height') is not None:
            self.height = m.get('height')
        return self

class BrowserScreen:
    """
    Browser screen options.
    """
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def _to_map(self):
        """
        Convert BrowserScreen to dictionary format.

        Returns:
            dict: Dictionary representation of the screen configuration.

        Example:
            ```python
            screen = BrowserScreen(width=1920, height=1080)
            screen_dict = screen.to_map()
            print(screen_dict)
            ```
        """
        screen_map = dict()
        if self.width is not None:
            screen_map['width'] = self.width
        if self.height is not None:
            screen_map['height'] = self.height
        return screen_map

    def _from_map(self, m: dict = None):
        """
        Update BrowserScreen from dictionary format.

        Args:
            m (dict): Dictionary containing screen configuration.

        Returns:
            BrowserScreen: Updated screen instance.

        Example:
            ```python
            screen = BrowserScreen()
            screen._from_map({"width": 2560, "height": 1440})
            print(f"Screen: {screen.width}x{screen.height}")
            ```
        """
        m = m or dict()
        if m.get('width') is not None:
            self.width = m.get('width')
        if m.get('height') is not None:
            self.height = m.get('height')
        return self

class BrowserFingerprint:
    """
    Browser fingerprint options.
    """
    def __init__(
        self,
        devices: list[Literal["desktop", "mobile"]] = None,
        operating_systems: list[Literal["windows", "macos", "linux", "android", "ios"]] = None,
        locales: list[str] = None
    ):
        self.devices = devices
        self.operating_systems = operating_systems
        self.locales = locales


        # Validation


        if devices is not None:
            if not isinstance(devices, list):
                raise ValueError("devices must be a list")
            for device in devices:
                if device not in ["desktop", "mobile"]:
                    raise ValueError("device must be desktop or mobile")

        if operating_systems is not None:
            if not isinstance(operating_systems, list):
                raise ValueError("operating_systems must be a list")
            for operating_system in operating_systems:
                if operating_system not in ["windows", "macos", "linux", "android", "ios"]:
                    raise ValueError("operating_system must be windows, macos, linux, android or ios")

    def _to_map(self):
        fingerprint_map = dict()
        if self.devices is not None:
            fingerprint_map['devices'] = self.devices
        if self.operating_systems is not None:
            fingerprint_map['operatingSystems'] = self.operating_systems
        if self.locales is not None:
            fingerprint_map['locales'] = self.locales
        return fingerprint_map

    def _from_map(self, m: dict = None):
        m = m or dict()
        if m.get('devices') is not None:
            self.devices = m.get('devices')
        if m.get('operatingSystems') is not None:
            self.operating_systems = m.get('operatingSystems')
        if m.get('locales') is not None:
            self.locales = m.get('locales')
        return self

class BrowserOption:
    """
    browser initialization options.
    """
    def __init__(
        self,
        use_stealth: bool = False,
        user_agent: str = None,
        viewport: BrowserViewport = None,
        screen: BrowserScreen = None,
        fingerprint: BrowserFingerprint = None,
        fingerprint_format: Optional["FingerprintFormat"] = None,
        fingerprint_persistent: bool = False,
        solve_captchas: bool = False,
        proxies: Optional[list[BrowserProxy]] = None,
        extension_path: Optional[str] = "/tmp/extensions/",
        cmd_args: Optional[list[str]] = None,
        default_navigate_url: Optional[str] = None,
        browser_type: Optional[Literal["chrome", "chromium"]] = None,
    ):
        self.use_stealth = use_stealth
        self.user_agent = user_agent
        self.viewport = viewport
        self.screen = screen
        self.fingerprint = fingerprint
        self.fingerprint_format = fingerprint_format
        self.solve_captchas = solve_captchas
        self.proxies = proxies
        self.extension_path = extension_path
        self.cmd_args = cmd_args
        self.default_navigate_url = default_navigate_url
        self.browser_type = browser_type

        # Check fingerprint persistent if provided
        if fingerprint_persistent:
            # Currently only support persistent fingerprint in docker env
            self.fingerprint_persist_path = os.path.join(_BROWSER_FINGERPRINT_PERSIST_PATH, "fingerprint.json")
        else:
            self.fingerprint_persist_path = None

        # Validate proxies list items
        if proxies is not None:
            if not isinstance(proxies, list):
                raise ValueError("proxies must be a list")
            if len(proxies) > 1:
                raise ValueError("proxies list length must be limited to 1")

        # Validate extension_path if provided
        if extension_path is not None:
            if not isinstance(extension_path, str):
                raise ValueError("extension_path must be a string")
            if not extension_path.strip():
                raise ValueError("extension_path cannot be empty")

        if cmd_args is not None:
            if not isinstance(cmd_args, list):
                raise ValueError("cmd_args must be a list")

        # Validate browser_type
        if browser_type is not None and browser_type not in ["chrome", "chromium"]:
            raise ValueError("browser_type must be 'chrome' or 'chromium'")

    def _to_map(self):
        option_map = dict()
        if behavior_simulate_env := os.getenv("AGENTBAY_BROWSER_BEHAVIOR_SIMULATE"):
            option_map['behaviorSimulate'] = behavior_simulate_env != "0"
        if self.use_stealth is not None:
            option_map['useStealth'] = self.use_stealth
        if self.user_agent is not None:
            option_map['userAgent'] = self.user_agent
        if self.viewport is not None:
            option_map['viewport'] = self.viewport._to_map()
        if self.screen is not None:
            option_map['screen'] = self.screen._to_map()
        if self.fingerprint is not None:
            option_map['fingerprint'] = self.fingerprint._to_map()
        if self.fingerprint_format is not None:
            # Encode fingerprint format to base64 string
            json_str = self.fingerprint_format._to_json()
            option_map['fingerprintRawData'] = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        if self.fingerprint_persist_path is not None:
            option_map['fingerprintPersistPath'] = self.fingerprint_persist_path
        if self.solve_captchas is not None:
            option_map['solveCaptchas'] = self.solve_captchas
        if self.proxies is not None:
            option_map['proxies'] = [proxy._to_map() for proxy in self.proxies]
        if self.extension_path is not None:
            option_map['extensionPath'] = self.extension_path
        if self.cmd_args is not None:
            option_map['cmdArgs'] = self.cmd_args
        if self.default_navigate_url is not None:
            option_map['defaultNavigateUrl'] = self.default_navigate_url
        if self.browser_type is not None:
            option_map['browserType'] = self.browser_type
        return option_map

    def _from_map(self, m: dict = None):
        m = m or dict()
        if m.get('useStealth') is not None:
            self.use_stealth = m.get('useStealth')
        else:
            self.use_stealth = False
        if m.get('userAgent') is not None:
            self.user_agent = m.get('userAgent')
        if m.get('viewport') is not None:
            self.viewport = BrowserViewport()._from_map(m.get('viewport'))
        if m.get('screen') is not None:
            self.screen = BrowserScreen()._from_map(m.get('screen'))
        if m.get('fingerprint') is not None:
            self.fingerprint = BrowserFingerprint()._from_map(m.get('fingerprint'))
        if m.get('fingerprintRawData') is not None:
            import base64
            from agentbay.browser.fingerprint import FingerprintFormat
            fingerprint_raw = m.get('fingerprintRawData')
            if isinstance(fingerprint_raw, str):
                # Decode base64 encoded fingerprint data
                fingerprint_json = base64.b64decode(fingerprint_raw.encode('utf-8')).decode('utf-8')
                self.fingerprint_format = FingerprintFormat._from_json(fingerprint_json)
            else:
                self.fingerprint_format = fingerprint_raw
        if m.get('fingerprintPersistPath') is not None:
            self.fingerprint_persist_path = m.get('fingerprintPersistPath')
        if m.get('solveCaptchas') is not None:
            self.solve_captchas = m.get('solveCaptchas')
        else:
            self.solve_captchas = False
        if m.get('proxies') is not None:
            proxy_list = m.get('proxies')
            if len(proxy_list) > 1:
                raise ValueError("proxies list length must be limited to 1")
            self.proxies = [BrowserProxy._from_map(proxy_data) for proxy_data in proxy_list]
        if m.get('cmdArgs') is not None:
            self.cmd_args = m.get('cmdArgs')
        if m.get('defaultNavigateUrl') is not None:
            self.default_navigate_url = m.get('defaultNavigateUrl')
        if m.get('browserType') is not None:
            self.browser_type = m.get('browserType')
        return self

class Browser(BaseService):
    """
    Browser provides browser-related operations for the session.
    """
    def __init__(self, session: "Session"):
        self.session = session
        self._endpoint_url = None
        self._initialized = False
        self._option = None
        self.agent = BrowserAgent(self.session, self)
        self.endpoint_router_port = None

    def initialize(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options.
        Returns True if successful, False otherwise.

        Args:
            option (BrowserOption): Browser configuration options.

        Returns:
            bool: True if initialization was successful, False otherwise.

        Example:
            ```python
            session = agent_bay.create().session
            browser_option = BrowserOption(use_stealth=True)
            success = session.browser.initialize(browser_option)
            print(f"Browser initialized: {success}")
            session.delete()
            ```
        """
        if self.is_initialized():
            return True
        try:
            browser_option_dict = option._to_map()

            # Enable record if session.enableBrowserReplay is True
            if hasattr(self.session, 'enableBrowserReplay') and self.session.enableBrowserReplay:
                browser_option_dict['enableRecord'] = True

            request = InitBrowserRequest(
                authorization=f"Bearer {self.session._get_api_key()}",
                session_id=self.session._get_session_id(),
                persistent_path=_BROWSER_DATA_PATH,
                browser_option=browser_option_dict,
            )
            response = self.session._get_client().init_browser(request)

            _logger.info(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self._initialized = True
                self._option = option
                _log_api_response_with_details(
                    api_name="InitBrowser",
                    success=True,
                    key_fields={
                        "port": data.get("Port"),
                        "status": "successfully initialized"
                    }
                )
                _logger.info("Browser instance was successfully initialized.")

            return success
        except Exception as e:
            _logger.exception(f"❌ Failed to initialize browser instance")
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    async def initialize_async(self, option: "BrowserOption") -> bool:
        """
        Initialize the browser instance with the given options asynchronously.
        Returns True if successful, False otherwise.

        Args:
            option (BrowserOption): Browser configuration options.

        Returns:
            bool: True if initialization was successful, False otherwise.

        Example:
            ```python
            session = agent_bay.create().session
            browser_option = BrowserOption(use_stealth=True)
            success = await session.browser.initialize_async(browser_option)
            print(f"Browser initialized: {success}")
            session.delete()
            ```
        """
        if self.is_initialized():
            return True
        try:
            browser_option_dict = option._to_map()

            # Enable record if session.enableBrowserReplay is True
            if hasattr(self.session, 'enableBrowserReplay') and self.session.enableBrowserReplay:
                browser_option_dict['enableRecord'] = True

            request = InitBrowserRequest(
                authorization=f"Bearer {self.session._get_api_key()}",
                session_id=self.session._get_session_id(),
                persistent_path=_BROWSER_DATA_PATH,
                browser_option=browser_option_dict,
            )
            response = await self.session._get_client().init_browser_async(request)
            _logger.debug(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self.endpoint_router_port = data.get("Port")
                self._initialized = True
                self._option = option
                _log_api_response_with_details(
                    api_name="InitBrowser (async)",
                    success=True,
                    key_fields={
                        "port": data.get("Port"),
                        "status": "successfully initialized"
                    }
                )
                _logger.info("Browser instance successfully initialized")
            return success
        except Exception as e:
            _logger.exception(f"❌ Failed to initialize browser instance asynchronously")
            self._initialized = False
            self._endpoint_url = None
            self._option = None
            return False

    def destroy(self):
        """
        Destroy the browser instance.

        Example:
            ```python
            session = agent_bay.create().session
            browser_option = BrowserOption()
            session.browser.initialize(browser_option)
            session.browser.destroy()
            session.delete()
            ```
        """
        self._stop_browser()

    async def screenshot(self, page, full_page: bool = False, **options) -> bytes:
        """
        Takes a screenshot of the specified page with enhanced options and error handling.
        This is the async version of the screenshot method.
        
        Args:
            page (Page): The Playwright Page object to take a screenshot of. This is a required parameter.
            full_page (bool): Whether to capture the full scrollable page. Defaults to False.
            **options: Additional screenshot options that will override defaults.
                      Common options include:
                      - type (str): Image type, either 'png' or 'jpeg' (default: 'png')
                      - quality (int): Quality of the image, between 0-100 (jpeg only)
                      - timeout (int): Maximum time in milliseconds (default: 60000)
                      - animations (str): How to handle animations (default: 'disabled')
                      - caret (str): How to handle the caret (default: 'hide')
                      - scale (str): Scale setting (default: 'css')
            
        Returns:
            bytes: Screenshot data as bytes.
            
        Raises:
            BrowserError: If browser is not initialized.
            RuntimeError: If screenshot capture fails.
        """
        # Check if browser is initialized
        if not self.is_initialized():
            raise BrowserError("Browser must be initialized before calling screenshot.")
        if page is None:
            raise ValueError("Page cannot be None")  
        # Set default enhanced options
        enhanced_options = {
            "animations": "disabled",
            "caret": "hide",
            "scale": "css",
            "timeout": options.get("timeout", 60000),
            "full_page": full_page,  # Use the function parameter, not options
            "type": options.get("type", "png"),
        }

        # Update with user-provided options (but full_page is already set from function parameter)
        enhanced_options.update(options)
        
        try:          
            # Wait for page to load
            # await page.wait_for_load_state("networkidle")
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_load_state("domcontentloaded", timeout=30000)
            # Scroll to load all content (especially for lazy-loaded elements)
            await self._scroll_to_load_all_content_async(page)
            
            # Ensure images with data-src attributes are loaded
            await page.evaluate("""
                () => {
                    document.querySelectorAll('img[data-src]').forEach(img => {
                        if (!img.src && img.dataset.src) {
                            img.src = img.dataset.src;
                        }
                    });
                    // Also handle background-image[data-bg]
                    document.querySelectorAll('[data-bg]').forEach(el => {
                        if (!el.style.backgroundImage) {
                            el.style.backgroundImage = `url(${el.dataset.bg})`;
                        }
                    });
                }
            """)
            
            # Wait a bit for images to load
            await page.wait_for_timeout(1500)
            final_height = await page.evaluate("document.body.scrollHeight")
            await page.set_viewport_size({"width": 1920, "height": min(final_height, 10000)})
            
            # Take the screenshot
            screenshot_bytes = await page.screenshot(**enhanced_options)
            _logger.info("Screenshot captured successfully.")
            return screenshot_bytes
            
        except Exception as e:
            # Convert exception to string safely to avoid comparison issues
            try:
                error_str = str(e)
            except:
                error_str = "Unknown error occurred"
            error_msg = f"Failed to capture screenshot: {error_str}"
            _logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    async def _scroll_to_load_all_content_async(self, page, max_scrolls: int = 8, delay_ms: int = 1200):
        """Async version of _scroll_to_load_all_content."""
        last_height = 0
        for _ in range(max_scrolls):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(delay_ms)
            new_height = await page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
            if new_height == last_height:
                break
            last_height = new_height

    def _stop_browser(self):
        """
        Stop the browser instance, internal use only.
        """
        if self.is_initialized():
            self.session.call_mcp_tool("stopChrome", {})
        else:
            raise BrowserError("Browser is not initialized. Cannot stop browser.")

    def get_endpoint_url(self) -> str:
        """
        Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
        When initialized, always fetches the latest CDP url from session.get_link().

        Returns:
            str: The browser CDP endpoint URL.

        Raises:
            BrowserError: If browser is not initialized or endpoint URL cannot be retrieved.

        Example:
            ```python
            session = agent_bay.create().session
            browser_option = BrowserOption()
            session.browser.initialize(browser_option)
            endpoint_url = session.browser.get_endpoint_url()
            print(f"CDP Endpoint: {endpoint_url}")
            session.delete()
            ```
        """
        if not self.is_initialized():
            raise BrowserError("Browser is not initialized. Cannot access endpoint URL.")
        try:
            if self.session.is_vpc:
                _logger.debug(f"VPC mode, endpoint_router_port: {self.endpoint_router_port}")
                self._endpoint_url = f"ws://{self.session.network_interface_ip}:{self.endpoint_router_port}"
            else:
                from agentbay.api.models import GetCdpLinkRequest
                request = GetCdpLinkRequest(
                    authorization=f"Bearer {self.session.agent_bay.api_key}",
                    session_id=self.session.session_id
                )
                response = self.session.agent_bay.client.get_cdp_link(request)
                if response.body and response.body.success and response.body.data:
                    self._endpoint_url = response.body.data.url
                else:
                    error_msg = response.body.message if response.body else "Unknown error"
                    raise BrowserError(f"Failed to get CDP link: {error_msg}")
            return self._endpoint_url
        except Exception as e:
            raise BrowserError(f"Failed to get endpoint URL from session: {e}")

    def get_option(self) -> Optional["BrowserOption"]:
        """
        Returns the current BrowserOption used to initialize the browser, or None if not set.

        Returns:
            Optional[BrowserOption]: The browser options if initialized, None otherwise.

        Example:
            ```python
            session = agent_bay.create().session
            browser_option = BrowserOption(use_stealth=True)
            session.browser.initialize(browser_option)
            current_options = session.browser.get_option()
            print(f"Stealth mode: {current_options.use_stealth}")
            session.delete()
            ```
        """
        return self._option

    def is_initialized(self) -> bool:
        """
        Returns True if the browser was initialized, False otherwise.

        Returns:
            bool: True if browser is initialized, False otherwise.

        Example:
            ```python
            session = agent_bay.create().session
            print(f"Initialized: {session.browser.is_initialized()}")
            browser_option = BrowserOption()
            session.browser.initialize(browser_option)
            print(f"Initialized: {session.browser.is_initialized()}")
            session.delete()
            ```
        """
        return self._initialized
