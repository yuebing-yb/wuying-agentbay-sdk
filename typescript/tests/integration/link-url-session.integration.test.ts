import { AgentBay } from "../../src";

describe("LinkUrl session integration", () => {
  test("create returns linkUrl/token and callMcpTool prefers linkUrl route", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({ apiKey });

    const createResult = await client.create({
      imageId: "linux_latest",
      labels: { "test-type": "link-url-integration" },
    });

    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    if (!createResult.session) {
      return;
    }

    const session = createResult.session;
    try {
      if (session.getToken() === "" || session.getLinkUrl() === "") {
        return;
      }

      const cmdResult = await session.command.executeCommand(
        "echo link-url-route-ok"
      );
      expect(cmdResult.success).toBe(true);
      expect(cmdResult.output).toContain("link-url-route-ok");

      const direct = await session.callMcpTool(
        "shell",
        { command: "echo direct-link-url-route-ok" },
        false,
        "wuying_shell"
      );
      expect(direct.success).toBe(true);
      expect(direct.data).toContain("direct-link-url-route-ok");
    } finally {
      await session.delete();
    }
  });
});

