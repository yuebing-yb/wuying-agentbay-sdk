import * as sinon from "sinon";
import { AgentBay } from "../../src/agent-bay";
import { Client } from "../../src/api/client";
import { Session } from "../../src/session";

describe("Session.getMetrics", () => {
  let mockAgentBay: sinon.SinonStubbedInstance<AgentBay>;
  let mockClient: sinon.SinonStubbedInstance<Client>;
  let session: Session;

  beforeEach(() => {
    mockClient = sinon.createStubInstance(Client);
    mockAgentBay = sinon.createStubInstance(AgentBay) as unknown as sinon.SinonStubbedInstance<AgentBay>;
    mockAgentBay.getAPIKey.returns("test_api_key");
    mockAgentBay.getClient.returns(mockClient as unknown as Client);
    session = new Session(mockAgentBay as unknown as AgentBay, "test_session_id");
  });

  afterEach(() => {
    sinon.restore();
  });

  it("should exist and be callable", () => {
    expect(typeof (session as any).getMetrics).toBe("function");
  });

  it("should parse JSON string from MCP get_metrics", async () => {
    const raw = {
      cpu_count: 4,
      cpu_used_pct: 1.0,
      disk_total: 105286258688,
      disk_used: 30269431808,
      mem_total: 7918718976,
      mem_used: 2139729920,
      rx_rate_kbyte_per_s: 0.22,
      tx_rate_kbyte_per_s: 0.38,
      rx_used_kbyte: 1247.27,
      tx_used_kbyte: 120.13,
      timestamp: "2025-12-24T10:54:23+08:00",
    };

    sinon.stub(session as any, "callMcpTool").resolves({
      requestId: "req-1",
      success: true,
      data: JSON.stringify(raw),
      errorMessage: "",
    });

    const result = await (session as any).getMetrics();
    expect(result.success).toBe(true);
    expect(result.requestId).toBe("req-1");
    expect(result.data).toBeDefined();
    expect(result.data.cpuCount).toBe(4);
    expect(result.data.cpuUsedPct).toBeCloseTo(1.0, 6);
    expect(result.data.memTotal).toBe(7918718976);
    expect(result.data.diskTotal).toBe(105286258688);
    expect(result.data.rxRateKbytePerS).toBeCloseTo(0.22, 6);
    expect(result.data.txRateKbytePerS).toBeCloseTo(0.38, 6);
    expect(result.data.timestamp).toBe("2025-12-24T10:54:23+08:00");
    expect(result.raw).toBeDefined();
    expect(result.raw.rx_rate_kbyte_per_s).toBeCloseTo(0.22, 6);
    expect(result.raw.tx_rate_kbyte_per_s).toBeCloseTo(0.38, 6);
  });

  it("should return error when JSON is invalid", async () => {
    sinon.stub(session as any, "callMcpTool").resolves({
      requestId: "req-2",
      success: true,
      data: "{not-json}",
      errorMessage: "",
    });

    const result = await (session as any).getMetrics();
    expect(result.success).toBe(false);
    expect(result.requestId).toBe("req-2");
    expect(result.data).toBeUndefined();
    expect(result.errorMessage).toContain("Failed to parse get_metrics response");
  });
});


