import os
import sys
import unasync

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTBAY_DIR = os.path.join(ROOT, "agentbay")
ASYNC_DIR = os.path.join(AGENTBAY_DIR, "_async")
SYNC_DIR = os.path.join(AGENTBAY_DIR, "_sync")

TEST_DIR = os.path.join(ROOT, "tests", "integration")
TEST_ASYNC_DIR = os.path.join(TEST_DIR, "_async")
TEST_SYNC_DIR = os.path.join(TEST_DIR, "_sync")

def _apply_custom_replacements(content: str, file_path: str) -> str:
    """Apply custom replacements that unasync doesn't handle."""
    # Fix asyncio.wait_for with stop_event.wait() - this is a common pattern in filesystem.py
    # Replace the entire try-except block (with correct indentation)
    content = content.replace(
        "                    try:\n                        asyncio.wait_for(stop_event.wait(), timeout=interval)\n                    except asyncio.TimeoutError:\n                        pass",
        "                    stop_event.wait(timeout=interval)"
    )
    # Also handle the case where it's just the call without try-except
    content = content.replace(
        "asyncio.wait_for(stop_event.wait(), timeout=interval)",
        "stop_event.wait(timeout=interval)"
    )
    return content

def generate_sync():
    # Define rules for unasync
    common_replacements = {
        # Class Renames
        "AsyncAgentBay": "AgentBay",
        "AsyncSession": "Session",
        "AsyncBrowser": "Browser",
        "AsyncCommand": "Command",
        "AsyncCode": "Code",
        "AsyncFileSystem": "FileSystem",
        "AsyncContextManager": "ContextManager",
        "AsyncContextService": "ContextService",
        "AsyncComputer": "Computer",
        "AsyncMobile": "Mobile",
        "AsyncFileTransfer": "FileTransfer",
        "AsyncContextSync": "ContextSync",
        "AsyncOss": "Oss",
        "AsyncAgent": "Agent",
        "AsyncBrowserAgent": "BrowserAgent",
        "AsyncBaseService": "BaseService",
        "AsyncExtensionsService": "ExtensionsService",

        # Variable/Attribute Renames
        "init_browser_async": "init_browser",
        "call_mcp_tool_async": "call_mcp_tool",
        "call_mcp_tool_with_options_async": "call_mcp_tool_with_options",
        "release_mcp_session_async": "release_mcp_session",
        "create_mcp_session_async": "create_mcp_session",
        "get_cdp_link_async": "get_cdp_link",
        "get_context_info_async": "get_context_info",
        "sync_context_async": "sync_context",
        "get_mcp_resource_async": "get_mcp_resource",
        "set_label_async": "set_label",
        "get_label_async": "get_label",
        "pause_session_async_async": "pause_session_async",
        "resume_session_async_async": "resume_session_async",
        "list_mcp_tools_async": "list_mcp_tools",
        "get_adb_link_async": "get_adb_link",
        "start_clear": "clear_async",

        # Client API methods rename
        "get_link_async": "get_link",
        "get_context_async": "get_context",
        "delete_context_async": "delete_context",
        "list_contexts_async": "list_contexts",
        "modify_context_async": "modify_context",
        "delete_context_file_async": "delete_context_file",
        "describe_context_files_async": "describe_context_files",
        "get_context_file_download_url_async": "get_context_file_download_url",
        "get_context_file_upload_url_async": "get_context_file_upload_url",
        "get_cdp_link_async": "get_cdp_link",
        "get_context_info_async": "get_context_info",
        "get_label_async": "get_label",
        "get_session_async": "get_session",
        "list_session_async": "list_session",
        "create_mcp_session_async": "create_mcp_session",
        "get_mcp_resource_async": "get_mcp_resource",
        "sync_context_async": "sync_context",
        "clear_context_async": "clear_context",

        # Browser Agent specific
        "navigate_async": "navigate",
        "screenshot_async": "screenshot",
        "act_async": "act",
        "observe_async": "observe",
        "extract_async": "extract",
        "close_async": "close",
        "_execute_act_async": "_execute_act",
        "_execute_extract_async": "_execute_extract",
        "_execute_observe_async": "_execute_observe",
        "_execute_screenshot_async": "_execute_screenshot",
        "_get_page_and_context_index_async": "_get_page_and_context_index",
        "_scroll_to_load_all_content_async": "_scroll_to_load_all_content",
        "page_use_act_async": "page_use_act",
        "page_use_extract_async": "page_use_extract",

        # Agent specific
        "async_execute_task": "async_execute_task",

        # Import fixes
        "from agentbay._async": "from agentbay._sync",
        "from ._async": "from ._sync",
        "from .._async": "from .._sync",

        # Asyncio replacements
        "asyncio.sleep": "time.sleep",
        "asyncio.Event": "threading.Event",
        "asyncio.TimeoutError": "RuntimeError",
        "async_playwright": "sync_playwright",
        "httpx.AsyncClient": "httpx.Client",
        "await ": "",
        "async def ": "def ",
        "async with ": "with ",
        "async for ": "for ",

        # Test specific
        "@pytest.mark.asyncio": "",
    }

    rules = [
        unasync.Rule(
            fromdir=ASYNC_DIR,
            todir=SYNC_DIR,
            additional_replacements=common_replacements
        ),
        unasync.Rule(
            fromdir=TEST_ASYNC_DIR,
            todir=TEST_SYNC_DIR,
            additional_replacements=common_replacements
        )
    ]

    filepaths = []
    # Walk _async dir
    for root, dirs, files in os.walk(ASYNC_DIR):
        for file in files:
            if file.endswith(".py"):
                filepaths.append(os.path.join(root, file))

    # Walk tests/_async dir
    if os.path.exists(TEST_ASYNC_DIR):
        for root, dirs, files in os.walk(TEST_ASYNC_DIR):
            for file in files:
                if file.endswith(".py"):
                    filepaths.append(os.path.join(root, file))

    # Unasync logic
    unasync.unasync_files(filepaths, rules)

    # Post-process
    process_dirs = [SYNC_DIR, TEST_SYNC_DIR]

    for directory in process_dirs:
        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r") as f:
                        content = f.read()

                    # Header check
                    header = "# DO NOT EDIT THIS FILE MANUALLY.\n# This file is auto-generated by scripts/generate_sync.py\n\n"
                    if not content.startswith(header):
                        content = header + content

                    # Fix httpx.SyncClient issue (unasync might produce this)
                    content = content.replace("httpx.SyncClient", "httpx.Client")

                    # Fix playwright import
                    content = content.replace("playwright.async_api", "playwright.sync_api")

                    # Custom Replacements
                    # Force replace asyncio.sleep if unasync missed it (common with await removal)
                    content = content.replace("asyncio.sleep", "time.sleep")

                    # Apply custom replacements
                    content = _apply_custom_replacements(content, path)

                    if "filesystem.py" in file:
                        # Fix asyncio.wait_for with stop_event.wait() in monitor loop
                        content = content.replace(
                            "                    try:\n                        asyncio.wait_for(stop_event.wait(), timeout=interval)\n                    except asyncio.TimeoutError:\n                        pass",
                            "                    stop_event.wait(timeout=interval)"
                        )

                        # _wait_for_event replacement
                        if "def _wait_for_event(self, event, timeout):" in content:
                             content = content.replace("try:\n            event.wait(timeout)\n        except RuntimeError:\n            pass", "event.wait(timeout)")
                             content = content.replace("try:\n            asyncio.wait_for(event.wait(), timeout=timeout)\n        except asyncio.TimeoutError:\n            pass", "event.wait(timeout)")
                             content = content.replace("asyncio.wait_for(event.wait(), timeout=timeout)", "event.wait(timeout)")

                        # _create_task
                        content = content.replace("def _create_task(self, func):", "def _create_task(self, func):")
                        content = content.replace("return asyncio.create_task(coro_func())", "t = threading.Thread(target=coro_func, daemon=True); t.start(); return t")
                        content = content.replace("return asyncio.create_task(func())", "t = threading.Thread(target=func, daemon=True); t.start(); return t")

                        # _create_event
                        content = content.replace("return asyncio.Event()", "return threading.Event()")
                        content = content.replace("stop_event = asyncio.Event()", "stop_event = threading.Event()")

                        # _run_in_thread
                        content = content.replace("return asyncio.to_thread(func, *args)", "return func(*args)")
                        content = content.replace("return await asyncio.to_thread(func, *args)", "return func(*args)")

                    if "browser_agent.py" in file:
                        content = content.replace("asyncio.get_event_loop().run_until_complete(", "")
                        pass

                    # Test specific cleanup
                    content = content.replace("@pytest.mark.asyncio", "@pytest.mark.sync")
                    content = content.replace("@pytest_asyncio.fixture", "@pytest.fixture")
                    content = content.replace("import pytest_asyncio", "import pytest")

                    with open(path, "w") as f:
                        f.write(content)

if __name__ == "__main__":
    print(f"Generating sync code from {ASYNC_DIR} to {SYNC_DIR}...")
    print(f"Generating sync tests from {TEST_ASYNC_DIR} to {TEST_SYNC_DIR}...")
    generate_sync()
    print("Done.")
