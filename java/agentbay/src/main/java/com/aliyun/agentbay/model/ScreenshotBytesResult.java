package com.aliyun.agentbay.model;

/**
 * Result object containing screenshot image bytes.
 */
public class ScreenshotBytesResult extends ApiResponse {
    private boolean success;
    private String type;
    private String mimeType;
    private byte[] data;
    private Integer width;
    private Integer height;
    private String errorMessage;

    public ScreenshotBytesResult() {
        this("", false, "", "", new byte[0], null, null, "");
    }

    public ScreenshotBytesResult(
        String requestId,
        boolean success,
        byte[] data,
        Integer width,
        Integer height,
        String errorMessage
    ) {
        this(requestId, success, "", "", data, width, height, errorMessage);
    }

    public ScreenshotBytesResult(
        String requestId,
        boolean success,
        String type,
        String mimeType,
        byte[] data,
        Integer width,
        Integer height,
        String errorMessage
    ) {
        super(requestId);
        this.success = success;
        this.type = type != null ? type : "";
        this.mimeType = mimeType != null ? mimeType : "";
        this.data = data != null ? data : new byte[0];
        this.width = width;
        this.height = height;
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }

    public ScreenshotBytesResult(
        String requestId,
        boolean success,
        String type,
        String mimeType,
        byte[] data,
        String errorMessage
    ) {
        this(requestId, success, type, mimeType, data, null, null, errorMessage);
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

    public Integer getWidth() {
        return width;
    }

    public void setWidth(Integer width) {
        this.width = width;
    }

    public Integer getHeight() {
        return height;
    }

    public void setHeight(Integer height) {
        this.height = height;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type != null ? type : "";
    }

    public String getMimeType() {
        return mimeType;
    }

    public void setMimeType(String mimeType) {
        this.mimeType = mimeType != null ? mimeType : "";
    }
}

