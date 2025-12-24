import { AgentBay } from "wuying-agentbay-sdk";

async function main(): Promise<void> {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable is not set");
  }

  const agentBay = new AgentBay({ apiKey });
  const create = await agentBay.create({ imageId: "linux_latest" });
  if (!create.success || !create.session) {
    throw new Error(create.errorMessage || "failed to create session");
  }

  const session = create.session;
  try {
    const metrics = await session.getMetrics();
    if (!metrics.success) {
      throw new Error(metrics.errorMessage || "getMetrics failed");
    }
    console.log(metrics.data);
  } finally {
    await session.delete();
  }
}

main().catch((err) => {
  // eslint-disable-next-line no-console
  console.error(err);
  process.exit(1);
});


