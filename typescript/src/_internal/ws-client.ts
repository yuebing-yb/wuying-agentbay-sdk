import crypto from "crypto";
import type { WebSocket as WsType } from "./ws";
import { logDebug, logWarn, maskSensitiveData } from "../utils/logger";
import { WsCancelledError } from "../exceptions";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const WebSocketImpl: typeof WsType = require("ws");

type OnEvent = (invocationId: string, data: Record<string, any>) => void;
type OnEnd = (invocationId: string, data: Record<string, any>) => void;
type OnError = (invocationId: string, err: Error) => void;
type PushCallback = (payload: { requestId: string; target: string; data: Record<string, any> }) => void | Promise<void>;

function newInvocationId(): string {
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
  private callbacksByTarget = new Map<string, Set<PushCallback>>();
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

  registerCallback(target: string, callback: PushCallback): () => void {
    if (!target || typeof target !== "string") {
      throw new Error("target must be a non-empty string");
    }
    if (typeof callback !== "function") {
      throw new Error("callback must be a function");
    }
    if (!this.callbacksByTarget.has(target)) {
      this.callbacksByTarget.set(target, new Set());
    }
    this.callbacksByTarget.get(target)?.add(callback);
    return () => this.unregisterCallback(target, callback);
  }

  unregisterCallback(target: string, callback?: PushCallback): void {
    if (!target || typeof target !== "string") {
      throw new Error("target must be a non-empty string");
    }
    if (!callback) {
      this.callbacksByTarget.delete(target);
      return;
    }
    const set = this.callbacksByTarget.get(target);
    if (!set) return;
    set.delete(callback);
    if (set.size === 0) {
      this.callbacksByTarget.delete(target);
    }
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
      const ws = new WebSocketImpl(this.wsUrl, {
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

  /**
   * Send a message to the target without expecting a response.
   * Used for one-way notifications like browser callback messages.
   * 
   * @param target - The target service identifier
   * @param data - The message data to send
   */
  async sendMessage(target: string, data: Record<string, any>): Promise<void> {
    await this.connect();
    const ws = this.ws;
    if (!ws) {
      throw new Error("WS is not connected");
    }

    const invocationId = newInvocationId();
    const payload = {
      invocationId,
      source: "SDK",
      target,
      data,
    };

    this.logFrame(">>", payload);
    ws.send(safeStringify(payload));
  }

  async callStream(params: {
    target: string;
    data: Record<string, any>;
    onEvent?: OnEvent;
    onEnd?: OnEnd;
    onError?: OnError;
  }): Promise<{
    invocationId: string;
    waitEnd: () => Promise<Record<string, any>>;
    cancel: () => Promise<void>;
  }> {
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
      cancel: async () => {
        this.cancelPending(invocationId);
      },
    };
  }

  private cancelPending(invocationId: string): void {
    const pending = this.pendingById.get(invocationId);
    if (!pending) return;
    const err = new WsCancelledError(`Stream ${invocationId} was cancelled by caller`);
    try {
      if (pending.onError) pending.onError(invocationId, err);
    } catch (_e) {
    }
    pending.rejectEnd(err);
    this.pendingById.delete(invocationId);
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
    const source = msg.source;
    const target = msg.target;
    const dataAny = msg.data;

    let data: Record<string, any> | null = null;
    if (dataAny && typeof dataAny === "object") {
      data = dataAny;
    } else if (typeof dataAny === "string") {
      try {
        const parsed = JSON.parse(dataAny);
        if (parsed && typeof parsed === "object") {
          logWarn("WS protocol violation: backend sent data as string; decoded to object");
          data = parsed;
        }
      } catch (_e) {
        data = null;
      }
    }

    if (!pending) {
      const routeTarget =
        target === "SDK" && typeof source === "string" && source && source !== "SDK"
          ? source
          : target;
      if (!routeTarget || typeof routeTarget !== "string") return;
      if (!data) return;
      const callbacks = Array.from(this.callbacksByTarget.get(routeTarget) ?? []);
      if (callbacks.length === 0) return;
      const payload = { requestId: invocationId, target: routeTarget, data };
      for (const cb of callbacks) {
        try {
          const r = cb(payload);
          if (r && typeof (r as any).then === "function") {
            (r as Promise<void>).catch(() => undefined);
          }
        } catch (_e) {
          continue;
        }
      }
      return;
    }

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
      const endData = data ?? {};
      if (pending.onEnd) pending.onEnd(invocationId, endData);
      pending.resolveEnd(endData);
      this.pendingById.delete(invocationId);
      return;
    }

    if (!data) return;

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

