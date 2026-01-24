import { AgentBay } from "../../src";

describe("BetaNetwork integration", () => {
  test("get network bind token", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({ apiKey });

    const netResult = await client.betaNetwork.getNetworkBindToken();
    expect(netResult.success).toBe(true);
    expect(netResult.networkId).not.toBe("");
    expect(netResult.networkToken).not.toBe("");
  });
});


