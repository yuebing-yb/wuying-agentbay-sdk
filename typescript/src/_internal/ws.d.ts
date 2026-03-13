// Type definitions for the 'ws' WebSocket package.
// Provides type safety without depending on @types/ws resolution,
// which can fail in CI environments using tnpm due to symlink issues.

import { EventEmitter } from "events";
import { ClientRequestArgs } from "http";

export interface WsClientOptions extends ClientRequestArgs {
  headers?: Record<string, string>;
}

export declare class WebSocket extends EventEmitter {
  constructor(address: string, options?: WsClientOptions);
  constructor(
    address: string,
    protocols?: string | string[],
    options?: WsClientOptions
  );

  close(code?: number, data?: string | Buffer): void;
  send(
    data: string | Buffer | ArrayBuffer | SharedArrayBuffer,
    callback?: (err?: Error) => void
  ): void;
  send(
    data: string | Buffer | ArrayBuffer | SharedArrayBuffer,
    options: {
      compress?: boolean;
      binary?: boolean;
      fin?: boolean;
      mask?: boolean;
    },
    callback?: (err?: Error) => void
  ): void;

  on(event: "open", listener: () => void): this;
  on(
    event: "message",
    listener: (data: Buffer | ArrayBuffer | Buffer[]) => void
  ): this;
  on(event: "error", listener: (err: Error) => void): this;
  on(event: "close", listener: (code: number, reason: Buffer) => void): this;
  on(event: string, listener: (...args: any[]) => void): this;
}
