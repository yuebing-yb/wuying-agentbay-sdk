import { expect } from "chai";
import * as sinon from "sinon";
import { Session } from "../../src/session";
import * as logger from "../../src/utils/logger";

describe("Session LinkUrl logging", () => {
  let fetchStub: sinon.SinonStub;
  let logStub: sinon.SinonStub;
  let hadFetch: boolean;

  beforeEach(() => {
    logger.setupLogger({ enableConsole: true, level: "ERROR" });
    logger.setLogLevel("ERROR");

    logStub = sinon.stub(logger, "logAPIResponseWithDetails");
    hadFetch = typeof (globalThis as any).fetch === "function";
    if (!hadFetch) {
      (globalThis as any).fetch = async () => {
        throw new Error("fetch not implemented");
      };
    }
    fetchStub = sinon.stub(globalThis as any, "fetch");
  });

  afterEach(() => {
    sinon.restore();
    if (!hadFetch) {
      delete (globalThis as any).fetch;
    }
  });

  it("should pass response body to logger on non-2xx LinkUrl response", async () => {
    const s = new Session({ getAPIKey: () => "ak" } as any, "sess-1");
    s.linkUrl = "http://127.0.0.1:9999";
    s.token = "tok_abcdef";

    fetchStub.resolves({
      ok: false,
      status: 502,
      text: async () => '{"code":"BadGateway","message":"upstream","token":"tok_123456"}',
    });

    const result = await s.callMcpTool("long_screenshot", { format: "png", max_screens: 2 }, false, "android");
    expect(result.success).to.equal(false);

    const calls = logStub.getCalls().filter(c => c.args[0] === "CallMcpTool(LinkUrl) Response");
    expect(calls.length).to.equal(1);
    expect(calls[0].args[2]).to.equal(false);
    expect(calls[0].args[3]).to.deep.include({ http_status: 502, tool_name: "long_screenshot" });
    expect(String(calls[0].args[4])).to.include("BadGateway");
    expect(String(calls[0].args[4])).to.include("tok_123456");
  });
});

