import { WebSocketServer } from "ws";

import { WsClient } from "../../src/_internal/ws-client";

function waitForSignal(timeoutMs: number): { promise: Promise<void>; resolve: () => void } {
  let resolve!: () => void;
  const promise = new Promise<void>((res, rej) => {
    resolve = res;
    setTimeout(() => rej(new Error(`timeout after ${timeoutMs}ms`)), timeoutMs);
  });
  return { promise, resolve };
}

describe("WsClient registerCallback", () => {
  test("should route push by target", async () => {
    const wss = new WebSocketServer({ port: 0, host: "127.0.0.1" });
    await new Promise<void>((res) => wss.on("listening", () => res()));
    const addr = wss.address();
    if (!addr || typeof addr === "string") throw new Error("unexpected ws address");
    const url = `ws://127.0.0.1:${addr.port}`;

    const { promise, resolve } = waitForSignal(2000);
    const received: any[] = [];

    wss.on("connection", (ws) => {
      ws.send(
        JSON.stringify({
          requestId: "push_1",
          target: "wuying_cdp_mcp_server",
          data: { method: "notification", hello: "world" },
        })
      );
    });

    const client = new WsClient(url, "token_test");
    client.registerCallback("wuying_cdp_mcp_server", (msg: { requestId: string; target: string; data: any }) => {
      received.push(msg);
      resolve();
    });

    await client.connect();
    await promise;

    expect(received).toEqual([
      {
        requestId: "push_1",
        target: "wuying_cdp_mcp_server",
        data: { method: "notification", hello: "world" },
      },
    ]);

    await client.close();
    wss.close();
  });

  test("should route push by source when target is SDK and data is string JSON", async () => {
    const wss = new WebSocketServer({ port: 0, host: "127.0.0.1" });
    await new Promise<void>((res) => wss.on("listening", () => res()));
    const addr = wss.address();
    if (!addr || typeof addr === "string") throw new Error("unexpected ws address");
    const url = `ws://127.0.0.1:${addr.port}`;

    const { promise, resolve } = waitForSignal(2000);
    const received: any[] = [];

    wss.on("connection", (ws) => {
      ws.send(
        JSON.stringify({
          invocationId: "push_2",
          source: "wuying_cdp_mcp_server",
          target: "SDK",
          data: JSON.stringify({ method: "notification", status: "ok" }),
        })
      );
    });

    const client = new WsClient(url, "token_test");
    client.registerCallback("wuying_cdp_mcp_server", (msg: { requestId: string; target: string; data: any }) => {
      received.push(msg);
      resolve();
    });

    await client.connect();
    await promise;

    expect(received).toEqual([
      {
        requestId: "push_2",
        target: "wuying_cdp_mcp_server",
        data: { method: "notification", status: "ok" },
      },
    ]);

    await client.close();
    wss.close();
  });
});

