import { AgentBay, newCreateSessionParams } from "../../src";

describe("Network integration", () => {
  test("create/describe network and bind session via networkId", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({ apiKey });

    const netResult = await client.network.getNetworkBindToken();
    expect(netResult.success).toBe(true);
    expect(netResult.networkId).not.toBe("");
    expect(netResult.networkToken).not.toBe("");

    const statusResult = await client.network.describe(netResult.networkId);
    expect(statusResult.success).toBe(true);

    const params = newCreateSessionParams()
      .withImageId("imgc-0ab5takhjgjky7htu")
      .withNetworkId(netResult.networkId)
      .withLabels({ "test-type": "network-integration" });

    const createResult = await client.create(params);
    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    if (!createResult.session) {
      return;
    }

    await createResult.session.delete();
  });
});


