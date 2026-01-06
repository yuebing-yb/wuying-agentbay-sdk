import os

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY is required")

    agent_bay = AsyncAgentBay(api_key=api_key)

    # When the cloud CreateSession response provides LinkUrl/ToolList, the SDK can:
    # - expose LinkUrl/Token from the session
    # - call MCP tools through the LinkUrl route (Java BaseService style)
    params = CreateSessionParams(
        image_id="imgc-0ab5takhjgjky7htu",
        is_vpc=True,
        labels={"example": "link-url-session"},
    )

    create_result = await agent_bay.create(params)
    if not create_result.success or not create_result.session:
        raise RuntimeError(create_result.error_message or "Failed to create session")

    session = create_result.session
    try:
        print(f"session_id={session.session_id}")
        print(f"token={session.get_token()}")
        print(f"link_url={session.get_link_url()}")
        print(f"mcp_tools_count={len(session.mcp_tools)}")

        cmd = await session.command.execute_command("echo hello-from-link-url-session")
        if not cmd.success:
            raise RuntimeError(cmd.error_message or "execute_command failed")
        print(cmd.output)
    finally:
        await session.delete()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())






