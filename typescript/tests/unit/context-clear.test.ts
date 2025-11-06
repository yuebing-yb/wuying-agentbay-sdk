import { ContextService } from "../../src/context";
import { ClearContextResult } from "../../src/types/api-response";
import { APIError } from "../../src/exceptions";
import * as sinon from "sinon";

describe("Context Clear Operations", () => {
    let mockContextService: ContextService;
    let mockAgentBay: any;
    let mockClient: any;
    let sandbox: sinon.SinonSandbox;

    beforeEach(() => {
        sandbox = sinon.createSandbox();

        mockClient = {
            clearContext: sandbox.stub(),
            getContext: sandbox.stub(),
        };

        mockAgentBay = {
            getAPIKey: sandbox.stub().returns("test-api-key"),
            getClient: sandbox.stub().returns(mockClient),
        };

        mockContextService = new ContextService(mockAgentBay);
    });

    afterEach(() => {
        sandbox.restore();
    });

    describe("clearAsync", () => {
        it("should successfully initiate context clearing", async () => {
            // Mock successful response
            const mockResponse = {
                body: {
                    success: true,
                    requestId: "test-request-id",
                    code: undefined,
                    message: undefined,
                },
            };

            mockClient.clearContext.resolves(mockResponse);

            const result = await mockContextService.clearAsync("context-123");

            expect(result.success).toBe(true);
            expect(result.contextId).toBe("context-123");
            expect(result.status).toBe("clearing");
            expect(result.errorMessage).toBe("");
            expect(result.requestId).toBe("test-request-id");
        });

        it("should handle API errors", async () => {
            // Mock error response
            const mockResponse = {
                body: {
                    success: false,
                    code: "Context.NotFound",
                    message: "Context not found",
                    requestId: "test-request-id",
                },
            };

            mockClient.clearContext.resolves(mockResponse);

            const result = await mockContextService.clearAsync("invalid-context-id");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("[Context.NotFound] Context not found");
            expect(result.requestId).toBe("test-request-id");
        });

        it("should handle empty response body", async () => {
            const mockResponse = {
                body: undefined,
            };

            mockClient.clearContext.resolves(mockResponse);

            const result = await mockContextService.clearAsync("context-123");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("Empty response body");
        });

        it("should throw APIError on network errors", async () => {
            mockClient.clearContext.rejects(new Error("Network error"));

            await expect(mockContextService.clearAsync("context-123")).rejects.toThrow(APIError);
        });
    });

    describe("getClearStatus", () => {
        it("should return clearing status", async () => {
            const mockResponse = {
                body: {
                    success: true,
                    data: {
                        id: "context-123",
                        state: "clearing",
                    },
                    requestId: "test-request-id",
                },
            };

            mockClient.getContext.resolves(mockResponse);

            const result = await mockContextService.getClearStatus("context-123");

            expect(result.success).toBe(true);
            expect(result.contextId).toBe("context-123");
            expect(result.status).toBe("clearing");
            expect(result.requestId).toBe("test-request-id");
        });

        it("should return available status", async () => {
            const mockResponse = {
                body: {
                    success: true,
                    data: {
                        id: "context-123",
                        state: "available",
                    },
                    requestId: "test-request-id",
                },
            };

            mockClient.getContext.resolves(mockResponse);

            const result = await mockContextService.getClearStatus("context-123");

            expect(result.success).toBe(true);
            expect(result.contextId).toBe("context-123");
            expect(result.status).toBe("available");
        });

        it("should handle missing data", async () => {
            const mockResponse = {
                body: {
                    success: true,
                    data: undefined,
                    requestId: "test-request-id",
                },
            };

            mockClient.getContext.resolves(mockResponse);

            const result = await mockContextService.getClearStatus("context-123");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("No data in response");
        });

        it("should handle API errors", async () => {
            const mockResponse = {
                body: {
                    success: false,
                    code: "Context.NotFound",
                    message: "Context not found",
                    requestId: "test-request-id",
                },
            };

            mockClient.getContext.resolves(mockResponse);

            const result = await mockContextService.getClearStatus("invalid-context-id");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("[Context.NotFound] Context not found");
        });
    });

    describe("clear", () => {
        it("should complete clearing successfully", async () => {
            // Mock clearAsync response
            const clearAsyncResponse = {
                body: {
                    success: true,
                    requestId: "clear-request-id",
                },
            };

            // Mock getClearStatus responses (clearing -> available)
            const statusResponses = [
                {
                    body: {
                        success: true,
                        data: {
                            id: "context-123",
                            state: "clearing",
                        },
                        requestId: "status-request-id-1",
                    },
                },
                {
                    body: {
                        success: true,
                        data: {
                            id: "context-123",
                            state: "available",
                        },
                        requestId: "status-request-id-2",
                    },
                },
            ];

            mockClient.clearContext.resolves(clearAsyncResponse);
            mockClient.getContext
                .onFirstCall().resolves(statusResponses[0])
                .onSecondCall().resolves(statusResponses[1]);

            const result = await mockContextService.clear("context-123", 10, 0.1);

            expect(result.success).toBe(true);
            expect(result.contextId).toBe("context-123");
            expect(result.status).toBe("available");
            expect(result.requestId).toBe("clear-request-id");
        });

        it("should timeout if clearing takes too long", async () => {
            const clearAsyncResponse = {
                body: {
                    success: true,
                    requestId: "clear-request-id",
                },
            };

            const statusResponse = {
                body: {
                    success: true,
                    data: {
                        id: "context-123",
                        state: "clearing",
                    },
                    requestId: "status-request-id",
                },
            };

            mockClient.clearContext.resolves(clearAsyncResponse);
            mockClient.getContext.resolves(statusResponse);

            await expect(mockContextService.clear("context-123", 1, 0.5)).rejects.toThrow(APIError);
        });

        it("should return early if clearAsync fails", async () => {
            const clearAsyncResponse = {
                body: {
                    success: false,
                    code: "Context.NotFound",
                    message: "Context not found",
                    requestId: "clear-request-id",
                },
            };

            mockClient.clearContext.resolves(clearAsyncResponse);

            const result = await mockContextService.clear("invalid-context-id");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("[Context.NotFound] Context not found");
        });

        it("should handle status check failures", async () => {
            const clearAsyncResponse = {
                body: {
                    success: true,
                    requestId: "clear-request-id",
                },
            };

            const statusResponse = {
                body: {
                    success: false,
                    code: "Context.NotFound",
                    message: "Context not found",
                    requestId: "status-request-id",
                },
            };

            mockClient.clearContext.resolves(clearAsyncResponse);
            mockClient.getContext.resolves(statusResponse);

            const result = await mockContextService.clear("context-123");

            expect(result.success).toBe(false);
            expect(result.errorMessage).toBe("[Context.NotFound] Context not found");
        });
    });

    describe("ClearContextResult", () => {
        it("should initialize with default values", () => {
            const result: ClearContextResult = {
                requestId: "",
                success: false,
            };

            expect(result.requestId).toBe("");
            expect(result.success).toBe(false);
            expect(result.status).toBeUndefined();
            expect(result.contextId).toBeUndefined();
            expect(result.errorMessage).toBeUndefined();
        });

        it("should initialize with provided values", () => {
            const result: ClearContextResult = {
                requestId: "test-request-id",
                success: true,
                status: "clearing",
                contextId: "context-123",
                errorMessage: "",
            };

            expect(result.requestId).toBe("test-request-id");
            expect(result.success).toBe(true);
            expect(result.status).toBe("clearing");
            expect(result.contextId).toBe("context-123");
            expect(result.errorMessage).toBe("");
        });
    });
});
