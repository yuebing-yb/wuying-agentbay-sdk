package com.aliyun.agentbay.model;

/**
 * Result object containing screenshot image bytes.
 */
public class ScreenshotBytesResult extends ApiResponse {
    private boolean success;
    private byte[] data;
    private String format;
    private String errorMessage;

    public ScreenshotBytesResult() {
        this("", false, new byte[0], "png", "");
    }

    public ScreenshotBytesResult(String requestId, boolean success, byte[] data, String format, String errorMessage) {
        super(requestId);
        this.success = success;
        this.data = data != null ? data : new byte[0];
        this.format = format != null ? format : "png";
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public byte[] getData() {
        return data;
    }

    public void setData(byte[] data) {
        this.data = data != null ? data : new byte[0];
    }

    public String getFormat() {
        return format;
    }

    public void setFormat(String format) {
        this.format = format != null ? format : "png";
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }
}

