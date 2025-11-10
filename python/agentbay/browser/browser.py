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
from agentbay.config import BROWSER_DATA_PATH, BROWSER_FINGERPRINT_PERSIST_PATH
from agentbay.logger import get_logger, log_api_response_with_details

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
    def to_map(self):
        """
        Convert BrowserProxy to dictionary format.

        Returns:
            dict: Dictionary representation of the proxy configuration.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserProxy

            agent_bay = AgentBay(api_key="your_api_key")

            def convert_proxy_to_map():
                try:
                    # Create custom proxy
                    custom_proxy = BrowserProxy(
                        proxy_type="custom",
                        server="127.0.0.1:9090",
                        username="user",
                        password="pass"
                    )

                    # Convert to map
                    proxy_map = custom_proxy.to_map()
                    print(f"Custom proxy map: {proxy_map}")
                    # Output: Custom proxy map: {'type': 'custom', 'server': '127.0.0.1:9090', 'username': 'user', 'password': 'pass'}

                    # Create wuying proxy with polling strategy
                    wuying_proxy = BrowserProxy(
                        proxy_type="wuying",
                        strategy="polling",
                        pollsize=10
                    )

                    proxy_map = wuying_proxy.to_map()
                    print(f"Wuying proxy map: {proxy_map}")
                    # Output: Wuying proxy map: {'type': 'wuying', 'strategy': 'polling', 'pollsize': 10}
                except Exception as e:
                    print(f"Error: {e}")

            convert_proxy_to_map()
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
    def from_map(cls, m: dict = None):
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserProxy

            agent_bay = AgentBay(api_key="your_api_key")

            def create_proxy_from_map():
                try:
                    # Create custom proxy from dictionary
                    custom_proxy_dict = {
                        "type": "custom",
                        "server": "127.0.0.1:9090",
                        "username": "user",
                        "password": "pass"
                    }

                    custom_proxy = BrowserProxy.from_map(custom_proxy_dict)
                    print(f"Created custom proxy: {custom_proxy.type} at {custom_proxy.server}")
                    # Output: Created custom proxy: custom at 127.0.0.1:9090

                    # Create wuying proxy from dictionary
                    wuying_proxy_dict = {
                        "type": "wuying",
                        "strategy": "polling",
                        "pollsize": 10
                    }

                    wuying_proxy = BrowserProxy.from_map(wuying_proxy_dict)
                    print(f"Created wuying proxy: {wuying_proxy.type} with {wuying_proxy.strategy} strategy")
                    # Output: Created wuying proxy: wuying with polling strategy
                except Exception as e:
                    print(f"Error: {e}")

            create_proxy_from_map()
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

    def to_map(self):
        """
        Convert BrowserViewport to dictionary format.

        Returns:
            dict: Dictionary representation of the viewport configuration.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserViewport

            agent_bay = AgentBay(api_key="your_api_key")

            def convert_viewport_to_map():
                try:
                    # Create viewport with custom size
                    viewport = BrowserViewport(width=1920, height=1080)

                    # Convert to map
                    viewport_map = viewport.to_map()
                    print(f"Viewport map: {viewport_map}")
                    # Output: Viewport map: {'width': 1920, 'height': 1080}

                    # Create viewport with mobile size
                    mobile_viewport = BrowserViewport(width=375, height=812)
                    mobile_map = mobile_viewport.to_map()
                    print(f"Mobile viewport map: {mobile_map}")
                    # Output: Mobile viewport map: {'width': 375, 'height': 812}
                except Exception as e:
                    print(f"Error: {e}")

            convert_viewport_to_map()
            ```
        """
        viewport_map = dict()
        if self.width is not None:
            viewport_map['width'] = self.width
        if self.height is not None:
            viewport_map['height'] = self.height
        return viewport_map

    def from_map(self, m: dict = None):
        """
        Update BrowserViewport from dictionary format.

        Args:
            m (dict): Dictionary containing viewport configuration.

        Returns:
            BrowserViewport: Updated viewport instance.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserViewport

            agent_bay = AgentBay(api_key="your_api_key")

            def create_viewport_from_map():
                try:
                    # Create a default viewport
                    viewport = BrowserViewport()
                    print(f"Default viewport: {viewport.width}x{viewport.height}")
                    # Output: Default viewport: 1920x1080

                    # Update viewport from dictionary
                    viewport_dict = {"width": 1280, "height": 720}
                    viewport.from_map(viewport_dict)
                    print(f"Updated viewport: {viewport.width}x{viewport.height}")
                    # Output: Updated viewport: 1280x720
                except Exception as e:
                    print(f"Error: {e}")

            create_viewport_from_map()
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

    def to_map(self):
        """
        Convert BrowserScreen to dictionary format.

        Returns:
            dict: Dictionary representation of the screen configuration.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserScreen

            agent_bay = AgentBay(api_key="your_api_key")

            def convert_screen_to_map():
                try:
                    # Create screen with custom size
                    screen = BrowserScreen(width=1920, height=1080)

                    # Convert to map
                    screen_map = screen.to_map()
                    print(f"Screen map: {screen_map}")
                    # Output: Screen map: {'width': 1920, 'height': 1080}

                    # Create screen with 4K size
                    screen_4k = BrowserScreen(width=3840, height=2160)
                    screen_4k_map = screen_4k.to_map()
                    print(f"4K screen map: {screen_4k_map}")
                    # Output: 4K screen map: {'width': 3840, 'height': 2160}
                except Exception as e:
                    print(f"Error: {e}")

            convert_screen_to_map()
            ```
        """
        screen_map = dict()
        if self.width is not None:
            screen_map['width'] = self.width
        if self.height is not None:
            screen_map['height'] = self.height
        return screen_map

    def from_map(self, m: dict = None):
        """
        Update BrowserScreen from dictionary format.

        Args:
            m (dict): Dictionary containing screen configuration.

        Returns:
            BrowserScreen: Updated screen instance.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserScreen

            agent_bay = AgentBay(api_key="your_api_key")

            def create_screen_from_map():
                try:
                    # Create a default screen
                    screen = BrowserScreen()
                    print(f"Default screen: {screen.width}x{screen.height}")
                    # Output: Default screen: 1920x1080

                    # Update screen from dictionary
                    screen_dict = {"width": 2560, "height": 1440}
                    screen.from_map(screen_dict)
                    print(f"Updated screen: {screen.width}x{screen.height}")
                    # Output: Updated screen: 2560x1440
                except Exception as e:
                    print(f"Error: {e}")

            create_screen_from_map()
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

    def to_map(self):
        fingerprint_map = dict()
        if self.devices is not None:
            fingerprint_map['devices'] = self.devices
        if self.operating_systems is not None:
            fingerprint_map['operatingSystems'] = self.operating_systems
        if self.locales is not None:
            fingerprint_map['locales'] = self.locales
        return fingerprint_map

    def from_map(self, m: dict = None):
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
            self.fingerprint_persist_path = os.path.join(BROWSER_FINGERPRINT_PERSIST_PATH, "fingerprint.json")
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

    def to_map(self):
        option_map = dict()
        if behavior_simulate_env := os.getenv("AGENTBAY_BROWSER_BEHAVIOR_SIMULATE"):
            option_map['behaviorSimulate'] = behavior_simulate_env != "0"
        if self.use_stealth is not None:
            option_map['useStealth'] = self.use_stealth
        if self.user_agent is not None:
            option_map['userAgent'] = self.user_agent
        if self.viewport is not None:
            option_map['viewport'] = self.viewport.to_map()
        if self.screen is not None:
            option_map['screen'] = self.screen.to_map()
        if self.fingerprint is not None:
            option_map['fingerprint'] = self.fingerprint.to_map()
        if self.fingerprint_format is not None:
            # Encode fingerprint format to base64 string
            json_str = self.fingerprint_format.to_json()
            option_map['fingerprintRawData'] = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
        if self.fingerprint_persist_path is not None:
            option_map['fingerprintPersistPath'] = self.fingerprint_persist_path
        if self.solve_captchas is not None:
            option_map['solveCaptchas'] = self.solve_captchas
        if self.proxies is not None:
            option_map['proxies'] = [proxy.to_map() for proxy in self.proxies]
        if self.extension_path is not None:
            option_map['extensionPath'] = self.extension_path
        if self.cmd_args is not None:
            option_map['cmdArgs'] = self.cmd_args
        if self.default_navigate_url is not None:
            option_map['defaultNavigateUrl'] = self.default_navigate_url
        if self.browser_type is not None:
            option_map['browserType'] = self.browser_type
        return option_map

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('useStealth') is not None:
            self.use_stealth = m.get('useStealth')
        else:
            self.use_stealth = False
        if m.get('userAgent') is not None:
            self.user_agent = m.get('userAgent')
        if m.get('viewport') is not None:
            self.viewport = BrowserViewport.from_map(m.get('viewport'))
        if m.get('screen') is not None:
            self.screen = BrowserScreen.from_map(m.get('screen'))
        if m.get('fingerprint') is not None:
            self.fingerprint = BrowserFingerprint.from_map(m.get('fingerprint'))
        if m.get('fingerprintRawData') is not None:
            import base64
            from agentbay.browser.fingerprint import FingerprintFormat
            fingerprint_raw = m.get('fingerprintRawData')
            if isinstance(fingerprint_raw, str):
                # Decode base64 encoded fingerprint data
                fingerprint_json = base64.b64decode(fingerprint_raw.encode('utf-8')).decode('utf-8')
                self.fingerprint_format = FingerprintFormat.from_json(fingerprint_json)
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
            self.proxies = [BrowserProxy.from_map(proxy_data) for proxy_data in proxy_list]
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption, BrowserViewport

            agent_bay = AgentBay(api_key="your_api_key")

            def initialize_browser():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Initialize browser with default options
                        browser_option = BrowserOption()
                        success = session.browser.initialize(browser_option)
                        if success:
                            print("Browser initialized successfully")
                            # Output: Browser initialized successfully
                        else:
                            print("Browser initialization failed")

                        # Initialize with custom viewport
                        browser_option = BrowserOption(
                            use_stealth=True,
                            viewport=BrowserViewport(width=1920, height=1080)
                        )
                        success = session.browser.initialize(browser_option)
                        if success:
                            print("Browser initialized with custom viewport")
                            # Output: Browser initialized with custom viewport

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            initialize_browser()
            ```
        """
        if self.is_initialized():
            return True
        try:
            browser_option_dict = option.to_map()

            # Enable record if session.enableBrowserReplay is True
            if hasattr(self.session, 'enableBrowserReplay') and self.session.enableBrowserReplay:
                browser_option_dict['enableRecord'] = True

            request = InitBrowserRequest(
                authorization=f"Bearer {self.session._get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
                browser_option=browser_option_dict,
            )
            response = self.session.get_client().init_browser(request)

            _logger.info(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self._initialized = True
                self._option = option
                log_api_response_with_details(
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption, BrowserViewport
            import asyncio

            agent_bay = AgentBay(api_key="your_api_key")

            async def initialize_browser_async():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Initialize browser asynchronously with default options
                        browser_option = BrowserOption()
                        success = await session.browser.initialize_async(browser_option)
                        if success:
                            print("Browser initialized successfully")
                            # Output: Browser initialized successfully
                        else:
                            print("Browser initialization failed")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            asyncio.run(initialize_browser_async())
            ```
        """
        if self.is_initialized():
            return True
        try:
            browser_option_dict = option.to_map()

            # Enable record if session.enableBrowserReplay is True
            if hasattr(self.session, 'enableBrowserReplay') and self.session.enableBrowserReplay:
                browser_option_dict['enableRecord'] = True

            request = InitBrowserRequest(
                authorization=f"Bearer {self.session._get_api_key()}",
                session_id=self.session.get_session_id(),
                persistent_path=BROWSER_DATA_PATH,
                browser_option=browser_option_dict,
            )
            response = await self.session.get_client().init_browser_async(request)
            _logger.debug(f"Response from init_browser: {response}")
            response_map = response.to_map()
            body = response_map.get("body", {})
            data = body.get("Data", {})
            success = data.get("Port") is not None
            if success:
                self.endpoint_router_port = data.get("Port")
                self._initialized = True
                self._option = option
                log_api_response_with_details(
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption

            agent_bay = AgentBay(api_key="your_api_key")

            def demonstrate_browser_destroy():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Initialize the browser
                        browser_option = BrowserOption(use_stealth=True)
                        success = session.browser.initialize(browser_option)

                        if success:
                            print("Browser initialized successfully")
                            # Output: Browser initialized successfully

                            # Check if browser is initialized
                            if session.browser.is_initialized():
                                print("Browser is active")
                                # Output: Browser is active

                            # Destroy the browser instance
                            session.browser.destroy()
                            print("Browser destroyed")
                            # Output: Browser destroyed

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            demonstrate_browser_destroy()
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
            await page.wait_for_load_state("networkidle")
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption

            agent_bay = AgentBay(api_key="your_api_key")

            def get_browser_endpoint():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Initialize the browser
                        browser_option = BrowserOption()
                        success = session.browser.initialize(browser_option)

                        if success:
                            # Get the browser endpoint URL
                            endpoint_url = session.browser.get_endpoint_url()
                            print(f"Browser endpoint URL: {endpoint_url}")
                            # Output: Browser endpoint URL: ws://127.0.0.1:9222/devtools/browser/...

                            # Use this URL to connect with Playwright or other automation tools
                            print("You can now connect to this browser using Playwright")
                            # Output: You can now connect to this browser using Playwright

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            get_browser_endpoint()
            ```
        """
        if not self.is_initialized():
            raise BrowserError("Browser is not initialized. Cannot access endpoint URL.")
        try:
            if self.session.is_vpc:
                _logger.debug(f"VPC mode, endpoint_router_port: {self.endpoint_router_port}")
                self._endpoint_url = f"ws://{self.session.network_interface_ip}:{self.endpoint_router_port}"
            else:
                cdp_url = self.session.get_link()
                self._endpoint_url = cdp_url.data
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption, BrowserViewport

            agent_bay = AgentBay(api_key="your_api_key")

            def get_browser_options():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Get options before initialization (should be None)
                        options = session.browser.get_option()
                        if options is None:
                            print("No browser options set yet")
                            # Output: No browser options set yet

                        # Initialize with specific options
                        browser_option = BrowserOption(
                            use_stealth=True,
                            viewport=BrowserViewport(width=1920, height=1080)
                        )
                        session.browser.initialize(browser_option)

                        # Get options after initialization
                        current_options = session.browser.get_option()
                        if current_options:
                            print(f"Browser initialized with stealth mode: {current_options.use_stealth}")
                            # Output: Browser initialized with stealth mode: True
                            print(f"Viewport size: {current_options.viewport.width}x{current_options.viewport.height}")
                            # Output: Viewport size: 1920x1080

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            get_browser_options()
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
            from agentbay import AgentBay
            from agentbay.browser.browser import BrowserOption

            agent_bay = AgentBay(api_key="your_api_key")

            def check_browser_initialization():
                try:
                    result = agent_bay.create()
                    if result.success:
                        session = result.session

                        # Check if browser is initialized before initialization
                        if not session.browser.is_initialized():
                            print("Browser not initialized yet")
                            # Output: Browser not initialized yet

                            # Initialize the browser
                            browser_option = BrowserOption(use_stealth=True)
                            success = session.browser.initialize(browser_option)

                            if success:
                                # Check again after initialization
                                if session.browser.is_initialized():
                                    print("Browser is now initialized")
                                    # Output: Browser is now initialized

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            check_browser_initialization()
            ```
        """
        return self._initialized
