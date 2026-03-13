import { AgentBay } from "../../src";
import { ContextSync, newSyncPolicy } from "../../src/context-sync";
import { log } from "../../src/utils/logger";
import fetch from "node-fetch";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";

const apiKey = process.env.AGENTBAY_API_KEY || "";

function createTempFileWithZeros(sizeMB: number): string {
  const filePath = path.join(
    os.tmpdir(),
    `agentbay-beta-wait-${Date.now()}-${Math.random()}.bin`
  );
  const fd = fs.openSync(filePath, "w");
  try {
    const chunk = Buffer.alloc(1024 * 1024, 0);
    for (let i = 0; i < sizeMB; i++) {
      fs.writeSync(fd, chunk);
    }
  } finally {
    fs.closeSync(fd);
  }
  return filePath;
}

async function uploadFileWithRetries(
  uploadUrl: string,
  localPath: string,
  maxAttempts = 5
): Promise<void> {
  const stat = fs.statSync(localPath);
  let lastError: any = null;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const stream = fs.createReadStream(localPath);
      const resp = await fetch(uploadUrl, {
        method: "PUT",
        body: stream as any,
        headers: {
          "Content-Length": String(stat.size),
        },
      });
      if ([200, 204].includes(resp.status)) {
        return;
      }
      lastError = new Error(`upload failed: status=${resp.status}`);
    } catch (e: any) {
      lastError = e;
    }
    if (attempt < maxAttempts) {
      const waitMs = Math.min(2 ** attempt * 1000, 10000);
      await new Promise((r) => setTimeout(r, waitMs));
    }
  }
  throw new Error(
    `Upload failed after ${maxAttempts} attempts: ${String(
      lastError?.message || lastError
    )}`
  );
}

async function assertDownloadTerminalSuccess(
  session: any,
  contextId: string,
  label: string
): Promise<void> {
  const info = await session.context.infoWithParams(
    contextId,
    undefined,
    "download"
  );
  if (!info.success) {
    throw new Error(
      `${label}: context info failed: ${info.errorMessage || "unknown"}`
    );
  }
  const statuses = (info.contextStatusData || [])
    .filter((it: any) => it.contextId === contextId)
    .map((it: any) => it.status);
  if (!statuses.length) {
    throw new Error(`${label}: expected at least one download status entry`);
  }
  for (const st of statuses) {
    if (st !== "Success" && st !== "Failed") {
      throw new Error(`${label}: non-terminal status=${st}`);
    }
    if (st === "Failed") {
      throw new Error(`${label}: download failed`);
    }
  }
}

async function waitDownloadTerminalSuccess(
  session: any,
  contextId: string,
  timeoutMs: number
): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  let lastStatuses: string[] = [];
  while (Date.now() < deadline) {
    const info = await session.context.infoWithParams(
      contextId,
      undefined,
      "download"
    );
    if (!info.success) {
      throw new Error(
        `Polling: context info failed: ${info.errorMessage || "unknown"}`
      );
    }
    const statuses = (info.contextStatusData || [])
      .filter((it: any) => it.contextId === contextId)
      .map((it: any) => it.status);
    if (statuses.length) {
      lastStatuses = statuses;
    }
    if (
      statuses.length &&
      statuses.every((s: string) => s === "Success" || s === "Failed")
    ) {
      if (statuses.includes("Failed")) {
        throw new Error(
          `Download failed: statuses=${JSON.stringify(statuses)}`
        );
      }
      return;
    }
    await new Promise((r) => setTimeout(r, 2000));
  }
  throw new Error(
    `Download did not complete within timeout. lastStatuses=${JSON.stringify(
      lastStatuses
    )}`
  );
}

describe("Session create betaWaitForCompletion (integration)", () => {
  jest.setTimeout(15 * 60 * 1000);

  it("should support wait-both / wait-one / wait-none using betaWaitForCompletion", async () => {
    if (!apiKey || process.env.CI) {
      return;
    }

    const agentBay = new AgentBay({ apiKey });
    const unique = Date.now();

    const ctx1Name = `test-beta-wait-flag-1-${unique}`;
    const ctx2Name = `test-beta-wait-flag-2-${unique}`;
    const ctx1Res = await agentBay.context.get(ctx1Name, true);
    const ctx2Res = await agentBay.context.get(ctx2Name, true);
    if (
      !ctx1Res.success ||
      !ctx1Res.context ||
      !ctx2Res.success ||
      !ctx2Res.context
    ) {
      throw new Error("Failed to create contexts");
    }
    const ctx1Id = (ctx1Res.context as any).id;
    const ctx2Id = (ctx2Res.context as any).id;

    const mount1 = "/tmp/beta-wait-flag-1";
    const mount2 = "/tmp/beta-wait-flag-2";
    const sizeMB = 200;

    const tmpFile = createTempFileWithZeros(sizeMB);
    try {
      const up1 = await agentBay.context.getFileUploadUrl(
        ctx1Id,
        `${mount1}/large.bin`
      );
      if (!up1.success || !up1.url) {
        throw new Error(
          `Failed to get upload URL for ctx1: ${up1.errorMessage || "unknown"}`
        );
      }
      await uploadFileWithRetries(up1.url, tmpFile, 5);

      const up2 = await agentBay.context.getFileUploadUrl(
        ctx2Id,
        `${mount2}/large.bin`
      );
      if (!up2.success || !up2.url) {
        throw new Error(
          `Failed to get upload URL for ctx2: ${up2.errorMessage || "unknown"}`
        );
      }
      await uploadFileWithRetries(up2.url, tmpFile, 5);

      const imageId = "linux_latest";

      const waitBothSyncs = [
        new ContextSync(ctx1Id, mount1, newSyncPolicy()),
        new ContextSync(ctx2Id, mount2, newSyncPolicy()),
      ];
      const t0 = Date.now();
      const waitBothRes = await agentBay.create({
        imageId,
        labels: { test: "beta-wait-flag", mode: "wait-both" },
        contextSync: waitBothSyncs,
      });
      const tWaitBoth = Date.now() - t0;
      if (!waitBothRes.success || !waitBothRes.session) {
        throw new Error(
          `Create wait-both failed: ${waitBothRes.errorMessage || "unknown"}`
        );
      }
      const sWaitBoth = waitBothRes.session;
      await assertDownloadTerminalSuccess(sWaitBoth, ctx1Id, "wait-both ctx1");
      await assertDownloadTerminalSuccess(sWaitBoth, ctx2Id, "wait-both ctx2");

      const waitOneSyncs = [
        new ContextSync(ctx1Id, mount1, newSyncPolicy()),
        new ContextSync(
          ctx2Id,
          mount2,
          newSyncPolicy()
        ).withBetaWaitForCompletion(false),
      ];
      const t1 = Date.now();
      const waitOneRes = await agentBay.create({
        imageId,
        labels: { test: "beta-wait-flag", mode: "wait-one" },
        contextSync: waitOneSyncs,
      });
      const tWaitOne = Date.now() - t1;
      if (!waitOneRes.success || !waitOneRes.session) {
        throw new Error(
          `Create wait-one failed: ${waitOneRes.errorMessage || "unknown"}`
        );
      }
      const sWaitOne = waitOneRes.session;
      await assertDownloadTerminalSuccess(sWaitOne, ctx1Id, "wait-one ctx1");
      await waitDownloadTerminalSuccess(sWaitOne, ctx2Id, 4 * 60 * 1000);

      const waitNoneSyncs = [
        new ContextSync(
          ctx1Id,
          mount1,
          newSyncPolicy()
        ).withBetaWaitForCompletion(false),
        new ContextSync(
          ctx2Id,
          mount2,
          newSyncPolicy()
        ).withBetaWaitForCompletion(false),
      ];
      const t2 = Date.now();
      const waitNoneRes = await agentBay.create({
        imageId,
        labels: { test: "beta-wait-flag", mode: "wait-none" },
        contextSync: waitNoneSyncs,
      });
      const tWaitNone = Date.now() - t2;
      if (!waitNoneRes.success || !waitNoneRes.session) {
        throw new Error(
          `Create wait-none failed: ${waitNoneRes.errorMessage || "unknown"}`
        );
      }
      const sWaitNone = waitNoneRes.session;
      await waitDownloadTerminalSuccess(sWaitNone, ctx1Id, 4 * 60 * 1000);
      await waitDownloadTerminalSuccess(sWaitNone, ctx2Id, 4 * 60 * 1000);

      log(
        `Create durations (ms): wait-both=${tWaitBoth} wait-one=${tWaitOne} wait-none=${tWaitNone}`
      );

      await agentBay.delete(sWaitBoth);
      await agentBay.delete(sWaitOne);
      await agentBay.delete(sWaitNone);
    } finally {
      try {
        fs.unlinkSync(tmpFile);
      } catch (e) {
        // ignore
      }
      try {
        await agentBay.context.delete({ id: ctx1Id, name: ctx1Name } as any);
      } catch (e) {
        // ignore
      }
      try {
        await agentBay.context.delete({ id: ctx2Id, name: ctx2Name } as any);
      } catch (e) {
        // ignore
      }
    }
  });
});
