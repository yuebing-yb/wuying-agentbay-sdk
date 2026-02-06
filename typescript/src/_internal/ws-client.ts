import { logDebug, maskSensitiveData } from "../utils/logger";

type OnEvent = (invocationId: string, data: Record<string, any>) => void;
type OnEnd = (invocationId: string, data: Record<string, any>) => void;
type OnError = (invocationId: string, err: Error) => void;

function newInvocationId(): string {
  const crypto = require("crypto");
  return crypto.randomBytes(16).toString("hex");
}

function safeStringify(obj: any): string {
  try {
    return JSON.stringify(obj);
  } catch (e) {
    return String(obj);
  }
}

function truncate(s: string, maxLen: number): string {
  if (s.length <= maxLen) return s;
  return s.slice(0, maxLen) + "...";
}

export class WsClient {
  private wsUrl: string;
  private token: string;
  private ws: any | null = null;
  private connecting: Promise<void> | null = null;
  private pendingById = new Map<
    string,
    {
      onEvent?: OnEvent;
      onEnd?: OnEnd;
      onError?: OnError;
      resolveEnd: (data: Record<string, any>) => void;
      rejectEnd: (err: Error) => void;
    }
  >();

  constructor(wsUrl: string, token: string) {
    this.wsUrl = wsUrl;
    this.token = token;
  }

  private logFrame(direction: ">>" | "<<", payload: any): void {
    const raw = safeStringify(payload);
    const masked = String(maskSensitiveData(raw));
    logDebug(`WS ${direction} ${truncate(masked, 1200)}`);
  }

  async connect(): Promise<void> {
    if (this.ws) return;
    if (this.connecting) return this.connecting;

    this.connecting = new Promise<void>((resolve, reject) => {
      const WebSocket = require("ws");
      const ws = new WebSocket(this.wsUrl, {
        headers: {
          "X-Access-Token": this.token,
        },
      });

      ws.on("open", () => {
        this.ws = ws;
        this.connecting = null;
        resolve();
      });

      ws.on("message", (data: any) => {
        this.handleIncoming(data);
      });

      ws.on("error", (err: any) => {
        const e = err instanceof Error ? err : new Error(String(err));
        this.failAllPending(e);
        this.ws = null;
        this.connecting = null;
        reject(e);
      });

      ws.on("close", () => {
        this.failAllPending(new Error("WS connection closed"));
        this.ws = null;
        this.connecting = null;
      });
    });

    return this.connecting;
  }

  async close(): Promise<void> {
    const ws = this.ws;
    this.ws = null;
    this.connecting = null;
    if (!ws) return;
    try {
      ws.close();
    } catch (_e) {
      return;
    }
  }

  async callStream(params: {
    target: string;
    data: Record<string, any>;
    onEvent?: OnEvent;
    onEnd?: OnEnd;
    onError?: OnError;
  }): Promise<{ invocationId: string; waitEnd: () => Promise<Record<string, any>> }> {
    await this.connect();
    const ws = this.ws;
    if (!ws) {
      throw new Error("WS is not connected");
    }

    const invocationId = newInvocationId();
    const payload = {
      invocationId,
      source: "SDK",
      target: params.target,
      data: params.data,
    };

    const endPromise = new Promise<Record<string, any>>((resolve, reject) => {
      this.pendingById.set(invocationId, {
        onEvent: params.onEvent,
        onEnd: params.onEnd,
        onError: params.onError,
        resolveEnd: resolve,
        rejectEnd: reject,
      });
    });

    this.logFrame(">>", payload);
    ws.send(safeStringify(payload));

    return {
      invocationId,
      waitEnd: async () => await endPromise,
    };
  }

  private handleIncoming(raw: any): void {
    const text = typeof raw === "string" ? raw : raw?.toString?.() ?? "";
    let msg: any;
    try {
      msg = JSON.parse(text);
    } catch (e) {
      this.failAllPending(new Error(`Invalid JSON message: ${e}`));
      return;
    }

    if (!msg || typeof msg !== "object") return;
    const invocationId = msg.invocationId || msg.requestId;
    if (!invocationId || typeof invocationId !== "string") return;

    const pending = this.pendingById.get(invocationId);
    if (!pending) return;

    const source = msg.source;
    const data = msg.data;

    if (source === "WEBSOCKET_SERVER") {
      this.logFrame("<<", { invocationId, source, data });
      const errMsg =
        (typeof msg.error === "string" && msg.error) ||
        (data && typeof data === "object" && typeof data.error === "string" ? data.error : "");
      if (errMsg) {
        const err = new Error(errMsg);
        if (pending.onError) pending.onError(invocationId, err);
        pending.rejectEnd(err);
        this.pendingById.delete(invocationId);
        return;
      }
      if (pending.onEnd) pending.onEnd(invocationId, typeof data === "object" ? data : {});
      pending.resolveEnd(typeof data === "object" ? data : {});
      this.pendingById.delete(invocationId);
      return;
    }

    const target = msg.target;
    if (typeof data !== "object" || !data) return;

    this.logFrame("<<", { invocationId, source, target, data });

    if (typeof data.error === "string" && data.error) {
      const err = new Error(data.error);
      if (pending.onError) pending.onError(invocationId, err);
      pending.rejectEnd(err);
      this.pendingById.delete(invocationId);
      return;
    }

    const phase = data.phase;
    if (phase === "event") {
      if (pending.onEvent) pending.onEvent(invocationId, data);
      return;
    }
    if (phase === "end") {
      if (pending.onEnd) pending.onEnd(invocationId, data);
      pending.resolveEnd(data);
      this.pendingById.delete(invocationId);
      return;
    }

    const err = new Error(`Unsupported phase: ${String(phase)}`);
    if (pending.onError) pending.onError(invocationId, err);
    pending.rejectEnd(err);
    this.pendingById.delete(invocationId);
  }

  private failAllPending(err: Error): void {
    for (const [invocationId, pending] of this.pendingById.entries()) {
      if (pending.onError) pending.onError(invocationId, err);
      pending.rejectEnd(err);
    }
    this.pendingById.clear();
  }
}

