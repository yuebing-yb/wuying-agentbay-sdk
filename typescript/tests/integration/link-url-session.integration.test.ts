import { AgentBay } from "../../src";

describe("LinkUrl session integration", () => {
  test("create returns linkUrl/toolList and callMcpTool prefers linkUrl route", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({ apiKey });

    const createResult = await client.create({
      imageId: "imgc-0ab5takhjgjky7htu",
      isVpc: true,
      labels: { "test-type": "link-url-integration" },
    });

    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    if (!createResult.session) {
      return;
    }

    const session = createResult.session;
    try {
      expect(session.getToken()).not.toBe("");
      expect(session.getLinkUrl()).not.toBe("");
      expect(session.mcpTools.length).toBeGreaterThan(0);

      // Force using LinkUrl route (not legacy ip:port route)
      (session as any).networkInterfaceIp = "";
      (session as any).httpPort = "";

      const cmdResult = await session.command.executeCommand(
        "echo link-url-route-ok"
      );
      expect(cmdResult.success).toBe(true);
      expect(cmdResult.output).toContain("link-url-route-ok");
    } finally {
      await session.delete();
    }
  });
});






