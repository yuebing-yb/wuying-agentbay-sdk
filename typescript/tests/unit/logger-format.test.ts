import { expect } from "chai";
import * as sinon from "sinon";
import {
  setupLogger,
  logAPICall,
  logAPIResponseWithDetails,
  setLogLevel,
} from "../../src/utils/logger";

describe("Logger SLS Format", () => {
  let stdoutWriteStub: sinon.SinonStub;
  let stderrWriteStub: sinon.SinonStub;

  beforeEach(() => {
    stdoutWriteStub = sinon.stub(process.stdout, "write");
    stderrWriteStub = sinon.stub(process.stderr, "write");
    setLogLevel('INFO');
  });

  afterEach(() => {
    sinon.restore();
    delete process.env.AGENTBAY_LOG_FORMAT;
  });

  it("should log API Call in compact format when AGENTBAY_LOG_FORMAT=sls", () => {
    process.env.AGENTBAY_LOG_FORMAT = "sls";
    // We need to re-setup logger to pick up env var if we rely on initial config, 
    // but our implementation checks env var in setupLogger OR if passed in config.
    setupLogger({ enableConsole: true, level: 'INFO' });

    logAPICall("TestAPI", "param=1");

    expect(stdoutWriteStub.called).to.be.true;
    const output = stdoutWriteStub.firstCall.args[0];
    // In our impl: "API Call: ${apiName}, ${maskedData}"
    // maskedData for string "param=1" is "param=1"
    expect(output).to.include("API Call: TestAPI, param=1");
    expect(output).to.not.include("🔗");
  });

  it("should log API Response in compact format when configured via setupLogger", () => {
     setupLogger({ enableConsole: true, level: 'INFO', format: 'sls' });

     logAPIResponseWithDetails("TestAPI", "req-1", true, { key: "value" });

     expect(stdoutWriteStub.called).to.be.true;
     const output = stdoutWriteStub.firstCall.args[0];
     // Impl: "API Response: TestAPI, RequestId=req-1, key=value"
     expect(output).to.include("API Response: TestAPI");
     expect(output).to.include("RequestId=req-1");
     expect(output).to.include("key=value");
     expect(output).to.not.include("✅");
     expect(output).to.not.include("└─");
  });
});

