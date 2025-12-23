/**
 * AgentBay SDK - Jupyter Context Persistence (R & Java) Example (TypeScript)
 *
 * This example demonstrates that consecutive `session.code.runCode()` calls within the same
 * session can share an execution context (Jupyter-like behavior) for R and Java, so variables
 * defined in one call can be reused in subsequent calls.
 */

import { AgentBay } from "wuying-agentbay-sdk";

async function main(): Promise<void> {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    console.error("Error: AGENTBAY_API_KEY environment variable not set");
    process.exit(1);
  }

  const agentBay = new AgentBay({ apiKey });
  const sessionResult = await agentBay.create({ imageId: "code_latest" });
  if (!sessionResult.success || !sessionResult.session) {
    throw new Error(`Failed to create session: ${sessionResult.errorMessage}`);
  }

  const session = sessionResult.session;
  console.log(`Session created: ${session.sessionId}`);

  try {
    console.log("\n===== R: Jupyter-like context persistence =====");
    const rSetup = `
x <- 41
cat("R_CONTEXT_SETUP_DONE\\n")
`.trim();
    const rSetupRes = await session.code.runCode(rSetup, "R");
    if (!rSetupRes.success) {
      throw new Error(`R setup failed: ${rSetupRes.errorMessage}`);
    }
    console.log(rSetupRes.result);

    const rUse = `cat(paste0("R_CONTEXT_VALUE:", x + 1, "\\n"))\n`;
    const rUseRes = await session.code.runCode(rUse, "r");
    if (!rUseRes.success) {
      throw new Error(`R context use failed: ${rUseRes.errorMessage}`);
    }
    console.log(rUseRes.result);

    if (!rUseRes.result.includes("R_CONTEXT_VALUE:42")) {
      throw new Error("R context persistence verification failed");
    }

    console.log("\n===== Java: Jupyter-like context persistence =====");
    const javaSetup = `
int x = 41;
System.out.println("JAVA_CONTEXT_SETUP_DONE");
`.trim();
    const javaSetupRes = await session.code.runCode(javaSetup, "JAVA");
    if (!javaSetupRes.success) {
      throw new Error(`Java setup failed: ${javaSetupRes.errorMessage}`);
    }
    console.log(javaSetupRes.result);

    const javaUse = `System.out.println("JAVA_CONTEXT_VALUE:" + (x + 1));\n`;
    const javaUseRes = await session.code.runCode(javaUse, "java");
    if (!javaUseRes.success) {
      throw new Error(`Java context use failed: ${javaUseRes.errorMessage}`);
    }
    console.log(javaUseRes.result);

    if (!javaUseRes.result.includes("JAVA_CONTEXT_VALUE:42")) {
      throw new Error("Java context persistence verification failed");
    }
  } finally {
    await session.delete();
  }
}

if (require.main === module) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}

export { main };


