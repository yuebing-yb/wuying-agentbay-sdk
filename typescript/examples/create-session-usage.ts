/**
 * Example demonstrating both interface-style and class-style usage of CreateSessionParams
 */

import { AgentBay,CreateSessionParams, CreateSessionParamsClass,BrowserContext,ContextSync } from "wuying-agentbay-sdk";


async function demonstrateUsage() {
  const agentBay = new AgentBay({ apiKey: process.env.API_KEY || "your-api-key" });

  // Method 1: Using interface-style object (plain object)
  console.log("=== Method 1: Interface-style usage ===");
  const interfaceParams: CreateSessionParams = {
    labels: { project: "demo", env: "test" },
    imageId: "custom-image-123",
    contextSync: [
      new ContextSync("context1", "/tmp/data1"),
      new ContextSync("context2", "/tmp/data2")
    ],
    browserContext: new BrowserContext("browser-ctx-1", true),
    enableBrowserReplay: true,
    framework: "custom-framework"
  };

  try {
    const result1 = await agentBay.create(interfaceParams);
    if (result1.success) {
      console.log("Session created successfully with interface params:", result1.session.sessionId);
      await result1.session.delete();
    }
  } catch (error) {
    console.error("Error with interface params:", error);
  }

  // Method 2: Using class instance with direct instantiation
  console.log("\n=== Method 2: Class instance usage ===");
  const classParams = new CreateSessionParamsClass({
    labels: { project: "demo", env: "production" },
    imageId: "custom-image-456",
    browserContext: new BrowserContext("browser-ctx-2", false),
    isVpc: true,
    mcpPolicyId: "policy-123",
    contextSync: [
      new ContextSync("context3", "/tmp/data3"),
      new ContextSync("context4", "/tmp/data4")
    ]
  });

  // You can also add additional properties that don't exist in the class
  classParams.enableBrowserReplay = false;
  classParams.framework = "langchain";
  classParams.betaNetworkId = "network-456";

  try {
    const result2 = await agentBay.create(classParams);
    if (result2.success) {
      console.log("Session created successfully with class params:", result2.session.sessionId);
      await result2.session.delete();
    }
  } catch (error) {
    console.error("Error with class params:", error);
  }
}

// Export for use in other files
export { demonstrateUsage };