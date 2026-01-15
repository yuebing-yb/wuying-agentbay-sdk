"use strict";
/**
 * Basic usage example for AgentBay Browser functionality in TypeScript.
 * This example demonstrates the core browser operations without external dependencies.
 */
Object.defineProperty(exports, "__esModule", { value: true });
const wuying_agentbay_sdk_1 = require("wuying-agentbay-sdk");
const zod_1 = require("zod");
const PageInfoSchema = zod_1.z.object({
    title: zod_1.z.string().describe("page title"),
    url: zod_1.z.string().describe("page url"),
});
async function main() {
    // Get API key from environment variable
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log("Error: AGENTBAY_API_KEY environment variable not set");
        return;
    }
    try {
        // Initialize AgentBay client
        console.log("Initializing AgentBay client...");
        const agentBay = new wuying_agentbay_sdk_1.AgentBay({ apiKey });
        // Create a session with browser image
        console.log("Creating a new session...");
        const params = new wuying_agentbay_sdk_1.CreateSessionParams();
        params.withImageId("browser_latest");
        const sessionResult = await agentBay.create(params);
        if (!sessionResult.success) {
            console.log("Failed to create session");
            return;
        }
        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);
        // Initialize browser
        console.log("Initializing browser...");
        // Note: persistentPath is currently ignored by the SDK implementation
        const initialized = await session.browser.initializeAsync({});
        if (!initialized) {
            console.log("Failed to initialize browser");
            return;
        }
        console.log("Browser initialized successfully");
        // Get browser endpoint for external connections (like Playwright)
        const endpointUrl = await session.browser.getEndpointUrl();
        console.log("Browser endpoint URL:", endpointUrl);
        // Example: Mock page object (in real usage, you'd get this from Playwright)
        const mockPage = {
            url: () => "https://example.com",
            title: () => "Example Domain",
        };
        // Example 1: Perform an action
        console.log("\n--- Example 1: Performing an action ---");
        try {
            const actOptions = {
                action: "Click the 'More information...' link",
                timeout: 5,
            };
            const actResult = await session.browser.agent.act(actOptions, mockPage);
            console.log("Action result:", {
                success: actResult.success,
                message: actResult.message,
            });
        }
        catch (error) {
            console.log("Action failed:", error);
        }
        // Example 2: Observe elements on the page
        console.log("\n--- Example 2: Observing page elements ---");
        try {
            const observeOptions = {
                instruction: "Find all links and buttons on the page",
            };
            const [observeSuccess, observations] = await session.browser.agent.observe(observeOptions, mockPage);
            console.log("Observe success:", observeSuccess);
            console.log("Number of observations:", observations.length);
            observations.forEach((obs, index) => {
                console.log(`Observation ${index + 1}:`, {
                    selector: obs.selector,
                    description: obs.description,
                    method: obs.method,
                });
            });
        }
        catch (error) {
            console.log("Observation failed:", error);
        }
        // Example 3: Extract structured data from the page
        console.log("\n--- Example 3: Extracting structured data ---");
        try {
            const extractOptions = {
                instruction: "Extract the page title and URL",
                schema: PageInfoSchema,
                use_text_extract: false,
            };
            const [extractSuccess, extracted] = await session.browser.agent.extract(extractOptions, mockPage);
            console.log("Extract success:", extractSuccess);
            if (extractSuccess && extracted) {
                console.log("Extracted data:", {
                    title: extracted.title,
                    url: extracted.url,
                });
            }
        }
        catch (error) {
            console.log("Extraction failed:", error);
        }
        // Clean up
        console.log("\n--- Cleanup ---");
        console.log("Browser session completed successfully");
    }
    catch (error) {
        console.error("Error in main function:", error);
    }
}
if (require.main === module) {
    main().catch(console.error);
}
