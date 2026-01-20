import { AgentBay } from "wuying-agentbay-sdk";
import fs from "node:fs";
import path from "node:path";

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY is not set");
  }

  const agentBay = new AgentBay({ apiKey });
  const create = await agentBay.create({ imageId: "imgc-0ab5takhnmlvhx9gp" });
  if (!create.success || !create.session) {
    throw new Error(`Failed to create session: ${create.errorMessage || ""}`);
  }

  const session = create.session;
  try {
    await new Promise((resolve) => setTimeout(resolve, 15000));

    const cmds = ["wm size 720x1280", "wm density 160"];
    for (const c of cmds) {
      const r = await session.command.executeCommand(c, 10000);
      if (!r.success) {
        throw new Error(`Command failed: ${c} error=${r.errorMessage || ""}`);
      }
    }

    const start = await session.mobile.startApp("monkey -p com.android.settings 1");
    if (!start.success) {
      throw new Error(`Failed to start Settings: ${start.errorMessage || ""}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const nav = await session.command.executeCommand("am start -a android.settings.SETTINGS", 10000);
    if (!nav.success) {
      throw new Error(`Command failed: am start -a android.settings.SETTINGS error=${nav.errorMessage || ""}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const outDir = "./tmp";
    fs.mkdirSync(outDir, { recursive: true });

    const s1 = await session.mobile.betaTakeScreenshot();
    if (!s1.success) {
      throw new Error(`beta_take_screenshot failed: ${s1.errorMessage || ""}`);
    }
    const p1 = path.join(outDir, "mobile_beta_screenshot.png");
    fs.writeFileSync(p1, Buffer.from(s1.data));
    console.log(
      `Saved ${p1} (${s1.data.length} bytes, size=${s1.width}x${s1.height})`
    );

    const s2 = await session.mobile.betaTakeLongScreenshot(2, "png");
    if (!s2.success) {
      console.error(`beta_take_long_screenshot failed: ${s2.errorMessage || ""}`);
      return;
    }
    const p2 = path.join(outDir, "mobile_beta_long_screenshot.png");
    fs.writeFileSync(p2, Buffer.from(s2.data));
    console.log(
      `Saved ${p2} (${s2.data.length} bytes, size=${s2.width}x${s2.height})`
    );
  } finally {
    await session.delete();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});

