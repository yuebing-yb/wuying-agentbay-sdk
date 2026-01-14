# Computer Linux as an All-in-One Sandbox (Computer + Browser + Code)

This use case explains a practical pattern: treating a **Linux Computer** session as an **all-in-one sandbox**.

With the `linux_latest` image, you can use:

- `session.computer` for Linux desktop automation
- `session.browser` for browser automation
- `session.code` for code execution (e.g., Python)

This is useful when you want a single session that can both interact with UI and run scripts (or quickly fetch something from the web) without switching images.

## Prerequisites

- Set `AGENTBAY_API_KEY` in your environment
- AgentBay Python SDK installed

## Implementation Examples (Python, Sync)

The following examples use the **same** `linux_latest` session type and demonstrate:

- Running code via `session.code.run_code()`
- Using browser agent APIs via `session.browser`

### Example 1: Run code inside `linux_latest` (Codespace-like)

```python
import os

from agentbay import AgentBay, CreateSessionParams


def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY environment variable not set")

    ab = AgentBay(api_key=api_key)
    create_result = ab.create(CreateSessionParams(image_id="linux_latest"))
    if not create_result.success:
        raise RuntimeError(create_result.error_message)

    session = create_result.session
    try:
        code = """
print("RUN_CODE_OK")
print(6 * 7)
""".strip()
        result = session.code.run_code(code, "python")
        if not result.success:
            raise RuntimeError(result.error_message)
        print(result.result)
    finally:
        session.delete()


if __name__ == "__main__":
    main()
```

### Example 2: Use browser APIs inside `linux_latest`

This example uses the **browser agent APIs** (no local Playwright required): navigate to a page and take a screenshot.

```python
import os

from agentbay import AgentBay, BrowserOption, CreateSessionParams


def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY environment variable not set")

    ab = AgentBay(api_key=api_key)
    create_result = ab.create(CreateSessionParams(image_id="linux_latest"))
    if not create_result.success:
        raise RuntimeError(create_result.error_message)

    session = create_result.session
    try:
        if not session.browser.initialize(BrowserOption()):
            raise RuntimeError("Failed to initialize browser")

        session.browser.agent.navigate("https://example.com")
        data = session.browser.agent.screenshot(full_page=False)
        print("Screenshot data prefix:", data[:30])
    finally:
        session.delete()


if __name__ == "__main__":
    main()
```

## Related Resources

- [Code Execution](../../codespace/code-execution.md)
- [Browser Use Guide](../../browser-use/README.md)
- [Computer Use Guide](../../computer-use/README.md)

