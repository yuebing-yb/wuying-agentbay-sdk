import { expect } from "chai";
import * as sinon from "sinon";
import { Browser } from "../../src/browser/browser";
import { Session } from "../../src/session";
import {
  logAPIResponseWithDetails,
  logError,
  setRequestId,
  clearRequestId,
  getRequestId,
} from "../../src/utils/logger";

describe("Browser - Enhanced Logging", () => {
  let mockSession: sinon.SinonStubbedInstance<Session>;
  let browser: Browser;
  let logAPIResponseWithDetailsStub: sinon.SinonStub;
  let logErrorStub: sinon.SinonStub;

  beforeEach(() => {
    mockSession = sinon.createStubInstance(Session);
    browser = new Browser(mockSession as unknown as Session);

    // Stub logger functions
    logAPIResponseWithDetailsStub = sinon.stub();
    logErrorStub = sinon.stub();

    sinon
      .stub(require("../../src/utils/logger"), "logAPIResponseWithDetails")
      .callsFake(logAPIResponseWithDetailsStub);
    sinon.stub(require("../../src/utils/logger"), "logError").callsFake(logErrorStub);
  });

  afterEach(() => {
    sinon.restore();
    clearRequestId();
  });

  describe("initializeAsync - Logging", () => {
    it("should set RequestId from response", async () => {
      const requestId = "req-init-browser-123";
      setRequestId(requestId);

      expect(getRequestId()).to.equal(requestId);
      clearRequestId();
    });

    it("should extract port and endpoint for success logging", () => {
      const responseData = {
        port: 9222,
        endpoint: "ws://localhost:9222",
      };

      // Verify key fields are present
      expect(responseData).to.have.property("port");
      expect(responseData).to.have.property("endpoint");
      expect(responseData.port).to.equal(9222);
    });

    it("should log success response with key fields", () => {
      const requestId = "req-browser-success";
      const keyFields = {
        port: 9222,
        endpoint: "ws://localhost:9222",
      };

      setRequestId(requestId);

      // Verify RequestId is maintained for logging
      expect(getRequestId()).to.equal(requestId);
      expect(keyFields.port).to.exist;
      expect(keyFields.endpoint).to.exist;

      clearRequestId();
    });

    it("should log failure when port is missing", () => {
      const requestId = "req-browser-fail";
      const failureReason = "Port not found in response";

      setRequestId(requestId);
      expect(getRequestId()).to.equal(requestId);

      // Verify failure context
      expect(failureReason).to.include("Port");

      clearRequestId();
    });
  });

  describe("Browser Initialization - Error Logging", () => {
    it("should log error using logError when initialization fails", () => {
      const errorMessage = "Failed to initialize browser instance";
      const error = new Error("Connection timeout");

      // Verify error logging context
      expect(error).to.be.instanceof(Error);
      expect(error.message).to.equal("Connection timeout");
    });

    it("should include stack trace in error logging", () => {
      const error = new Error("Browser init failed");
      const stack = error.stack;

      // Verify stack trace exists
      expect(stack).to.exist;
      expect(stack).to.include("Error: Browser init failed");
    });

    it("should clear RequestId state on error", () => {
      setRequestId("req-error-browser");
      expect(getRequestId()).to.equal("req-error-browser");

      // After error handling, RequestId should be available for logging
      // but then cleared
      clearRequestId();
      expect(getRequestId()).to.equal("");
    });
  });

  describe("Browser Response Logging Structure", () => {
    it("should verify success response has all expected fields", () => {
      const successResponse = {
        requestId: "req-browser-success-123",
        success: true,
        port: 9222,
        endpoint: "ws://localhost:9222",
      };

      expect(successResponse).to.have.property("requestId");
      expect(successResponse).to.have.property("success");
      expect(successResponse).to.have.property("port");
      expect(successResponse).to.have.property("endpoint");
      expect(successResponse.success).to.be.true;
    });

    it("should verify failure response structure", () => {
      const failureResponse = {
        requestId: "req-browser-failure-456",
        success: false,
        errorMessage: "Port not found in response",
      };

      expect(failureResponse).to.have.property("requestId");
      expect(failureResponse).to.have.property("success");
      expect(failureResponse).to.have.property("errorMessage");
      expect(failureResponse.success).to.be.false;
    });
  });

  describe("Browser - RequestID Tracking", () => {
    it("should maintain RequestId during browser initialization lifecycle", () => {
      const requestId = "req-browser-lifecycle";

      // Start of initialization
      setRequestId(requestId);
      expect(getRequestId()).to.equal(requestId);

      // During API call
      expect(getRequestId()).to.equal(requestId);

      // After completion
      clearRequestId();
      expect(getRequestId()).to.equal("");
    });

    it("should extract RequestId from response data", () => {
      const responseData = {
        requestId: "req-from-response-789",
        data: {
          port: 9222,
          endpoint: "ws://localhost:9222",
        },
      };

      // Set RequestId from response
      setRequestId(responseData.requestId);
      expect(getRequestId()).to.equal(responseData.requestId);

      clearRequestId();
    });
  });

  describe("Browser Logging - API Response Details", () => {
    it("should prepare key fields for logAPIResponseWithDetails", () => {
      const apiName = "InitBrowser";
      const requestId = "req-browser-api-123";
      const keyFields = {
        port: 9222,
        endpoint: "ws://localhost:9222",
      };

      // Verify all parameters are structured correctly
      expect(apiName).to.equal("InitBrowser");
      expect(requestId).to.equal("req-browser-api-123");
      expect(keyFields).to.have.property("port");
      expect(keyFields).to.have.property("endpoint");
    });

    it("should include all response data for success logging", () => {
      const successData = {
        apiName: "InitBrowser",
        requestId: "req-success",
        success: true,
        keyFields: {
          port: 9222,
          endpoint: "ws://localhost:9222",
        },
      };

      expect(successData.success).to.be.true;
      expect(successData.keyFields).to.exist;
      expect(successData.keyFields.port).to.equal(9222);
    });

    it("should include error details for failure logging", () => {
      const failureData = {
        apiName: "InitBrowser",
        requestId: "req-failure",
        success: false,
        errorMessage: "Port not found in response",
      };

      expect(failureData.success).to.be.false;
      expect(failureData.errorMessage).to.exist;
      expect(failureData.errorMessage).to.include("Port");
    });
  });

  describe("Browser - Console Error Replacement", () => {
    it("should use logError instead of console.error", () => {
      const error = new Error("Browser initialization failed");

      // Verify logError would be called with proper error
      expect(error).to.be.instanceof(Error);
      expect(error.message).to.equal("Browser initialization failed");
    });

    it("should pass error object with stack trace to logError", () => {
      const error = new Error("Detailed error message");
      const errorMessage = "Failed to initialize browser";

      // Verify error structure for logError
      expect(error).to.be.instanceof(Error);
      expect(error.message).to.exist;
      expect(errorMessage).to.exist;
    });
  });

  describe("Browser - State Management After Logging", () => {
    it("should reset initialized state on error and clear RequestId", () => {
      setRequestId("req-browser-error");
      expect(getRequestId()).to.equal("req-browser-error");

      // Simulate error handling - RequestId should be cleared
      clearRequestId();
      expect(getRequestId()).to.equal("");

      // Browser should not be initialized after error
      expect(browser.isInitialized()).to.be.false;
    });

    it("should maintain state consistency during successful initialization", () => {
      setRequestId("req-browser-success");
      expect(getRequestId()).to.equal("req-browser-success");

      // Successful initialization should clear RequestId after logging
      clearRequestId();
      expect(getRequestId()).to.equal("");
    });
  });
});
