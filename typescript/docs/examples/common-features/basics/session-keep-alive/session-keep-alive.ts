import { AgentBay, log, logError, CreateSessionParams } from "wuying-agentbay-sdk";

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable is not set");
  }

  const agentBay = new AgentBay({ apiKey });
  let session: any = null;

  try {
    const params: CreateSessionParams = {
      imageId: "linux_latest",
      idleReleaseTimeout: 30,
      labels: { example: "session-keep-alive", sdk: "typescript" },
    };

    const create = await agentBay.create(params);
    if (!create.success || !create.session) {
      throw new Error(`Failed to create session: ${create.errorMessage || "Unknown error"}`);
    }
    session = create.session;
    log(`Session ID: ${session.sessionId}`);

    log("Sleeping for 15 seconds...");
    await sleep(15000);

    log("Calling keepAlive() to refresh idle timer...");
    const keepAliveResult = await session.keepAlive();
    log(`keepAlive success: ${keepAliveResult.success}`);
    log(`requestId: ${keepAliveResult.requestId || ""}`);
    if (!keepAliveResult.success) {
      log(`error: ${keepAliveResult.errorMessage || ""}`);
    }
  } catch (error) {
    logError("Error:", error);
  } finally {
    if (session) {
      await agentBay.delete(session);
    }
  }
}

main().catch(err => {
  logError("Error in main:", err);
  process.exit(1);
});

