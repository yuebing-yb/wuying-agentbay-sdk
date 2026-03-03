package com.aliyun.agentbay.exception;

/**
 * Raised when a WS stream is cancelled by the caller.
 */
public class WsCancelledException extends AgentBayException {
    public WsCancelledException(String message) {
        super(message);
    }

    public WsCancelledException(String message, Throwable cause) {
        super(message, cause);
    }
}

