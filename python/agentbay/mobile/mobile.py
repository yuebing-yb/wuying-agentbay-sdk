"""
Mobile module for mobile device UI automation and configuration.
Handles touch operations, UI element interactions, application management, screenshot capabilities,
and mobile environment configuration operations.
"""

from typing import List, Optional, Dict, Any

from agentbay.api.base_service import BaseService
from agentbay.exceptions import AgentBayError, SessionError
from agentbay.model import BoolResult, OperationResult, ApiResponse
from agentbay.model.response import AdbUrlResult
from agentbay.computer.computer import (
    InstalledAppListResult,
    ProcessListResult,
    AppOperationResult,
    Process,
    InstalledApp,
)
from agentbay.logger import get_logger
from agentbay.command import MOBILE_COMMAND_TEMPLATES

# Initialize logger for this module
logger = get_logger("mobile")


class UIElementListResult(ApiResponse):
    """Result of UI element listing operations."""
    def __init__(
        self,
        request_id: str = "",
        success: bool = False,
        elements: Optional[List[Dict[str, Any]]] = None,
        error_message: str = "",
    ):
        super().__init__(request_id)
        self.success = success
        self.elements = elements or []
        self.error_message = error_message


class KeyCode:
    """
    Key codes for mobile device input.
    """

    HOME = 3
    BACK = 4
    VOLUME_UP = 24
    VOLUME_DOWN = 25
    POWER = 26
    MENU = 82


class Mobile(BaseService):
    """
    Handles mobile UI automation operations and configuration in the AgentBay cloud environment.
    Provides comprehensive mobile automation capabilities including touch operations,
    UI element interactions, application management, screenshot capabilities,
    and mobile environment configuration operations.
    """

    def __init__(self, session):
        """
        Initialize a Mobile object.

        Args:
            session: The session object that provides access to the AgentBay API.
        """
        super().__init__(session)

    # Touch Operations
    def tap(self, x: int, y: int) -> BoolResult:
        """
        Taps on the mobile screen at the specified coordinates.

        Args:
            x (int): X coordinate in pixels.
            y (int): Y coordinate in pixels.

        Returns:
            BoolResult: Object with success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()
            
            if result.success:
                session = result.session
                mobile = session.mobile
                
                # Tap at coordinates
                tap_result = mobile.tap(500, 1000)
                if tap_result.success:
                    print("Tap successful")
                
                session.delete()
            ```

        See Also:
            swipe, long_press
        """
        args = {"x": x, "y": y}
        try:
            result = self.session.call_mcp_tool("tap", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to tap: {str(e)}",
            )

    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration_ms: int = 300,
    ) -> BoolResult:
        """
        Performs a swipe gesture from one point to another.

        Args:
            start_x (int): Starting X coordinate.
            start_y (int): Starting Y coordinate.
            end_x (int): Ending X coordinate.
            end_y (int): Ending Y coordinate.
            duration_ms (int, optional): Duration of the swipe in milliseconds.
                Defaults to 300.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Swipe from one point to another
                swipe_result = mobile.swipe(100, 500, 900, 500, duration_ms=300)
                if swipe_result.success:
                    print("Swipe successful")

                session.delete()
            ```
        """
        args = {
            "start_x": start_x,
            "start_y": start_y,
            "end_x": end_x,
            "end_y": end_y,
            "duration_ms": duration_ms,
        }
        try:
            result = self.session.call_mcp_tool("swipe", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to perform swipe: {str(e)}",
            )

    def input_text(self, text: str) -> BoolResult:
        """
        Inputs text into the active field.

        Args:
            text (str): The text to input.

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Input text into active field
                input_result = mobile.input_text("Hello World")
                if input_result.success:
                    print("Text input successful")

                session.delete()
            ```
        """
        args = {"text": text}
        try:
            result = self.session.call_mcp_tool("input_text", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to input text: {str(e)}",
            )

    def send_key(self, key: int) -> BoolResult:
        """
        Sends a key press event.

        Args:
            key (int): The key code to send. Supported key codes are:
                - 3 : HOME
                - 4 : BACK
                - 24 : VOLUME UP
                - 25 : VOLUME DOWN
                - 26 : POWER
                - 82 : MENU

        Returns:
            BoolResult: Result object containing success status and error message if any.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.mobile.mobile import KeyCode

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Send HOME key
                key_result = mobile.send_key(KeyCode.HOME)
                if key_result.success:
                    print("Key press successful")

                session.delete()
            ```
        """
        args = {"key": key}
        try:
            result = self.session.call_mcp_tool("send_key", args)

            if not result.success:
                return BoolResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return BoolResult(
                request_id=result.request_id,
                success=True,
                data=True,
                error_message="",
            )
        except Exception as e:
            return BoolResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to send key: {str(e)}",
            )

    # UI Element Operations
    def get_clickable_ui_elements(self, timeout_ms: int = 2000) -> UIElementListResult:
        """
        Retrieves all clickable UI elements within the specified timeout.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 2000.

        Returns:
            UIElementListResult: Result object containing clickable UI elements and
                error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Get clickable UI elements
                elements_result = mobile.get_clickable_ui_elements(timeout_ms=2000)
                if elements_result.success:
                    print(f"Found {len(elements_result.elements)} clickable elements")

                session.delete()
            ```
        """
        args = {"timeout_ms": timeout_ms}
        try:
            result = self.session.call_mcp_tool("get_clickable_ui_elements", args)
            request_id = result.request_id

            if not result.success:
                return UIElementListResult(
                    request_id=request_id,
                    success=False,
                    elements=None,
                    error_message=result.error_message,
                )

            try:
                import json
                elements = json.loads(result.data)
                return UIElementListResult(
                    request_id=request_id,
                    success=True,
                    elements=elements,
                    error_message="",
                )
            except Exception as e:
                return UIElementListResult(
                    request_id=request_id,
                    success=False,
                    elements=None,
                    error_message=f"Failed to parse clickable UI elements data: {e}",
                )
        except Exception as e:
            return UIElementListResult(
                request_id="",
                success=False,
                elements=None,
                error_message=f"Failed to get clickable UI elements: {str(e)}",
            )

    def get_all_ui_elements(self, timeout_ms: int = 2000) -> UIElementListResult:
        """
        Retrieves all UI elements within the specified timeout.

        Args:
            timeout_ms (int, optional): Timeout in milliseconds. Defaults to 2000.

        Returns:
            UIElementListResult: Result object containing UI elements and error
                message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Get all UI elements
                elements_result = mobile.get_all_ui_elements(timeout_ms=2000)
                if elements_result.success:
                    print(f"Found {len(elements_result.elements)} total elements")

                session.delete()
            ```
        """
        args = {"timeout_ms": timeout_ms}

        def parse_element(element: Dict[str, Any]) -> Dict[str, Any]:
            """
            Recursively parses a UI element and its children.

            Args:
                element (Dict[str, Any]): The UI element to parse.

            Returns:
                Dict[str, Any]: The parsed UI element.
            """
            parsed = {
                "bounds": element.get("bounds", ""),
                "className": element.get("className", ""),
                "text": element.get("text", ""),
                "type": element.get("type", ""),
                "resourceId": element.get("resourceId", ""),
                "index": element.get("index", -1),
                "isParent": element.get("isParent", False),
            }
            children = element.get("children", [])
            if children:
                parsed["children"] = [parse_element(child) for child in children]
            else:
                parsed["children"] = []
            return parsed

        try:
            result = self.session.call_mcp_tool("get_all_ui_elements", args)
            request_id = result.request_id

            if not result.success:
                return UIElementListResult(
                    request_id=request_id,
                    success=False,
                    elements=None,
                    error_message=result.error_message,
                )

            try:
                import json
                elements = json.loads(result.data)
                parsed_elements = [parse_element(element) for element in elements]
                return UIElementListResult(
                    request_id=request_id,
                    success=True,
                    elements=parsed_elements,
                    error_message="",
                )
            except Exception as e:
                return UIElementListResult(
                    request_id=request_id,
                    success=False,
                    elements=None,
                    error_message=f"Failed to parse UI elements data: {e}",
                )
        except Exception as e:
            return UIElementListResult(
                request_id="",
                success=False,
                elements=None,
                error_message=f"Failed to get all UI elements: {str(e)}",
            )

    # Application Management Operations
    def get_installed_apps(
        self, start_menu: bool, desktop: bool, ignore_system_apps: bool
    ) -> InstalledAppListResult:
        """
        Retrieves a list of installed applications.

        Args:
            start_menu (bool): Whether to include start menu applications.
            desktop (bool): Whether to include desktop applications.
            ignore_system_apps (bool): Whether to ignore system applications.

        Returns:
            InstalledAppListResult: The result containing the list of installed
                applications.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.session_params import CreateSessionParams

            agent_bay = AgentBay(api_key="your_api_key")

            def list_installed_apps():
                try:
                    # Create a session with mobile_latest image
                    params = CreateSessionParams(image_id="mobile_latest")
                    result = agent_bay.create(params)
                    if result.success:
                        session = result.session

                        # Get installed apps (excluding system apps)
                        apps_result = session.mobile.get_installed_apps(
                            start_menu=False,
                            desktop=False,
                            ignore_system_apps=True
                        )

                        if apps_result.success:
                            print(f"Found {len(apps_result.data)} installed apps")
                            for app in apps_result.data:
                                print(f"App: {app.name}, Package: {app.start_cmd}")
                        else:
                            print(f"Failed to get apps: {apps_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            list_installed_apps()
            ```
        """
        try:
            args = {
                "start_menu": start_menu,
                "desktop": desktop,
                "ignore_system_apps": ignore_system_apps,
            }

            result = self.session.call_mcp_tool("get_installed_apps", args)

            if not result.success:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message,
                )

            try:
                import json
                apps_json = json.loads(result.data)
                installed_apps = []

                for app_data in apps_json:
                    app = InstalledApp.from_dict(app_data)
                    installed_apps.append(app)

                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=True,
                    data=installed_apps,
                )
            except json.JSONDecodeError as e:
                return InstalledAppListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse applications JSON: {e}",
                )
        except Exception as e:
            return InstalledAppListResult(
                success=False, error_message=str(e)
            )

    def start_app(
        self, start_cmd: str, work_directory: str = "", activity: str = ""
    ) -> ProcessListResult:
        """
        Starts an application with the given command, optional working directory and
            optional activity.

        Args:
            start_cmd (str): The command to start the application.
            work_directory (str, optional): The working directory for the application.
            activity (str, optional): Activity name to launch (e.g. ".SettingsActivity"
                or "com.package/.Activity"). Defaults to "".

        Returns:
            ProcessListResult: The result containing the list of processes started.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.session_params import CreateSessionParams

            agent_bay = AgentBay(api_key="your_api_key")

            def start_mobile_app():
                try:
                    # Create a session with mobile_latest image
                    params = CreateSessionParams(image_id="mobile_latest")
                    result = agent_bay.create(params)
                    if result.success:
                        session = result.session

                        # Start Settings app with activity
                        start_result = session.mobile.start_app(
                            start_cmd="com.android.settings",
                            activity=".Settings"
                        )

                        if start_result.success:
                            print(f"Started {len(start_result.data)} processes")
                            for process in start_result.data:
                                print(f"Process: {process.name}, PID: {process.pid}")
                        else:
                            print(f"Failed to start app: {start_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            start_mobile_app()
            ```
        """
        try:
            args = {"start_cmd": start_cmd}
            if work_directory:
                args["work_directory"] = work_directory
            if activity:
                args["activity"] = activity

            result = self.session.call_mcp_tool("start_app", args)

            if not result.success:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=result.error_message,
                )

            try:
                import json
                processes_json = json.loads(result.data)
                processes = []

                for process_data in processes_json:
                    process = Process.from_dict(process_data)
                    processes.append(process)

                return ProcessListResult(
                    request_id=result.request_id, success=True, data=processes
                )
            except json.JSONDecodeError as e:
                return ProcessListResult(
                    request_id=result.request_id,
                    success=False,
                    error_message=f"Failed to parse processes JSON: {e}",
                )
        except Exception as e:
            return ProcessListResult(success=False, error_message=str(e))

    def stop_app_by_cmd(self, stop_cmd: str) -> AppOperationResult:
        """
        Stops an application by stop command.

        Args:
            stop_cmd (str): The command to stop the application.

        Returns:
            AppOperationResult: The result of the operation.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.session_params import CreateSessionParams

            agent_bay = AgentBay(api_key="your_api_key")

            def stop_mobile_app():
                try:
                    # Create a session with mobile_latest image
                    params = CreateSessionParams(image_id="mobile_latest")
                    result = agent_bay.create(params)
                    if result.success:
                        session = result.session

                        # Stop an application using package name
                        stop_result = session.mobile.stop_app_by_cmd("com.android.settings")

                        if stop_result.success:
                            print("App stopped successfully")
                        else:
                            print(f"Failed to stop app: {stop_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            stop_mobile_app()
            ```
        """
        try:
            args = {"stop_cmd": stop_cmd}
            result = self.session.call_mcp_tool("stop_app_by_cmd", args)

            return AppOperationResult(
                request_id=result.request_id,
                success=result.success,
                error_message=result.error_message,
            )
        except Exception as e:
            return AppOperationResult(success=False, error_message=str(e))

    # Screenshot Operations
    def screenshot(self) -> OperationResult:
        """
        Takes a screenshot of the current screen.

        Returns:
            OperationResult: Result object containing the path to the screenshot
                and error message if any.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session
                mobile = session.mobile

                # Take a screenshot
                screenshot_result = mobile.screenshot()
                if screenshot_result.success:
                    print(f"Screenshot saved to: {screenshot_result.data}")

                session.delete()
            ```
        """
        args = {}
        try:
            result = self.session.call_mcp_tool("system_screenshot", args)

            if not result.success:
                return OperationResult(
                    request_id=result.request_id,
                    success=False,
                    data=None,
                    error_message=result.error_message,
                )

            return OperationResult(
                request_id=result.request_id,
                success=True,
                data=result.data,
                error_message="",
            )
        except Exception as e:
            return OperationResult(
                request_id="",
                success=False,
                data=None,
                error_message=f"Failed to take screenshot: {str(e)}",
            )

    # Mobile Configuration Operations
    def configure(self, mobile_config):
        """
        Configure mobile settings from MobileExtraConfig.

        This method is typically called automatically during session creation when
        MobileExtraConfig is provided in CreateSessionParams. It can also be called
        manually to reconfigure mobile settings during a session.

        Args:
            mobile_config (MobileExtraConfig): Mobile configuration object with settings for:
                - lock_resolution (bool): Whether to lock device resolution
                - app_manager_rule (AppManagerRule): App whitelist/blacklist rules
                - hide_navigation_bar (bool): Whether to hide navigation bar
                - uninstall_blacklist (List[str]): Apps protected from uninstallation

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.session_params import (
                CreateSessionParams,
                ExtraConfigs,
                MobileExtraConfig,
                AppManagerRule
            )

            agent_bay = AgentBay(api_key="your_api_key")

            def demonstrate_mobile_configuration():
                try:
                    # Method 1: Configure mobile settings during session creation
                    app_rule = AppManagerRule(
                        rule_type="White",
                        app_package_name_list=[
                            "com.android.settings",
                            "com.android.chrome",
                            "com.example.myapp"
                        ]
                    )

                    mobile_config = MobileExtraConfig(
                        lock_resolution=True,
                        app_manager_rule=app_rule,
                        hide_navigation_bar=True,
                        uninstall_blacklist=[
                            "com.android.settings",
                            "com.example.important"
                        ]
                    )

                    extra_configs = ExtraConfigs(mobile=mobile_config)
                    params = CreateSessionParams(
                        image_id="mobile_latest",
                        extra_configs=extra_configs
                    )

                    # Mobile configuration is applied automatically during creation
                    result = agent_bay.create(params)
                    if result.success:
                        session = result.session
                        print("Mobile session created with configuration")
                        # Output: Mobile session created with configuration

                        # Method 2: Manually reconfigure mobile settings during session
                        new_app_rule = AppManagerRule(
                            rule_type="Black",
                            app_package_name_list=[
                                "com.example.unwanted",
                                "com.ads.provider"
                            ]
                        )

                        new_mobile_config = MobileExtraConfig(
                            lock_resolution=False,
                            app_manager_rule=new_app_rule,
                            hide_navigation_bar=False
                        )

                        # Apply new configuration
                        session.mobile.configure(new_mobile_config)
                        print("Mobile configuration updated")
                        # Output: Mobile configuration updated

                        session.delete()

                except Exception as e:
                    print(f"Error: {e}")

            demonstrate_mobile_configuration()
            ```

        Note:
            - This method is called automatically during session creation if MobileExtraConfig is provided
            - Configuration changes are applied immediately
            - Resolution lock prevents resolution changes
            - App whitelist/blacklist affects app launching permissions
            - Uninstall blacklist protects apps from being uninstalled

        See Also:
            set_resolution_lock, set_app_whitelist, set_app_blacklist,
            set_navigation_bar_visibility, set_uninstall_blacklist
        """
        if not mobile_config:
            logger.warning("No mobile configuration provided")
            return
        
        # Configure resolution lock
        if mobile_config.lock_resolution is not None:
            self._set_resolution_lock(mobile_config.lock_resolution)
        
        # Configure app management rules
        if mobile_config.app_manager_rule and mobile_config.app_manager_rule.rule_type:
            app_rule = mobile_config.app_manager_rule
            package_names = app_rule.app_package_name_list or []
            
            if package_names and app_rule.rule_type in ["White", "Black"]:
                if app_rule.rule_type == "White":
                    self._set_app_whitelist(package_names)
                else:
                    self._set_app_blacklist(package_names)
            elif not package_names:
                logger.warning(f"No package names provided for {app_rule.rule_type} list")
        
        # Configure navigation bar visibility
        if mobile_config.hide_navigation_bar is not None:
            self._set_navigation_bar_visibility(mobile_config.hide_navigation_bar)
        
        # Configure uninstall blacklist
        if mobile_config.uninstall_blacklist and len(mobile_config.uninstall_blacklist) > 0:
            self._set_uninstall_blacklist(mobile_config.uninstall_blacklist)

    def set_resolution_lock(self, enable: bool):
        """
        Set display resolution lock for mobile devices.

        Args:
            enable (bool): True to enable, False to disable.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session

                # Enable resolution lock to prevent resolution changes
                session.mobile.set_resolution_lock(True)

                # Disable resolution lock to allow resolution changes
                session.mobile.set_resolution_lock(False)

                session.delete()
            ```
        """
        self._set_resolution_lock(enable)

    def set_app_whitelist(self, package_names: List[str]):
        """
        Set application whitelist.

        Args:
            package_names (List[str]): List of Android package names to whitelist.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session

                # Set whitelist to only allow specific apps
                whitelist = [
                    "com.android.settings",
                    "com.android.chrome",
                    "com.example.myapp"
                ]
                session.mobile.set_app_whitelist(whitelist)

                session.delete()
            ```

        Notes:
            - Only apps in the whitelist will be allowed to run
            - System apps may be affected depending on the configuration
            - Whitelist takes precedence over blacklist if both are set
        """
        if not package_names:
            logger.warning("Empty package names list for whitelist")
            return
        self._set_app_whitelist(package_names)

    def set_app_blacklist(self, package_names: List[str]):
        """
        Set application blacklist.

        Args:
            package_names (List[str]): List of Android package names to blacklist.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session

                # Blacklist specific apps to prevent them from running
                blacklist = [
                    "com.example.unwanted",
                    "com.ads.provider"
                ]
                session.mobile.set_app_blacklist(blacklist)

                session.delete()
            ```

        Notes:
            - Apps in the blacklist will be blocked from running
            - Whitelist takes precedence over blacklist if both are set
        """
        if not package_names:
            logger.warning("Empty package names list for blacklist")
            return
        self._set_app_blacklist(package_names)

    def set_navigation_bar_visibility(self, hide: bool):
        """
        Set navigation bar visibility for mobile devices.

        Args:
            hide (bool): True to hide navigation bar, False to show navigation bar.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session

                # Hide the navigation bar for fullscreen experience
                session.mobile.set_navigation_bar_visibility(hide=True)

                # Show the navigation bar
                session.mobile.set_navigation_bar_visibility(hide=False)

                session.delete()
            ```

        Notes:
            - Hiding the navigation bar provides a fullscreen experience
            - The navigation bar can still be accessed by swiping from the edge
        """
        self._set_navigation_bar_visibility(hide)

    def set_uninstall_blacklist(self, package_names: List[str]):
        """
        Set uninstall protection blacklist for mobile devices.

        Args:
            package_names (List[str]): List of Android package names to protect from uninstallation.

        Example:
            ```python
            from agentbay import AgentBay

            agent_bay = AgentBay(api_key="your_api_key")
            result = agent_bay.create()

            if result.success:
                session = result.session

                # Protect critical apps from uninstallation
                protected_apps = [
                    "com.android.settings",
                    "com.example.important",
                    "com.security.app"
                ]
                session.mobile.set_uninstall_blacklist(protected_apps)

                session.delete()
            ```

        Notes:
            - Apps in the uninstall blacklist cannot be uninstalled
            - This is useful for protecting critical applications
            - The protection persists for the session lifetime
        """
        if not package_names:
            logger.warning("Empty package names list for uninstall blacklist")
            return
        self._set_uninstall_blacklist(package_names)

    def get_adb_url(self, adbkey_pub: str) -> AdbUrlResult:
        """
        Retrieves the ADB connection URL for the mobile environment.

        This method is only supported in mobile environments (mobile_latest image).
        It uses the provided ADB public key to establish the connection and returns
        the ADB connect URL.

        Args:
            adbkey_pub (str): The ADB public key for connection authentication.

        Returns:
            AdbUrlResult: Result object containing the ADB connection URL
                         (format: "adb connect <IP>:<Port>") and request ID.
                         Returns error if not in mobile environment.

        Raises:
            SessionError: If the session is not in mobile environment.

        Example:
            ```python
            from agentbay import AgentBay
            from agentbay.session_params import CreateSessionParams

            agent_bay = AgentBay(api_key="your_api_key")

            def get_adb_connection():
                try:
                    # Create a session with mobile_latest image
                    params = CreateSessionParams(image_id="mobile_latest")
                    result = agent_bay.create(params)
                    if result.success:
                        session = result.session

                        # Get ADB URL with public key
                        adbkey_pub = "QAAAAM0muSn7yQCY...your_adb_public_key...EAAQAA="
                        adb_result = session.mobile.get_adb_url(adbkey_pub)

                        if adb_result.success:
                            print(f"ADB URL: {adb_result.data}")
                            print(f"Request ID: {adb_result.request_id}")
                        else:
                            print(f"Failed to get ADB URL: {adb_result.error_message}")

                        session.delete()
                except Exception as e:
                    print(f"Error: {e}")

            get_adb_connection()
            ```
        """
        try:
            # Build options JSON with adbkey_pub
            import json
            options_json = json.dumps({"adbkey_pub": adbkey_pub})

            # Call get_link with protocol_type="adb" and options
            result = self.session.get_link(protocol_type="adb", options=options_json)

            # Log the operation
            logger.info(f"✅ get_adb_url completed successfully. RequestID: {result.request_id}")

            # Return wrapped in AdbUrlResult
            return AdbUrlResult(
                request_id=result.request_id,
                success=result.success,
                data=result.data,
                error_message=result.error_message if not result.success else "",
            )

        except Exception as e:
            error_msg = f"Failed to get ADB URL: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return AdbUrlResult(
                request_id="",
                success=False,
                data=None,
                error_message=error_msg,
            )

    def _execute_template_command(self, template_name: str, params: Dict[str, Any], operation_name: str):
        """Execute a command using template and parameters."""
        template = MOBILE_COMMAND_TEMPLATES.get(template_name)
        if not template:
            logger.error(f"Template '{template_name}' not found")
            return
            
        command = template.format(**params)
        
        logger.info(f"Executing {operation_name}")
        result = self.session.command.execute_command(command)
        
        if result.success:
            logger.info(f"✅ {operation_name} completed successfully")
        else:
            logger.error(f"❌ {operation_name} failed: {result.error_message}")

    def _set_resolution_lock(self, enable: bool):
        """Execute resolution lock command."""
        params = {"lock_switch": 1 if enable else 0}
        operation_name = f"Resolution lock {'enable' if enable else 'disable'}"
        self._execute_template_command("resolution_lock", params, operation_name)

    def _set_app_whitelist(self, package_names: List[str]):
        """Execute app whitelist command."""
        params = {
            "package_list": '\n'.join(package_names),
            "package_count": len(package_names)
        }
        operation_name = f"App whitelist configuration ({len(package_names)} packages)"
        self._execute_template_command("app_whitelist", params, operation_name)

    def _set_app_blacklist(self, package_names: List[str]):
        """Execute app blacklist command."""
        params = {
            "package_list": '\n'.join(package_names),
            "package_count": len(package_names)
        }
        operation_name = f"App blacklist configuration ({len(package_names)} packages)"
        self._execute_template_command("app_blacklist", params, operation_name)

    def _set_navigation_bar_visibility(self, hide: bool):
        """Execute navigation bar visibility command."""
        template_name = "hide_navigation_bar" if hide else "show_navigation_bar"
        operation_name = f"Navigation bar visibility (hide: {hide})"
        self._execute_template_command(template_name, {}, operation_name)

    def _set_uninstall_blacklist(self, package_names: List[str]):
        """Execute uninstall blacklist command."""
        # Use semicolon-separated format for uninstall blacklist property
        params = {
            "package_list": ';'.join(package_names)
        }
        operation_name = f"Uninstall blacklist configuration ({len(package_names)} packages)"
        self._execute_template_command("uninstall_blacklist", params, operation_name)
